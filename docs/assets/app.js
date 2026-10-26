/* Static archive reader. No dependencies: catalog + per-document JSON. */
(() => {
"use strict";

const $ = (sel, root = document) => root.querySelector(sel);
const main = $("#main"), nav = $("#nav"), tocEl = $("#toc"), panel = $("#panel");
const qInput = $("#q"), results = $("#search-results");

const state = {
  catalog: null,
  docs: new Map(),
  docCache: new Map(),
  search: null,
  searchPromise: null,
  results: [],
  sel: -1,
};

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const docUrl = (id) => "./data/doc/" + id.replace(/\//g, "__") + ".json";
const relTime = (s) => s || "";

/* ---------- theme ---------- */
const themeBtn = $("#theme");
function applyTheme(t) {
  if (t) document.documentElement.dataset.theme = t;
  else delete document.documentElement.dataset.theme;
  themeBtn.textContent = (t === "dark" || (!t && matchMedia("(prefers-color-scheme: dark)").matches)) ? "◑" : "◐";
  themeBtn.setAttribute("aria-pressed", String(!!t));
}
applyTheme(localStorage.getItem("theme"));
themeBtn.addEventListener("click", () => {
  const cur = localStorage.getItem("theme");
  const next = cur === "dark" ? "light" : cur === "light" ? null : "dark";
  if (next) localStorage.setItem("theme", next); else localStorage.removeItem("theme");
  applyTheme(next);
});

/* ---------- boot ---------- */
async function boot() {
  const res = await fetch("./data/docs.json", { cache: "no-cache" });
  state.catalog = await res.json();
  for (const d of state.catalog.docs) state.docs.set(d.id, d);
  renderNav();
  window.addEventListener("hashchange", route);
  qInput.addEventListener("input", onType);
  qInput.addEventListener("keydown", onSearchKey);
  $("#search-form").addEventListener("submit", (e) => { e.preventDefault(); if (state.results[0]) openDoc(state.results[0].id); });
  document.addEventListener("keydown", onGlobalKey);
  document.addEventListener("click", onDocClick);
  initPreview();
  initSources();
  panel.addEventListener("click", (e) => { if (e.target.closest("[data-close-panel]")) hidePanel(); });
  $("#nav-toggle").addEventListener("click", () => {
    const open = $(".sidebar").classList.toggle("open");
    $("#nav-toggle").setAttribute("aria-expanded", String(open));
  });
  route();
}

/* ---------- navigation ---------- */
function renderNav() {
  const { collections, docs } = state.catalog;
  const byColl = new Map(collections.map((c) => [c.id, []]));
  for (const d of docs) if (byColl.has(d.collection)) byColl.get(d.collection).push(d);
  const current = location.hash.match(/^#\/doc\/(.+)$/)?.[1];
  nav.innerHTML = collections.map((c) => {
    const list = byColl.get(c.id);
    const inColl = current && current.startsWith(c.id + "/");
    return `<details class="nav-group"${inColl || c.id === "dossier" ? " open" : ""}>
      <summary><span>${esc(c.title)}</span><span class="nav-count">${list.length}</span></summary>
      <ul class="nav-docs">${list.slice(0, 40).map((d) =>
        `<li><a href="#/doc/${d.id}" data-link title="${esc(d.title)}"${d.id === current ? ' aria-current="page"' : ""}>${esc(d.title)}</a></li>`
      ).join("")}${list.length > 40 ? `<li><a href="#/collection/${c.id}" data-link>…all ${list.length} documents</a></li>` : ""}</ul></details>`;
  }).join("");

  const refs = document.createElement("details");
  refs.className = "nav-group";
  refs.innerHTML = `<summary><span>Reference register</span><span class="nav-count">${state.catalog.references.length}</span></summary>
    <ul class="nav-docs">${state.catalog.references.slice(0, 400).map((r) =>
      `<li><a href="#/ref/${r.id}" data-link title="${esc(r.citation)}">${r.id} · ${esc(r.citation.slice(0, 52))}</a></li>`
    ).join("")}</ul>`;
  nav.appendChild(refs);
}

function setCurrentNav(docId) {
  for (const a of nav.querySelectorAll(".nav-docs a")) a.removeAttribute("aria-current");
  const link = docId && nav.querySelector(`.nav-docs a[href="#/doc/${CSS.escape(docId)}"]`);
  if (link) {
    link.setAttribute("aria-current", "page");
    const group = link.closest("details");
    if (group) group.open = true;
    link.scrollIntoView({ block: "nearest" });
  }
}

/* ---------- router ---------- */
function parseHash() {
  const h = location.hash.replace(/^#/, "") || "/";
  const [path, anchor] = h.split("#");
  if (path === "/" || path === "") return { name: "home" };
  let m = path.match(/^\/doc\/(.+)$/);
  if (m) return { name: "doc", id: decodeURIComponent(m[1]), anchor };
  m = path.match(/^\/ref\/([A-Z]\d+)$/);
  if (m) return { name: "ref", id: m[1] };
  m = path.match(/^\/collection\/(.+)$/);
  if (m) return { name: "collection", id: m[1] };
  m = path.match(/^\/search(?:\/(.*))?$/);
  if (m) return { name: "search", q: decodeURIComponent(m[1] || "") };
  return { name: "home" };
}

async function route() {
  const r = parseHash();
  hidePanel();
  $(".sidebar").classList.remove("open");
  tocEl.hidden = true;
  tocEl.innerHTML = "";
  document.querySelectorAll(".nav-docs a").forEach((a) => a.removeAttribute("aria-current"));
  if (r.name === "home") return renderHome();
  if (r.name === "collection") return renderCollection(r.id);
  if (r.name === "doc") return renderDoc(r.id, r.anchor);
  if (r.name === "ref") return renderRefCard(r.id);
  if (r.name === "search") return renderSearchPage(r.q);
}

function setTitle(t) { document.title = t ? `${t} — Jesus Christ archive` : "Jesus Christ — evidence archive"; }

/* ---------- home ---------- */
function renderHome() {
  setTitle("");
  const { collections, docs, references } = state.catalog;
  const last = localStorage.getItem("lastDoc");
  const lastDoc = last && state.docs.get(last);
  const recent = [...docs].sort((a, b) => (b.fetched || "").localeCompare(a.fetched || "")).slice(0, 10);
  main.innerHTML = `<div class="main-inner">
    <h1 class="page-title">Jesus Christ — evidence archive</h1>
    <p class="page-lede">Every source cited by <em>A Chronological Research Dossier</em>, gathered as collections: scripture, gospels inside and outside the canon, the church fathers, non-Christian witnesses, Roman legal documents, archaeology, and the modern scholarship the dossier relies on. ${docs.length} documents, ${references.length} numbered references.</p>
    ${lastDoc ? `<div class="continue"><span class="muted">Continue reading</span> <a href="#/doc/${lastDoc.id}" data-link>${esc(lastDoc.title)}</a> <button class="icon-btn" type="button" data-forget aria-label="Forget reading position">✕</button></div>` : ""}
    <h2 class="section">Collections</h2>
    <ul class="coll-list">${collections.map((c) => `<li>
      <a href="#/collection/${c.id}" data-link>
        <span class="coll-name">${esc(c.title)}</span><span class="coll-n">${c.docs} ${c.docs === 1 ? "document" : "documents"}</span>
        <span class="coll-blurb">${esc(c.blurb)}</span>
      </a></li>`).join("")}
    </ul>
    <h2 class="section">Recently added</h2>
    <ul class="doc-list">${recent.map((d) => `<li><a href="#/doc/${d.id}" data-link>${esc(d.title)}
      <span class="meta">${esc(collTitle(d.collection))}${d.words ? ` · ${d.words.toLocaleString()} words` : ""}${d.fetched ? ` · ${esc(d.fetched)}` : ""}</span></a></li>`).join("")}
    </ul>
    <h2 class="section">The dossier itself</h2>
    <ul class="doc-list">${docs.filter((d) => d.collection === "dossier").map((d) => `<li><a href="#/doc/${d.id}" data-link>${esc(d.title)}</a></li>`).join("")}
      <li><a href="./Jesus_Christ_Research_Dossier.pdf" data-ext>Original PDF</a></li>
    </ul>
    <p class="muted" style="font-size:.8rem;margin-top:2rem">Built ${esc(state.catalog.generated)}. All mirrored texts are public domain; copyrighted scholarship is linked, never copied.</p>
  </div>`;
  main.querySelector("[data-forget]")?.addEventListener("click", () => { localStorage.removeItem("lastDoc"); renderHome(); });
  window.scrollTo(0, 0);
}

const collTitle = (id) => state.catalog.collections.find((c) => c.id === id)?.title || id;

function renderCollection(id) {
  const c = state.catalog.collections.find((x) => x.id === id);
  if (!c) return renderHome();
  setTitle(c.title);
  const docs = state.catalog.docs.filter((d) => d.collection === id);
  main.innerHTML = `<div class="main-inner">
    <p class="crumbs"><a href="#/" data-link>Home</a></p>
    <h1 class="page-title">${esc(c.title)}</h1>
    <p class="page-lede">${esc(c.blurb)}</p>
    <ul class="doc-list">${docs.map((d) => `<li><a href="#/doc/${d.id}" data-link>${esc(d.title)}
      <span class="meta">${d.words ? `${d.words.toLocaleString()} words` : ""}${d.source_name ? ` · ${esc(d.source_name)}` : ""}</span></a></li>`).join("")}</ul>
  </div>`;
  window.scrollTo(0, 0);
}

/* ---------- reader ---------- */
async function loadDoc(id) {
  if (state.docCache.has(id)) return state.docCache.get(id);
  const res = await fetch(docUrl(id), { cache: "no-cache" });
  if (!res.ok) throw new Error("document not found: " + id);
  const data = await res.json();
  state.docCache.set(id, data);
  return data;
}

async function renderDoc(id, anchor) {
  const meta = state.docs.get(id);
  if (!meta) return renderNotFound(id);
  let data;
  try { data = await loadDoc(id); } catch { return renderNotFound(id); }
  setTitle(data.title);
  localStorage.setItem("lastDoc", id);
  setCurrentNav(id);
  const refCount = (data.refs || []).length;
  main.innerHTML = `<div class="main-inner">
    <p class="crumbs"><a href="#/" data-link>Home</a><span class="sep">›</span>
      <a href="#/collection/${data.collection}" data-link>${esc(collTitle(data.collection))}</a></p>
    <article class="prose" id="doc">${data.html}</article>
    <div class="docmeta">${data.words ? `${data.words.toLocaleString()} words` : ""}
      ${data.source_name ? ` · source: ${esc(data.source_name)}` : ""}
      ${data.source_url ? ` · <a href="${esc(data.source_url)}" data-ext>original</a>` : ""}
      ${data.license ? ` · ${esc(data.license)}` : ""}
      ${refCount ? ` · ${refCount} linked reference${refCount === 1 ? "" : "s"}` : ""}
      · <a href="https://github.com/0xSero/all-historical-evidence-of-jesus-christ/blob/main/collections/${esc(data.path)}" data-ext>markdown</a></div>
    ${(data.siblings || []).length ? `<section class="related" aria-label="Other sources in this collection">
      <h2>Other sources in ${esc(collTitle(data.collection))}</h2>
      <p class="muted">${data.sibling_total > data.siblings.length ? `Showing ${data.siblings.length} of ${data.sibling_total}. Press <kbd>s</kbd> for every source in the archive.` : `Press <kbd>s</kbd> for every source in the archive.`}</p>
      <ul>${data.siblings.map((id) => `<li><a href="#/doc/${id}" data-link>${esc(state.docs.get(id)?.title || id)}</a></li>`).join("")}</ul>
    </section>` : ""}
    <nav class="pager" aria-label="Document navigation">
      ${data.prev ? `<a href="#/doc/${data.prev}" data-link><span class="dir">Previous</span>${esc(state.docs.get(data.prev)?.title || data.prev)}</a>` : "<span></span>"}
      ${data.next ? `<a href="#/doc/${data.next}" data-link class="next"><span class="dir">Next</span>${esc(state.docs.get(data.next)?.title || data.next)}</a>` : "<span></span>"}
    </nav>
  </div>`;
  // The document's own H1 duplicates the page title; keep it for print/anchors.
  buildToc(data.headings || []);
  if (anchor) {
    const target = document.getElementById(anchor);
    if (target) target.scrollIntoView();
    else window.scrollTo(0, 0);
  } else window.scrollTo(0, 0);
}

function renderNotFound(id) {
  const known = state.docs.get(id);
  const raw = known
    ? `https://github.com/0xSero/all-historical-evidence-of-jesus-christ/blob/main/collections/${esc(known.path)}`
    : "https://github.com/0xSero/all-historical-evidence-of-jesus-christ/tree/main/collections";
  main.innerHTML = `<div class="main-inner"><h1 class="page-title">This document could not be loaded</h1>
    <p class="page-lede"><code>${esc(id)}</code> is${known ? "" : " not"} in the catalog, but its rendered page
      did not arrive. The Markdown source is always available:
      <a href="${raw}" target="_blank" rel="noopener" data-ext>open it on GitHub</a>.</p>
    <p class="page-lede">Other ways in: <a href="#/" data-link>index</a> ·
      <button class="icon-btn" type="button" onclick="document.getElementById('sources-btn').click()">all sources</button> ·
      press <kbd>/</kbd> to search.</p></div>`;
}

function buildToc(headings) {
  const usable = headings.filter((h) => h.level === 2 || h.level === 3);
  if (usable.length < 5) { tocEl.hidden = true; return; }
  tocEl.hidden = false;
  tocEl.innerHTML = `<h2>On this page</h2><ol>${usable.map((h) =>
    `<li class="l${h.level}"><a href="#${h.id}" data-anchor="${h.id}">${esc(h.text)}</a></li>`).join("")}</ol>`;
  const links = new Map([...tocEl.querySelectorAll("a")].map((a) => [a.dataset.anchor, a]));
  const observer = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      links.forEach((a) => a.classList.remove("active"));
      links.get(e.target.id)?.classList.add("active");
    }
  }, { rootMargin: "-4.5rem 0px -70% 0px" });
  for (const id of links.keys()) {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  }
}

/* ---------- reference cards ---------- */
function refById(id) { return state.catalog.references.find((r) => r.id === id); }

function refCardHtml(r) {
  const rows = [];
  if (r.resource_type) rows.push(["Type", esc(r.resource_type)]);
  rows.push(["Register", esc(r.section_title)]);
  const urls = (r.urls && r.urls.length ? r.urls : (r.url ? [r.url] : []));
  if (urls.length) {
    rows.push(["Source", urls.map((u) => `<a href="${esc(u)}" data-ext>${esc(u.replace(/^https?:\/\//, "").slice(0, 64))}</a>`).join("<br>")]);
  } else if (r.domains?.length) {
    rows.push(["Source domain", r.domains.map((d) => `<a href="https://${esc(d)}" data-ext>${esc(d)}</a>`).join(", ")]);
  }
  if (r.doc) rows.push(["Mirrored here", `<a href="#/doc/${r.doc}" data-link>${esc(state.docs.get(r.doc)?.title || r.doc)}</a>`]);
  const cited = Object.entries(r.cited_in || {}).filter(([k]) => k !== "07-references");
  if (cited.length) rows.push(["Cited in", cited.map(([k, n]) => `<a href="#/doc/dossier/${esc(k)}" data-link>${esc(k.replace(/^\d+-/, ""))}</a> ×${n}`).join("<br>")]);
  return `<h3>Reference ${esc(r.id)}</h3>
    <p class="ref-cite">${esc(r.citation)}</p>
    ${r.note ? `<p class="ref-note">${esc(r.note)}</p>` : ""}
    <dl>${rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>
    <div class="more"><a href="#/ref/${r.id}" data-link>Full card</a>
      <button class="icon-btn" type="button" data-close-panel aria-label="Close">✕</button></div>`;
}

function showPanel(refId) {
  const r = refById(refId);
  if (!r) return;
  panel.innerHTML = `<button class="icon-btn close" data-close-panel aria-label="Close">✕</button>` + refCardHtml(r);
  panel.hidden = false;
}
function hidePanel() { panel.hidden = true; panel.innerHTML = ""; }

async function renderRefCard(id) {
  const r = refById(id);
  if (!r) return renderNotFound(id);
  setTitle(`${id} — ${r.citation}`);
  const related = r.doc ? state.docs.get(r.doc) : null;
  main.innerHTML = `<div class="main-inner">
    <p class="crumbs"><a href="#/" data-link>Home</a><span class="sep">›</span>Reference register<span class="sep">›</span>${esc(id)}</p>
    <h1 class="page-title">${esc(r.citation)}</h1>
    ${r.note ? `<p class="page-lede">${esc(r.note)}</p>` : ""}
    <div class="prose" style="max-width:60ch">${refCardHtml(r)}</div>
    ${related ? `<p class="pager" style="border:0"><a href="#/doc/${r.doc}" data-link class="next"><span class="dir">Read the mirrored text</span>${esc(related.title)}</a></p>` : ""}
  </div>`;
  window.scrollTo(0, 0);
}

/* ---------- search ---------- */
function ensureSearch() {
  if (!state.searchPromise) {
    state.searchPromise = fetch("./data/search.json", { cache: "no-cache" }).then((r) => r.json()).then((data) => {
      state.search = data.map((d) => ({ ...d, lx: d.x.toLowerCase(), lt: d.t.toLowerCase() }));
      return state.search;
    });
  }
  return state.searchPromise;
}

function termRe(term) {
  const esc = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`\\b${esc}`, "g");
}

function score(entry, terms) {
  const t = entry.lt, x = entry.lx;
  let s = 0;
  for (const term of terms) {
    const inTitle = t.includes(term);
    const n = (x.match(termRe(term)) || []).length;
    if (!inTitle && !n) return -1;
    if (t.startsWith(term)) s += 60;
    else if (inTitle) s += 30;
    s += Math.min(n, 40) * 2;
  }
  return s + Math.min(entry.x.length / 20000, 3);
}

function runSearch(q) {
  if (!state.search) return [];
  const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return [];
  return state.search
    .map((e) => ({ e, s: score(e, terms) }))
    .filter((r) => r.s > 0)
    .sort((a, b) => b.s - a.s)
    .slice(0, 60)
    .map((r) => r.e);
}

function snippet(text, terms, width = 150) {
  const low = text.toLowerCase();
  let at = -1;
  for (const t of terms) { const i = low.indexOf(t); if (i >= 0 && (at < 0 || i < at)) at = i; }
  if (at < 0) return "";
  const start = Math.max(0, at - 50);
  let s = text.slice(start, start + width).replace(/\s+/g, " ").trim();
  if (start > 0) s = "… " + s;
  return esc(s).replace(new RegExp(`(${terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`, "gi"), "<mark>$1</mark>");
}

async function onType() {
  const q = qInput.value.trim();
  if (!q) { results.hidden = true; state.results = []; state.sel = -1; return; }
  await ensureSearch();
  state.results = runSearch(q);
  state.sel = -1;
  if (location.hash.startsWith("#/search")) history.replaceState(null, "", "#/search/" + encodeURIComponent(q));
  results.innerHTML = state.results.length
    ? state.results.slice(0, 12).map((d, i) => `<a class="sr-item" role="option" href="#/doc/${d.id}" data-link data-i="${i}" aria-selected="false">
        <span class="sr-title">${esc(d.t)}</span><div class="sr-meta">${esc(collTitle(d.c))}</div>
        <div class="sr-snip">${snippet(d.x, q.toLowerCase().split(/\s+/))}</div></a>`).join("")
      + `<div class="sr-empty"><a href="#/search/${encodeURIComponent(q)}" data-link>All ${state.results.length} results →</a></div>`
    : `<div class="sr-empty">No match for “${esc(q)}”.</div>`;
  results.hidden = false;
}

function onSearchKey(e) {
  if (e.key === "Escape") { results.hidden = true; qInput.blur(); return; }
  if (e.key !== "ArrowDown" && e.key !== "ArrowUp" && e.key !== "Enter") return;
  const items = [...results.querySelectorAll(".sr-item")];
  if (!items.length) return;
  if (e.key === "Enter" && state.sel >= 0) { e.preventDefault(); openDoc(items[state.sel].dataset.id || state.results[state.sel].id); results.hidden = true; qInput.blur(); return; }
  e.preventDefault();
  state.sel = e.key === "ArrowDown" ? Math.min(state.sel + 1, items.length - 1) : Math.max(state.sel - 1, 0);
  items.forEach((el, i) => el.setAttribute("aria-selected", String(i === state.sel)));
  items[state.sel].scrollIntoView({ block: "nearest" });
}

async function renderSearchPage(q) {
  qInput.value = q;
  await ensureSearch();
  const hits = runSearch(q);
  setTitle(`Search: ${q}`);
  main.innerHTML = `<div class="main-inner">
    <h1 class="page-title">Search</h1>
    <p class="count">${hits.length} document${hits.length === 1 ? "" : "s"} matching “${esc(q)}”</p>
    <div id="hits">${hits.map((d) => `<div class="hit">
      <div class="meta">${esc(collTitle(d.c))}</div>
      <h3><a href="#/doc/${d.id}" data-link>${esc(d.t)}</a></h3>
      <div class="snip">${snippet(d.x, q.toLowerCase().split(/\s+/), 240)}</div></div>`).join("")}</div>
  </div>`;
  window.scrollTo(0, 0);
}

function openDoc(id) { location.hash = "#/doc/" + encodeURIComponent(id); }


/* ---------- hover previews for every internal source link ---------- */
const previewEl = $("#preview");
let previewTimer = 0, previewFor = null;

function docMeta(id) { return state.docs.get(id); }

function previewForLink(a) {
  const m = a.getAttribute("href").match(/^#\/doc\/(.+?)(?:#.*)?$/);
  if (!m) return null;
  return docMeta(decodeURIComponent(m[1]));
}

function showPreview(a) {
  const doc = previewForLink(a);
  if (!doc) return;
  const coll = collTitle(doc.collection);
  previewEl.innerHTML = `
    <div class="pv-meta">${esc(coll)}${doc.kind === "primary" ? " · primary source" : ""}</div>
    <div class="pv-title">${esc(doc.title)}</div>
    <div class="pv-excerpt">${esc((doc.excerpt || "").slice(0, 240))}${(doc.excerpt || "").length > 240 ? "…" : ""}</div>
    <div class="pv-foot">${doc.words ? doc.words.toLocaleString() + " words · " : ""}${esc(doc.source_name || "")}</div>`;
  previewEl.hidden = false;
  const r = a.getBoundingClientRect();
  const box = previewEl.getBoundingClientRect();
  let left = Math.min(Math.max(8, r.left), window.innerWidth - box.width - 8);
  let top = r.bottom + 8;
  if (top + box.height > window.innerHeight - 8) top = Math.max(8, r.top - box.height - 8);
  previewEl.style.left = left + "px";
  previewEl.style.top = top + "px";
  previewFor = a;
}

function hidePreview() {
  clearTimeout(previewTimer);
  previewEl.hidden = true;
  previewFor = null;
}

function initPreview() {
  const over = (e) => {
    const a = e.target.closest && e.target.closest('a[href^="#/doc/"]');
    if (!a || a === previewFor) return;
    if (document.querySelector("#sources")?.hidden === false) return;
    clearTimeout(previewTimer);
    previewTimer = setTimeout(() => showPreview(a), 220);
  };
  document.addEventListener("mouseover", over);
  document.addEventListener("focusin", over);
  document.addEventListener("mouseout", (e) => {
    if (e.target.closest && e.target.closest('a[href^="#/doc/"]')) hidePreview();
  });
  document.addEventListener("focusout", hidePreview);
  window.addEventListener("scroll", hidePreview, { passive: true });
  window.addEventListener("hashchange", hidePreview);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") hidePreview(); });
}

/* ---------- "all sources" dialog, reachable from every page ---------- */
const sourcesEl = $("#sources");
const sourcesList = $("#sources-list");
const sourcesFilter = $("#sources-filter");
let dlgItems = [], dlgSel = -1, dlgOpen = false;

function sourcesRender(filter = "") {
  const q = filter.trim().toLowerCase();
  const groups = new Map();
  for (const d of state.catalog.docs) {
    const hay = (d.title + " " + collTitle(d.collection) + " " + (d.source_name || "") + " " + (d.excerpt || "")).toLowerCase();
    if (q && !hay.includes(q)) continue;
    if (!groups.has(d.collection)) groups.set(d.collection, []);
    groups.get(d.collection).push(d);
  }
  dlgItems = [];
  let html = "";
  for (const [cid, docs] of groups) {
    html += `<div class="dlg-group">${esc(collTitle(cid))} <span class="muted">${docs.length}</span></div>`;
    for (const d of docs) {
      const i = dlgItems.push(d) - 1;
      html += `<a class="dlg-item" role="option" aria-selected="false" data-i="${i}" href="#/doc/${d.id}" data-link>
        <span class="t">${esc(d.title)}</span>
        <span class="m">${d.words ? d.words.toLocaleString() : ""}${d.kind === "primary" ? " · primary" : ""}</span></a>`;
    }
  }
  sourcesList.innerHTML = html || `<div class="sr-empty">Nothing matches “${esc(filter)}”.</div>`;
  $("#sources-foot").textContent = `${dlgItems.length} of ${state.catalog.docs.length} documents · ↑↓ to move · Enter to open · Esc to close`;
  dlgSel = -1;
}

function openSources() {
  dlgOpen = true;
  sourcesEl.hidden = false;
  sourcesFilter.value = "";
  sourcesRender("");
  sourcesFilter.focus();
  hidePreview();
}

function closeSources() {
  dlgOpen = false;
  sourcesEl.hidden = true;
  $("#sources-btn")?.focus();
}

function sourcesMove(delta) {
  const items = [...sourcesList.querySelectorAll(".dlg-item")];
  if (!items.length) return;
  dlgSel = Math.max(0, Math.min(items.length - 1, dlgSel + delta));
  items.forEach((el, i) => el.setAttribute("aria-selected", String(i === dlgSel)));
  items[dlgSel].scrollIntoView({ block: "nearest" });
}

function initSources() {
  $("#sources-btn").addEventListener("click", () => (dlgOpen ? closeSources() : openSources()));
  sourcesEl.addEventListener("click", (e) => {
    if (e.target === sourcesEl || e.target.closest("[data-close-sources]")) { closeSources(); return; }
    const item = e.target.closest(".dlg-item");
    if (item) { closeSources(); }
  });
  sourcesFilter.addEventListener("input", () => sourcesRender(sourcesFilter.value));
  sourcesFilter.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") { e.preventDefault(); sourcesMove(1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); sourcesMove(-1); }
    else if (e.key === "Enter") {
      e.preventDefault();
      const items = [...sourcesList.querySelectorAll(".dlg-item")];
      const target = dlgSel >= 0 ? items[dlgSel] : items[0];
      if (target) { closeSources(); location.hash = target.getAttribute("href"); }
    } else if (e.key === "Escape") { e.preventDefault(); closeSources(); }
  });
}

/* ---------- global keys & click handling ---------- */
function onGlobalKey(e) {
  const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
  if (e.key === "/" && !typing) { e.preventDefault(); qInput.focus(); qInput.select(); return; }
  if (e.key === "Escape") { hidePanel(); if (typing) { qInput.blur(); results.hidden = true; } return; }
  if (e.key === "s" && !typing) { e.preventDefault(); dlgOpen ? closeSources() : openSources(); return; }
  if (typing) return;
  if (e.key === "j" || e.key === "k") { window.scrollBy({ top: e.key === "j" ? 240 : -240, behavior: "smooth" }); return; }
  if (e.key === "n" || e.key === "p") {
    const m = location.hash.match(/^#\/doc\/(.+)$/);
    if (!m) return;
    const id = decodeURIComponent(m[1]);
    const doc = state.docCache.get(id);
    const target = e.key === "n" ? doc?.next : doc?.prev;
    if (target) openDoc(target);
  }
}

function onDocClick(e) {
  const a = e.target.closest("a");
  if (!a) return;
  if (a.dataset.ref) { e.preventDefault(); showPanel(a.dataset.ref); return; }
  if (a.dataset.anchor) { e.preventDefault(); location.hash = location.hash.split("#").slice(0, 2).join("#") + "#" + a.dataset.anchor; document.getElementById(a.dataset.anchor)?.scrollIntoView(); return; }
  if (a.matches("[data-ext]")) { a.target = "_blank"; a.rel = "noopener"; return; }
  // In-page hash routing: let the browser update, then route() runs.
}

boot().catch((err) => {
  main.innerHTML = `<div class="main-inner"><h1 class="page-title">Could not load the archive</h1>
    <p class="page-lede">${esc(err.message)}. The data files live next to this page under <code>data/</code>.</p></div>`;
});
})();
