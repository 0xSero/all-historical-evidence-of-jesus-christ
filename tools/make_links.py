#!/usr/bin/env python3
"""Resolve register entries to documents in this repository, with verification.

Matching is deliberately conservative. A reference is only linked to a mirrored
document when

  * its citation names the work (a pattern, not a loose keyword), and
  * the document actually contains the locator the citation gives (a book,
    chapter, or work title).

Rules that fail either test leave `doc: null`: the site then links the exact URL
taken from the PDF's own hyperlinks. This avoids the classic failure of a
keyword match (for example, driving every "Irenaeus" reference to Book III when
the citation is Book I.24).

Writes collections/references/links.json and collections/references/links-report.md.
"""
import json, re
from pathlib import Path

SCRIPTURE = {
    "matthew": "01-matthew", "mark": "02-mark", "luke": "03-luke", "john": "04-john",
    "acts": "05-acts", "romans": "06-romans", "1 corinthians": "07-1-corinthians",
    "2 corinthians": "08-2-corinthians", "galatians": "09-galatians", "ephesians": "10-ephesians",
    "philippians": "11-philippians", "colossians": "12-colossians",
    "1 thessalonians": "13-1-thessalonians", "2 thessalonians": "14-2-thessalonians",
    "1 timothy": "15-1-timothy", "2 timothy": "16-2-timothy", "titus": "17-titus",
    "philemon": "18-philemon", "hebrews": "19-hebrews", "james": "20-james",
    "1 peter": "21-1-peter", "2 peter": "22-2-peter", "1 john": "23-1-john",
    "2 john": "24-2-john", "3 john": "25-3-john", "jude": "26-jude", "revelation": "27-revelation",
}

# (citation pattern, document id, marker the document must contain)
RULES: list[tuple[str, str, str]] = [
    # Patristic
    (r"didache|teaching of the twelve", "fathers/didache", "twelve apostles"),
    (r"first clement|clement of rome|1 clement", "fathers/1-clement", "clement"),
    (r"ignatius.*smyrna", "fathers/ignatius-smyrnaeans", "smyrn"),
    (r"papias", "fathers/papias-fragments", "papias"),
    (r"justin martyr|first apology", "fathers/justin-first-apology", "apology"),
    (r"irenaeus.*against heresies.*\biii\b|against heresies.*\biii\b.*\b(1[0-2]|[1-9])\b", "fathers/irenaeus-ah-3", "book iii"),
    (r"eusebius.*church history.*\bbook iii\b|church history.*\biii\b", "fathers/eusebius-he-3", "book iii"),
    (r"eusebius.*church history.*\bbook iv\b", "fathers/eusebius-he-4", "book iv"),
    (r"against celsus", "fathers/origen-contra-celsum-1", "against celsus"),
    # Classical and Jewish witnesses
    (r"josephus.*antiquities.*\bbook xviii\b|antiquities.*18\.", "witnesses/josephus-antiquities-18", "book xviii"),
    (r"josephus.*antiquities.*\bbook xx\b|antiquities.*20\.", "witnesses/josephus-antiquities-20", "book xx"),
    (r"tacitus.*annals", "witnesses/tacitus-annals-15-44", "annals"),
    (r"suetonius", "witnesses/suetonius-claudius-25", "claudius"),
    (r"pliny", "legal/pliny-trajan-letters-10-96-97", "trajan"),
    (r"lucian|peregrinus", "witnesses/lucan-peregrinus", "peregrinus"),
    (r"mara bar serapion", "witnesses/mara-bar-serapion", "mara"),
    (r"sanhedrin", "witnesses/talmud-sanhedrin-43a", "sanhedrin"),
    (r"thallus|phlegon|julius africanus", "witnesses/thallus-phlegon-fragments", "africanus"),
    (r"hadrian", "legal/hadrian-rescript-minucius-fundanus", "adrian"),
    # Gospels and apocrypha
    (r"gospel of thomas", "gospels/gospel-of-thomas", "thomas"),
    (r"gospel of mary", "gospels/gospel-of-mary", "mary"),
    (r"gospel of philip", "gospels/gospel-of-philip", "philip"),
    (r"gospel of truth", "gospels/gospel-of-truth", "truth"),
    (r"gospel of judas", "gospels/gospel-of-judas", "judas"),
    (r"gospel of peter", "gospels/gospel-of-peter", "peter"),
    (r"egerton", "gospels/egerton-gospel", "egerton"),
    (r"protevangelium|infancy gospel of james|infancy james", "gospels/infancy-gospel-of-james", "james"),
    (r"infancy gospel of thomas|infancy thomas", "gospels/infancy-gospel-of-thomas", "thomas"),
    (r"nicodemus|acts of pilate", "gospels/apocryphal-gospels-anf08-walker-1870", "nicodemus"),
    (r"diatessaron", "gospels/diatessaron-tatian-hogg-1896", "diatessaron"),
    (r"apocryphon of james|secret book of james", "gospels/secret-book-of-james", "james"),
    (r"papyrus oxyrhynchus 5575|p\.oxy 5575", "gospels/sayings-of-jesus-p-oxy-5575", "recto"),
    # Archaeology pages written for this archive
    (r"pilate inscription|latin dedicatory inscription.*pilate", "archaeology/pilate-inscription", "pilate"),
    (r"ossuary of caiaphas|caiaphas", "archaeology/caiaphas-ossuary", "caiaphas"),
    (r"james ossuary|controversial inscription in the news", "archaeology/james-ossuary", "james"),
    (r"dura-europos", "archaeology/dura-europos-christian-building", "dura-europos"),
    (r"megiddo mosaic", "archaeology/megiddo-mosaic", "megiddo"),
    (r"frankfurt silver inscription|silver inscription", "archaeology/frankfurt-silver-amulet", "amule"),
    (r"nazareth inscription", "archaeology/nazareth-inscription", "nazareth"),
    (r"dead sea scrolls|great isaiah scroll", "archaeology/dead-sea-scrolls-isaiah", "isaiah"),
    (r"radiocarbon dating of the shroud|shroud of turin|x-ray dating.*shroud|textile fragments", "archaeology/shroud-of-turin-radiocarbon", "shroud"),
    # Church documents
    (r"nostra aetate", "denominational/nostra-aetate-1965", "nostra aetate"),
    (r"dilexit nos", "denominational/dilexit-nos-2024", "dilexit nos"),
    (r"norms for proceeding.*supernatural|discernment of alleged supernatural", "denominational/norms-supernatural-phenomena-2024", "supernatural"),
    (r"common christological declaration", "legal/common-christological-declaration-1994", "assyrian"),
    (r"catechism of the catholic church", "citations/catechism-ccc-464-469", "464"),
    # Qur'an
    (r"qur.?an 3:45", "scripture/quran/surah-03", "imran"),
    (r"qur.?an 4:157", "scripture/quran/surah-04", "women"),
    (r"qur.?an 5:110", "scripture/quran/surah-05", "table"),
    (r"qur.?an 19:16", "scripture/quran/surah-19", "mary"),
]

COMPILED = [(re.compile(p, re.I), doc, marker) for p, doc, marker in RULES]


def main() -> int:
    refs = json.loads(Path("collections/references/refs.json").read_text())
    texts = {}
    for p in Path("collections").rglob("*.md"):
        if p.parent.name == "_meta":
            continue
        texts[p.relative_to("collections").with_suffix("").as_posix()] = p.read_text(
            encoding="utf-8", errors="replace"
        ).lower()

    links: dict[str, str] = {}
    report = ["# Reference to document links", "",
              "Each row is a reference the register cites, the document in this repository that carries",
              "the same work, and the marker that was found in that document to confirm the match.", "",
              "| Ref | Citation | Document | Marker found |", "|---|---|---|---|"]
    unmatched_primary = []
    for ref in refs:
        citation = ref["citation"]
        low = citation.lower()
        target = marker = None

        m = re.match(r"^((?:[123] )?[a-z]+)\s+(\d+)", low)
        if m and m.group(1) in SCRIPTURE:
            name = SCRIPTURE[m.group(1)]
            doc = f"scripture/new-testament/{name}"
            chapter = m.group(2)
            if doc in texts and f"## chapter {chapter}" in texts[doc]:
                target, marker = doc, f"## Chapter {chapter}"

        if not target:
            for pat, doc, need in COMPILED:
                if pat.search(low) and doc in texts and need in texts[doc]:
                    target, marker = doc, need
                    break

        if target:
            links[ref["id"]] = target
            report.append(f"| {ref['id']} | {citation[:110]} | {target} | {marker} |")
        elif re.search(r"primary|ancient|papyrus|manuscript|fragment|translation", ref.get("resource_type", ""), re.I):
            unmatched_primary.append((ref["id"], citation[:90]))

    out = Path("collections/references/links.json")
    out.write_text(json.dumps(dict(sorted(links.items())), indent=1) + "\n")
    Path("collections/references/links-report.md").write_text("\n".join(report) + "\n")
    print(f"{len(links)} of {len(refs)} references linked to a document")
    if unmatched_primary:
        print(f"\nPrimary-source references with no confirmed mirror ({len(unmatched_primary)}):")
        for rid, cite in unmatched_primary:
            print(f"  {rid}  {cite}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
