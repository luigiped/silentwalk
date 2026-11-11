#!/usr/bin/env bash
# Uso: scripts/encode_audio.sh "percorso/traccia-originale" [--mono] [--loudnorm]
# CBR 96 kbps stereo (o 64 kbps mono), 44.1 kHz → assets/traccia.mp3
set -euo pipefail
IN="${1:?Specifica il file audio di origine}"; shift || true
AC=2; BR=96k; AF=()
for arg in "$@"; do
  case "$arg" in
    --mono) AC=1; BR=64k ;;
    --loudnorm) AF=(-af "loudnorm=I=-16:TP=-1.5:LRA=11") ;;
  esac
done
cd "$(dirname "$0")/.."
ffmpeg -hide_banner -y -i "$IN" -vn -map_metadata -1 -ac "$AC" -ar 44100 ${AF[@]+"${AF[@]}"} \
  -c:a libmp3lame -b:a "$BR" -write_xing 1 -id3v2_version 3 \
  -metadata title="Silent Walk" -metadata artist="FreeSpace APS" \
  assets/traccia.mp3
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=nw=1 assets/traccia.mp3
