#!/usr/bin/env bash
# usage: check-img.sh <img.png> "<what this figure must show>"
# Asks codex (vision) to inspect a generated figure for anatomy errors and mismatches with the brief.
# Prints the verdict; exit 0 = PASS, 1 = FAIL, 2 = could not judge.
set -euo pipefail
img="$1"; expect="$2"
wd="$(mktemp -d "${TMPDIR:-/tmp}/gptcheck.XXXXXX")"
cp "$img" "$wd/img.png"
full="You are a strict QA reviewer for an illustration (attached, also saved as img.png). Do NOT generate or edit images. Look carefully and answer.

STEP 1 - ANATOMY, check every person:
- Count the visible hands. For EACH hand, trace it back along its arm/sleeve to a shoulder. Report how many people, how many hands, how many arms each person has.
- Assume the image generator often gets this wrong: do not trust a first glance. For each arm, say WHERE on the body it starts (left shoulder, right shoulder, neck, middle of the back...).
  A person seen from behind has the left arm starting at the image-left shoulder and the right arm at the image-right shoulder. An arm that starts from the neck, behind the head or the middle of the back reads as an extra arm = FAIL.
  If one shoulder has no arm coming out of it while another arm appears from an odd place, that is an extra arm = FAIL.
- Any hand or arm that does not connect to a shoulder, a third hand, an extra or missing finger (more than 5), fused or melted fingers, a limb coming from an impossible place = FAIL.
- Also flag: duplicated objects that should be unique, objects floating without support, any visible text, letters or numbers.

STEP 2 - BRIEF, the figure must show:
${expect}
Check each point of the brief one by one. Any point not met = FAIL. Do not fail a point only because a still image cannot show the direction of a motion (lifting vs. putting back); judge the poses and objects.

Reply in this exact format and nothing else:
HANDS: <people> people, <hands> hands (<per arm: where it starts on the body -> which hand>)
BRIEF: <each brief point -> ok / NOT MET: reason>
OTHER: <other problems or none>
VERDICT: PASS or FAIL"
codex exec --skip-git-repo-check -s read-only -C "$wd" -o "$wd/answer.txt" ${CODEX_MODEL:+-m "$CODEX_MODEL"} "$full" -i "$wd/img.png" </dev/null > "$wd/log.txt" 2>&1 || { tail -20 "$wd/log.txt" >&2; exit 2; }
ans="$(cat "$wd/answer.txt" 2>/dev/null)"
grep -q '^VERDICT:' <<< "$ans" || { tail -20 "$wd/log.txt" >&2; exit 2; }
echo "$ans"
grep -q '^VERDICT: *PASS' <<< "$ans"
