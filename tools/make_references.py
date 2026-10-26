#!/usr/bin/env python3
"""Extract the register's reference entries together with their exact destinations.

The dossier's PDF does not merely print hostnames: every "Open source" line is a
live hyperlink whose target is a particular page, sometimes a particular passage
(e.g. Irenaeus III.24, Josephus XVIII, Perseus Republic 2.362a). This tool reads
those link annotations from the PDF and attaches them to the reference whose
vertical band on the page contains the link, so each entry carries the exact URL
rather than a guess from its hostname.

Output: collections/references/refs.json
  id, section, section_title, citation, note, resource_type,
  domains (as printed), urls (from the PDF links, in printed order),
  pdf_page, cited_in (dossier documents that cite the id)

    python3 tools/make_references.py
"""
import json, re, subprocess
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader

SECTIONS = [
    (5076, "context", "Context, evidence, and the modern period"),
    (5463, "canonical", "Canonical life and teaching record"),
    (5675, "prophecy", "Prophecy and scriptural interpretation"),
    (6029, "ancient", "Ancient records and religious movements"),
]
FURNITURE = re.compile(r"^(Research cutoff: 26 October|JESUS CHRIST / LIFE, RECORDS|\d{2,3})$")
REF_RE = re.compile(r"^\[([A-Z]\d+)\]\s*(.*)$")


def register_lines(pdf: Path) -> list[str]:
    text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True
    ).stdout
    return text.splitlines()


def section_at(i: int) -> tuple[str, str]:
    current = ("context", "Context, evidence, and the modern period")
    for ln, sid, title in SECTIONS:
        if i >= ln:
            current = (sid, title)
    return current


def parse_entries(lines: list[str]) -> dict[str, dict]:
    try:
        first = next(i for i, l in enumerate(lines) if "This register contains 238 reference entries" in l)
    except StopIteration:
        raise SystemExit("reference register not found in PDF")
    refs: dict[str, dict] = {}
    cur = None
    for i in range(first, len(lines)):
        s = lines[i].strip()
        if not s or FURNITURE.match(s):
            continue
        m = REF_RE.match(s)
        if m:
            cur = m.group(1)
            sid, stitle = section_at(i)
            refs[cur] = {
                "id": cur,
                "section": sid,
                "section_title": stitle,
                "lines": [m.group(2)] if m.group(2) else [],
                "domains": [],
            }
            continue
        if cur is None:
            continue
        if "Research cutoff: 26 October" in s or "JESUS CHRIST / LIFE, RECORDS" in s:
            continue
        if s.startswith("Open source:") or s.startswith("Related source"):
            refs[cur]["domains"] += [
                u.rstrip(".,;") for u in re.findall(r"(?:www\.|https?://)[^\s|,]+", s)
            ]
        else:
            refs[cur]["lines"].append(s)
    return refs


def page_marks_and_links(page) -> tuple[list[tuple[float, str]], list[tuple[float, float, str]]]:
    marks: list[tuple[float, str]] = []
    seen: set[str] = set()

    def visit(text, cm, tm, font, size):
        for m in re.finditer(r"\[([A-Z]\d+)\]", text):
            rid = m.group(1)
            if rid in seen:
                continue
            seen.add(rid)
            marks.append((round(cm[5] + tm[5], 1), rid))

    page.extract_text(visitor_text=visit)
    links = []
    for a in page.get("/Annots") or []:
        o = a.get_object()
        action = o.get("/A")
        uri = action.get_object().get("/URI") if action else None
        if uri:
            rect = o.get("/Rect")
            links.append((round(float(rect[3]), 1), round(float(rect[0]), 1), uri))
    marks.sort(key=lambda t: -t[0])
    links.sort(key=lambda t: -t[0])
    return marks, links


def attach_urls(pdf: Path, refs: dict[str, dict]) -> None:
    reader = PdfReader(str(pdf))
    for pno in range(len(reader.pages)):
        marks, links = page_marks_and_links(reader.pages[pno])
        if not marks:
            continue
        for i, (y, rid) in enumerate(marks):
            low = marks[i + 1][0] if i + 1 < len(marks) else -1
            band = [u for (ay, ax, u) in links if low - 3 <= ay <= y + 4]
            entry = refs.setdefault(rid, {"id": rid, "lines": [], "domains": [], "section": "ancient",
                                          "section_title": "Ancient records and religious movements"})
            entry["pdf_page"] = pno + 1
            entry["urls"] = band


def citations(refs: dict) -> dict:
    cited = defaultdict(dict)
    for path in sorted(Path("collections/dossier").glob("*.md")):
        text = path.read_text()
        for rid in set(re.findall(r"\[([A-Z]\d+)\]", text)):
            if rid in refs:
                cited[rid][path.stem] = len(re.findall(rf"\[{rid}\]", text))
    return cited


def main() -> int:
    pdf = Path("Jesus_Christ_Research_Dossier.pdf")
    raw = parse_entries(register_lines(pdf))
    attach_urls(pdf, raw)
    cited = citations(raw)

    out = []
    for rid, r in raw.items():
        lines_ = [l for l in r["lines"] if l]
        rt = ""
        for l in lines_:
            m = re.match(r"^Resource type:\s*(.*)$", l)
            if m:
                rt = m.group(1).strip()
        lines_ = [
            re.sub(r"\s*Research cutoff: 26 October 2026\s*\d*", "", l) for l in lines_
        ]
        lines_ = [l for l in lines_ if l.strip() and "JESUS CHRIST / LIFE" not in l]
        cite_lines = [l for l in lines_ if not l.startswith("Resource type:")]
        citation = " ".join(cite_lines[:2]).strip()
        note = " ".join(cite_lines[2:]).strip() if len(cite_lines) > 2 else ""
        if not note and len(cite_lines) == 2 and len(cite_lines[1]) > 90:
            citation, note = cite_lines[0], cite_lines[1]
        domains = []
        for d in r["domains"]:
            d = re.sub(r"^https?://", "", d).rstrip("/")
            if d not in domains:
                domains.append(d)
        urls = [u for u in dict.fromkeys(r.get("urls", [])) if not u.lower().endswith(".pdf") or True]
        out.append(
            {
                "id": rid,
                "section": r["section"],
                "section_title": r["section_title"],
                "citation": citation,
                "note": note,
                "resource_type": rt,
                "domains": domains,
                "urls": urls,
                "url": urls[0] if urls else "",
                "pdf_page": r.get("pdf_page"),
                "cited_in": cited.get(rid, {}),
                "doc": None,
            }
        )
    out.sort(key=lambda r: (r["section"], int(re.sub(r"\D", "", r["id"]))))
    target = Path("collections/references/refs.json")
    target.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    with_url = sum(1 for r in out if r["urls"])
    print(f"{len(out)} references -> {target}")
    print(f"with exact PDF links: {with_url}; without: {len(out) - with_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
