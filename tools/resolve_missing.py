#!/usr/bin/env python3
"""Resolve a few register entries that carry no embedded PDF link.

The dossier prints a source for every entry, but five of them were typeset
without a hyperlink. For those, the destination is pinned here by hand and
verified with an HTTP request at build time; anything that does not answer is
left unlinked rather than guessed.

    python3 tools/resolve_missing.py [--write]
"""
import json, sys, urllib.request
from pathlib import Path

CANDIDATES = {
    "A27": "https://www.inscriptionsisraelpalestine.org/",
    "A38": "https://www.jw.org/en/library/books/",
    "L25": "https://www.biblegateway.com/passage/?search=Matthew+2&version=KJV",
    "R70": "https://www.newadvent.org/fathers/0103125.htm",
    "R79": "https://www.fourthcentury.com/nicaea-325-canons/",
}
NOTE = {
    "A27": "The Inscriptions of Israel/Palestine project home; the register cites a project page under this site.",
    "A38": "jw.org landing page; the register gives the organisation but not the article URL.",
    "L25": "Bible Gateway, Matthew 2 KJV, as printed; the same chapter is mirrored here in the World English Bible.",
    "R70": "New Advent, Against Heresies I.25, the chapter the register cites.",
    "R79": "Fourth Century Christianity, canons of Nicaea, the site the register names.",
}


def alive(url: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status < 400
    except Exception:
        return False


def main() -> int:
    path = Path("collections/references/refs.json")
    refs = json.loads(path.read_text())
    by_id = {r["id"]: r for r in refs}
    for rid, url in CANDIDATES.items():
        ok = alive(url)
        print(f"{rid} {'OK ' if ok else 'DEAD'} {url}")
        if ok and rid in by_id and not by_id[rid]["urls"]:
            by_id[rid]["urls"] = [url]
            by_id[rid]["url"] = url
            by_id[rid]["resolved_note"] = NOTE.get(rid, "")
    if "--write" in sys.argv:
        path.write_text(json.dumps(refs, indent=1, ensure_ascii=False) + "\n")
        print("written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
