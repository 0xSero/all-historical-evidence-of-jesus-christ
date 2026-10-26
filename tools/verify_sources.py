#!/usr/bin/env python3
"""Check that every mirrored source actually contains the text it claims to.

A fetch can silently return a page shell, a login screen, or a different work.
This tool holds, per document, strings that must appear in the text, and a
minimum size. Run it after any fetch; it exits non-zero on failure.

    python3 tools/verify_sources.py
"""
import re, sys
from pathlib import Path

# document -> (required substrings, minimum characters)
CHECKS: dict[str, tuple[list[str], int]] = {
    "fathers/didache": (["twelve apostles", "two ways"], 8000),
    "fathers/1-clement": (["clement", "corinthians"], 20000),
    "fathers/ignatius-smyrnaeans": (["smyrn", "ignatius"], 8000),
    "fathers/papias-fragments": (["papias", "mark"], 8000),
    "fathers/justin-first-apology": (["apology", "antoninus"], 20000),
    "fathers/irenaeus-ah-3": (["book iii", "it is not possible that the gospels"], 20000),
    "fathers/irenaeus-ah-1": (["book i", "valentinus"], 20000),
    "fathers/eusebius-he-1": (["book i", "abgar"], 15000),
    "fathers/eusebius-he-3": (["book iii"], 20000),
    "fathers/eusebius-he-4": (["book iv"], 20000),
    "fathers/eusebius-he-5": (["book v", "montanus"], 15000),
    "fathers/origen-contra-celsum-1": (["celsus", "jesus"], 20000),
    "fathers/hippolytus-refutation-9": (["elchasai"], 8000),
    "fathers/athanasius-festal-39": (["letter"], 5000),
    "witnesses/josephus-antiquities-18": (["wise man", "pilate"], 20000),
    "witnesses/josephus-antiquities-20": (["james", "ananus"], 15000),
    "witnesses/tacitus-annals-15-44": (["christus", "pilatus"], 5000),
    "witnesses/suetonius-claudius-25": (["chrestus"], 5000),
    "witnesses/lucan-peregrinus": (["peregrin", "crucified"], 8000),
    "witnesses/mara-bar-serapion": (["mara"], 1000),
    "witnesses/talmud-sanhedrin-43a": (["sanhedrin", "jesus"], 1000),
    "witnesses/thallus-phlegon-fragments": (["thallus", "phlegon"], 8000),
    "legal/pliny-trajan-letters-10-96-97": (["trajan", "christians"], 5000),
    "legal/hadrian-rescript-minucius-fundanus": (["adrian", "fundanus"], 1000),
    "legal/common-christological-declaration-1994": (["assyrian"], 1000),
    "gospels/gospel-of-thomas": (["saying 114", "thomas"], 20000),
    "gospels/gospel-of-philip": (["philip"], 20000),
    "gospels/gospel-of-truth": (["truth"], 20000),
    "gospels/gospel-of-mary": (["mary"], 5000),
    "gospels/gospel-of-judas": (["judas"], 15000),
    "gospels/gospel-of-peter": (["pilate"], 5000),
    "gospels/egerton-gospel": (["fragment"], 2000),
    "gospels/infancy-gospel-of-james": (["joachim", "mary"], 15000),
    "gospels/infancy-gospel-of-thomas": (["child"], 10000),
    "gospels/secret-book-of-james": (["james"], 10000),
    "gospels/strangers-book": (["stranger"], 3000),
    "gospels/secret-gospel-of-mark": (["clement", "mark"], 3000),
    "gospels/sayings-of-jesus-p-oxy-5575": (["recto"], 800),
    "gospels/q-sayings-source": (["q"], 10000),
    "gospels/diatessaron-tatian-hogg-1896": (["diatessaron", "tatian"], 100000),
    "gospels/apocryphal-gospels-anf08-walker-1870": (["nicodemus", "protevangelium"], 50000),
    "gospels/gutenberg/pistis-sophia-horner-1924": (["pistis sophia"], 200000),
    "gospels/gutenberg/gnosis-of-the-light-lamplugh-1918": (["bruce"], 50000),
    "gospels/gutenberg/gnostic-crucifixion-mead-1907": (["crucifixion"], 30000),
    "gospels/gutenberg/apocryphal-new-testament-hone-1820": (["nicodemus", "infancy"], 200000),
    "denominational/nostra-aetate-1965": (["nostra aetate", "jews"], 5000),
    "denominational/dilexit-nos-2024": (["heart", "jesus"], 100000),
    "denominational/norms-supernatural-phenomena-2024": (["supernatural"], 20000),
    "scripture/quran/surah-03": (["imran"], 2000),
    "scripture/quran/surah-04": (["women"], 2000),
    "scripture/quran/surah-05": (["table"], 2000),
    "scripture/quran/surah-19": (["mary"], 2000),
}


def main() -> int:
    failures = []
    for doc, (needs, minimum) in sorted(CHECKS.items()):
        path = Path("collections") / f"{doc}.md"
        if not path.exists():
            path = Path("collections") / f"{doc}.txt"
        if not path.exists():
            failures.append((doc, "missing file"))
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        if len(text) < minimum:
            failures.append((doc, f"too short: {len(text)} < {minimum}"))
            continue
        absent = [n for n in needs if n not in text]
        if absent:
            failures.append((doc, f"missing: {', '.join(absent)}"))
    for doc, why in failures:
        print(f"FAIL {doc}: {why}")
    print(f"{len(CHECKS) - len(failures)}/{len(CHECKS)} documents verified")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
