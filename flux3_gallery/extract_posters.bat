@echo off
set FFMPEG=D:\AI_software\ffmpeg\bin\ffmpeg.exe
set DST=D:\AI_software\Hermes_agent_outputs\flux3_videos\flux3_gallery\assets\posters

for %%f in (01 02 03 04 05 06) do (
  echo Extracting poster for video %%f
  "%FFMPEG%" -y -ss 1 -i "D:\AI_software\Hermes_agent_outputs\flux3_videos\flux3_gallery\assets\videos\flux3_hermes_vid%%f.mp4" -frames:v 1 -q:v 2 "%DST%\flux3_hermes_vid%%f.jpg" 2>&1
)
echo Done.
