#!/usr/bin/env python3
"""Fetch a source page and store it as a normalized Markdown document.

Usage:
    python3 tools/fetch_source.py --url URL --out collections/<group>/<slug>.md \
        --title "Title" --source-name "e.g. Ante-Nicene Fathers vol. 1" \
        [--license "Public domain"] [--selector "div#content"] [--note "..."]

Writes the Markdown file plus a sidecar at collections/<group>/_meta/<slug>.json.
HTML is converted with a light built-in converter (headings, paragraphs, lists,
blockquotes, links, tables, bold/italic). Scripts, styles, nav, and footers are
dropped. If the page is already plain text, it is wrapped as-is.
"""
import argparse, json, re, sys, time, urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
DROP_TAGS = {"script", "style", "noscript", "nav", "footer", "header", "form", "iframe", "svg", "button", "select", "input"}
BLOCK = {"p", "div", "section", "article", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "table", "ul", "ol", "dl", "dt", "dd"}


def fetch(url: str, timeout: int = 40) -> tuple[str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,text/plain,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        ctype = r.headers.get("Content-Type", "")
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc), ctype
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace"), ctype


class Extractor(HTMLParser):
    """Collects text from the region of the page that holds the document."""

    def __init__(self, selector_tag: str | None, selector_attr: str | None):
        super().__init__(convert_charrefs=True)
        self.capture_depth = 0 if not selector_tag else None
        self.selector_tag = selector_tag
        self.selector_attr = selector_attr
        self.skip = 0
        self.buf: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.pending_href = None
        self.in_pre = 0
        self.marker_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in DROP_TAGS:
            self.skip += 1
            return
        if self.capture_depth is None:
            if tag == self.selector_tag and (self.selector_attr is None or self.selector_attr in a.get("id", "") or self.selector_attr in a.get("class", "")):
                self.capture_depth = 0
            return
        if tag in BLOCK:
            self.buf.append("\n\n" if tag not in ("br",) else "\n")
        if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
            self.buf.append("\n\n" + "#" * int(tag[1]) + " ")
        if tag == "li":
            self.buf.append("- ")
        if tag == "pre":
            self.in_pre += 1
            self.buf.append("\n```\n")
        if tag == "blockquote":
            self.buf.append("> ")
        if tag == "tr":
            self.buf.append("| ")
        if tag in ("td", "th"):
            self.buf.append(" | ")
        if tag in ("b", "strong"):
            self.buf.append("**")
            self.marker_stack.append("**")
        if tag in ("i", "em"):
            self.buf.append("*")
            self.marker_stack.append("*")
        if tag == "a" and a.get("href"):
            self.pending_href = a["href"]

    def handle_endtag(self, tag):
        if tag in DROP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
            self.buf.append("\n\n")
        if tag == "pre":
            self.in_pre -= 1
            self.buf.append("\n```\n")
        if tag in BLOCK:
            self.buf.append("\n")
        if tag in ("b", "strong", "i", "em") and self.marker_stack:
            self.buf.append(self.marker_stack.pop())
        if tag == "a":
            self.pending_href = None

    def handle_data(self, data):
        if self.capture_depth is None or self.skip:
            return
        text = data if self.in_pre else re.sub(r"\s+", " ", data)
        self.buf.append(text)

    def text(self) -> str:
        out = "".join(self.buf)
        out = re.sub(r"[ \t]+\n", "\n", out)
        out = re.sub(r"\n{3,}", "\n\n", out)
        out = re.sub(r"[ \t]{2,}", " ", out)
        return out.strip()


def strip_chrome(html: str) -> str:
    for pat in (
        r"<script\b.*?</script>", r"<style\b.*?</style>", r"<noscript\b.*?</noscript>",
        r"<nav\b.*?</nav>", r"<footer\b.*?</footer>", r"<header\b.*?</header>",
        r"<!--.*?-->", r"<svg\b.*?</svg>", r"<form\b.*?</form>",
    ):
        html = re.sub(pat, " ", html, flags=re.S | re.I)
    return html


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--source-name", default="")
    ap.add_argument("--license", default="Public domain")
    ap.add_argument("--selector", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--max-chars", type=int, default=0)
    args = ap.parse_args()

    for attempt in range(3):
        try:
            body, ctype = fetch(args.url)
            break
        except Exception as exc:  # network hiccup, retry
            if attempt == 2:
                print(f"FAIL {args.url}: {exc}", file=sys.stderr)
                return 1
            time.sleep(2 * (attempt + 1))

    assert len(body) > 0, "empty response"
    if "html" in ctype.lower() or body.lstrip().lower().startswith(("<html", "<!doctype")):
        sel_tag = sel_attr = None
        if args.selector:
            m = re.match(r"([a-z0-9]+)(?:[#.]([\w-]+))?", args.selector)
            if m:
                sel_tag, sel_attr = m.group(1), m.group(2)
        p = Extractor(sel_tag, sel_attr)
        p.feed(strip_chrome(body))
        text = p.text()
        if len(text) < 400:  # selector missed; redo on the whole page
            p = Extractor(None, None)
            p.feed(strip_chrome(body))
            text = p.text()
    else:
        text = body.strip()

    if args.max_chars and len(text) > args.max_chars:
        text = text[: args.max_chars].rsplit("\n", 1)[0] + "\n\n[Excerpt truncated at the fetch limit.]"

    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    text = "\n".join(lines)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    meta_dir = out.parent / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    slug = out.stem

    header = [f"<!-- Fetched from {args.url} on {date.today().isoformat()}. -->", ""]
    if args.note:
        header += [f"> {args.note}", ""]
    out.write_text("\n".join(header) + text + "\n", encoding="utf-8")

    meta = {
        "slug": slug,
        "title": args.title,
        "source_name": args.source_name,
        "source_url": args.url,
        "license": args.license,
        "fetched": date.today().isoformat(),
        "chars": len(text),
        "sha256": __import__("hashlib").sha256(text.encode()).hexdigest(),
    }
    (meta_dir / f"{slug}.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"OK {slug} {len(text)} chars -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
