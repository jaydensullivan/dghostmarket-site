#!/usr/bin/env bash
# Рендер всех версий: 9:16 и 4:5, русский и узбекский, с выравниванием громкости.
#   bash tools/render-all.sh            — всё
#   bash tools/render-all.sh 916 ru     — один формат и язык
# 4:5 хранится в formats/45.html: на время рендера он подменяет index.html
# (в проекте может быть только один корневой файл).
set -euo pipefail
cd "$(dirname "$0")/.."
HF="node ${HF_SKILLS:-$HOME/.claude/skills}/hyperframes/scripts/plugin-cli.mjs"
FORMATS="${1:-916 45}"; LANGS="${2:-ru uz}"
mkdir -p renders
cp index.html /tmp/dghost-index-916.html
trap 'cp /tmp/dghost-index-916.html index.html' EXIT
for f in $FORMATS; do
  if [ "$f" = 45 ]; then cp formats/45.html index.html; else cp /tmp/dghost-index-916.html index.html; fi
  for l in $LANGS; do
    $HF render -q delivery --skill=hyperframes --variables "{\"lang\":\"$l\"}" -o "renders/raw-$f-$l.mp4" > "/tmp/dghost-render-$f-$l.log" 2>&1
    ffmpeg -v error -y -i "renders/raw-$f-$l.mp4" -c:v copy -af "loudnorm=I=-15:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k -movflags +faststart "renders/dghost-3-mira-$f-$l.mp4"
    rm "renders/raw-$f-$l.mp4"
    echo "renders/dghost-3-mira-$f-$l.mp4"
  done
done
