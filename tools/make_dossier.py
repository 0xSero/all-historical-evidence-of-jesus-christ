#!/usr/bin/env python3
"""Convert the dossier PDF into sectioned Markdown for the site reader.

The PDF's own table of contents supplies every section heading and its page
number, so headings can be restored exactly where the typesetting placed them
instead of being guessed from font sizes.

    python3 tools/make_dossier.py [--pdf Jesus_Christ_Research_Dossier.pdf] \
        [--outdir collections/dossier]

Writes one Markdown file per PART, plus `_meta/` sidecars with title and page
range. Page furniture (running head, footer, page number) is stripped.
"""
import argparse, json, re, subprocess
from datetime import date
from pathlib import Path

PARTS = {
    "01": ("01-guide-and-world-before-jesus", "Guide to the research and the world before Jesus"),
    "02": ("02-life-chronological-catalogue", "Jesus's life: a chronological catalogue of the surviving canonical narratives"),
    "03": ("03-prophecies-critical-catalogue", "The prophecies associated with Jesus: a critical catalogue"),
    "04": ("04-documentary-record", "The documentary record of Jesus and the movements that interpreted him"),
    "05": ("05-medieval-devotion-to-present", "From medieval devotion to the present"),
    "06": ("06-what-evidence-can-establish", "What the evidence can and cannot establish"),
}
RUNNING_HEAD = "JESUS CHRIST / LIFE, RECORDS, PROPHECIES & RECEPTION"


def pdf_text(pdf: Path) -> list[str]:
    out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    return out.split("\f")


def clean_page(page: str) -> str:
    lines = []
    for line in page.splitlines():
        s = line.strip()
        if s == RUNNING_HEAD:
            continue
        if re.match(r"^Research cutoff: 26 October 2026\s+\d{1,3}$", s):
            continue
        if re.match(r"^\d{1,3}$", s):
            continue
        if s.startswith("Research cutoff: 26 October 2026"):
            continue
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def toc_entries(pages: list[str]) -> list[tuple[str, int]]:
    entries = []
    for page in pages[:6]:
        for line in page.splitlines():
            s = line.strip()
            m = re.match(r"^(.*?)[\s.]*\.\s?(?:\.\s?){4,}\s*(\d+)$", s)
            if m and len(m.group(1)) > 4:
                entries.append((re.sub(r"\s+", " ", m.group(1)).strip(), int(m.group(2))))
    return entries


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def find_heading(text: str, heading: str) -> int | None:
    """Locate a heading in page text, tolerating line wrapping and quotes."""
    want = "".join(ch for ch in heading.lower() if ch.isalnum())
    flat = []
    index = []
    for i, ch in enumerate(text):
        if ch.isalnum():
            flat.append(ch.lower())
            index.append(i)
    pos = "".join(flat).find(want)
    if pos < 0:
        return None
    return index[pos]


def heading_end(text: str, start: int, heading: str) -> int:
    """Return the index just past a (possibly line-wrapped) heading occurrence."""
    need = sum(ch.isalnum() for ch in heading)
    seen = 0
    for i in range(start, len(text)):
        if text[i].isalnum():
            seen += 1
            if seen >= need:
                return i + 1
    return start + len(heading)


def strip_part_header(body: str, title: str) -> str:
    """Drop the 'PART NN' divider and the part title printed under it."""
    lines = body.splitlines()
    out = []
    i = 0
    want = normalize(title)
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*PART \d\d\s*$", line):
            i += 1
            acc = ""
            j = i
            while j < len(lines):
                s = lines[j].strip()
                if not s:
                    j += 1
                    continue
                nxt = (acc + " " + normalize(s)).strip()
                if want.startswith(nxt):
                    acc = nxt
                    j += 1
                    continue
                break
            if acc:
                i = j
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="Jesus_Christ_Research_Dossier.pdf")
    ap.add_argument("--outdir", default="collections/dossier")
    args = ap.parse_args()

    pages = [clean_page(p) for p in pdf_text(Path(args.pdf))]
    toc = toc_entries(pages)
    outdir = Path(args.outdir)
    (outdir / "_meta").mkdir(parents=True, exist_ok=True)

    # Map each page to the headings that begin on it, in TOC order.
    by_page: dict[int, list[tuple[int, str]]] = {}
    for order, (title, page) in enumerate(toc):
        by_page.setdefault(page - 1, []).append((order, title))

    # Locate every PART divider.
    parts: list[tuple[str, int]] = []
    for i, page in enumerate(pages):
        for line in page.splitlines():
            m = re.match(r"^\s*PART (\d\d)\s*$", line)
            if m and m.group(1) in PARTS:
                parts.append((m.group(1), i))
    parts.sort(key=lambda p: p[1])
    bounds = {}
    for n, (num, page_idx) in enumerate(parts):
        end = parts[n + 1][1] if n + 1 < len(parts) else len(pages)
        bounds[num] = (page_idx, end)

    written = []
    for num, (slug, title) in PARTS.items():
        if num not in bounds:
            continue
        start, end = bounds[num]
        chunks: list[str] = [f"# {title}\n"]
        placed = 0
        for pidx in range(start, end):
            text = pages[pidx]
            for order, heading in sorted(by_page.get(pidx, []), key=lambda x: x[0]):
                pos = find_heading(text, heading)
                if pos is None:
                    continue
                stop = heading_end(text, pos, heading)
                text = text[:pos] + f"\n\n## {heading}\n\n" + text[stop:]
                placed += 1
            chunks.append(text)

        body = strip_part_header("\n\n".join(chunks), title)

        # Second pass: headings whose page-level match failed (wrapped, or on a
        # page boundary) are located in the joined text and marked there.
        for _, h in [x for pg in range(start, end + 1) for x in by_page.get(pg, [])]:
            if any(l.strip() == f"## {h}" for l in body.splitlines()):
                continue
            pos = find_heading(body, h)
            if pos is None:
                continue
            stop = heading_end(body, pos, h)
            body = body[:pos] + f"## {h}" + body[stop:]
        # The reference register has its own document so its 238 entries can be
        # linked individually.
        refs_split = ""
        m = re.search(r"^(?:#+\s*)?Sources and further reading\s*$", body, re.M)
        if m:
            refs_split = "## Sources and further reading\n\n" + body[m.end():].lstrip()
            body = body[:m.start()].rstrip()

        # Numbered catalogue entries: "12. The magi, star, and Herod." -> bold lead.
        body = re.sub(r"(?m)^(\d{1,3})\. ([A-Z][^.\n]{2,90}\.)", r"**\1. \2**", body)
        body = re.sub(r"(?m)^([A-Z]{1,2}\d{2})\. ", r"**\1. **", body)
        body = re.sub(r"\n{3,}", "\n\n", body)
        path = outdir / f"{slug}.md"
        path.write_text(
            f"<!-- Converted from {Path(args.pdf).name}, pages {start + 1}-{end}. -->\n\n" + body.strip() + "\n",
            encoding="utf-8",
        )
        meta = {
            "slug": slug,
            "title": title,
            "source_name": Path(args.pdf).name,
            "source_url": "",
            "license": "Original research dossier in this repository.",
            "pages": f"{start + 1}-{end}",
            "converted": date.today().isoformat(),
            "chars": len(body),
        }
        (outdir / "_meta" / f"{slug}.json").write_text(json.dumps(meta, indent=2) + "\n")
        written.append((slug, len(body), placed))
        if refs_split:
            ref_path = outdir / "07-references.md"
            ref_path.write_text(
                f"<!-- Converted from {Path(args.pdf).name}, reference register. -->\n\n" + refs_split.strip() + "\n",
                encoding="utf-8",
            )
            (outdir / "_meta" / "07-references.json").write_text(json.dumps({
                "slug": "07-references",
                "title": "Sources and further reading",
                "source_name": Path(args.pdf).name,
                "source_url": "",
                "license": "Original research dossier in this repository.",
                "converted": date.today().isoformat(),
                "chars": len(refs_split),
            }, indent=2) + "\n")

    for w in written:
        print(w)
    print("headings mapped:", sum(len(v) for v in by_page.values()), "of", len(toc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
