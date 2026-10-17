#!/usr/bin/env bash
# Validate the question bank structure. Run locally or in CI.
# Each `### Q:` entry must be followed (within a few lines) by a **Difficulty:** line
# and a **Tags:** line, and no legacy source-link markers should remain.
set -euo pipefail

fail=0
note() { echo "::error file=$1::$2" 2>/dev/null || echo "ERROR $1: $2"; fail=1; }

shopt -s nullglob
files=(questions/0[1-9]*.md questions/10*.md)

total=0
for f in "${files[@]}"; do
  # pull the line number of every "### Q:" heading
  while IFS=: read -r ln _; do
    total=$((total+1))
    block=$(sed -n "${ln},$((ln+6))p" "$f")
    grep -q '\*\*Difficulty:\*\*' <<<"$block" || note "$f:$ln" "Q missing **Difficulty:**"
    grep -q '\*\*Tags:\*\*'       <<<"$block" || note "$f:$ln" "Q missing **Tags:**"
  done < <(grep -n '^### Q:' "$f")
done

# no leftover source-link markers in question files
if grep -rn '🔗' questions/0[1-9]*.md questions/10*.md >/dev/null 2>&1; then
  grep -rn '🔗' questions/0[1-9]*.md questions/10*.md | while read -r l; do
    note "${l%%:*}" "stray source-link marker (🔗) — answers are original, no source lines"
  done
fi

echo "checked $total question entries across ${#files[@]} files"
if [ "$fail" -ne 0 ]; then
  echo "VALIDATION FAILED"; exit 1
fi
echo "VALIDATION PASSED"
