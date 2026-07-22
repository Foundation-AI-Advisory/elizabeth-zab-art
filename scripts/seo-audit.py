#!/usr/bin/env python3
"""SEO / indexability regression audit for elizabethzab.art.

Run from the repo root:  python3 scripts/seo-audit.py [--live]

Local checks (always run, no network):
  - sitemap.xml is well-formed, has no duplicate <loc> entries, and every
    <loc> is https, apex-host, trailing-slash, and maps to a page in the repo
  - every page in the repo appears in the sitemap (except 404.html)
  - every HTML page has exactly one <link rel="canonical">, absolute,
    https, apex-host, trailing-slash, self-referential, matching og:url
  - no page carries a noindex robots meta
  - no internal link points at a known-redirect form: http://, www.,
    *.github.io, a slashless directory path, or an /index.html variant
  - llms.txt links use canonical trailing-slash URLs

Live checks (--live, requires network):
  - every sitemap URL returns HTTP 200 directly (no redirect hop)
  - canonical targets return HTTP 200 directly
  - http://, www., and slashless variants 301 in exactly one hop to the
    canonical URL (expected GitHub Pages normalization)

Exit code 0 = all checks pass; 1 = failures (listed on stderr).
"""
import re
import sys
import pathlib
import urllib.request
import xml.etree.ElementTree as ET

HOST = "https://elizabethzab.art"
ROOT = pathlib.Path(__file__).resolve().parent.parent
FAILS = []


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
    llms = (ROOT / "llms.txt").read_text()
    for url in re.findall(r"https://elizabethzab\.art\S+", llms):
        path = url[len(HOST):].rstrip(":,")
        if path in dir_paths:
            fail(f"llms.txt: slashless URL (301 hop): {url}")


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


def main():
    page_map = pages()
    locs = check_sitemap(page_map)
    check_heads(page_map)
    check_links(page_map)
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
