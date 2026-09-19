"""Render Krea 2 LoKR demo stills (with LoRA / without LoRA) on ComfyUI.

    D:/AI_software/Fizgig/venv/Scripts/python.exe render_krea2.py

Writes PNGs to loras_j0nt11awm_site/scripts/_renders/krea2/.
Base workflow: Hermes_agent_outputs/local_comfyUI_wedge/image_krea2_turbo_t2i_API.json
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

import requests

COMFY = "http://127.0.0.1:8188"
COMFY_ROOT = Path(r"D:/AI_software/ComfyUI_windows_portable/ComfyUI")
BASE_WF = Path(r"D:/AI_software/Hermes_agent_outputs/local_comfyUI_wedge/image_krea2_turbo_t2i_API.json")
SITE = Path(r"D:/AI_software/Fizgig/loras_j0nt11awm_site")
OUT = SITE / "scripts" / "_renders" / "krea2"

TRIGGER = "j0nt11awm"
WANT_LORA = "krea2_t2i_lokr_j0nt11awm_v02_fizgig.safetensors"

PROMPTS = {
    "blazer": f"Photograph of {TRIGGER} man in a navy blue blazer, standing outdoors in soft natural afternoon light, natural skin texture, 35mm lens, high detail",
    "portrait": f"Close-up portrait of {TRIGGER} man, neutral expression, studio lighting, highly detailed face, sharp focus",
    "neon": f"Photograph of {TRIGGER} man at night on a city street, warm street lamps and soft bokeh lights behind him, wearing a dark jacket, cinematic, shallow depth of field",
    "beach": f"Photograph of {TRIGGER} man walking on a sunny beach boardwalk, wearing a light grey t-shirt and dark shorts, candid medium shot, bright daylight, natural skin texture",
}

SEEDS = {"blazer": 424242, "portrait": 777001, "neon": 5150, "beach": 90210}


def lora_name_for(want: str) -> str:
    r = requests.get(f"{COMFY}/object_info/LoraLoaderModelOnly", timeout=30)
    r.raise_for_status()
    opts = r.json()["LoraLoaderModelOnly"]["input"]["required"]["lora_name"][0]
    for o in opts:
        if Path(o.replace("\\", "/")).name == want:
            return o
    raise SystemExit(f"{want} not found in ComfyUI lora list:\n" + "\n".join(opts))


def build(prompt_key: str, use_lora: bool) -> dict:
    wf = json.loads(BASE_WF.read_text(encoding="utf-8"))
    tag = "with" if use_lora else "without"
    wf["30:6"]["inputs"]["text"] = PROMPTS[prompt_key]           # kill the refiner link, set prompt
    wf["30:24"]["inputs"]["value"] = False                        # no LLM prompt refinement
    wf["30:19"]["inputs"]["value"] = PROMPTS[prompt_key]
    wf["30:23"]["inputs"]["value"] = use_lora                     # model switch
    wf["30:15"]["inputs"]["lora_name"] = lora_name_for(WANT_LORA)
    wf["30:15"]["inputs"]["strength_model"] = 1.0
    wf["30:3"]["inputs"]["seed"] = SEEDS[prompt_key]
    wf["30:3"]["inputs"]["steps"] = 8
    wf["49"]["inputs"]["aspect_ratio"] = "1:1 (Square)"
    wf["49"]["inputs"]["megapixels"] = 1
    wf["29"]["inputs"]["filename_prefix"] = f"krea2_j0nt11awm/{prompt_key}_{tag}"
    return wf


def queue(wf: dict) -> str:
    r = requests.post(f"{COMFY}/prompt", json={"prompt": wf}, timeout=60)
    if r.status_code != 200:
        raise SystemExit(f"queue rejected: {r.text[:2000]}")
    return r.json()["prompt_id"]


def wait(pid: str, timeout_s: float = 900) -> dict:
    t0 = time.time()
    while True:
        h = requests.get(f"{COMFY}/history/{pid}", timeout=30).json()
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "success":
                return h[pid]
            if st.get("status_str") == "error":
                raise SystemExit(f"execution error:\n{json.dumps(st)[:2500]}")
        if time.time() - t0 > timeout_s:
            raise SystemExit(f"timeout on {pid}")
        time.sleep(2)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(k, use) for k in PROMPTS for use in (True, False)]
    for key, use in jobs:
        tag = "with" if use else "without"
        t0 = time.time()
        pid = queue(build(key, use))
        entry = wait(pid)
        files = []
        for _n, o in (entry.get("outputs") or {}).items():
            for it in o.get("images", []) or []:
                files.append(COMFY_ROOT / "output" / (it.get("subfolder") or "") / it["filename"])
        if not files:
            raise SystemExit(f"no image output for {key} {tag}")
        src = files[-1]
        dst = OUT / f"krea2_{key}_{tag}.png"
        shutil.copy2(src, dst)
        print(f"[{time.time()-t0:5.1f}s] {key:9s} lora={tag:7s} -> {dst.name}  ({src.stat().st_size/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
