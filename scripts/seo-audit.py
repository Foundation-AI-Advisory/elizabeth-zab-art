#!/usr/bin/env python3
"""SEO / indexability regression audit for elizabethzab.art.

Run from the repo root:  python3 scripts/seo-audit.py [--live | --selftest]

Local checks (always run, no network):
  - sitemap.xml is well-formed, has no duplicate <loc> entries, and every
    <loc> is https, apex-host, trailing-slash, and maps to a page in the repo
  - every page in the repo appears in the sitemap (except 404.html)
  - every HTML page has exactly one <link rel="canonical">, absolute,
    https, apex-host, trailing-slash, self-referential, matching og:url
  - no page carries a noindex robots meta
  - no internal link points at a known-redirect form: http://, www.,
    *.github.io, a slashless directory path, or an /index.html variant
  - no internal link points at the deleted /medina-art-in-the-park/ route
  - the deleted /medina-art-in-the-park/ route never appears in sitemap.xml,
    any JSON-LD block, or llms.txt
  - no expired-event wording remains (the "Art in the Park" / "Artfest" /
    "Booth #" / "Medina County" show copy). The legitimate studio address
    "3987 Medina Rd" and the areaServed / service-area "Medina" are EXEMPT.
  - every JSON-LD (application/ld+json) block is valid JSON
  - every referenced local image/asset exists on disk (pages + sitemap images)
  - every intended page is linked from at least one other page (no orphans)
  - every intended page has a <title> and exactly one <h1>
  - llms.txt links use canonical trailing-slash URLs

Live checks (--live, requires network):
  - every sitemap URL returns HTTP 200 directly (no redirect hop)
  - canonical targets return HTTP 200 directly (canonicals == sitemap URLs)
  - http://, www., and slashless variants 301 in exactly one hop to the
    canonical URL (expected GitHub Pages normalization); a redirect chain or
    loop fails because the single hop must land on the canonical

Self-test (--selftest, no network): copies the repo to a temp dir, injects
  each defect above ONE AT A TIME into a fresh copy, and asserts the audit
  exits non-zero and names the specific defect; also asserts a clean copy
  exits zero. The real repo files are never modified.

Exit code 0 = all checks pass; 1 = failures (listed on stderr).
"""
import re
import sys
import json
import pathlib
import urllib.request
import xml.etree.ElementTree as ET

HOST = "https://elizabethzab.art"
ROOT = pathlib.Path(__file__).resolve().parent.parent
FAILS = []

# The event page and its content were removed once the show was over; the
# route must never resurface anywhere the crawlers or LLMs read.
DELETED_ROUTE = "/medina-art-in-the-park/"

# Distinctive expired-event wording. Deliberately NOT the bare word "Medina":
# "3987 Medina Rd" (studio address) and areaServed / service-area "Medina"
# are legitimate and must stay, so only unambiguous show copy is matched.
EVENT_TERMS = [
    r"art in the park",
    r"artfest",
    r"medina county",
    r"booth\s*#?\s*\d+",
    r"view event details",
]

# Extensions that identify a reference as a file that must exist on disk
# (page routes such as "/work/" have no extension and are checked elsewhere).
ASSET_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico", ".gif",
              ".css", ".js", ".woff", ".woff2", ".avif")


def fail(msg):
    FAILS.append(msg)


def pages():
    """Repo HTML pages -> canonical path ('/', '/work/', ...)."""
    out = {}
    for f in sorted(ROOT.rglob("*.html")):
        rel = f.relative_to(ROOT)
        if rel.parts[0] in (".git", "scripts", "_brand", "assets"):
            continue
        if rel.name == "404.html":
            continue
        if rel.name == "index.html":
            parent = "/".join(rel.parts[:-1])
            out["/" + (parent + "/" if parent else "")] = f
        else:
            out["/" + str(rel)] = f
    return out


def check_sitemap(page_map):
    tree = ET.parse(ROOT / "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [e.text.strip() for e in tree.findall(".//s:url/s:loc", ns)]
    if len(locs) != len(set(locs)):
        fail("sitemap: duplicate <loc> entries")
    for loc in locs:
        if not loc.startswith(HOST + "/"):
            fail(f"sitemap: non-canonical host/protocol: {loc}")
        path = loc[len(HOST):]
        if not path.endswith("/"):
            fail(f"sitemap: missing trailing slash: {loc}")
        if path not in page_map:
            fail(f"sitemap: no repo page for {loc}")
    for path in page_map:
        if HOST + path not in locs:
            fail(f"sitemap: repo page missing from sitemap: {path}")
    return locs


def check_heads(page_map):
    for path, f in page_map.items():
        s = f.read_text()
        canons = re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', s)
        if len(canons) != 1:
            fail(f"{f}: expected exactly 1 canonical, found {len(canons)}")
            continue
        want = HOST + path
        if canons[0] != want:
            fail(f"{f}: canonical is {canons[0]}, expected {want}")
        og = re.findall(r'<meta\s+property="og:url"\s+content="([^"]+)"', s)
        if og and og[0] != want:
            fail(f"{f}: og:url {og[0]} conflicts with canonical {want}")
        if re.search(r'<meta\s+name="robots"[^>]*noindex', s, re.I):
            fail(f"{f}: unexpected noindex directive")


def check_links(page_map):
    dir_paths = {p.rstrip("/") for p in page_map if p != "/"}
    files = list(page_map.values()) + [ROOT / "404.html"]
    for f in files:
        for href in re.findall(r'href="([^"]+)"', f.read_text()):
            if re.match(r"https?://(www\.)?elizabethzab\.art", href):
                if href.startswith("http://") or "//www." in href:
                    fail(f"{f}: link via redirect host/protocol: {href}")
                href = re.sub(r"https?://(www\.)?elizabethzab\.art", "", href) or "/"
            if "github.io" in href:
                fail(f"{f}: link to github.io: {href}")
            if href in dir_paths:
                fail(f"{f}: slashless internal link (301 hop): {href}")
            if href.endswith("/index.html"):
                fail(f"{f}: link to index.html duplicate variant: {href}")
            if href.split("#")[0].split("?")[0].rstrip("/") == DELETED_ROUTE.rstrip("/"):
                fail(f"{f}: internal link to deleted route: {href}")
    llms = (ROOT / "llms.txt").read_text()
    for url in re.findall(r"https://elizabethzab\.art\S+", llms):
        path = url[len(HOST):].rstrip(":,")
        if path in dir_paths:
            fail(f"llms.txt: slashless URL (301 hop): {url}")


JSONLD_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S | re.I)


def _all_page_items(page_map):
    """Intended pages plus 404.html, as (label, Path) pairs."""
    return list(page_map.items()) + [("/404.html", ROOT / "404.html")]


def check_deleted_route(page_map):
    """The removed event route must not appear in sitemap, JSON-LD, or llms."""
    token = DELETED_ROUTE.strip("/")
    if token in (ROOT / "sitemap.xml").read_text():
        fail(f"sitemap.xml: references deleted route {DELETED_ROUTE}")
    if token in (ROOT / "llms.txt").read_text():
        fail(f"llms.txt: references deleted route {DELETED_ROUTE}")
    for _, f in _all_page_items(page_map):
        for block in JSONLD_RE.findall(f.read_text()):
            if token in block:
                fail(f"{f}: JSON-LD references deleted route {DELETED_ROUTE}")


def check_event_wording(page_map):
    """No expired-event copy anywhere crawlers read (address/areaServed exempt)."""
    scan = _all_page_items(page_map) + [("llms.txt", ROOT / "llms.txt"),
                                        ("sitemap.xml", ROOT / "sitemap.xml")]
    for label, f in scan:
        s = f.read_text()
        for term in EVENT_TERMS:
            m = re.search(term, s, re.I)
            if m:
                fail(f"{f if isinstance(f, pathlib.Path) else label}: "
                     f"expired-event wording /{term}/ -> {m.group(0)!r}")


def check_jsonld(page_map):
    """Every application/ld+json block must be valid JSON."""
    for _, f in _all_page_items(page_map):
        for block in JSONLD_RE.findall(f.read_text()):
            try:
                json.loads(block.strip())
            except ValueError as e:
                fail(f"{f}: invalid JSON-LD: {e}")


def _asset_refs(text):
    """Referenced paths from href/src/content attrs and CSS url(...)."""
    refs = set(re.findall(r'(?:href|src|content)="([^"]+)"', text))
    refs.update(m[1] for m in re.findall(r"url\((['\"]?)([^)]+)\1\)", text))
    return refs


def check_assets(page_map):
    """Every referenced local image/asset file must exist on disk."""
    for f in list(page_map.values()) + [ROOT / "404.html"]:
        for ref in _asset_refs(f.read_text()):
            ref = ref.strip()
            if ref.startswith(HOST):
                ref = ref[len(HOST):]
            if not ref.startswith("/") or ref.startswith("//"):
                continue  # data:, #frag, mailto:, external host, protocol-rel
            ref = ref.split("?")[0].split("#")[0]
            if not ref.lower().endswith(ASSET_EXTS):
                continue  # page route, not a file
            if not (ROOT / ref.lstrip("/")).is_file():
                fail(f"{f}: referenced asset missing on disk: {ref}")
    tree = ET.parse(ROOT / "sitemap.xml")
    ns = {"image": "http://www.google.com/schemas/sitemap-image/1.1"}
    for e in tree.findall(".//image:loc", ns):
        loc = e.text.strip()
        if loc.startswith(HOST):
            p = loc[len(HOST):]
            if not (ROOT / p.lstrip("/")).is_file():
                fail(f"sitemap image missing on disk: {loc}")


def _norm_href(href):
    """Reduce an href to a canonical page path, or '' if not a local page."""
    href = href.strip()
    href = re.sub(r"^https?://(www\.)?elizabethzab\.art", "", href)
    href = href.split("#")[0].split("?")[0]
    if href.endswith("/index.html"):
        href = href[: -len("index.html")]
    if href == "/index.html":
        href = "/"
    if href == "":
        href = "/"
    return href


def check_orphans(page_map):
    """Every intended page must be linked from at least one *other* page."""
    file_to_path = {f: p for p, f in page_map.items()}
    inbound = {p: set() for p in page_map}
    for f in list(page_map.values()) + [ROOT / "404.html"]:
        src = file_to_path.get(f)  # None for 404.html
        for href in re.findall(r'href="([^"]+)"', f.read_text()):
            t = _norm_href(href)
            if t in inbound and t != src:
                inbound[t].add(f)
    for p, srcs in sorted(inbound.items()):
        if not srcs:
            fail(f"orphan page: {p} is not linked from any other page")


def check_title_h1(page_map):
    """Every intended page needs a <title> and exactly one <h1>."""
    for path, f in page_map.items():
        s = f.read_text()
        if not re.search(r"<title[\s>]", s, re.I):
            fail(f"{f}: no <title>")
        h1 = re.findall(r"<h1[\s>]", s, re.I)
        if len(h1) != 1:
            fail(f"{f}: expected exactly 1 <h1>, found {len(h1)}")


def head_req(url):
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "seo-audit/1.0"})

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(req, timeout=20)
        return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")


def check_live(locs):
    for loc in locs:
        code, _ = head_req(loc)
        if code != 200:
            fail(f"live: {loc} returned {code}, expected direct 200")
        path = loc[len(HOST):]
        for variant in (loc.replace("https://", "http://"),
                        loc.replace("://", "://www."),
                        HOST + path.rstrip("/") if path != "/" else None):
            if not variant or variant == loc:
                continue
            code, dest = head_req(variant)
            if code not in (301, 308):
                fail(f"live: {variant} returned {code}, expected 301")
            elif dest not in (loc, loc.replace("https://", "http://")):
                if not (dest == HOST + "/" and path == "/"):
                    if dest != loc:
                        fail(f"live: {variant} redirects to {dest}, expected {loc}")


def _first_page(root, name="work/index.html"):
    return root / name


def _inject_before(path, needle, snippet):
    t = path.read_text()
    if needle not in t:
        raise AssertionError(f"self-test setup: {needle!r} not in {path}")
    path.write_text(t.replace(needle, snippet + needle, 1))


# Mutation registry for --selftest. Each entry: (name, mutate(root), signature).
# mutate() corrupts ONE thing in a fresh clean copy; signature is a substring
# the audit's failure output must contain to prove the *specific* defect was
# caught (not merely that something else failed).
def _mutations():
    def m_llms_slashless(root):
        p = root / "llms.txt"
        p.write_text(p.read_text().replace(
            "https://elizabethzab.art/work/", "https://elizabethzab.art/work", 1))

    def m_dup_sitemap(root):
        p = root / "sitemap.xml"
        p.write_text(p.read_text().replace(
            "</urlset>",
            "  <url><loc>https://elizabethzab.art/qa/</loc></url>\n</urlset>", 1))

    def m_medina_sitemap(root):
        p = root / "sitemap.xml"
        p.write_text(p.read_text().replace(
            "</urlset>",
            "  <url><loc>https://elizabethzab.art/medina-art-in-the-park/"
            "</loc></url>\n</urlset>", 1))

    def m_medina_llms(root):
        p = root / "llms.txt"
        p.write_text(p.read_text().rstrip() +
                     "\n- https://elizabethzab.art/medina-art-in-the-park/: page\n")

    def m_medina_jsonld(root):
        _inject_before(_first_page(root), "</body>",
                       '<script type="application/ld+json">'
                       '{"@context":"https://schema.org","@type":"WebPage",'
                       '"url":"https://elizabethzab.art/medina-art-in-the-park/"}'
                       '</script>')

    def m_medina_link(root):
        _inject_before(_first_page(root), "</body>",
                       '<a href="/medina-art-in-the-park/">Show</a>')

    def m_event_phrase(root):
        _inject_before(_first_page(root), "</body>",
                       "<p>See Liz at Medina County Art in the Park, "
                       "Booth #79.</p>")

    def m_missing_asset(root):
        _inject_before(_first_page(root), "</body>",
                       '<img src="/assets/__does_not_exist__.jpg" alt="x">')

    def m_second_canonical(root):
        _inject_before(_first_page(root), "</head>",
                       '<link rel="canonical" '
                       'href="https://elizabethzab.art/work/">')

    def m_noindex(root):
        _inject_before(_first_page(root), "</head>",
                       '<meta name="robots" content="noindex, nofollow">')

    def m_remove_h1(root):
        p = _first_page(root)
        t = p.read_text().replace("<h1", "<h2", 1)
        t = re.sub(r"</h1>", "</h2>", t, count=1)
        p.write_text(t)

    def m_remove_title(root):
        p = _first_page(root)
        p.write_text(re.sub(r"<title>.*?</title>", "", p.read_text(),
                            count=1, flags=re.S))

    def m_invalid_jsonld(root):
        _inject_before(_first_page(root), "</body>",
                       '<script type="application/ld+json">'
                       '{"@context":"https://schema.org",}</script>')

    def m_orphan(root):
        for f in list(pages_of(root)) + [root / "404.html"]:
            f.write_text(f.read_text().replace('href="/qa/"', 'href="/studio/"'))

    return [
        ("slashless llms URL",            m_llms_slashless,  "slashless"),
        ("duplicate sitemap <loc>",       m_dup_sitemap,     "duplicate <loc>"),
        ("deleted route in sitemap",      m_medina_sitemap,
         "sitemap.xml: references deleted route"),
        ("deleted route in llms.txt",     m_medina_llms,
         "llms.txt: references deleted route"),
        ("deleted route in JSON-LD",      m_medina_jsonld,
         "JSON-LD references deleted route"),
        ("internal link to deleted route", m_medina_link,
         "internal link to deleted route"),
        ("expired-event wording",         m_event_phrase,
         "expired-event wording"),
        ("missing referenced asset",      m_missing_asset,
         "asset missing on disk"),
        ("second canonical",              m_second_canonical,
         "expected exactly 1 canonical"),
        ("noindex meta",                  m_noindex,         "noindex"),
        ("removed <h1>",                  m_remove_h1,
         "expected exactly 1 <h1>"),
        ("removed <title>",               m_remove_title,    "no <title>"),
        ("invalid JSON-LD",               m_invalid_jsonld,  "invalid JSON-LD"),
        ("orphaned page",                 m_orphan,          "orphan page"),
    ]


def pages_of(root):
    """HTML pages under a copied repo root (mirrors pages(), any root)."""
    root = pathlib.Path(root)
    out = []
    for f in sorted(root.rglob("*.html")):
        rel = f.relative_to(root)
        if rel.parts[0] in (".git", "scripts", "_brand", "assets"):
            continue
        if rel.name == "404.html":
            continue
        out.append(f)
    return out


def selftest():
    import shutil
    import tempfile
    import subprocess

    def run_audit(root):
        r = subprocess.run(
            [sys.executable, str(pathlib.Path(root) / "scripts" / "seo-audit.py")],
            capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def fresh(tmp, tag):
        dst = pathlib.Path(tmp) / f"copy_{tag}"
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git"))
        return dst

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        code, out = run_audit(fresh(tmp, "clean"))
        clean_ok = (code == 0)
        results.append(("(clean copy exits 0)", clean_ok, code, "exit 0"))
        for i, (name, mutate, sig) in enumerate(_mutations()):
            c = fresh(tmp, i)
            mutate(c)
            code, out = run_audit(c)
            caught = code != 0 and sig.lower() in out.lower()
            results.append((name, caught, code, sig))

    ok = all(r[1] for r in results)
    print("SELF-TEST: mutation audit (clean baseline + one defect per copy)")
    for name, passed, code, sig in results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}  "
              f"(exit={code}, expects {sig!r})")
    n_def = len(results) - 1
    caught = sum(1 for r in results[1:] if r[1])
    print(f"SELF-TEST {'PASS' if ok else 'FAIL'} — clean baseline "
          f"{'ok' if results[0][1] else 'BROKEN'}, "
          f"{caught}/{n_def} injected defects caught")
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    page_map = pages()
    locs = check_sitemap(page_map)
    check_heads(page_map)
    check_links(page_map)
    check_deleted_route(page_map)
    check_event_wording(page_map)
    check_jsonld(page_map)
    check_assets(page_map)
    check_orphans(page_map)
    check_title_h1(page_map)
    if "--live" in sys.argv:
        check_live(locs)
    if FAILS:
        print(f"FAIL — {len(FAILS)} issue(s):", file=sys.stderr)
        for m in FAILS:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)
    n = "local+live" if "--live" in sys.argv else "local"
    print(f"PASS — {len(page_map)} pages, {len(locs)} sitemap URLs, {n} checks clean")


if __name__ == "__main__":
    main()
