#!/usr/bin/env bash
# Validate the question bank. Run locally or in CI.
# Every question page (questions/<topic>/NN-*.md, excluding README.md) must carry a
# **Difficulty:** and **Tags:** line, and no legacy source-link markers (🔗).
set -euo pipefail

fail=0
note() { echo "::error file=$1::$2" 2>/dev/null || echo "ERROR $1: $2"; fail=1; }

shopt -s nullglob
pages=()
for d in questions/[0-9][0-9]-*/; do
  for p in "$d"[0-9][0-9]-*.md; do pages+=("$p"); done
  [ -f "$d/README.md" ] || note "$d" "topic folder missing README.md index"
done

for p in "${pages[@]}"; do
  grep -q '\*\*Difficulty:\*\*' "$p" || note "$p" "missing **Difficulty:**"
  grep -q '\*\*Tags:\*\*'       "$p" || note "$p" "missing **Tags:**"
  grep -q '\[↑ Index\]'        "$p" || note "$p" "missing index/nav link"
done

if grep -rn '🔗' questions/ >/dev/null 2>&1; then
  grep -rn '🔗' questions/ | while read -r l; do
    note "${l%%:*}" "stray source-link marker (🔗)"
  done
fi

echo "checked ${#pages[@]} question pages across $(ls -d questions/[0-9][0-9]-*/ | wc -l | tr -d ' ') topics"
[ "$fail" -eq 0 ] || { echo "VALIDATION FAILED"; exit 1; }
echo "VALIDATION PASSED"
