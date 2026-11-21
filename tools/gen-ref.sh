#!/usr/bin/env bash
# usage: gen-ref.sh "<ref1.png,ref2.png,...>" "<prompt>" <out.png>
# Generates an image with gpt-image-2 via codex, passing several reference images.
# refs may be "" (no reference images). Set CODEX_MODEL to override codex's default model.
set -euo pipefail
refs="$1"; prompt="$2"; out="$3"
wd="$(mktemp -d "${TMPDIR:-/tmp}/gptref.XXXXXX")"
args=(); i=1; list=""
IFS=',' read -ra R <<< "$refs"
for r in ${R[@]+"${R[@]}"}; do cp "$r" "$wd/ref$i.png"; args+=(-i "$wd/ref$i.png"); list+="ref$i.png "; i=$((i+1)); done
if [[ -n "$list" ]]; then
  intro="create ONE new image, using the attached reference images (also saved in your working directory as: ${list}) as described below."
  must="- You MUST call the image_generation tool with the reference images as input."
else
  intro="create ONE new image as described below."
  must="- You MUST call the image_generation tool."
fi
full="Use your image_generation tool (gpt-image-2) to ${intro}

${prompt}
SIZE: 1536x864

Requirements:
${must}
- Do NOT write a Python script or fabricate a PNG any other way.
- Save the PNG as out.png in your current working directory. Reply with only the file name."
codex exec --skip-git-repo-check -s workspace-write -C "$wd" ${CODEX_MODEL:+-m "$CODEX_MODEL"} "$full" ${args[@]+"${args[@]}"} </dev/null > "$wd.log" 2>&1 || { tail -20 "$wd.log" >&2; exit 1; }
img="$wd/out.png"; [[ -f "$img" ]] || img="$(ls -t "$wd"/*.png | grep -v '/ref[0-9]*\.png$' | head -1)"
[[ -n "$img" && -f "$img" ]] || { tail -20 "$wd.log" >&2; exit 1; }
cp "$img" "$out"; echo "$out"
