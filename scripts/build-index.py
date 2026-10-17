#!/usr/bin/env python3
"""Generate questions/README.md — a master index of every question page.

Scans questions/<topic>/NN-*.md, reads each page's H1 (the question) and Difficulty,
and writes one grouped, Ctrl-F-friendly catalog. Run from repo root.
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
QDIR = ROOT / "questions"
DIFF_RE = re.compile(r"\*\*Difficulty:\*\*\s*([A-Za-z]+)")

def main():
    topics = sorted(d for d in QDIR.iterdir() if d.is_dir() and re.match(r"\d\d-", d.name))
    out = ["# All Questions\n",
           "Every question in one place — use Ctrl-F. Each links to its own page.\n"]
    counts = {}
    total = 0
    sections = []
    for d in topics:
        title = (d / "README.md").read_text().splitlines()[0].lstrip("# ").strip()
        pages = sorted(p for p in d.glob("[0-9][0-9]-*.md"))
        rows = []
        for p in pages:
            txt = p.read_text()
            q = txt.splitlines()[0].lstrip("# ").strip()
            m = DIFF_RE.search(txt)
            diff = m.group(1) if m else "—"
            counts[diff] = counts.get(diff, 0) + 1
            rel = f"./{d.name}/{p.name}"
            rows.append(f"| [{q}]({rel}) | {diff} |")
            total += 1
        sections.append(
            f"## {title}  ·  [index](./{d.name}/)\n\n"
            "| Question | Difficulty |\n|----------|------------|\n"
            + "\n".join(rows) + "\n"
        )
    order = ["Easy", "Intermediate", "Medium", "Advanced", "Hard"]
    summ = " · ".join(f"{k} {counts[k]}" for k in order if k in counts)
    out.append(f"**{total} questions** — {summ}\n")
    out.extend(sections)
    out.append("[← Home](../README.md)\n")
    (QDIR / "README.md").write_text("\n".join(out))
    print(f"wrote questions/README.md — {total} questions, {len(topics)} topics")

if __name__ == "__main__":
    main()
