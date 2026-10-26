#!/usr/bin/env python3
"""Strip site navigation and reader chrome from fetched source texts.

The fetch tools keep whatever text a page renders, which for university and
archive sites includes menus, breadcrumbs, reading-widget status lines, and
footer links. Those lines are not part of the source and pollute both reading
and search, so they are removed here.

    python3 tools/clean_fetched.py [--dry-run]

Rules are line patterns anchored to the beginning or end of the file. Only
navigation-shaped lines are touched; the ancient text itself is never edited.
"""
import re
import sys
from pathlib import Path

START_PATTERNS = [
    r"^- (Josephus Home|Antiquities:|Preface|[IVX]+|Index|Next|Previous)\s*$",
    r"^- (Antiquities|The Wars of the Jews|Against Apion|Life of Josephus).*$",
    r"^Short URL for this page:.*$",
    r"^https?://penelope\.uchicago\.edu/\S*$",
    r"^View the original site,.*$",
    r"^Buy (the|this) book.*$",
    r"^Sacred Texts\s*$",
    r"^Buy this Book on Kindle\s*$",
    r"^Index\s+Previous\s+Next\s*$",
    r"^(Home|Contents|Index) (Page )?[↑|»>].*$",
    r"^bit\.ly/\S*$",
    r"^- [A-Z][A-Za-z .']{0,30}$",
    r"^\s*\|[\s|]*$",
    r"^\s*Share\s*$",
    r"^\s*\[AR - BE\s*-.*\]\s*$",
    r"^#+ \*The\* \*\*Holy See\*\*$",
    r"^\s*Français.*$",
    r"^\s*Deutsch.*$",
    r"^\s*Print\s*$",
]
END_PATTERNS = [
    r"^\s*Table Of Contents\s*$",
    r"^\s*Accessibility\s*$",
    r"^\s*See my copyright page for details.*$",
    r"^\s*Page updated:.*$",
    r"^\s*\d+ of \d+ · Chapter.*$",
    r"^\s*No bookmarks yet\s*$",
    r"^\s*Add one from the reader toolbar\.\s*$",
    r"^\s*Letters of Pliny : Index Page.*$",
    r"^\s*Attalus' home page.*$",
    r"^\s*The URL for this page is.*$",
    r"^\s*(Next|Previous):\s.*$",
    r"^\s*\|[\s|]*$",
    r"^\s*A page or image on this site is in the public domain.*$",
    r"^\s*Sign up free for the full reader\s*$",
    r"^\s*## Comments and social are coming soon\s*$",
    r"^\s*Reader conversations and shared activity will appear here\.\s*$",
    r"^\s*The URL for this page is.*$",
    r"^\s*See the.*copyright.*$",
    r"^\s*(Classical Texts|LacusCurtius|Home)\s*\|?\s*$",
    r"^\s*\|\s*(Classical Texts|LacusCurtius|Home)\s*$",
    r"^\s*Images with borders lead to more information\.\s*$",
    r"^\s*The thicker the border.*$",
    r"^\s*\|\s*\|\s*UP TO:\s*\|?\s*$",
    r"^\s*[A-Z][\w'’ ]{1,22}\s*\|\s*$",
    r"^\s*$",
]
COMPILED_START = [re.compile(p) for p in START_PATTERNS]
COMPILED_END = [re.compile(p) for p in END_PATTERNS]


HEAD_LINES = 120


def clean(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    removed = 0
    kept = []
    for i, line in enumerate(lines):
        if i < HEAD_LINES and any(p.match(line) for p in COMPILED_START):
            removed += 1
            continue
        kept.append(line)
    lines = kept
    keep_to = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if any(p.match(lines[i]) for p in COMPILED_END):
            keep_to = i
            continue
        break
    removed += len(lines) - keep_to
    out = "\n".join(lines[:keep_to])
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + "\n", removed


def main() -> int:
    dry = "--dry-run" in sys.argv
    targets = sorted(Path("collections").glob("*/*.md")) + sorted(Path("collections").glob("*/*.txt"))
    targets = [p for p in targets if p.parent.name != "_meta" and p.name != "README.md"]
    changed = 0
    for path in targets:
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("<!-- Fetched from") and not text.startswith("<!-- Extracted from"):
            continue
        new, removed = clean(text)
        if removed and new.strip():
            changed += 1
            print(f"{path}: removed {removed} line(s), {len(text)} -> {len(new)} chars")
            if not dry:
                path.write_text(new, encoding="utf-8")
    print(f"{changed} file(s) {'' if dry else ''}updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
