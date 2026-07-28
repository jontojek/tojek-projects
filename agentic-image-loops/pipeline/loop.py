#!/usr/bin/env python3
"""
exp05 deterministic runner ("written in stone"). v2: adds img2img support.

Watches <run-dir>/inbox/ for step files written by the agent, runs each one
through the frozen workflow, saves the image, appends a row to logs/run.jsonl.
No AI in this file. Ever.

Step file fields:
  n        int   required  iteration number
  prompt   str   required
  seed     int   required
  denoise  float optional  injected into KSampler (i2i runs)
  image_path  str optional  project-side image to use as i2i input; loop.py
                            uploads it to ComfyUI via /upload/image into the
                            input subfolder "exp05_morph" (no manual copying)
  image_input str optional  name already inside ComfyUI's input dir (skips upload)

Protocol:
  agent writes   inbox/step_000.json
  loop.py writes iterations/iter_000.png and appends logs/run.jsonl
  agent (or human) writes inbox/STOP -> graceful exit

Run once per session:
  python loop.py --run-dir <RUN>                                          (t2i)
  python loop.py --run-dir <RUN> --workflow <...>\shared\workflow_api_i2i.json  (i2i)
"""
import argparse
import glob
import json
import os
import re
import time
import urllib.parse
import urllib.request

COMFY_URL = "http://127.0.0.1:8188"
UPLOAD_SUBFOLDER = "exp05_morph"
POLL_S = 1.0


def http_json(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def upload_image(path):
    """Upload a project-side image into ComfyUI's input/<UPLOAD_SUBFOLDER>/."""
    name = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()
    boundary = "----exp05boundary7f3a"

    def field(k, v):
        return (f"--{boundary}\r\nContent-Disposition: form-data; "
                f"name=\"{k}\"\r\n\r\n{v}\r\n").encode()

    body = field("subfolder", UPLOAD_SUBFOLDER) + field("overwrite", "true")
    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
             f"filename=\"{name}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode()
    body += data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{COMFY_URL}/upload/image", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.load(r)
    sub = resp.get("subfolder", "")
    return f"{sub}/{resp['name']}" if sub else resp["name"]


def queue_and_wait(workflow):
    resp = http_json(f"{COMFY_URL}/prompt", {"prompt": workflow})
    pid = resp["prompt_id"]
    while True:
        time.sleep(POLL_S)
        hist = http_json(f"{COMFY_URL}/history/{pid}")
        if pid in hist:
            h = hist[pid]
            status = h.get("status", {})
            if status.get("status_str") == "error":
                raise RuntimeError("ComfyUI error: " + json.dumps(status)[:800])
            if h.get("outputs"):
                return h["outputs"]


def fetch_first_image(outputs):
    for out in outputs.values():
        for im in out.get("images", []):
            q = urllib.parse.urlencode({
                "filename": im["filename"],
                "subfolder": im.get("subfolder", ""),
                "type": im.get("type", "output"),
            })
            with urllib.request.urlopen(f"{COMFY_URL}/view?{q}", timeout=120) as r:
                return r.read()
    raise RuntimeError("workflow produced no image output")


def inject(workflow, prompt, seed, prefix, image_name=None, denoise=None):
    wf = json.loads(json.dumps(workflow))  # deep copy
    for node in wf.values():
        ct = node["class_type"]
        if ct == "CLIPTextEncode":
            node["inputs"]["text"] = prompt
        elif ct == "KSampler":
            node["inputs"]["seed"] = seed
            if denoise is not None:
                node["inputs"]["denoise"] = denoise
        elif ct == "SaveImage":
            node["inputs"]["filename_prefix"] = prefix
        elif ct == "LoadImage" and image_name is not None:
            node["inputs"]["image"] = image_name
    return wf


def already_done(log_path):
    done = set()
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    done.add(json.loads(line)["n"])
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--workflow", default=None,
                    help="default: ../shared/workflow_api_t2i.json relative to run-dir")
    args = ap.parse_args()

    run_dir = os.path.abspath(args.run_dir)
    wf_path = args.workflow or os.path.join(run_dir, "..", "shared", "workflow_api_t2i.json")
    inbox = os.path.join(run_dir, "inbox")
    iters = os.path.join(run_dir, "iterations")
    logs = os.path.join(run_dir, "logs")
    for d in (inbox, iters, logs):
        os.makedirs(d, exist_ok=True)
    log_path = os.path.join(logs, "run.jsonl")

    with open(wf_path, encoding="utf-8") as f:
        base_wf = json.load(f)

    tag = os.path.basename(run_dir)
    print(f"[loop] watching {inbox}")
    print(f"[loop] workflow: {os.path.abspath(wf_path)}")
    print("[loop] write inbox/STOP to end the run.")

    while True:
        if os.path.exists(os.path.join(inbox, "STOP")):
            print("[loop] STOP found. Ending run.")
            break

        done = already_done(log_path)
        pending = []
        for p in glob.glob(os.path.join(inbox, "step_*.json")):
            m = re.search(r"step_(\d+)\.json$", p)
            if m and int(m.group(1)) not in done:
                pending.append((int(m.group(1)), p))
        if not pending:
            time.sleep(POLL_S)
            continue

        n, path = min(pending)
        try:
            with open(path, encoding="utf-8") as f:
                step = json.load(f)
        except (json.JSONDecodeError, OSError):
            time.sleep(POLL_S)  # agent may still be writing the file
            continue

        prompt = step["prompt"]
        seed = step["seed"]
        denoise = step.get("denoise")
        print(f"[loop] iter {n:03d} seed={seed} denoise={denoise} prompt={prompt[:70]!r}")

        row = {
            "n": n, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "prompt": prompt, "seed": seed,
            "steps": 8, "cfg": 1, "sampler": "er_sde/sgm_uniform",
            "width": 1664, "height": 928,
        }
        if denoise is not None:
            row["denoise"] = denoise
        t0 = time.time()
        try:
            image_name = None
            if step.get("image_path"):
                src = step["image_path"]
                if not os.path.isabs(src):
                    src = os.path.join(run_dir, src)
                image_name = upload_image(src)
                row["i2i_input"] = step["image_path"]
            elif step.get("image_input"):
                image_name = step["image_input"]
                row["i2i_input"] = image_name

            wf = inject(base_wf, prompt, seed, f"{tag}_{n:03d}", image_name, denoise)
            outputs = queue_and_wait(wf)
            png = fetch_first_image(outputs)
            img_rel = f"iterations/iter_{n:03d}.png"
            with open(os.path.join(run_dir, img_rel), "wb") as f:
                f.write(png)
            row.update(status="done", image=img_rel, gen_time_s=round(time.time() - t0, 2))
            print(f"[loop] iter {n:03d} done in {row['gen_time_s']}s -> {img_rel}")
        except Exception as e:  # log and keep watching; never die mid-run
            row.update(status="error", error=str(e)[:500], gen_time_s=round(time.time() - t0, 2))
            print(f"[loop] iter {n:03d} ERROR: {e}")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
