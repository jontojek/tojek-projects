"""Render the MiniMax H3 talking-head demo (with LoRA / without LoRA) on ComfyUI.

    D:/AI_software/Fizgig/venv/Scripts/python.exe render_h3.py

Long job: loads the 32B text encoder + 21GB int8 DiT, then renders two clips.
Writes MP4s to loras_j0nt11awm_site/scripts/_renders/h3/.
Base workflow: Hermes_agent_outputs/research_and_create_v03/workflows/minimax_h3_i2v_local.api.json
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

import requests
from PIL import Image

COMFY = "http://127.0.0.1:8188"
COMFY_ROOT = Path(r"D:/AI_software/ComfyUI_windows_portable/ComfyUI")
BASE_WF = Path(r"D:/AI_software/Hermes_agent_outputs/research_and_create_v03/workflows/minimax_h3_i2v_local.api.json")
SITE = Path(r"D:/AI_software/Fizgig/loras_j0nt11awm_site")
OUT = SITE / "scripts" / "_renders" / "h3"
WORK = SITE / "scripts" / "_work"

TRIGGER = "j0nt11awm"
IDENTITY_LORA = "mmh3_t2v_lora_j0nt11awm_v01_fizgig.safetensors"
TURBO_LORA = "minimax_h3_turbo_v4_step600.safetensors"
FIRST_FRAME = Path(r"D:/AI_software/Fizgig/dataset/j0nt11_v02/images/FaceCrop_024.png")

W, H = 768, 1344       # portrait, both sides multiples of 32
FRAMES = 124          # 5 + 7*17
SEED = 20260918
STEPS = 6
TURBO_STRENGTH = 0.75

PROMPT = (
    "integrated_multimodal_description: [Shot 1] A vertical portrait close-up of "
    f"{TRIGGER} man, his head and shoulders filling the tall frame, facing camera and talking in a "
    "relaxed, conversational tone. His whole face is in frame, chin to hairline, and his mouth is "
    "clearly visible and moving as he speaks. He wears a dark grey crewneck t-shirt. He sits in front of "
    "a plain, flat, light grey wall with soft even lighting and nothing else in the background. The "
    "framing stays tight on his face: the camera is locked off and static, no cuts, no zoom, no "
    "pull-back, no reframing. He speaks naturally with accurate lip sync and says (S1) <d>[English] "
    "Hey, this is my identity LoRA, and it was trained right here on this machine.</d>"
    "\noverall_soundscape: quiet room tone, his voice close to the microphone, a faint chair creak."
    "\nnon_diegetic_music: N/A"
)


def named(opts: list[str], want: str) -> str:
    for o in opts:
        if Path(o.replace("\\", "/")).name == want:
            return o
    raise SystemExit(f"{want} missing from ComfyUI list:\n" + "\n".join(opts))


def lora_name(want: str) -> str:
    r = requests.get(f"{COMFY}/object_info/LoraLoaderModelOnly", timeout=30)
    return named(r.json()["LoraLoaderModelOnly"]["input"]["required"]["lora_name"][0], want)


def make_first_frame() -> Path:
    WORK.mkdir(parents=True, exist_ok=True)
    dst = WORK / "h3_first_frame.png"
    with Image.open(FIRST_FRAME) as im:
        im = im.convert("RGB")
        target = W / H
        w, h = im.size
        if w / h > target:                       # too wide -> trim sides
            nw = int(h * target)
            box = ((w - nw) // 2, 0, (w - nw) // 2 + nw, h)
        else:                                    # too tall -> trim bottom, keep head
            nh = int(w / target)
            top = int(h * 0.06)
            top = min(top, h - nh)
            box = (0, top, w, top + nh)
        im = im.crop(box)
        im.thumbnail((W, H), Image.Resampling.LANCZOS)
        im.save(dst, "PNG")
    return dst


def upload(path: Path, name: str) -> str:
    with open(path, "rb") as fh:
        r = requests.post(f"{COMFY}/upload/image",
                          files={"image": (name, fh, "image/png")},
                          data={"overwrite": "true"}, timeout=120)
    r.raise_for_status()
    return r.json().get("name", name)


def build(first_frame_name: str, use_lora: bool) -> dict:
    wf = json.loads(BASE_WF.read_text(encoding="utf-8"))
    tag = "with" if use_lora else "without"

    wf["114"]["inputs"]["image"] = first_frame_name
    wf["104"]["inputs"]["prompt"] = PROMPT
    wf["104"]["inputs"]["width"] = W
    wf["104"]["inputs"]["height"] = H
    wf["104"]["inputs"]["length"] = FRAMES
    wf["15"]["inputs"]["noise_seed"] = SEED
    wf["9"]["inputs"]["steps"] = STEPS
    wf["9"]["inputs"]["scheduler"] = "simple"
    wf["92"]["inputs"]["filename_prefix"] = f"h3_j0nt11awm/{tag}"

    # turbo LoRA rides on top of the base model, always on (this is how the training previews ran)
    wf["6T"] = {
        "class_type": "LoraLoaderModelOnly",
        "inputs": {"lora_name": lora_name(TURBO_LORA), "strength_model": TURBO_STRENGTH, "model": ["6", 0]},
    }
    if use_lora:
        wf["6L"] = {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {"lora_name": lora_name(IDENTITY_LORA), "strength_model": 1.0, "model": ["6T", 0]},
        }
        model_src = ["6L", 0]
    else:
        model_src = ["6T", 0]
    wf["9"]["inputs"]["model"] = model_src
    wf["16"]["inputs"]["model"] = model_src
    return wf


def queue(wf: dict) -> str:
    r = requests.post(f"{COMFY}/prompt", json={"prompt": wf}, timeout=120)
    if r.status_code != 200:
        raise SystemExit(f"queue rejected: {r.text[:3000]}")
    return r.json()["prompt_id"]


def wait(pid: str, timeout_s: float = 5400) -> dict:
    t0 = time.time()
    last = 0.0
    while True:
        h = requests.get(f"{COMFY}/history/{pid}", timeout=30).json()
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "success":
                return h[pid]
            if st.get("status_str") == "error":
                raise SystemExit(f"execution error:\n{json.dumps(st)[:3000]}")
        el = time.time() - t0
        if el > timeout_s:
            raise SystemExit(f"timeout on {pid} after {el:.0f}s")
        if el - last >= 60:
            last = el
            print(f"  ...{el/60:.1f} min", flush=True)
        time.sleep(5)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    requests.get(f"{COMFY}/system_stats", timeout=10).raise_for_status()
    ff = make_first_frame()
    name = upload(ff, "h3_jon_first_frame.png")
    print(f"first frame uploaded as {name} ({ff.stat().st_size/1e6:.2f} MB)", flush=True)

    for use_lora in (True, False):
        tag = "with" if use_lora else "without"
        t0 = time.time()
        pid = queue(build(name, use_lora))
        print(f"[{tag}] queued {pid}", flush=True)
        entry = wait(pid)
        files = []
        for _n, o in (entry.get("outputs") or {}).items():
            for key in ("videos", "gifs", "images"):
                for it in o.get(key, []) or []:
                    if "filename" in it:
                        files.append(COMFY_ROOT / "output" / (it.get("subfolder") or "") / it["filename"])
        if not files:
            raise SystemExit(f"no video output for {tag}\n{json.dumps(entry.get('outputs'))[:1500]}")
        src = files[-1]
        dst = OUT / f"h3_jon_talking_{tag}.mp4"
        shutil.copy2(src, dst)
        print(f"[{tag}] {time.time()-t0:.0f}s -> {dst.name} ({src.stat().st_size/1e6:.2f} MB)", flush=True)


if __name__ == "__main__":
    main()
