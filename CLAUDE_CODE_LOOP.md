# LOOP — Elizabeth Zab Art: Multi-page Rebuild + SEO/AEO/GEO + Vercel Deploy

Foundation AI Advisory · Thomas Wagenberg
Handoff: Cowork → Claude Code
Status: ready to execute. Do not skip steps. Do not silently ad-lib design.

---

## Objective

Take the three single-page brand-locked prototypes in `~/Downloads/vercel_deploys/` and ship them as **three separate Vercel projects**, each restructured as a real multi-page site, each with a brand-color cookie banner, full SEO + AEO + GEO optimization, and a clean public URL for partner review.

Three sites. Six pages each. Eighteen HTML files total. Shared design system. Painting images served as static files under each project's `/assets/` directory (not base64-inlined, not Instagram CDN, not external) so each page stays small and crawlers can read it.

**Not client-ready. Partner-review-ready.**

## Inputs

Working directory: `~/Downloads/vercel_deploys/`

Current state — single-page prototypes:
```
vercel_deploys/
├── DEPLOY_ALL.command          (legacy single-page deploy script — ignore)
├── README.txt
├── elizabeth-zab-prototype-a/
│   ├── index.html              (3.5 MB single page, base64 paintings)
│   └── vercel.json
├── elizabeth-zab-prototype-b/
│   ├── index.html              (4.1 MB single page, base64 paintings)
│   └── vercel.json
└── elizabeth-zab-prototype-c/
    ├── index.html              (4.1 MB single page, base64 paintings)
    └── vercel.json
```

Painting JPEGs (raw, not base64) are available at:
```
~/Downloads/painting_1.jpg          Pink/green pour — Wicked-inspired — HERO
~/Downloads/painting_3.jpg          Rust, slate blue, cream pour
~/Downloads/painting_5.jpg          Blue/black/white wet pour on her work table — PROCESS
~/Downloads/painting_6.jpg          Purple, silver, yellow burst on dark ground
~/Downloads/painting_7.jpg          Black/white charcoal pour
~/Downloads/painting_8.jpg          Black/yellow/red bold vertical pour
~/Downloads/painting_2_backup.jpg   30×40 blank canvas in her studio — STUDIO interior
~/Downloads/painting_4.jpg          AI/Canva room visualization — STAGING (label as visualization)
```

If those files aren't where this loop expects, extract them from the existing single-page HTML files (they're base64-encoded inside `data:image/jpeg;base64,...` declarations and can be decoded with `python3` + `base64`).

## Role

You are Thomas's deployment engineer at Foundation AI Advisory. The brand-lock has already been QA'd in Cowork — palette, type, copy, image curation, image labels, structural QA. Your job is to **restructure, harden, and deploy** — not to redesign. If something looks wrong, report it; don't patch silently. If a brand decision is needed mid-flight, stop and ask Thomas, don't improvise.

## Locked Design System — Use These Exactly

**Palette (hex tokens, all CSS must use these and only these):**
```
--bg:         #F3F6F1   dominant background
--bg-wash:    #C7DED0   soft section wash
--ink:        #2D4434   strong headings, nav, dark sections
--brand:      #8BBBA6   primary brand blocks, CTAs, tags
--brand-deep: #60937B   hover, secondary brand
--accent:     #D4C56C   gold accent — sparingly
--accent-wash:#DDD995   pale yellow wash
--body:       #555555   body text
--rule:       #2E2A29   dividers, fine lines
--qr-black:   #1F1F1F
--white:      #FFFFFF
```

No terracotta, no peach, no brass, no pink-as-a-brand-color, no brown editorial palette, no unrelated gradients. If gradients are needed, use only palette colors with opacity.

**Typography — Quicksand only.** Weights 300, 400, 500. No Inter, Manrope, Plus Jakarta, Fraunces, Cormorant, or any serif/cursive face. No 600/700/800 bold-heavy weights. Load from Google Fonts.

**Voice.** Soft, calm, professional. Real, not corporate. Verbatim Elizabeth lines must remain intact (do not paraphrase):
- "Color, movement, organic flow."
- "I approach painting as a kind of dance."
- "The hairdryer is part of the process. It moves the paint, opens the cells, and gives each piece its breath."

**Image labels.** `painting_4.jpg` (the room mockup) MUST carry the overlay text `Visualization · room mockup, not a finished installation` on every page where it appears. Do not present it as a real installed home photo.

**Shipping copy in the Q&A — exact wording:**
> Shipping or pickup can be discussed when you inquire. Most local buyers (Akron, Cleveland, Medina, Hudson) pick up directly at the studio, which is the easiest option. International shipping is not offered at this time.

Do not paraphrase. Do not claim continental US shipping. Do not invent specific countries served.

## Step 1 — Extract Painting JPEGs (if not already present)

```bash
cd ~/Downloads/vercel_deploys
mkdir -p _assets_master

# Decode base64 paintings out of the existing single-page HTML
# Each painting appears once in elizabeth-zab-prototype-a/index.html as a data URI
# Use python3 with regex to extract them in order.
```

Write a small Python script that opens `elizabeth-zab-prototype-a/index.html`, finds all `data:image/jpeg;base64,...` matches preserving order, and writes them as `_assets_master/painting_1.jpg ... painting_8.jpg`. Then verify by file size:
```
painting_1.jpg ≈ 80 KB    (hero, pink/green)
painting_3.jpg ≈ 450 KB   (rust/blue)
painting_4.jpg ≈ 570 KB   (room viz)
painting_5.jpg ≈ 205 KB   (process wet pour)
painting_6.jpg ≈ 625 KB   (purple burst)
painting_7.jpg ≈ 235 KB   (B&W charcoal)
painting_8.jpg ≈ 240 KB   (black/yellow/red)
painting_2_backup.jpg ≈ 255 KB (30×40 blank canvas in studio)
```

If `~/Downloads/painting_*.jpg` already exist (Cowork left them there), skip extraction and copy them into `_assets_master/`.

## Step 2 — Restructure Each Prototype as Multi-Page

For each of `elizabeth-zab-prototype-a`, `-b`, `-c`, the final tree must be:

```
elizabeth-zab-prototype-<x>/
├── index.html       Home — hero, brief intro, 2–3 featured pieces, primary CTAs
├── work.html        Gallery — full set of paintings + captions
├── story.html       Story — hairdryer narrative, pull-quote, process imagery
├── studio.html      Visit the Studio — Salon Lofts, address, hours, directions, map link
├── designers.html   Designers & Realtors — staging lane with room visualization
├── qa.html          Q&A — full FAQ (also the AEO surface)
├── sitemap.xml
├── robots.txt
├── vercel.json
└── assets/
    ├── painting_1.jpg
    ├── painting_3.jpg
    ├── painting_4.jpg
    ├── painting_5.jpg
    ├── painting_6.jpg
    ├── painting_7.jpg
    ├── painting_8.jpg
    └── painting_2_backup.jpg
```

**Important:** the three prototypes share the same six pages and the same shared components (header, footer, cookie banner, schema.org blocks). The differentiation lives only in:

- **Prototype A — Brand Homepage.** Home page is the balanced brand statement: hero, brief story tease, 3 featured pieces, CTAs to Work and Studio. Standard sticky header.
- **Prototype B — Gallery First.** Home page leads with a larger hero and an immediate row of 4 featured pieces. Less text on the home page than A. Headline reads `Pour painter. Akron.` Subnav same.
- **Prototype C — Studio Visit / Local Conversion.** Sticky header has a brand-teal `Visit the studio` CTA button at the top right (always visible across all pages of C). Home page hero reads `Walk in. See the work. Take one home.` with `Plan a visit` + `Call (440) 477-1972` CTAs. Home page features the Studio block prominently above the featured pieces strip.

All six sub-pages (`work`, `story`, `studio`, `designers`, `qa`) carry identical content and visual treatment across A, B, and C — they're shared. Only the home page and the header treatment differ.

## Step 3 — Shared Components Every Page Must Include

### Sticky Header

- Wordmark left: `Elizabeth Zab · Art` (Quicksand 500, ink color; "· Art" in brand-deep)
- Nav right: `Work`, `Story`, `Designers`, `Q&A`, `Visit the studio` (for C, the last one is a brand-teal button; for A and B, it's a text link)
- On mobile (≤720px), hide Q&A and the phone number; keep Work/Story/Designers/Visit
- Sticky positioned with `backdrop-filter: blur(8px)` and bg `rgba(243, 246, 241, 0.96)`

### Boston Mills Artfest Strip (top of every page)

Background `--ink`, gold accent on `Boston Mills Artfest`, dot-separated:
```
Boston Mills Artfest · June 27–28 · Booth #88, North Tent · Cuyahoga Valley, OH
```

### Cookie Banner — brand-locked

**Spec — implement exactly. Inline JS, no external dependencies.**

Place this component on every page, at the very end of `<body>`. It shows only if the user hasn't already accepted/rejected (localStorage key: `ezart_cookie_v1`).

Styling:
- Position fixed, bottom: 24px, left: 24px, max-width 420px, full width below 640px
- Background `--bg-wash` (#C7DED0)
- 1px solid `--ink` border at 18% opacity
- 24px padding, border-radius 0 (sharp, gallery-card feel)
- box-shadow `0 8px 32px rgba(45, 68, 52, 0.16)`
- Headline: Quicksand 500, `--ink`, 14px, letter-spacing 0.02em — text: `A note on cookies`
- Body: Quicksand 400, `--ink`, 13px, line-height 1.6 — text: `This site uses a small set of cookies to keep the studio visit experience smooth. We don't sell your data and we don't run ad networks.`
- Two buttons inline, gap 8px:
  - `Decline` — ghost: transparent bg, `--ink` text, 1px solid `--ink` border, 10px 16px, 12px font
  - `Accept` — solid: `--ink` bg, `--white` text, 1px solid `--ink`, 10px 16px, 12px font; hover: `--brand-deep` bg
- Both buttons set `localStorage.setItem('ezart_cookie_v1', 'accept'|'decline')` and hide the banner
- No tracking pixel, no GTM, no GA — this is purely a UX banner for now. Do NOT add analytics. If/when Elizabeth wants analytics, that's a separate decision.

### Footer

Background `--ink`, three columns:
- Left: wordmark, tagline `Pour paintings, made in Akron, seen at the studio.`
- Middle: Studio header, address `3987 Medina Rd / Akron, OH 44333 / Inside Salon Lofts`
- Right: Reach header, `(440) 477-1972` and `@liz_zab47`
- Bottom legal line: `© Elizabeth Zab Art · Akron, OH`

## Step 4 — Page Content Spec (Every Sub-page, All Three Prototypes)

### `work.html` — Gallery

Page H1: `The work.`
Subhead: `A selection of recent pieces, made one breath at a time.`

Asymmetric gallery wall of all 7 real paintings (skip painting_4 — staging image). Use the same wrap/span pattern as A's existing gallery. Each piece has caption with `No. NN — <description>`.

Order:
1. `painting_6.jpg` — Purple, silver, and yellow on a dark ground (span 7)
2. `painting_3.jpg` — Rust, slate blue, and cream pour (span 5)
3. `painting_7.jpg` — Black-and-white charcoal pour on canvas (span 5)
4. `painting_8.jpg` — Black, yellow, and red — bold vertical pour (span 7)
5. `painting_1.jpg` — Pink, green, and silver pour (span 6)
6. `painting_5.jpg` — Blue, black, and white pour, still wet on the table (span 6)
7. `painting_2_backup.jpg` — A 30×40 canvas on the work table, in her studio (span 12 / full)

Closing CTA at bottom: `Come see them in person.` button → `studio.html`.

### `story.html` — Story / Hairdryer

Page H1: `A painting is a kind of dance.`

Two-column layout:
- Left column (text): Three paragraphs in Elizabeth's voice. First paragraph: who she is + Akron + Salon Lofts. Second: pull-quote with `--brand` left border, the hairdryer line. Third: signed, dated, finished by hand on the back of the canvas.
- Right column: `painting_5.jpg` (process shot, wet pour on table) at aspect-ratio 4/5

Below the two-column: a full-width band, `--bg-wash` background, centered:
`Want to see the process in person?` button → `studio.html`.

### `studio.html` — Visit the Studio

Page H1: `Visit the studio.`
Subhead: `Walk in from the Salon Lofts lobby. Anytime.`

Two-column layout:
- Left: `painting_2_backup.jpg` (real studio interior — 30×40 canvas on her work table with paint supplies) at aspect-ratio 4/5
- Right: studio card on `--white` background, 40px padding, 1px `--ink` border at 8%. Contents:
  - Eyebrow `Visit the studio`
  - H3 `Salon Lofts, Akron.`
  - 3 paragraphs about walk-ins and what to expect
  - Definition list:
    - Address: 3987 Medina Rd, Akron, OH 44333
    - Studio: Inside Salon Lofts · walk in from the main lobby
    - Hours: Walk-ins welcome during lobby hours. Appointments anytime.
    - Reach: (440) 477-1972 · @liz_zab47
  - `Get directions` button → `https://maps.google.com/?q=3987+Medina+Rd+Akron+OH+44333` (target=_blank, rel=noopener)

Below the two-column: Boston Mills Artfest call-out strip, brand-deep background, gold accent on the dates.

### `designers.html` — Designers & Realtors

Page H1: `Stage with originals.`
Section background: `--ink` (dark green) for the hero area of this page only.

Two-column layout:
- Left: `painting_4.jpg` (room visualization) at aspect-ratio 4/3 — **must** carry the overlay label `Visualization · room mockup, not a finished installation` (font Quicksand 500, 10px uppercase, white text on rgba(45,68,52,0.78) background, positioned bottom-left of the image)
- Right (white text on dark): eyebrow in gold `For designers & realtors`, H2 `Stage with originals.`, three-paragraph offering, numbered list of three things she does:
  01. Stage a listing with original work, with pickup or swap when the home sells
  02. Commission a palette to match a buyer's room or a client's space
  03. Signed originals as closing or client gifts
- Contact line: phone + IG

Closing band: `Tell me about your listing or your client.` mailto/call CTAs.

### `qa.html` — Q&A (AEO surface)

Page H1: `Good to know.`
Subhead: `Common questions about the work, the studio, and how to buy.`

Eight `<details>` accordion items. ALL eight required (in this order):
1. What is pour painting?
2. What is the hairdryer for?
3. Can I commission a custom piece?
4. Can I pick up at the studio?
5. Do you ship? — **use the exact safe shipping copy from above**
6. Do you offer Certificates of Authenticity?
7. Do you work with realtors or designers?
8. Where can I see the work in person?

Each `<details>` uses the same expand styling as the current single-page version (brand-teal `+`/`−` indicator).

**Crucially: this page must include the FAQPage schema.org JSON-LD block** (see Step 5 for the exact structure).

## Step 5 — SEO + AEO + GEO Implementation

### Per-Page `<head>` template

Every page must have:

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{PAGE_TITLE} — Elizabeth Zab Art · Akron, OH</title>
  <meta name="description" content="{PAGE_DESCRIPTION}">
  <meta name="author" content="Elizabeth Zabart">
  <link rel="canonical" href="{CANONICAL_URL}">

  <!-- Open Graph -->
  <meta property="og:type" content="{OG_TYPE}">
  <meta property="og:title" content="{OG_TITLE}">
  <meta property="og:description" content="{PAGE_DESCRIPTION}">
  <meta property="og:image" content="{CANONICAL_URL_BASE}/assets/painting_1.jpg">
  <meta property="og:url" content="{CANONICAL_URL}">
  <meta property="og:site_name" content="Elizabeth Zab Art">
  <meta property="og:locale" content="en_US">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{OG_TITLE}">
  <meta name="twitter:description" content="{PAGE_DESCRIPTION}">
  <meta name="twitter:image" content="{CANONICAL_URL_BASE}/assets/painting_1.jpg">

  <!-- GEO -->
  <meta name="geo.region" content="US-OH">
  <meta name="geo.placename" content="Akron, Ohio">
  <meta name="geo.position" content="41.0814;-81.5190">
  <meta name="ICBM" content="41.0814, -81.5190">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500&display=swap" rel="stylesheet">

  <style>{INLINE_CSS}</style>
</head>
```

Per-page title + description (use exactly):

| Page | Title segment | Description (≤155 chars) |
|---|---|---|
| index.html | `Pour paintings, made in Akron` | `Original acrylic pour paintings by Elizabeth Zabart. Studio inside Salon Lofts, Akron, OH. Walk in to see the work, or commission a custom palette.` |
| work.html | `The work` | `A selection of recent original pour paintings by Elizabeth Zab — color, movement, organic flow. Made in Akron, available at the studio.` |
| story.html | `A painting is a kind of dance` | `How a pour painting is made: poured palettes, warm air from a hairdryer, and a long slow dry. Elizabeth Zabart's process, from her Salon Lofts studio.` |
| studio.html | `Visit the studio in Akron` | `Walk in to Elizabeth Zab's studio at 3987 Medina Rd, Akron — inside Salon Lofts. See original pour paintings, pick up, or ask about a commission.` |
| designers.html | `Stage with originals` | `For interior designers and realtors: stage listings with original Elizabeth Zab pour paintings, commission palettes to match a buyer's room, or order signed client gifts.` |
| qa.html | `Common questions` | `Pour painting, the hairdryer technique, studio pickup, shipping, Certificates of Authenticity, working with realtors — Elizabeth Zab Art FAQ.` |

OG types: `website` for index, `article` for story, `website` for the rest.

### JSON-LD blocks

**On `index.html`** — combined `Person` + `LocalBusiness` + `WebSite`:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "@id": "{BASE}/#person",
      "name": "Elizabeth Zabart",
      "alternateName": "Liz Zab",
      "url": "{BASE}/",
      "image": "{BASE}/assets/painting_1.jpg",
      "jobTitle": "Pour Painter",
      "worksFor": { "@id": "{BASE}/#org" },
      "sameAs": [
        "https://www.instagram.com/liz_zab47/"
      ]
    },
    {
      "@type": "LocalBusiness",
      "@id": "{BASE}/#org",
      "name": "Elizabeth Zab Art",
      "url": "{BASE}/",
      "telephone": "+1-440-477-1972",
      "image": "{BASE}/assets/painting_2_backup.jpg",
      "founder": { "@id": "{BASE}/#person" },
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "3987 Medina Rd",
        "addressLocality": "Akron",
        "addressRegion": "OH",
        "postalCode": "44333",
        "addressCountry": "US"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": 41.0814,
        "longitude": -81.5190
      },
      "areaServed": ["Akron", "Cleveland", "Medina", "Hudson", "Northeast Ohio"],
      "priceRange": "$$"
    },
    {
      "@type": "WebSite",
      "@id": "{BASE}/#website",
      "url": "{BASE}/",
      "name": "Elizabeth Zab Art",
      "publisher": { "@id": "{BASE}/#org" },
      "inLanguage": "en-US"
    }
  ]
}
```

**On `qa.html`** — `FAQPage` with all 8 Q/A pairs:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "What is pour painting?", "acceptedAnswer": {"@type": "Answer", "text": "Pour painting is an acrylic technique..."}},
    {"@type": "Question", "name": "What is the hairdryer for?", "acceptedAnswer": {"@type": "Answer", "text": "Warm air opens cells in the paint..."}},
    {"@type": "Question", "name": "Can I commission a custom piece?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. I take commissions for specific palettes..."}},
    {"@type": "Question", "name": "Can I pick up at the studio?", "acceptedAnswer": {"@type": "Answer", "text": "Yes — local pickup at the Salon Lofts studio..."}},
    {"@type": "Question", "name": "Do you ship?", "acceptedAnswer": {"@type": "Answer", "text": "Shipping or pickup can be discussed when you inquire..."}},
    {"@type": "Question", "name": "Do you offer Certificates of Authenticity?", "acceptedAnswer": {"@type": "Answer", "text": "Every original ships with a signed Certificate of Authenticity..."}},
    {"@type": "Question", "name": "Do you work with realtors or designers?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. I work with realtors and interior designers..."}},
    {"@type": "Question", "name": "Where can I see the work in person?", "acceptedAnswer": {"@type": "Answer", "text": "At my studio inside Salon Lofts, 3987 Medina Rd, Akron, OH..."}}
  ]
}
```

Fill in answer text from the existing single-page Q&A copy in `elizabeth-zab-prototype-a/index.html`. Match exactly. Don't paraphrase.

**On `studio.html`** — `Place` schema with address + geo + opening hours line: `Mo-Su 09:00-18:00` as a working default; flag this for confirmation with Elizabeth.

**On `designers.html`** — `Service` schema with `serviceType: "Art Staging and Commissioning"`, providing organization linked to `#org`.

### `sitemap.xml` (per project)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE}/</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>
  <url><loc>{BASE}/work</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>
  <url><loc>{BASE}/story</loc><changefreq>yearly</changefreq><priority>0.7</priority></url>
  <url><loc>{BASE}/studio</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>
  <url><loc>{BASE}/designers</loc><changefreq>yearly</changefreq><priority>0.6</priority></url>
  <url><loc>{BASE}/qa</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
</urlset>
```

### `robots.txt` (per project)

```
User-agent: *
Allow: /
Sitemap: {BASE}/sitemap.xml
```

### AEO (Answer Engine Optimization) priorities

AEO is the part where AI assistants (ChatGPT, Claude, Gemini, Perplexity) directly answer user questions. To rank, the Q&A page must:
- Use natural-question H2s ("What is pour painting?" not "Pour Painting Info")
- Have a clean FAQPage JSON-LD block (above)
- Be linked from the home page footer AND from the global nav
- Have plain-English, complete-sentence answers (no marketing fluff, no "as a special offer")

This is already 90% done by following the spec above. Don't ad-lib.

### GEO (Generative Engine Optimization) priorities

GEO is the broader "make this site discoverable by generative engines." Beyond AEO:
- Local SEO via the `LocalBusiness` schema (above)
- Geographic meta tags (above)
- Plain text mentions of `Akron, OH`, `Salon Lofts`, `3987 Medina Rd` on every page (the footer handles this — verify)
- Plain text mention of named entities the site cares about: `Boston Mills Artfest`, `Tremont Arts Festival`, `Medina Art in the Park`, `pour painting`, `acrylic pour`, `Certificate of Authenticity`. Sprinkle naturally in copy where they already make sense — do not keyword-stuff.

## Step 6 — `vercel.json` per project

```json
{
  "name": "elizabeth-zab-prototype-<x>",
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/(.*).html",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" }
      ]
    }
  ]
}
```

`cleanUrls: true` lets `/work` serve `/work.html` (no `.html` extension in URL).

## Step 7 — Local Verification Before Deploy

Each project, before pushing to Vercel:

```bash
cd elizabeth-zab-prototype-a
python3 -m http.server 8000 &
SERVER_PID=$!
sleep 1
for page in "" /work /story /studio /designers /qa; do
  CODE=$(curl -sS -o /dev/null -w "%{http_code}" "http://127.0.0.1:8000$page" || echo "fail")
  echo "$page -> $CODE"
done
# Verify every page has the cookie banner element
for page in index work story studio designers qa; do
  COUNT=$(grep -c 'ezart_cookie_v1' $page.html)
  echo "cookie on $page: $COUNT"
done
# Verify FAQPage JSON-LD on qa.html
grep -q '"@type": "FAQPage"' qa.html && echo "AEO FAQPage: ok" || echo "AEO FAQPage: MISSING"
# Verify no IG CDN refs
grep -E 'cdninstagram|fbcdn' *.html && echo "IG CDN LEAK" || echo "no IG refs: ok"
# Verify shipping safe copy on qa.html
grep -q "Shipping or pickup can be discussed" qa.html && echo "shipping copy ok" || echo "shipping copy WRONG"
kill $SERVER_PID
```

Expected: every page returns 200; cookie present on all 6; FAQPage present on qa.html; no IG CDN references; shipping safe-copy present.

Repeat for B and C.

## Step 8 — Vercel Deploy

```bash
# One-time auth check
if ! npx -y vercel whoami > /dev/null 2>&1; then
  npx -y vercel login
fi

for slug in elizabeth-zab-prototype-a elizabeth-zab-prototype-b elizabeth-zab-prototype-c; do
  cd ~/Downloads/vercel_deploys/$slug
  npx -y vercel deploy --prod --yes --name=$slug
  cd -
done
```

Capture the production URL printed at the end of each deploy. Save to `~/Downloads/vercel_deploys/_DEPLOY_URLS.txt`.

## Step 9 — Live URL Verification

For each of the three URLs and each of the six paths (`/`, `/work`, `/story`, `/studio`, `/designers`, `/qa`):

```bash
# 1. HTTP 200
curl -sS -o /dev/null -w "%{http_code}\n" $URL$PATH

# 2. Correct title for the page+prototype combo
curl -sS $URL$PATH | grep -o '<title>[^<]*</title>'

# 3. Cookie banner element present
curl -sS $URL$PATH | grep -c "ezart_cookie_v1"

# 4. No IG CDN
curl -sS $URL$PATH | grep -c "cdninstagram\|fbcdn"

# 5. Painting served as /assets/*, not data: URI (page should be small)
curl -sSI $URL$PATH | grep -i content-length
# Each HTML page should now be <100 KB, not 4 MB.

# 6. Painting JPEGs reachable
curl -sS -o /dev/null -w "%{http_code}" $URL/assets/painting_1.jpg
# Expect 200 on every painting referenced from any page.
```

For `qa.html` only, also verify:
```bash
curl -sS $URL/qa | grep '"@type": "FAQPage"'
```

For `studio.html` only:
```bash
curl -sS $URL/studio | grep -E '"@type": "(LocalBusiness|Place)"'
```

For sitemap and robots:
```bash
curl -sS $URL/sitemap.xml | head -10
curl -sS $URL/robots.txt
```

## Step 10 — Self-Check / Stopping Rule

Stop when, for all three projects:

- All 6 pages return 200 on the live URL
- All pages serve the cookie banner element
- qa.html contains a valid FAQPage JSON-LD block
- studio.html contains a LocalBusiness or Place schema block
- index.html contains the combined Person + LocalBusiness + WebSite schema
- No `cdninstagram` or `fbcdn` strings appear in any deployed HTML
- Every painting at `/assets/painting_*.jpg` returns 200
- Each page is <200 KB (paintings externalized successfully)
- `Shipping or pickup can be discussed when you inquire` appears on qa.html
- `Visualization · room mockup, not a finished installation` overlay text appears on designers.html
- `sitemap.xml` and `robots.txt` are reachable on each project
- The three home pages are clearly different per their direction (A balanced, B gallery-led, C studio-CTA-led with sticky brand-teal button)

If any check fails twice in a row on the same project, stop and report — don't loop further.

## Final Output Format

Print to stdout in this exact format, and also write to `~/Downloads/vercel_deploys/_DEPLOY_URLS.txt`:

```
ELIZABETH ZAB ART — VERCEL DEPLOY · PARTNER REVIEW READY

Prototype A — Brand Homepage             | <url>
Prototype B — Gallery First              | <url>
Prototype C — Studio Visit / Local       | <url>

All three sites have six pages: /, /work, /story, /studio, /designers, /qa

Recommend partners open first: Prototype A
  (most representative of brand; cleanest balance of work + studio + story + commission)

Verification:
  ✓ All 18 page paths returned 200 on the live URLs
  ✓ Cookie banner present on every page (brand colors, localStorage-backed)
  ✓ FAQPage schema live on /qa for AEO
  ✓ LocalBusiness + Person + WebSite schema live on / for GEO
  ✓ sitemap.xml and robots.txt reachable on all three
  ✓ All 8 painting JPEGs reachable under /assets/ on all three
  ✓ No Instagram CDN dependencies anywhere
  ✓ Shipping safe copy ("Shipping or pickup can be discussed...") live on /qa
  ✓ Visualization label live on /designers (painting_4 correctly labeled)
  ✓ Average page weight: <100 KB per HTML (paintings externalized successfully)

Remaining risks:
  - Studio opening hours in the schema are a working default (Mo-Su 09:00-18:00).
    Confirm with Elizabeth before client launch.
  - painting_4 (room visualization) is still AI/Canva-style. Label is in place.
    Replace with a real staged listing photo if/when one becomes available.
  - Quicksand is a 70%-confidence match to the business card. Confirm with the
    actual card PDF before client launch.
  - Cookie banner is UX-only (no analytics tied in). If GA4/Plausible is
    desired later, that's a separate request from Elizabeth.

Status: partner-review-ready. NOT marked client-ready.
```

## What NOT To Do

- Do not introduce off-brand colors. The palette is locked.
- Do not switch fonts. Quicksand only.
- Do not add `Inter`, `Manrope`, `Plus Jakarta`, `Fraunces`, `Cormorant`, or any other family.
- Do not add Google Analytics, GTM, Hotjar, or any tracking script. The cookie banner is UX-only.
- Do not paraphrase Elizabeth's verbatim lines or the safe shipping copy.
- Do not put painting_4 anywhere without the visualization overlay label.
- Do not deploy to a preview URL. Use `--prod`.
- Do not let Vercel auto-generate project slugs. Use `--name=<slug>`.
- Do not enable Vercel Password Protection / SSO — partner review needs public URLs.
- Do not delete `~/Downloads/vercel_deploys/` after deploy; Thomas may need to redeploy.
- Do not mark as client-ready. Partner-review-ready only.

---

Built by Thomas Wagenberg · Foundation AI Advisory · June 22, 2026
After URLs print, paste them back into Cowork for visual QA at desktop + mobile widths on all 6 page paths.
