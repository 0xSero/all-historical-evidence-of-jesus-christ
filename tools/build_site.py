#!/usr/bin/env python3
"""Render the collections into a static, searchable site under docs/.

    python3 tools/build_site.py

Output
  docs/index.html          app shell (copied from site/)
  docs/assets/*            css and js (copied from site/)
  docs/data/docs.json      catalog: collections, documents, references
  docs/data/search.json    full-text search payload
  docs/data/doc/<id>.json  rendered HTML + headings + neighbours per document

The site is plain files: no build server, no CDN, no framework.
"""
import html, json, re, shutil
from pathlib import Path

import mistune

ROOT = Path(".")
COLLECTIONS = ROOT / "collections"
SITE = ROOT / "site"
OUT = ROOT / "docs"
DATA = OUT / "data"

md = mistune.create_markdown(
    escape=False,
    plugins=["table", "strikethrough", "url", "footnotes"],
)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def render(text: str, doc_id: str, alias: dict[str, str]) -> tuple[str, list[dict]]:
    text = re.sub(r"^<!--.*?-->\n", "", text, flags=re.S)

    # Internal links: markdown file paths become router links.
    def relink(m):
        label, target = m.group(1), m.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        clean = target.split("#")[0].lstrip("./")
        base = Path(doc_id.split("/")[0])
        cand = (Path("collections") / clean).as_posix()
        for key in (clean, cand, f"{base}/{clean}", Path(clean).name):
            if key in alias:
                frag = "#" + target.split("#", 1)[1] if "#" in target else ""
                return f"[{label}](#/doc/{alias[key]}{frag})"
        return m.group(0)

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", relink, text)
    body = md(text)

    headings = []
    def add_id(m):
        level, inner = int(m.group(1)), m.group(2)
        hid = slug(re.sub(r"<[^>]+>", "", inner)) or f"h{len(headings)}"
        headings.append({"id": hid, "text": re.sub(r"<[^>]+>", "", inner), "level": level})
        return f'<h{level} id="{hid}">{inner}</h{level}>'

    body = re.sub(r"<h([1-4])>(.*?)</h\1>", add_id, body, flags=re.S)
    # Footnote anchors get stable ids already; make ref markers clickable.
    body = re.sub(r"\[([A-Z]\d+)\]", r'<a class="ref" href="#/ref/\1" data-ref="\1">\1</a>', body)
    # External links open in a new tab; internal router links stay in place.
    body = re.sub(
        r'<a href="(https?://[^"]+)"(?![^>]*data-ext)',
        r'<a href="\1" target="_blank" rel="noopener" data-ext',
        body,
    )
    return body, headings


def main() -> int:
    catalog = json.loads((COLLECTIONS / "catalog.json").read_text())
    docs = catalog["docs"]
    alias: dict[str, str] = {}
    for d in docs:
        alias[d["id"]] = d["id"]
        alias[d["path"]] = d["id"]
        alias[Path(d["path"]).name] = d["id"]
        alias[Path(d["path"]).stem] = d["id"]
        alias[d["id"].split("/", 1)[1]] = d["id"]

    refs_by_id = {r["id"]: r for r in catalog["references"]}

    if not SITE.is_dir():
        raise SystemExit("site/ shell missing; the UI lives there")
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SITE, OUT)
    DATA.mkdir(parents=True, exist_ok=True)

    present = {d["collection"] for d in docs}
    catalog["collections"] = [c for c in catalog["collections"] if c["id"] in present]
    search = []
    for i, d in enumerate(docs):
        text = (COLLECTIONS / d["path"]).read_text(encoding="utf-8", errors="replace")
        body, headings = render(text, d["id"], alias)
        plain = re.sub(r"<[^>]+>", " ", body)
        plain = html.unescape(re.sub(r"\s+", " ", plain))

        incoming = []
        for rid, ref in refs_by_id.items():
            if ref.get("doc") == d["id"]:
                incoming.append(rid)

        payload = {
            "id": d["id"],
            "title": d["title"],
            "collection": d["collection"],
            "html": body,
            "headings": headings,
            "prev": docs[i - 1]["id"] if i > 0 else None,
            "next": docs[i + 1]["id"] if i + 1 < len(docs) else None,
            "refs": incoming,
            "source_url": d.get("source_url", ""),
            "source_name": d.get("source_name", ""),
            "license": d.get("license", ""),
            "path": d["path"],
            "words": d["words"],
        }
        target = DATA / "doc"
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{d['id'].replace('/', '__')}.json").write_text(
            json.dumps(payload, ensure_ascii=False)
        )
        search.append(
            {
                "id": d["id"],
                "t": d["title"],
                "c": d["collection"],
                "x": plain[:60000],
            }
        )

    # Reference cards as documents too, so they can be read and linked.
    for rid, ref in sorted(refs_by_id.items()):
        pass

    pdf = ROOT / "Jesus_Christ_Research_Dossier.pdf"
    if pdf.exists():
        shutil.copy2(pdf, OUT / pdf.name)
    (DATA / "docs.json").write_text(json.dumps(catalog, ensure_ascii=False))
    (COLLECTIONS / "catalog.json").write_text(json.dumps(catalog, indent=1, ensure_ascii=False) + "\n")
    (DATA / "search.json").write_text(json.dumps(search, ensure_ascii=False))
    print(f"built {OUT}: {len(docs)} documents, {len(search)} search records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
