# Registry of Gospels and Their Canonical Status

This registry lists every gospel and gospel-type text about Jesus that survives in full, survives in fragments, or is known only from ancient citations. For each one it records how the text was judged in ancient canon lists and what its canonical status is in Christian traditions today. Where this repository holds a public-domain text, the **Text here** column links to it.

Dates of composition are scholarly ranges. Manuscript dates are a separate thing, and many texts survive only in copies made centuries after they were written (see the dossier's distinction between *event chronology* and *document chronology*).

## Status key

| Status | Meaning |
|---|---|
| **Canonical (universal)** | Accepted as scripture by every Christian church today. |
| **Canonical (historical/local)** | Functioned as scripture in some churches for a period but is canonical nowhere today. |
| **Canonical (non-Christian canon)** | Scripture in a religion other than mainstream Christianity, e.g. Manichaeism. |
| **Disputed (antilegomena)** | Read in some churches, but ancient lists placed it among disputed or spurious books. It never became canonical. |
| **Non-canonical, liturgically influential** | Never scripture, but its stories shaped feasts, iconography, or saints' names in Catholic and Orthodox practice. |
| **Rejected** | Named and rejected, or classed as heretical, by an ancient authority or list. |
| **Non-canonical (unlisted)** | Never canonical, and absent from the ancient canon lists, often because it was lost until modern discovery. |
| **Hypothetical / disputed authenticity** | A modern scholarly reconstruction, or a text whose ancient origin is contested. |

### Ancient authorities cited

| Abbrev. | Source | Date |
|---|---|---|
| Iren. | Irenaeus, *Against Heresies* (four-gospel argument at 3.11.8) | c. 180 |
| Orig. | Origen, *Homily 1 on Luke*, which names the gospels of the Egyptians, the Twelve, Basilides, Thomas, and Matthias as gospels the church does not accept | c. 233 |
| Eus. | Eusebius, *Church History* 3.25. Categories: *homologoumena* (accepted), *antilegomena* (disputed), *notha* (spurious), heretical | c. 325 |
| Ath. | Athanasius, 39th Festal Letter: the first list of exactly the 27 NT books | 367 |
| Gel. | *Decretum Gelasianum*, a list of rejected books (attributed to Pope Gelasius, probably 6th c.) | 6th c. |
| Niceph. | Stichometry of Nicephorus, which divides books into canonical, *antilegomena*, and *apocrypha* | 9th c. |

---

## 1. The canonical gospels

All four are **Canonical (universal)**: Catholic, Eastern Orthodox, Oriental Orthodox (Coptic, Ethiopian, Eritrean, Armenian, Syriac), Assyrian Church of the East, and Protestant. Iren. defends exactly four. Eus. lists them first among the *homologoumena*. Ath. lists them.

| Gospel | Composed (est.) | Earliest manuscript witnesses | Notes | Text here |
|---|---|---|---|---|
| Matthew | c. 80–90 | P104 (2nd c.), P64+67 (c. 200) | Traditionally attributed to the apostle Matthew; the work itself is anonymous. | [01-matthew.md](texts/new-testament/01-matthew.md) |
| Mark | c. 66–75 | P45 (3rd c.) | Usually considered the earliest gospel. The longer ending (16:9–20) is absent from Codex Sinaiticus and Codex Vaticanus. It is canonical for Catholics (Trent) and Orthodox, and bracketed in many Protestant translations. | [02-mark.md](texts/new-testament/02-mark.md) |
| Luke | c. 80–95 | P75 (c. 175–225), P4 | First volume of Luke–Acts. Marcion's gospel (below) was a shorter form of it. | [03-luke.md](texts/new-testament/03-luke.md) |
| John | c. 90–110 | P52 (2nd c.), P66, P75 | The story of the woman taken in adultery (7:53–8:11) is absent from the earliest manuscripts. | [04-john.md](texts/new-testament/04-john.md) |

## 2. Gospel harmonies

| Gospel | Composed | Witnesses | Ancient verdict | Status today | Text here |
|---|---|---|---|---|---|
| **Diatessaron** (Tatian) | c. 170 | Original (Syriac or Greek) lost. Witnesses include Ephrem's Syriac commentary (4th c.), the Arabic harmony, Codex Fuldensis (Latin, 546), and possibly the Dura-Europos fragment (before 256) | The standard gospel text of Syriac-speaking churches into the 5th c. Theodoret of Cyrrhus removed some 200 copies from his diocese, and Rabbula of Edessa ordered the separate gospels to be used | **Canonical (historical/local)**: Syriac churches until the 5th c. Not canonical anywhere today. | [diatessaron-tatian-hogg-1896.txt](texts/extracanonical/diatessaron-tatian-hogg-1896.txt) |

## 3. Sayings gospels and sayings collections

| Gospel | Composed | Witnesses | Ancient verdict | Status today | Text here |
|---|---|---|---|---|---|
| **Gospel of Thomas** | c. 50–140 (disputed) | Greek P.Oxy. 1, 654, 655 (c. 200–250); complete Coptic text in Nag Hammadi Codex II,2 (c. 350) | Hippolytus quotes it. Orig. rejects. Eus. lists it among heretical works. Cyril of Jerusalem attributes it to Manichaeans. Niceph. apocrypha | **Rejected** | [gospel-of-thomas.md](texts/extracanonical/gospel-of-thomas.md) (Mattison); [GG 01](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/01-Gospel-of-Thomas.pdf) (Lambdin) |
| **Q** (sayings source) | c. 40–70 (if it existed) | No manuscript. Reconstructed from the non-Markan material shared by Matthew and Luke | Unknown in antiquity | **Hypothetical**: a modern scholarly reconstruction | [q-sayings-source.md](texts/extracanonical/q-sayings-source.md) |
| **Sayings of Jesus (P.Oxy. 5575)** | Copy dated c. 150–200 | A single Greek papyrus leaf, published in 2023 (*Oxyrhynchus Papyri* 87) | Unknown in antiquity. Its sayings parallel Matthew, Luke, and Thomas | **Non-canonical (unlisted)** | [sayings-of-jesus-p-oxy-5575.md](texts/extracanonical/sayings-of-jesus-p-oxy-5575.md) |

## 4. Gnostic and revelation gospels (the "Gnostic Bible")

These texts present Jesus revealing secret knowledge (*gnosis*), usually after the resurrection. Most come from the Nag Hammadi codices (found 1945), the Berlin Codex (BG 8502), the Askew and Bruce codices, or Codex Tchacos.

**Our Gnostic Bible.** The reference editions are the eleven PDFs in [0xSero/gnostic-gospels](https://github.com/0xSero/gnostic-gospels), cited below as **GG 00–11**. That repo's `MANIFEST.json` records each PDF's translator, source URL, and SHA-256. Nine of its translations are under copyright (Robinson's *Nag Hammadi Library* translators), so they are linked here rather than copied. Only Mattison's Mary and Judas are public domain. GG 07–09 are not gospels; they are listed at the end of this section because they belong to that set.

| Gospel | Composed | Witnesses | Ancient verdict | Status today | Text here |
|---|---|---|---|---|---|
| **Gospel of Mary** | 2nd c. | Greek P.Ryl. 463 and P.Oxy. 3525 (3rd c.); Coptic Berlin Codex 8502 (5th c.) | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [gospel-of-mary.md](texts/extracanonical/gospel-of-mary.md); [GG 02](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/02-Gospel-of-Mary.pdf) (both Mattison) |
| **Gospel of Judas** | c. 130–170 | Codex Tchacos 3 (Coptic, radiocarbon c. 280 ± 60) | Iren. 1.31.1 names it as used by the "Cainites" | **Rejected** | [gospel-of-judas.md](texts/extracanonical/gospel-of-judas.md); [GG 06](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/06-Gospel-of-Judas.pdf) (both Mattison) |
| **Gospel of Philip** | 2nd–3rd c. | Nag Hammadi Codex II,3 (c. 350) | Epiphanius quotes a "Gospel of Philip" (possibly a different work) | **Non-canonical (unlisted)** | [gospel-of-philip.md](texts/extracanonical/gospel-of-philip.md) (Mattison); [GG 05](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/05-Gospel-of-Philip.pdf) (Isenberg) |
| **Gospel of Truth** | c. 140–180 (Valentinian) | Nag Hammadi Codices I,3 and XII,2 | Iren. 3.11.9 says the Valentinians had a "Gospel of Truth" | **Rejected** | [gospel-of-truth.md](texts/extracanonical/gospel-of-truth.md) (Mattison); [GG 03](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/03-Gospel-of-Truth.pdf) (Attridge & MacRae) |
| **Secret Book (Apocryphon) of James** | 2nd c. | Nag Hammadi Codex I,2 | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [secret-book-of-james.md](texts/extracanonical/secret-book-of-james.md) |
| **The Stranger's Book** (Allogenes, CT 4) | 2nd–3rd c. | Codex Tchacos 4 | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [strangers-book.md](texts/extracanonical/strangers-book.md) |
| **Pistis Sophia** | 3rd c. | Askew Codex (Coptic, 4th c.?) | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [pistis-sophia-horner-1924.txt](texts/extracanonical/gutenberg/pistis-sophia-horner-1924.txt) |
| **Untitled Text of the Bruce Codex** | 3rd c. | Bruce Codex (Coptic) | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [gnosis-of-the-light-lamplugh-1918.txt](texts/extracanonical/gutenberg/gnosis-of-the-light-lamplugh-1918.txt) |
| **Hymn and vision of the cross** (Acts of John 94–102) | 2nd–3rd c. | Greek Acts of John manuscripts | Acts of John: Eus. heretical. Rejected at the Second Council of Nicaea (787) | **Rejected** | [gnostic-crucifixion-mead-1907.txt](texts/extracanonical/gutenberg/gnostic-crucifixion-mead-1907.txt) |
| Secret Book (Apocryphon) of John | 2nd c. | Nag Hammadi Codices II,1, III,1, IV,1; Berlin Codex 8502,2 | Iren. 1.29 summarizes closely parallel teaching | **Non-canonical (unlisted)** | [GG 04](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/04-Apocryphon-of-John.pdf) (Waldstein & Wisse, long recension) |
| Gospel of the Egyptians (Coptic; *Holy Book of the Great Invisible Spirit*) | 2nd–3rd c. (Sethian) | Nag Hammadi Codices III,2 and IV,2 | Not mentioned in any ancient list (distinct from the Greek work below) | **Non-canonical (unlisted)** | [GG 11](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/11-Gospel-of-the-Egyptians.pdf) (Böhlig & Wisse) |
| Dialogue of the Savior | 2nd c. | Nag Hammadi Codex III,5 | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [GG 10](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/10-Dialogue-of-the-Savior.pdf) (Emmel) |
| Books of Jeu | 3rd c. | Bruce Codex | Not mentioned in any ancient list | **Non-canonical (unlisted)** | — |
| Gospel of Eve | 2nd–4th c. | Lost; quoted by Epiphanius (*Panarion* 26) | Rejected as heretical | **Rejected** | — |
| Gospel of Basilides | 2nd c. | Lost | Orig. rejects | **Rejected** | — |
| Gospel of Matthias / Traditions of Matthias | 2nd c. | Lost; quoted by Clement of Alexandria | Orig. and Eus. heretical. Gel. rejects | **Rejected** | — |
| Living Gospel of Mani | 3rd c. | Fragments (e.g. Cologne Mani Codex) | Scripture of Manichaeism | **Canonical (non-Christian canon)**: Manichaean | — |
| *Hypostasis of the Archons* (not a gospel) | 3rd c. | Nag Hammadi Codex II,4 | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [GG 07](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/07-Hypostasis-of-the-Archons.pdf) (Layton) |
| *On the Origin of the World* (not a gospel) | 3rd–4th c. | Nag Hammadi Codices II,5 and XIII,2 | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [GG 08](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/08-On-the-Origin-of-the-World.pdf) (Bethge & Layton) |
| *Thunder, Perfect Mind* (revelation poem, not a gospel) | 2nd–3rd c. | Nag Hammadi Codex VI,2 | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [GG 09](https://github.com/0xSero/gnostic-gospels/blob/main/pdfs/09-Thunder-Perfect-Mind.pdf) (MacRae) |

## 5. Jewish-Christian gospels

| Gospel | Composed | Witnesses | Ancient verdict | Status today | Text here |
|---|---|---|---|---|---|
| Gospel of the Hebrews | early–mid 2nd c. | Lost; quoted by Clement of Alexandria, Origen, Jerome | Eus.: "some" place it among the spurious (*notha*) books. Niceph.: *antilegomena* | **Disputed (antilegomena)** | — |
| Gospel of the Nazarenes | 2nd c. | Lost; Jerome and later marginal notes (the grouping is modern) | Never accepted | **Non-canonical (unlisted)** | — |
| Gospel of the Ebionites | 2nd c. | Lost; quoted by Epiphanius (*Panarion* 30) | Treated as heretical | **Rejected** | — |
| Gospel of the Egyptians (Greek) | 2nd c. | Lost; quoted by Clement of Alexandria (*Stromata* 3) | Orig. rejects | **Rejected** | — |

## 6. Narrative and Passion gospels

| Gospel | Composed | Witnesses | Ancient verdict | Status today | Text here |
|---|---|---|---|---|---|
| **Gospel of Peter** | 2nd c. | Akhmim fragment (8th–9th c. manuscript); P.Oxy. 2949 (debated) | Serapion of Antioch (c. 200) first allowed it at Rhossus, then rejected it. Eus. heretical. Gel. rejects | **Rejected** | [gospel-of-peter.md](texts/extracanonical/gospel-of-peter.md) |
| **Egerton Gospel** (Unknown Gospel) | 2nd c. | P.Egerton 2 and P.Köln 255 (copy c. 150–200) | Not mentioned in any ancient list | **Non-canonical (unlisted)** | [egerton-gospel.md](texts/extracanonical/egerton-gospel.md) |
| **Gospel of Nicodemus** (Acts of Pilate and Descent into Hell) | 4th–5th c. in its current form | Greek, Latin, Coptic, Syriac, Armenian | Very widely read in the medieval West. Source of the Harrowing of Hell tradition | **Non-canonical, liturgically influential** | [ANF 8](texts/extracanonical/apocryphal-gospels-anf08-walker-1870.txt); [Hone](texts/extracanonical/gutenberg/apocryphal-new-testament-hone-1820.txt) |
| **Pilate cycle** (Letter and Report of Pilate, Giving Up of Pilate, Death of Pilate, Narrative of Joseph of Arimathaea, Avenging of the Saviour) | 4th–8th c. | Greek and Latin | Never canonical. The Ethiopian church venerates Pilate and his wife Procla as saints; Eastern Orthodoxy venerates Procla | **Non-canonical** | [ANF 8](texts/extracanonical/apocryphal-gospels-anf08-walker-1870.txt) |
| **Secret Gospel of Mark** | Disputed | Known only from a letter attributed to Clement of Alexandria, which Morton Smith reported finding at Mar Saba in 1958. Only photographs survive | Unknown in antiquity | **Disputed authenticity**: some scholars regard it as a modern forgery | [secret-gospel-of-mark.md](texts/extracanonical/secret-gospel-of-mark.md) |
| Gospel of Marcion | c. 140 | Lost; reconstructed from Tertullian and Epiphanius | The sole gospel of Marcion's church. Rejected by Irenaeus, Tertullian, and others | **Canonical (historical/local)**: Marcionite church only. **Rejected** by proto-orthodox writers | — |
| Gospel of Bartholomew / Questions of Bartholomew | 3rd–6th c. | Greek, Latin, Slavonic, Coptic | Gel. rejects "Gospels in the name of Bartholomew" | **Rejected** | — |
| Gospel of the Savior (Unknown Berlin Gospel) | 2nd–3rd c. | P.Berol. 22220 (Coptic) | Not mentioned in any ancient list | **Non-canonical (unlisted)** | — |
| Gospel of Gamaliel | 5th–6th c. | Coptic fragments; Ethiopic *Lament of Mary* | Never canonical | **Non-canonical** | — |
| Gospel of Barnabas (medieval) | 14th–16th c. | Italian and Spanish manuscripts (16th c.) | Unrelated to the lost "Gospel of Barnabas" rejected by Gel. Presents an Islamic portrait of Jesus | **Non-canonical** in any church | — |

## 7. Infancy gospels

| Gospel | Composed | Witnesses | Ancient verdict | Status today | Text here |
|---|---|---|---|---|---|
| **Infancy Gospel of James** (Protevangelium) | c. 150 | Papyrus Bodmer V (3rd–4th c.); more than 140 Greek manuscripts | Gel. rejects the "Gospel of James the Younger". Source of the names Joachim and Anne and of the feast of the Presentation of Mary | **Non-canonical, liturgically influential** (Orthodox and Catholic) | [Mattison](texts/extracanonical/infancy-gospel-of-james.md); [ANF 8](texts/extracanonical/apocryphal-gospels-anf08-walker-1870.txt); [Hone](texts/extracanonical/gutenberg/apocryphal-new-testament-hone-1820.txt) |
| **Infancy Gospel of Thomas** | 2nd c. | Earliest complete Greek manuscript: Hagios Saba 259 (11th c.); older Syriac and Latin versions | Iren. 1.20.1 cites a story from it as used by the Marcosians. Gel. rejects a book "of the infancy of the Saviour" | **Rejected** | [Mattison](texts/extracanonical/infancy-gospel-of-thomas.md); [ANF 8](texts/extracanonical/apocryphal-gospels-anf08-walker-1870.txt); [Hone](texts/extracanonical/gutenberg/apocryphal-new-testament-hone-1820.txt) |
| **Gospel of Pseudo-Matthew** | 7th c. (Latin) | Latin manuscripts | Shaped medieval Western art (e.g. the ox and ass at the manger) | **Non-canonical, liturgically influential** | [ANF 8](texts/extracanonical/apocryphal-gospels-anf08-walker-1870.txt) |
| **Gospel of the Nativity of Mary** | 9th c. (Latin) | Latin manuscripts | Never canonical | **Non-canonical** | [ANF 8](texts/extracanonical/apocryphal-gospels-anf08-walker-1870.txt); [Hone](texts/extracanonical/gutenberg/apocryphal-new-testament-hone-1820.txt) |
| **Arabic Infancy Gospel** | 5th–6th c. (Syriac origin) | Arabic and Syriac | Never canonical | **Non-canonical** | [ANF 8](texts/extracanonical/apocryphal-gospels-anf08-walker-1870.txt); [Hone](texts/extracanonical/gutenberg/apocryphal-new-testament-hone-1820.txt) |
| **History of Joseph the Carpenter** | 5th–7th c. | Coptic and Arabic | Never canonical | **Non-canonical** | [ANF 8](texts/extracanonical/apocryphal-gospels-anf08-walker-1870.txt) |
| Armenian Infancy Gospel | 6th c. or later | Armenian | Never canonical | **Non-canonical** | — |

---

## New Testament canon by tradition

The four gospels are canonical everywhere. Traditions differ only on the rest of the New Testament:

| Tradition | NT books | Differences from the 27-book canon |
|---|---|---|
| Catholic | 27 | Defined dogmatically at Trent (1546). |
| Eastern Orthodox | 27 | Revelation is canonical but is not read in the liturgy. |
| Protestant | 27 | Luther questioned Hebrews, James, Jude, and Revelation and placed them last in his 1522 New Testament. They were never removed. |
| Coptic, Armenian, Syriac Orthodox | 27 | The Syriac Peshitta originally had 22 books. The other five came in through later Syriac versions (Philoxenian, Harklean). The Armenian church at times included 3 Corinthians. |
| Assyrian Church of the East | 22 | The Peshitta canon: it omits 2 Peter, 2 and 3 John, Jude, and Revelation. |
| Ethiopian Orthodox Tewahedo | 27 (narrower) / 35 (broader) | The broader canon adds the Sinodos (4 parts), the Book of the Covenant (2), Ethiopic Clement (1), and the Ethiopic Didascalia (1). None of these is a gospel. |

The full 27-book text is in [texts/new-testament](texts/new-testament/README.md).

## Sources for this registry

- Eusebius, *Church History* 3.25; Athanasius, *Festal Letter* 39; Irenaeus, *Against Heresies*; Origen, *Homily 1 on Luke*. Translations: [New Advent / CCEL](https://www.newadvent.org/fathers/).
- Bart D. Ehrman and Zlatko Pleše, *The Apocryphal Gospels: Texts and Translations* (Oxford, 2011).
- Bruce M. Metzger, *The Canon of the New Testament* (Oxford, 1987).
- [NASSCAL e-Clavis: Christian Apocrypha](https://www.nasscal.com/e-clavis-christian-apocrypha/), which has per-text manuscript and bibliography entries.
- [Gospels.net](https://www.gospels.net/), Mark M. Mattison's public-domain translations and manuscript notes.
- [Early Christian Writings](https://www.earlychristianwritings.com/), an index of texts, translations, and dating ranges.
