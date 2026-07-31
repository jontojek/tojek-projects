@echo off
set FFMPEG=D:\AI_software\ffmpeg\bin\ffmpeg.exe
set SRC=D:\AI_software\Hermes_agent_outputs\flux3_videos
set DST=D:\AI_software\Hermes_agent_outputs\flux3_videos\flux3_gallery\assets\videos

for %%f in (01 02 03 04 05 06) do (
  echo === Compressing video %%f ===
  "%FFMPEG%" -y -i "%SRC%\flux3_hermes_vid%%f.mp4" -vf "scale=-2:540" -c:v libx264 -crf 24 -preset fast -c:a aac -b:a 96k "%DST%\flux3_hermes_vid%%f.mp4"
  echo ---
)
echo All videos compressed.
