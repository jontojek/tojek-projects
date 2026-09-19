"""Write a sidecar .txt beside every render produced for the landing page.

    D:/AI_software/Fizgig/venv/Scripts/python.exe write_sidecars.py
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

SITE = Path(r"D:/AI_software/Fizgig/loras_j0nt11awm_site")
KR = SITE / "scripts" / "_renders" / "krea2"
HR = SITE / "scripts" / "_renders" / "h3"

TRIGGER = "j0nt11awm"
KREA_LORA = "krea2_t2i_lokr_j0nt11awm_v02_fizgig.safetensors"

KREA = {
    "blazer": ("Photograph of j0nt11awm man in a navy blue blazer, standing outdoors in soft natural "
               "afternoon light, natural skin texture, 35mm lens, high detail", 424242, 6.1),
    "portrait": ("Close-up portrait of j0nt11awm man, neutral expression, studio lighting, highly "
                 "detailed face, sharp focus", 777001, 6.1),
    "neon": ("Photograph of j0nt11awm man at night on a city street, warm street lamps and soft bokeh "
             "lights behind him, wearing a dark jacket, cinematic, shallow depth of field", 5150, 6.1),
    "beach": ("Photograph of j0nt11awm man walking on a sunny beach boardwalk, wearing a light grey "
              "t-shirt and dark shorts, candid medium shot, bright daylight, natural skin texture", 90210, 6.1),
}

H3_PROMPT = (
    "integrated_multimodal_description: [Shot 1] A medium close-up of j0nt11awm man facing camera, "
    "talking in a relaxed, conversational tone. He wears a light blue dress shirt. He sits in front of "
    "a plain, flat, light grey wall with soft even lighting and nothing else in the background. The "
    "camera is locked off and static with no cuts and no motion. He speaks naturally with accurate lip "
    "sync and says (S1) <d>[English] Hey, this is my identity LoRA, and it was trained right here on "
    "this machine.</d>\noverall_soundscape: quiet room tone, his voice close to the microphone, a faint "
    "chair creak.\nnon_diegetic_music: N/A"
)

STAMP = datetime.now().strftime("%Y-%m-%d %H:%M")


def krea_sidecar(key: str, tag: str) -> None:
    prompt, seed, secs = KREA[key]
    on = tag == "with"
    txt = f"""# Render sidecar — Krea 2 identity LoRA
Date: {STAMP} PDT
File: krea2_{key}_{tag}.png
Generator: ComfyUI (portable), API workflow image_krea2_turbo_t2i_API.json
Model: krea2_turbo_fp8_scaled.safetensors (Krea 2 Turbo, 12.9B DiT)
Text encoder: qwen3vl_4b_fp8_scaled.safetensors (type krea2)
VAE: qwen_image_vae.safetensors

LoRA: {KREA_LORA if on else '(none — base model)'}
LoRA strength: {1.0 if on else 'n/a'}
Architecture: LoKR (LyCORIS Kronecker), factor 8

Prompt: {prompt}
Trigger word: {TRIGGER}
Seed: {seed}
Steps: 8   CFG: 1   Sampler: euler   Scheduler: simple   Denoise: 1.0
Resolution: 1024 x 1024 (ResolutionSelector, 1 MP, 1:1)
Batch: 1
Render time: {secs:.1f} s
Purpose: with/without comparison for the landing page (same prompt, same seed, only the LoRA differs)
"""
    (KR / f"krea2_{key}_{tag}_sidecar.txt").write_text(txt, encoding="utf-8")
    print(f"  krea2_{key}_{tag}_sidecar.txt")


def h3_sidecar(tag: str, secs: float, size_mb: float) -> None:
    on = tag == "with"
    txt = f"""# Render sidecar — MiniMax H3 identity + voice LoRA
Date: {STAMP} PDT
File: h3_jon_talking_{tag}.mp4
Generator: ComfyUI (portable), API workflow minimax_h3_i2v_local.api.json
Mode: image-to-video (i2v)
Model: minimax_h3_fl2va_pruned_int8_convrot.safetensors (MiniMax H3, 33B DiT, pruned int8)
Text encoder: qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
Video VAE: minimax_h3_video_vae_fp16.safetensors
Audio VAE: minimax_h3_audio_vae_fp32.safetensors

First frame: D:\\AI_software\\Fizgig\\dataset\\j0nt11_v02\\images\\FaceCrop_024.png
  (cropped to 0.571 portrait, 768x1344 working copy, uploaded to ComfyUI input as h3_jon_first_frame.png)
Identity LoRA: {'mmh3_t2v_lora_j0nt11awm_v01_fizgig.safetensors @ 1.0' if on else '(none — base model)'}
Turbo LoRA: minimax_h3_turbo_v4_step600.safetensors @ 0.75 (both clips)

Prompt: {H3_PROMPT}
Trigger word: {TRIGGER}
Seed: 20260918
Steps: 6   Scheduler: simple   Sampler: res_multistep   Guider: BasicGuider
Canvas: 768 x 1344 (portrait)   Frames: 124   FPS: 24   Duration: 5.167 s
Audio: generated jointly with the picture, 32 kHz stereo AAC
Render time: {secs:.0f} s
File size: {size_mb:.2f} MB
Purpose: with/without comparison for the landing page (same still, same prompt, same seed)
"""
    (HR / f"h3_jon_talking_{tag}_sidecar.txt").write_text(txt, encoding="utf-8")
    print(f"  h3_jon_talking_{tag}_sidecar.txt")


if __name__ == "__main__":
    for key in KREA:
        for tag in ("with", "without"):
            if (KR / f"krea2_{key}_{tag}.png").exists():
                krea_sidecar(key, tag)
    for tag, secs in (("with", 148.0), ("without", 30.0)):
        p = HR / f"h3_jon_talking_{tag}.mp4"
        if p.exists():
            h3_sidecar(tag, secs, p.stat().st_size / 1e6)
