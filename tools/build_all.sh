#!/usr/bin/env bash
# Regenerate every deliverable of "Nobles & Common Folk at Quarrel".
# Needs: python3 with numpy + pillow, node 18+ with the playwright package and a Chromium,
# and the LDraw parts library (https://library.ldraw.org, "complete.zip").
#   LDRAW_LIB=/path/to/ldraw ./tools/build_all.sh
# Optional: CHROME=/path/to/chrome  PLAYWRIGHT_REQUIRE=/dir/containing/node_modules/
set -euo pipefail
: "${LDRAW_LIB:?set LDRAW_LIB to the ldraw/ folder of the LDraw parts library}"
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(dirname "$HERE")
WORK=${NOBLES_WORK:-$REPO/build/work}
mkdir -p "$WORK/www/models"
if [ ! -d "$WORK/node_modules/three" ]; then (cd "$WORK" && npm init -y >/dev/null && npm install three@0.186.1); fi
ln -sfn "$LDRAW_LIB" "$WORK/www/ldraw"
ln -sfn "$WORK/node_modules/three" "$WORK/www/three"
cp "$HERE/render/render.html" "$WORK/www/render.html"
cp "$HERE/render/render.mjs" "$WORK/render.mjs"
python3 "$HERE/make_filemap.py" > "$WORK/www/filemap.json"
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$WORK/www" >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER' EXIT
export NOBLES_WWW="$WORK/www/models" NOBLES_RENDER="$WORK/render.mjs"
cd "$HERE"
python3 make_outputs.py       # LDraw models, BrickLink wanted lists, parts list, budget
python3 instructions.py       # step images + part icons (slow: ~30 min with software WebGL)
python3 make_renders.py       # hero renders
python3 make_booklets.py      # PDF instruction booklets
python3 make_viewer.py        # interactive web viewer
