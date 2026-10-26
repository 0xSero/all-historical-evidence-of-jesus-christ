#!/usr/bin/env python3
"""Build collections/catalog.json: one record per document, with references.

Sources of truth
  collections/<collection>/<slug>.md|.txt   the document itself
  collections/<collection>/_meta/<slug>.json  sidecar written by the fetch tools
  collections/references/refs.json             the dossier's 238 reference entries
  collections/references/links.json            reference id -> document id or URL

Run after adding documents:  python3 tools/build_catalog.py
"""
import json, re
from pathlib import Path

COLLECTIONS = {
    "dossier": ("The dossier", "The research dossier itself, converted from the PDF: every catalogue, prophecy ledger, and source register."),
    "scripture": ("Scripture", "The New Testament in the public-domain World English Bible, one file per book."),
    "gospels": ("Gospels outside the canon", "Gnostic, infancy, passion, and sayings gospels, plus the Gospel of Nicodemus and Tatian's Diatessaron."),
    "fathers": ("Church Fathers", "Ignatius, Clement, Papias, Justin, Irenaeus, Eusebius, Origen, and the Didache, in 19th-century public-domain translations."),
    "witnesses": ("Ancient witnesses", "Non-Christian testimony: Josephus, Tacitus, Suetonius, Pliny, Lucian, the Talmud, Mara bar Serapion, Thallus and Phlegon."),
    "legal": ("Legal and administrative documents", "Roman rescripts, edicts, inscriptions, and official correspondence that mention Christians or Jesus."),
    "archaeology": ("Archaeology and artifacts", "Inscriptions, ossuaries, mosaics, buildings, and scientific studies of relics."),
    "modern": ("Modern scholarship", "Articles, books, and reference works cited by the dossier; metadata and links only where the work is in copyright."),
    "denominational": ("Denominational and institutional statements", "How churches and movements describe Jesus in their own words."),
    "registry": ("Gospel registry", "Fifty-two gospels and gospel-type texts with dates, manuscripts, ancient verdicts, and canonical status in each tradition."),
    "citations": ("Reference cards", "One page per numbered entry in the dossier's register: what the source is, what the dossier says it supports, and where it is cited."),
}
TEXT_GLOBS = ("*.md", "*.txt")
SKIP = {"README.md", "catalog.json", "refs.json", "links.json"}


def title_of(path: Path, meta: dict) -> str:
    if meta.get("title"):
        return meta["title"]
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:8]:
        m = re.match(r"^#{1,2} (.+)$", line.strip())
        if m:
            return re.sub(r"\*\*|\*", "", m.group(1)).strip()
    words = path.stem.replace("-", " ").split()
    return " ".join(w if w.isdigit() else w[:1].upper() + w[1:] for w in words)


def first_paragraph(text: str) -> str:
    body = re.sub(r"^<!--.*?-->\n", "", text, flags=re.S)
    for block in re.split(r"\n\s*\n", body):
        b = " ".join(block.split())
        if len(b) > 60 and not b.startswith(("#", "|", "[^")):
            b = re.sub(r"[*_`>#]", "", b)
            return b[:300]
    return ""


def main() -> int:
    root = Path("collections")
    docs = []
    for coll, (ctitle, cblurb) in COLLECTIONS.items():
        cdir = root / coll
        if not cdir.is_dir():
            continue
        for pattern in TEXT_GLOBS:
            for path in sorted(cdir.rglob(pattern)):
                rel = path.relative_to(root)
                if path.name in SKIP or path.parent.name == "_meta":
                    continue
                stem = path.stem
                meta_path = path.parent / "_meta" / f"{stem}.json"
                meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
                text = path.read_text(encoding="utf-8", errors="replace")
                doc_id = f"{coll}/{stem}"
                if path.parent != cdir:  # nested, e.g. scripture/new-testament or gospels/gutenberg
                    doc_id = f"{coll}/{path.parent.name}/{stem}"
                docs.append(
                    {
                        "id": doc_id,
                        "title": title_of(path, meta),
                        "collection": coll,
                        "path": str(rel),
                        "kind": "primary" if coll in {"scripture", "gospels", "fathers", "witnesses", "legal", "dossier"} else "secondary",
                        "bucket": meta.get("bucket", ""),
                        "source_name": meta.get("source_name", ""),
                        "source_url": meta.get("source_url", ""),
                        "license": meta.get("license", ""),
                        "fetched": meta.get("fetched") or meta.get("converted", ""),
                        "words": len(text.split()),
                        "chars": len(text),
                        "excerpt": first_paragraph(text),
                        "refs": [],
                    }
                )

    by_path = {d["path"]: d for d in docs}
    alias = {}
    for d in docs:
        alias[d["id"]] = d["id"]
        alias[d["path"]] = d["id"]
        alias[Path(d["path"]).name] = d["id"]
        alias[Path(d["path"]).stem] = d["id"]

    refs_path = root / "references" / "refs.json"
    refs = json.loads(refs_path.read_text()) if refs_path.exists() else []
    links_path = root / "references" / "links.json"
    links = json.loads(links_path.read_text()) if links_path.exists() else {}

    for ref in refs:
        link = links.get(ref["id"])
        if link:
            target = alias.get(link)
            if target:
                ref["doc"] = target
                next(d for d in docs if d["id"] == target)["refs"].append(ref["id"])
            else:
                ref["doc"] = None
                if link.startswith("http"):
                    ref.setdefault("urls", [])
                    if link not in ref["urls"]:
                        ref["urls"].insert(0, link)
                    ref["url"] = ref["urls"][0]
        else:
            ref["doc"] = None
        if not ref.get("url") and ref.get("urls"):
            ref["url"] = ref["urls"][0]

    catalog = {
        "generated": __import__("datetime").date.today().isoformat(),
        "collections": [
            {
                "id": k,
                "title": v[0],
                "blurb": v[1],
                "docs": sum(1 for d in docs if d["collection"] == k),
            }
            for k, v in COLLECTIONS.items()
        ],
        "docs": docs,
        "references": refs,
    }
    out = root / "catalog.json"
    out.write_text(json.dumps(catalog, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(docs)} documents, {len(refs)} references -> {out}")
    missing = [r["id"] for r in refs if r.get("doc")]
    print("references mirrored to a document:", len(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
