#!/usr/bin/env python3
"""Normalize question subpages: rebuild prev/next nav + topic READMEs.

Source of truth is the page files themselves (questions/<topic>/NN-*.md). Add a new
page as `# Question\n\n**Difficulty:** ...\n<body>` (no nav needed) and run this to wire
nav + regenerate the topic index. Then run build-index.py for the master list.
"""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
QDIR = ROOT / "questions"
DIFF_RE = re.compile(r"\*\*Difficulty:\*\*\s*([A-Za-z]+)")
NAV_RE = re.compile(r"^\[↑ Index\]\(\./README\.md\)")

def strip(text):
    lines = text.splitlines()
    # title = first '# ' line
    ti = next(i for i, l in enumerate(lines) if l.startswith("# "))
    title = lines[ti][2:].strip()
    rest = [l for l in lines[ti+1:] if not NAV_RE.match(l.strip())]
    body = "\n".join(rest).strip()
    body = re.sub(r"\n*---\s*$", "", body).strip()   # drop trailing separator
    return title, body

def main():
    topics = sorted(d for d in QDIR.iterdir() if d.is_dir() and re.match(r"\d\d-", d.name))
    for d in topics:
        pages = sorted(p for p in d.glob("[0-9][0-9]-*.md"))
        parsed = [(p, *strip(p.read_text())) for p in pages]
        rows = []
        for i, (p, title, body) in enumerate(parsed):
            prev = f"[← Prev](./{parsed[i-1][0].name})" if i > 0 else ""
            nxt  = f"[Next →](./{parsed[i+1][0].name})" if i < len(parsed)-1 else ""
            nav = " · ".join(x for x in ["[↑ Index](./README.md)", prev, nxt] if x)
            p.write_text(f"# {title}\n\n{nav}\n\n{body}\n\n---\n\n{nav}\n")
            m = DIFF_RE.search(body)
            rows.append(f"| {i+1} | [{title}](./{p.name}) | {m.group(1) if m else '—'} |")
        # preserve intro: everything in README before the table
        readme = d / "README.md"
        head = readme.read_text().split("| # | Question")[0].rstrip() if readme.exists() else f"# {d.name}"
        readme.write_text(head + "\n\n| # | Question | Difficulty |\n|---|----------|------------|\n"
                          + "\n".join(rows) + "\n\n[← All topics](../../README.md)\n")
        print(f"{d.name}: {len(parsed)} pages")

if __name__ == "__main__":
    main()
