#!/usr/bin/env python3
"""Split flat topic files (questions/NN-topic.md) into one subpage per question.

Layout produced:
  questions/NN-topic/README.md        -> topic index (intro + table of questions)
  questions/NN-topic/MM-slug.md       -> one question + answer, with prev/next nav

Run from repo root:  python3 scripts/build-subpages.py
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
QDIR = ROOT / "questions"

FLAT = sorted(QDIR.glob("[0-9][0-9]-*.md"))  # flat topic files only (not dirs)

DIFF_RE = re.compile(r"\*\*Difficulty:\*\*\s*([A-Za-z]+)")

def slugify(text: str, maxwords=8) -> str:
    text = re.sub(r"`[^`]*`", " ", text)            # drop code spans
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    words = text.split()
    return "-".join(words[:maxwords]) or "question"

def main():
    if not FLAT:
        print("no flat topic files found (already split?)"); return
    topics = []
    for f in FLAT:
        raw = f.read_text()
        lines = raw.splitlines()
        title = lines[0].lstrip("# ").strip()
        # split: intro = before first '### Q:' ; then each '### Q:' block
        parts = re.split(r"(?m)^### Q:\s*", raw)
        head = parts[0]
        # intro = everything in head after the H1 line
        intro = "\n".join(head.splitlines()[1:]).strip()
        qblocks = parts[1:]
        slug_dir = f.stem                              # e.g. 01-core-concepts
        outdir = QDIR / slug_dir
        outdir.mkdir(exist_ok=True)
        entries = []
        for i, block in enumerate(qblocks, 1):
            block = block.strip()
            # question = first line; body = rest, trimmed of trailing '---'
            qline, _, body = block.partition("\n")
            question = qline.strip()
            body = body.strip()
            body = re.sub(r"\n*---\s*$", "", body).strip()
            m = DIFF_RE.search(body)
            diff = m.group(1) if m else "—"
            slug = f"{i:02d}-{slugify(question)}"
            entries.append((i, question, diff, slug))
        # write each question page with nav
        for idx, (i, question, diff, slug) in enumerate(entries):
            prev_link = f"[← Prev](./{entries[idx-1][3]}.md)" if idx > 0 else ""
            nxt_link  = f"[Next →](./{entries[idx+1][3]}.md)" if idx < len(entries)-1 else ""
            nav = " · ".join(x for x in ["[↑ Index](./README.md)", prev_link, nxt_link] if x)
            # recover body: re-read from block (need same split)
            block = qblocks[i-1].strip()
            _, _, body = block.partition("\n")
            body = re.sub(r"\n*---\s*$", "", body.strip()).strip()
            page = f"# {question}\n\n{nav}\n\n{body}\n\n---\n\n{nav}\n"
            (outdir / f"{slug}.md").write_text(page)
        # topic README
        rows = "\n".join(
            f"| {i} | [{question}](./{slug}.md) | {diff} |"
            for (i, question, diff, slug) in entries
        )
        readme = f"# {title}\n\n"
        if intro:
            readme += intro + "\n\n"
        readme += (
            "| # | Question | Difficulty |\n|---|----------|------------|\n"
            + rows + "\n\n[← All topics](../../README.md)\n"
        )
        (outdir / "README.md").write_text(readme)
        topics.append((slug_dir, title, len(entries)))
        f.unlink()  # remove the flat file
        print(f"{slug_dir}: {len(entries)} pages")
    print("done:", sum(t[2] for t in topics), "question pages")

if __name__ == "__main__":
    main()
