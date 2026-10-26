# Jesus Christ: a chronological research dossier, its sources, and an archive

This repository holds three things:

1. **The dossier** — [Jesus_Christ_Research_Dossier.pdf](Jesus_Christ_Research_Dossier.pdf), a chronological guide to the evidence about Jesus (175 life entries, 100 scriptural connections, 238 numbered references, research cutoff 26 October 2026).
2. **The sources it cites** — every ancient text the dossier quotes, mirrored in a public-domain translation where one exists, with the exact destination of every reference link taken from the PDF itself.
3. **A readable, searchable site** — [docs/index.html](docs/index.html), which turns the collections into a searchable archive with a reading pane, reference cards, and cross-links between the dossier's passages and the documents behind them.

**Read it:** open `docs/index.html` in a browser, or serve it:

```sh
python3 -m http.server -d docs 8123   # then open http://127.0.0.1:8123/
```

## The collections

<!-- collections:start -->
| Collection | Documents | What it holds |
|---|---|---|
| [dossier](collections/dossier/) | 7 | The PDF's own text, sectioned, plus the 238-entry reference register |
| [scripture](collections/scripture/) | 31 | New Testament, World English Bible, one file per book |
| [gospels](collections/gospels/) | 20 | Thomas, Philip, Truth, Mary, Judas, Peter, Egerton, the infancy gospels, Q, P.Oxy. 5575, Nicodemus, the Diatessaron |
| [fathers](collections/fathers/) | 14 | Didache, Clement, Ignatius, Papias, Justin, Irenaeus, Eusebius, Origen, Hippolytus, Athanasius |
| [witnesses](collections/witnesses/) | 8 | Josephus, Tacitus, Suetonius, Lucian, Mara bar Serapion, the Talmud, Thallus and Phlegon |
| [legal](collections/legal/) | 2 | Pliny and Trajan, Hadrian's rescript, the 1994 Common Christological Declaration |
| [archaeology](collections/archaeology/) | 9 | Pilate inscription, both ossuaries, Dura-Europos, Megiddo, the Frankfurt amulet, Nazareth inscription, Isaiah scroll, the shroud |
| [denominational](collections/denominational/) | 3 | Nostra aetate, Dilexit nos, the 2024 norms on alleged supernatural phenomena |
| [registry](collections/registry/) | 1 | Thirty-six gospels and gospel-type texts with dates, manuscripts, ancient verdicts, and canonical status in each tradition. |
| [citations](collections/citations/) | 238 | One page per register entry: the citation, what it supports, and where it is cited |
| [references](collections/references/) | 238 | `refs.json` (exact link destinations from the PDF), `links.json` (mirrored entries), `links-report.md` (the verified match for each) |
<!-- collections:end -->

Also: [the gospel registry](collections/registry/gospel-registry.md), a register of 36 gospels and gospel-type texts with dates, manuscripts, ancient verdicts, and canonical status by tradition.

## How the reference layer works

The dossier prints a source for each of its 238 entries. Its PDF also carries a live hyperlink for 233 of them, often to a specific passage (Perseus *Republic* 2.362a, New Advent *Against Heresies* I.24, Josephus XVIII, the Yale Dura-Europos record). `tools/make_references.py` reads those link annotations out of the PDF and attaches each one to the reference whose position on the page it belongs to, so the archive carries the exact destination rather than a guessed hostname.

The remaining five were resolved by hand and checked with an HTTP request at build time (`tools/resolve_missing.py`). All 238 entries therefore have a URL.

A reference is linked to a mirrored document only when two things hold: the citation names the work, **and** the document actually contains the cited locator. `collections/references/links-report.md` records each match and the marker that confirmed it. 89 entries are mirrored; the rest link out.

## Build

Everything derived is reproducible:

```sh
./tools/build-all.sh
```

| Tool | Does |
|---|---|
| `tools/fetch_source.py` | Fetch a URL to normalized Markdown plus a metadata sidecar |
| `tools/ccel_section.py` | Extract one work from a CCEL volume text (caches volumes under `.cache/`) |
| `tools/make_references.py` | PDF → 238 reference entries with their exact link destinations |
| `tools/resolve_missing.py` | Pins the five entries that carry no embedded link, after an HTTP check |
| `tools/make_dossier.py` | PDF → sectioned Markdown, headings restored from the table of contents |
| `tools/make_cards.py` | One page per reference entry |
| `tools/make_links.py` | Verified reference → document mapping, with a report |
| `tools/build_catalog.py` | Filesystem + sidecars → `collections/catalog.json` |
| `tools/build_site.py` | Catalog → `docs/` (site shell, per-document HTML, search index) |
| `tools/verify_sources.py` | Asserts every mirrored source contains the text it claims |
| `tools/clean_fetched.py` | Strips site navigation and reader chrome from fetched pages |

## Sourcing and licensing

Mirrored texts are public domain: the World English Bible (public domain; "World English Bible" is a trademark of eBible.org, and the wording here is unaltered), the Ante-Nicene and Nicene-and-Post-Nicene Fathers translations, Whiston's Josephus, the Fowler Lucian, Cureton's Mara bar Serapion, Palmer's Qur'an, Project Gutenberg editions, and Mark M. Mattison's public-domain gospel translations.

**One exception:** the Talmud passage in [collections/witnesses/talmud-sanhedrin-43a.md](collections/witnesses/talmud-sanhedrin-43a.md) is the William Davidson edition, licensed **CC BY-NC 4.0**. The public-domain English translation of Sanhedrin (Rodkinson, 1918) omits this passage. The licence is recorded in that file's metadata.

Copyrighted scholarship is **linked, never copied**. Museum and archaeology entries are original summaries written for this archive, with links to the holding institution; no inscription text or photograph is reproduced where its translation or image is still in copyright.

The [nine Archaeology entries](collections/archaeology/) are the archive's own prose. They state what each artifact does and does not establish, and flag the disputed cases (the James ossuary, the Nazareth inscription's provenance, the shroud's dating) as disputed.
