#!/usr/bin/env python3
"""Generate one card per dossier reference under collections/citations/.

Each of the 238 reference entries cited in the dossier gets a page that carries
the dossier's own citation and its note on what the source supports, the source
domains printed in the register, the dossier sections that cite it, and a link
to the mirrored document when this repository has one.

    python3 tools/make_cards.py
"""
import json, re
from pathlib import Path

BUCKET = {
    "context": "modern",
    "canonical": "scripture",
    "prophecy": "scripture",
    "ancient": "witnesses",
}
ANCIENT_PRIMARY = re.compile(r"primary|ancient|papyrus|manuscript|translation|fragment", re.I)


def main() -> int:
    refs = json.loads(Path("collections/references/refs.json").read_text())
    outdir = Path("collections/citations")
    (outdir / "_meta").mkdir(parents=True, exist_ok=True)
    made = 0
    for ref in refs:
        rid = ref["id"]
        lines = [f"# {rid} — {ref['citation']}", ""]
        lines.append(f"> {ref['note']}" if ref["note"] else "")
        lines.append("")
        lines.append("## What the dossier says this supports")
        lines.append("")
        lines.append(ref["note"] or "(no note in the register)")
        lines.append("")
        meta_bits = []
        if ref["resource_type"]:
            meta_bits.append(("Resource type", ref["resource_type"]))
        meta_bits.append(("Register section", ref["section_title"]))
        if ref.get("url"):
            meta_bits.append(("Source", f"[{ref['url']}]({ref['url']})"))
        elif ref["domains"]:
            meta_bits.append(("Source domain", ", ".join(ref["domains"])))
        if ref.get("doc"):
            meta_bits.append(("Mirrored in this repository", f"[{ref['doc']}](#/doc/{ref['doc']})"))
        if ref.get("cited_in"):
            where = ", ".join(f"{k} ({v}×)" for k, v in ref["cited_in"].items() if k != "07-references")
            if where:
                meta_bits.append(("Cited in", where))
        lines.append("| Field | Value |")
        lines.append("|---|---|")
        for k, v in meta_bits:
            lines.append(f"| {k} | {v} |")
        lines.append("")
        text = "\n".join(lines)
        (outdir / f"{rid}.md").write_text(
            f"<!-- Generated from the dossier's reference register. -->\n\n{text}\n", encoding="utf-8"
        )
        (outdir / "_meta" / f"{rid}.json").write_text(
            json.dumps(
                {
                    "slug": rid,
                    "title": f"{rid} — {ref['citation'][:80]}",
                    "source_name": "Jesus_Christ_Research_Dossier.pdf, reference register",
                    "source_url": ref.get("url", ""),
                    "license": "Generated card; citation text from the dossier.",
                    "bucket": BUCKET.get(ref["section"], "modern"),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
        made += 1
    print(f"{made} reference cards -> {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
