ELIZABETH ZAB ART — WEBSITE
===========================

Live site:  https://elizabethzab.art
Hosting:    GitHub Pages (served from the `main` branch, root)
Domain:     elizabethzab.art (DNS at GoDaddy -> GitHub Pages; bound via the CNAME file)

This repository IS the website. It is a hand-built static site — plain HTML and
CSS, no build step, no framework, no package manager. What is committed to `main`
is exactly what is served. Edit a file, commit to `main`, and GitHub Pages
redeploys automatically within a minute or two.


PRODUCTION STRUCTURE (root = the live site)
-------------------------------------------
  index.html            Home page
  work/index.html       /work/      — gallery
  story/index.html      /story/     — about / story
  studio/index.html     /studio/    — visit the studio
  designers/index.html  /designers/ — for interior designers
  qa/index.html         /qa/        — Q&A

  assets/               Painting images + hero photo used by the pages
  favicon.ico, favicon.svg, favicon-32.png, favicon-192.png, apple-touch-icon.png
                        Favicons / app icons (referenced from every page's <head>)

  CNAME                 Custom domain binding for GitHub Pages (elizabethzab.art)
  robots.txt            Allows search crawling; points to the sitemap
  sitemap.xml           Lists all 6 pages for search engines
  llms.txt              Plain-text summary for AI / LLM crawlers
  .nojekyll             Tells GitHub Pages to serve files as-is (no Jekyll build)

  _brand/               SOURCE brand assets (master favicon/app-icon set, incl.
                        icon-512.png). Not required at runtime — the favicons the
                        site actually serves are the copies at the repo root — but
                        kept here as the canonical source files.

  README.txt            This file
  .gitignore            Ignores OS/editor junk


CLEAN URLs
----------
Each page lives in its own folder as index.html (e.g. work/index.html), so it is
reachable at a clean path like /work/ on any static host. Internal links use those
paths. There is no .html in the public URLs.


HOW TO EDIT / DEPLOY
--------------------
1. Edit the relevant HTML file (e.g. index.html or work/index.html).
2. Commit and push to `main`.
3. GitHub Pages rebuilds and redeploys automatically (~1-2 min).
4. Verify at https://elizabethzab.art (a hard refresh may be needed).


ANALYTICS
---------
Google Analytics 4 (gtag.js) is installed in the <head> of every page.
Measurement ID: G-F039HJSL10  (property "Elizabeth Zab Art").


NOTES
-----
- This site was selected from an earlier set of prototypes (A / B / C). Only the
  final approved design lives here now; the old prototype folders and the former
  Vercel build/deploy tooling have been removed.
- To take the site OUT of search results again, set robots.txt to "Disallow: /"
  and change the robots/googlebot <meta> tags back to "noindex, nofollow".


SEO REGRESSION CHECK
--------------------
Run `python3 scripts/seo-audit.py` (add `--live` after deploy) before and
after any change that touches URLs, canonicals, sitemap.xml, or navigation.
It verifies sitemap/page parity, canonical + og:url self-consistency, and
that no internal link points through a redirect.
