#!/usr/bin/env python3
"""Check the built site's internal integrity.

Fails when a generated page or data file points at something that does not
exist: unknown document ids in router links, missing per-document JSON, broken
relative asset paths, or a search index that names a document the catalog does
not contain.

    python3 tools/check_site.py
"""
import json, re, sys
from pathlib import Path

OUT = Path("docs")
problems: list[str] = []


def main() -> int:
    catalog = json.loads((OUT / "data/docs.json").read_text())
    docs = {d["id"] for d in catalog["docs"]}
    refs = {r["id"] for r in catalog["references"]}

    for d in catalog["docs"]:
        target = OUT / "data/doc" / (d["id"].replace("/", "__") + ".json")
        if not target.exists():
            problems.append(f"missing document json: {d['id']}")

    search = json.loads((OUT / "data/search.json").read_text())
    for row in search:
        if row["id"] not in docs:
            problems.append(f"search row for unknown document: {row['id']}")

    for docjson in (OUT / "data/doc").glob("*.json"):
        payload = json.loads(docjson.read_text())
        for href in re.findall(r'href="#/doc/([^"#]+)', payload["html"]):
            if href not in docs:
                problems.append(f"{docjson.name}: router link to unknown document {href}")
        for href in re.findall(r'href="#/ref/([A-Z]\d+)"', payload["html"]):
            if href not in refs:
                problems.append(f"{docjson.name}: router link to unknown reference {href}")
        for rid in payload.get("refs", []):
            if rid not in refs:
                problems.append(f"{docjson.name}: unknown reference id {rid}")

    for page in ["index.html", "assets/app.js", "assets/app.css"]:
        if not (OUT / page).exists():
            problems.append(f"missing site file: {page}")

    for r in catalog["references"]:
        if r.get("doc") and r["doc"] not in docs:
            problems.append(f"reference {r['id']} maps to missing document {r['doc']}")
        if not r.get("url") and not r.get("doc"):
            problems.append(f"reference {r['id']} has neither a document nor a URL")

    for p in problems[:40]:
        print("FAIL", p)
    print(f"{len(docs)} documents, {len(refs)} references, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
