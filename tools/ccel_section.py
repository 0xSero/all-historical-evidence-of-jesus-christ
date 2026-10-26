#!/usr/bin/env python3
"""Extract a titled section out of a CCEL (Christian Classics Ethereal Library) volume text.

CCEL publishes each volume as one plain-text file, e.g.
    https://www.ccel.org/ccel/s/schaff/anf01/cache/anf01.txt
Sections inside it are set as a heading on a line by itself, indented three
spaces, usually surrounded by blank lines and sometimes by a row of
underscores (_______) that marks a rule.

Usage:
    python3 tools/ccel_section.py --volume anf01 --start "The Didache" \
        --end "Constitutions of the Holy Apostles" --out collections/fathers/didache.md \
        --title "The Didache" --source-name "Ante-Nicene Fathers vol. 1"

--start / --end are regular expressions matched against stripped lines.
The section runs from the matched start heading up to the line before the end
match. The volume text is cached under .cache/ccel/.
"""
import argparse, hashlib, json, re, sys, urllib.request
from datetime import date
from pathlib import Path

CACHE = Path(".cache/ccel")


def volume_text(volume: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{volume}.txt"
    if not p.exists():
        url = f"https://www.ccel.org/ccel/s/schaff/{volume}/cache/{volume}.txt"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            p.write_bytes(r.read())
    return p.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--volume", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--source-name", required=True)
    ap.add_argument("--occurrence", type=int, default=1, help="which match of --start to use")
    args = ap.parse_args()

    text = volume_text(args.volume)
    lines = text.splitlines()
    starts = [i for i, l in enumerate(lines) if re.search(args.start, l.strip())]
    if len(starts) < args.occurrence:
        print(f"FAIL start pattern not found ({len(starts)} hits): {args.start}", file=sys.stderr)
        return 1
    s = starts[args.occurrence - 1]
    ends = [i for i, l in enumerate(lines) if i > s + 5 and re.search(args.end, l.strip())]
    if not ends:
        print(f"FAIL end pattern not found after start: {args.end}", file=sys.stderr)
        return 1
    e = ends[0]

    body = lines[s:e]
    while body and (not body[-1].strip() or set(body[-1].strip()) <= {"_"}):
        body.pop()
    cleaned = []
    for l in body:
        if set(l.strip()) <= {"_"} and l.strip():
            cleaned.append("---")
        else:
            cleaned.append(l[3:] if l.startswith("   ") else l)
    out_text = "\n".join(cleaned).strip()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://www.ccel.org/ccel/s/schaff/{args.volume}/cache/{args.volume}.txt"
    out.write_text(
        f"<!-- Extracted from {url} on {date.today().isoformat()}. -->\n\n" + out_text + "\n",
        encoding="utf-8",
    )
    meta_dir = out.parent / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "slug": out.stem,
        "title": args.title,
        "source_name": args.source_name,
        "source_url": url,
        "license": "Public domain",
        "fetched": date.today().isoformat(),
        "chars": len(out_text),
        "sha256": hashlib.sha256(out_text.encode()).hexdigest(),
    }
    (meta_dir / f"{out.stem}.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"OK {out.stem} {len(out_text)} chars (lines {s}-{e})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
