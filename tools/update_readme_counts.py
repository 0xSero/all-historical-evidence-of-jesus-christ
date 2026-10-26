#!/usr/bin/env python3
"""Rewrite the collection table in README.md from collections/catalog.json.

The table lives between the markers `<!-- collections:start -->` and
`<!-- collections:end -->`, so it cannot drift from the actual contents.

    python3 tools/update_readme_counts.py
"""
import json, re
from pathlib import Path

BLURB = {
    "dossier": "The PDF's own text, sectioned, plus the 238-entry reference register",
    "scripture": "New Testament, World English Bible, one file per book",
    "gospels": "Thomas, Philip, Truth, Mary, Judas, Peter, Egerton, the infancy gospels, Q, P.Oxy. 5575, Nicodemus, the Diatessaron",
    "fathers": "Didache, Clement, Ignatius, Papias, Justin, Irenaeus, Eusebius, Origen, Hippolytus, Athanasius",
    "witnesses": "Josephus, Tacitus, Suetonius, Lucian, Mara bar Serapion, the Talmud, Thallus and Phlegon",
    "legal": "Pliny and Trajan, Hadrian's rescript, the 1994 Common Christological Declaration",
    "archaeology": "Pilate inscription, both ossuaries, Dura-Europos, Megiddo, the Frankfurt amulet, Nazareth inscription, Isaiah scroll, the shroud",
    "denominational": "Nostra aetate, Dilexit nos, the 2024 norms on alleged supernatural phenomena",
    "citations": "One page per register entry: the citation, what it supports, and where it is cited",
}


def main() -> int:
    cat = json.loads(Path("collections/catalog.json").read_text())
    counts = {c["id"]: c["docs"] for c in cat["collections"]}
    rows = ["| Collection | Documents | What it holds |", "|---|---|---|"]
    for cid, n in counts.items():
        if not n:
            continue
        rows.append(f"| [{cid}](collections/{cid}/) | {n} | {BLURB.get(cid, cat['collections'][[c['id'] for c in cat['collections']].index(cid)]['blurb'])} |")
    rows.append(f"| [references](collections/references/) | {len(cat['references'])} | `refs.json` (exact link destinations from the PDF), `links.json` (mirrored entries), `links-report.md` (the verified match for each) |")
    block = "\n".join(rows)

    readme = Path("README.md")
    text = readme.read_text()
    pat = re.compile(r"<!-- collections:start -->.*?<!-- collections:end -->", re.S)
    if not pat.search(text):
        print("markers not found in README.md")
        return 1
    readme.write_text(pat.sub(f"<!-- collections:start -->\n{block}\n<!-- collections:end -->", text))
    print(f"{len(counts)} collections written to README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
