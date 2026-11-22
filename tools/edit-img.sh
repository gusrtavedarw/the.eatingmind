#!/usr/bin/env bash
# usage: edit-img.sh <ref.png> "<prompt>" <out.png>
set -euo pipefail
ref="$1"; prompt="$2"; out="$3"
wd="$(mktemp -d "${TMPDIR:-/tmp}/gptedit.XXXXXX")"
cp "$ref" "$wd/ref.png"
full="Use your image_generation tool (gpt-image-2) to create a new image based on the attached reference image (also saved as ref.png in your working directory). Keep the exact same drawing style, paper texture, camera angle, framing, table, wall and object positions as the reference, changing only what is described.

CHANGE: ${prompt}
SIZE: 1536x864

Requirements:
- You MUST call the image_generation tool, using the reference image as input.
- Do NOT write a Python script or fabricate a PNG any other way.
- Save the PNG as out.png in your current working directory. Reply with only the file name."
codex exec --skip-git-repo-check -s workspace-write -C "$wd" ${CODEX_MODEL:+-m "$CODEX_MODEL"} "$full" -i "$wd/ref.png" </dev/null > "$wd.log" 2>&1 || { tail -20 "$wd.log" >&2; exit 1; }
img="$wd/out.png"; [[ -f "$img" ]] || img="$(ls -t "$wd"/*.png | grep -v ref.png | head -1)"
[[ -f "$img" && "$img" != "$wd/ref.png" ]] || { tail -20 "$wd.log" >&2; exit 1; }
cp "$img" "$out"; echo "$out"
