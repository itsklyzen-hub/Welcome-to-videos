#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 audio.py music.wav
python3 render.py | ffmpeg -y -hide_banner -loglevel error -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i - \
  -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -movflags +faststart Welcome_to_Italie_sans_son.mp4
J=$(ffmpeg -hide_banner -i music.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
AF="loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true"
ffmpeg -y -hide_banner -loglevel error -i Welcome_to_Italie_sans_son.mp4 -i music.wav -map 0:v -map 1:a -c:v copy -af "$AF" \
  -ar 44100 -c:a aac -b:a 192k -shortest -movflags +faststart Welcome_to_Italie.mp4
echo DONE
