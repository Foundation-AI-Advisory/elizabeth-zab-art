#!/usr/bin/env python3
"""
Elizabeth Zab Art — multi-page rebuild generator.
Builds 3 Vercel projects (A/B/C), 6 pages each, shared design system + components,
SEO/AEO/GEO, cookie banner, assets. Brand-locked. Partner-review-ready.
Run from ~/Downloads/vercel_deploys/.
"""
import os, re, json, shutil

ROOT = os.path.expanduser('~/Downloads/vercel_deploys')
PAINT_SRC = os.path.expanduser('~/Downloads')

PAINTINGS = [
    'painting_1.jpg', 'painting_3.jpg', 'painting_4.jpg', 'painting_5.jpg',
    'painting_6.jpg', 'painting_7.jpg', 'painting_8.jpg', 'painting_2_backup.jpg',
    # background-cleaned crops (wood/clutter removed) used in the gallery + story
    'painting_3_c.jpg', 'painting_5_c.jpg', 'painting_7_c.jpg',
]

PROTOS = {
    'b': {'slug': 'elizabeth-zab-prototype-b', 'base': 'https://elizabeth-zab-prototype-b.vercel.app'},
    'c': {'slug': 'elizabeth-zab-prototype-c', 'base': 'https://elizabeth-zab-prototype-c.vercel.app'},
}

TRANSPARENT = ("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==")
HERO_GRADIENT = ("linear-gradient(105deg, rgba(45,68,52,0.72) 0%, rgba(45,68,52,0.42) 45%, "
                 "rgba(45,68,52,0.10) 75%, rgba(45,68,52,0.02) 100%)")

PHONE = "(440) 477-1972"
TEL = "tel:+14404771972"
IG = "https://www.instagram.com/elizabethzabartllc?igsh=MXY0MHR5dWs1bWlk"
IG_HANDLE = "@elizabethzabartllc"
# Instagram glyph as inline SVG, tinted with currentColor so it picks up the site's palette
# (NOT the native Instagram gradient) in whatever context it sits.
IG_SVG = ('<svg class="ig-glyph" viewBox="0 0 24 24" width="20" height="20" fill="currentColor" '
          'aria-hidden="true" focusable="false"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 '
          '3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 '
          '4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-'
          '3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-'
          '3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 '
          '2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 '
          '6.78 6.98 6.98C8.333 23.986 8.741 24 12 24s3.668-.014 4.948-.072c4.354-.2 6.782-2.618 6.979-6.98.059-'
          '1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 '
          '15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 '
          '8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>')

# Studio hours (client-supplied 2026-06-23): Tue/Thu/Fri 11:30-3, Wed 3-7, Sat 10-2; closed Sun/Mon.
STUDIO_HOURS = [
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Tuesday", "Thursday", "Friday"], "opens": "11:30", "closes": "15:00"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Wednesday", "opens": "15:00", "closes": "19:00"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "10:00", "closes": "14:00"},
]

# ---------------------------------------------------------------------------
# CSS — locked design system (extracted verbatim from prototype C) + additions
# ---------------------------------------------------------------------------

def base_css():
    src = os.path.join(ROOT, 'elizabeth-zab-prototype-c', 'index.html')
    with open(src, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()
    style = re.search(r'<style>(.*?)</style>', html, re.S).group(1)
    # neutralise the baked-in base64 backgrounds (hero is overridden inline; others unused)
    style = re.sub(r'data:image/[a-zA-Z]+;base64,[A-Za-z0-9+/=]+', TRANSPARENT, style)
    return style.strip()

EXTRA_CSS = r"""
/* ---------- multi-page additions ---------- */
[hidden]{ display:none !important; }

/* sub-page heading band */
.page-head{ padding: clamp(56px,8vw,104px) 0 clamp(24px,3vw,44px); }
.page-head .eyebrow{ display:block; margin-bottom:14px; }
.page-head h1{ max-width: 900px; }
.page-head .sub{ font-size:18px; color:var(--body); margin-top:18px; max-width:660px; line-height:1.6; }

/* generic media tiles */
.media{ width:100%; background-size:cover; background-position:center; background-color:var(--bg-wash); }
.r-45{ aspect-ratio:4/5; } .r-43{ aspect-ratio:4/3; } .r-34{ aspect-ratio:3/4; }
.r-169{ aspect-ratio:16/9; } .r-32{ aspect-ratio:3/2; }

/* visualization overlay label (painting_4) */
.viz{ position:relative; }
.viz::after{
  content:"Visualization · room mockup, not a finished installation";
  position:absolute; bottom:12px; left:12px;
  font-family:var(--font); font-weight:500; font-size:10px;
  letter-spacing:0.12em; text-transform:uppercase;
  color:rgba(255,255,255,0.92); background:rgba(45,68,52,0.78); padding:6px 10px;
}

/* featured grids on home pages */
.feat{ display:grid; gap:24px; }
.feat-3{ grid-template-columns:repeat(3,1fr); }
.feat-4{ grid-template-columns:repeat(4,1fr); }
@media (max-width:880px){ .feat-3,.feat-4{ grid-template-columns:repeat(2,1fr); } }
@media (max-width:560px){ .feat-3,.feat-4{ grid-template-columns:1fr; } }
.feat .cap{ font-size:12px; color:var(--body); margin-top:12px; letter-spacing:0.04em; line-height:1.5; }
.feat .cap .no{ color:var(--brand-deep); font-weight:500; margin-right:10px; letter-spacing:0.12em; text-transform:uppercase; }

/* full-width gallery span + mobile collapse */
.gw-w-12{ grid-column: span 12; }
@media (max-width:880px){ .gw-w-12{ grid-column: span 1; } }

/* centered CTA band */
.band{ background:var(--bg-wash); text-align:center; padding: clamp(48px,7vw,88px) 32px; }
.band h2{ font-weight:300; margin-bottom:24px; }
.band p{ max-width:560px; margin:0 auto 24px; font-size:16px; }

/* artfest call-out (studio page) */
.artfest-callout{ background:var(--brand-deep); color:var(--white); text-align:center; padding:30px 32px; font-size:15px; letter-spacing:0.03em; }
.artfest-callout strong{ color:var(--accent); font-weight:500; }
.artfest-callout .shows{ display:block; margin-top:8px; font-size:13px; color:rgba(255,255,255,0.82); letter-spacing:0.02em; }

/* contact line */
.contact-line{ margin-top:28px; }
.contact-line a{ text-decoration:underline; }

/* ---------- prototype B home ---------- */
.hero-b{ min-height:96vh; }
.hero-b h1{ font-size:clamp(48px,7vw,88px); font-weight:300; }
.hero-b .hero-content{ max-width:1080px; }
.gallery-b-section{ padding:60px 0 96px; }

/* ---------- prototype C home + header ---------- */
.site-header .nav-right .visit-cta{
  display:inline-block; padding:10px 18px; background:var(--brand); color:var(--ink);
  font-weight:500; font-size:13px; letter-spacing:0.06em; transition:background .2s;
}
.site-header .nav-right .visit-cta:hover{ background:var(--brand-deep); color:var(--white); }
.hero-c h1{ font-weight:300; }
.hero-c .lede{ color:rgba(255,255,255,0.96); }
.address-strip{
  background:var(--white); padding:18px 32px; text-align:center; font-size:14px;
  border-bottom:1px solid rgba(46,42,41,0.08);
}
.address-strip strong{ color:var(--ink); font-weight:500; }
.studio-pulled-up{ background:var(--bg-wash); }
.studio-pulled-up .studio-card{ background:var(--white); border-color:var(--brand); }
.final-cta-row{ background:var(--ink); color:var(--white); padding:80px 32px; text-align:center; }
.final-cta-row h2{ color:var(--white); font-weight:300; }
.final-cta-row p{ color:rgba(255,255,255,0.78); max-width:540px; margin:16px auto 32px; }
.final-cta-row .phone-line{ display:block; margin-top:18px; font-size:14px; color:rgba(255,255,255,0.7); }
.final-cta-row .phone-line a{ color:var(--accent); }

/* ---------- cookie banner (brand-locked) ---------- */
.cookie-banner{
  position:fixed; bottom:24px; left:24px; max-width:420px; width:auto;
  background:var(--bg-wash); border:1px solid rgba(45,68,52,0.18);
  padding:24px; border-radius:0; box-shadow:0 8px 32px rgba(45,68,52,0.16); z-index:90;
}
.cookie-banner .cookie-title{ font-family:var(--font); font-weight:500; color:var(--ink); font-size:14px; letter-spacing:0.02em; }
.cookie-banner .cookie-body{ font-family:var(--font); font-weight:400; color:var(--ink); font-size:13px; line-height:1.6; margin-top:8px; }
.cookie-banner .cookie-actions{ display:flex; gap:8px; margin-top:16px; }
.cookie-banner .cookie-btn{ font-family:var(--font); font-weight:500; font-size:12px; padding:10px 16px; border:1px solid var(--ink); border-radius:0; cursor:pointer; transition:all .2s ease; }
.cookie-banner .cookie-decline{ background:transparent; color:var(--ink); }
.cookie-banner .cookie-decline:hover{ background:var(--ink); color:var(--white); }
.cookie-banner .cookie-accept{ background:var(--ink); color:var(--white); }
.cookie-banner .cookie-accept:hover{ background:var(--brand-deep); border-color:var(--brand-deep); }
@media (max-width:640px){ .cookie-banner{ left:0; right:0; bottom:0; max-width:none; width:100%; } }

/* ---------- mobile header (<=720px): stack wordmark over a centered nav row ---------- */
@media (max-width:720px){
  .site-header .row{ flex-direction:column; align-items:center; gap:12px; padding:14px 20px; }
  .site-header .wordmark{ font-size:17px; white-space:nowrap; }
  .site-header .wordmark span{ white-space:nowrap; }
  .site-header .nav-right{ width:100%; justify-content:center; flex-wrap:wrap; gap:8px 20px; font-size:13px; }
  .site-header .nav-right a{ white-space:nowrap; }
  .site-header .nav-right .hide-sm{ display:none; }
  .site-header .nav-right .visit-cta{ padding:8px 14px; white-space:nowrap; }
}

/* ---------- Instagram glyph (brand-colored via currentColor, not the IG gradient) ---------- */
.ig-glyph{ vertical-align:middle; display:inline-block; }
a.ig-link{ display:inline-flex; align-items:center; line-height:0; }
a.ig-btn{ display:inline-flex; align-items:center; justify-content:center; gap:8px; }
a.ig-btn .ig-glyph{ width:18px; height:18px; }

/* ---------- center action buttons on mobile ---------- */
@media (max-width:720px){
  .hero .cta-row{ justify-content:center; }
  .studio-card .card-actions{ justify-content:center; }
  .studio-card .card-actions .btn{ width:100%; text-align:center; }
  .final-cta-row .btn{ display:inline-flex; }
}
"""

# ---------------------------------------------------------------------------
# SEO head
# ---------------------------------------------------------------------------

PAGES_META = {
    'index':     ('Pour paintings, made in Akron',
                  'Original acrylic pour paintings by Elizabeth Zab. Studio inside Salon Lofts, Akron, OH. Walk in to see the work, or commission a custom palette.',
                  '', 'website'),
    'work':      ('The work',
                  'A selection of recent original pour paintings by Elizabeth Zab — color, movement, organic flow. Made in Akron, available at the studio.',
                  'work', 'website'),
    'story':     ('A painting is a kind of dance',
                  "How a pour painting is made: poured palettes, warm air from a hairdryer, and a long slow dry. Elizabeth Zab's process, from her Salon Lofts studio.",
                  'story', 'article'),
    'studio':    ('Visit the studio in Akron',
                  "Walk in to Elizabeth Zab's studio at 3987 Medina Rd, Akron — inside Salon Lofts. See original pour paintings, pick up, or ask about a commission.",
                  'studio', 'website'),
    'designers': ('Stage with originals',
                  "For interior designers and realtors: stage listings with original Elizabeth Zab pour paintings, commission palettes to match a buyer's room, or order signed client gifts.",
                  'designers', 'website'),
    'qa':        ('Common questions',
                  'Pour painting, the hairdryer technique, studio pickup, shipping, Certificates of Authenticity, working with realtors — Elizabeth Zab Art FAQ.',
                  'qa', 'website'),
}


def esc(s):
    return (s.replace('&', '&amp;').replace('"', '&quot;'))


def head(proto, page, jsonld=''):
    base = PROTOS[proto]['base']
    seg, desc, path, ogtype = PAGES_META[page]
    canonical = f"{base}/" if path == '' else f"{base}/{path}"
    title = f"{seg} — Elizabeth Zab Art · Akron, OH"
    ogtitle = f"{seg} · Elizabeth Zab Art"
    ogimg = f"{base}/assets/painting_1.jpg"
    desc_e = esc(desc)
    parts = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="googlebot" content="noindex, nofollow">
<title>{esc(title)}</title>
<meta name="description" content="{desc_e}">
<meta name="author" content="Elizabeth Zab">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{esc(ogtitle)}">
<meta property="og:description" content="{desc_e}">
<meta property="og:image" content="{ogimg}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Elizabeth Zab Art">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(ogtitle)}">
<meta name="twitter:description" content="{desc_e}">
<meta name="twitter:image" content="{ogimg}">
<meta name="geo.region" content="US-OH">
<meta name="geo.placename" content="Akron, Ohio">
<meta name="geo.position" content="41.0814;-81.5190">
<meta name="ICBM" content="41.0814, -81.5190">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#2D4434">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
{jsonld}</head>
"""
    return parts


# ---------------------------------------------------------------------------
# shared components
# ---------------------------------------------------------------------------

ARTFEST_STRIP = """<div class="artfest-strip">
  <strong>Boston Mills Artfest</strong>
  <span class="sep">·</span> June 27–28
  <span class="sep">·</span> Booth #88, North Tent
  <span class="sep">·</span> Cuyahoga Valley, OH
</div>
"""


def header(proto):
    if proto == 'c':
        nav = """      <a href="/work">Work</a>
      <a href="/story">Story</a>
      <a href="/designers">Designers</a>
      <a href="/qa" class="hide-sm">Q&amp;A</a>
      <a href="/studio" class="visit-cta">Visit the studio</a>"""
    else:
        nav = f"""      <a href="/work">Work</a>
      <a href="/story">Story</a>
      <a href="/designers">Designers</a>
      <a href="/qa" class="hide-sm">Q&amp;A</a>
      <a href="{TEL}" class="hide-sm">{PHONE}</a>
      <a href="/studio">Visit the studio</a>"""
    return f"""<header class="site-header">
  <div class="row">
    <a href="/" class="wordmark">Elizabeth Zab <span>· Art</span></a>
    <nav class="nav-right">
{nav}
    </nav>
  </div>
</header>
"""


FOOTER = f"""<footer class="site-footer">
  <div class="row">
    <div>
      <div class="wordmark"><a href="/" style="color:var(--white);">Elizabeth Zab <span style="color: var(--accent); font-weight: 300;">· Art</span></a></div>
      <p style="margin-top: 14px;">Pour paintings, made in Akron, seen at the studio.</p>
    </div>
    <div>
      <h4>Studio</h4>
      <p>3987 Medina Rd, Studio 3<br>Akron, OH 44333<br>Inside Salon Lofts</p>
    </div>
    <div>
      <h4>Reach</h4>
      <p><a href="{TEL}">{PHONE}</a><br><a href="{IG}" class="ig-link" target="_blank" rel="noopener" aria-label="Instagram @elizabethzabartllc" title="Instagram (@elizabethzabartllc)">{IG_SVG}</a></p>
    </div>
  </div>
  <nav class="legal-nav" style="max-width:1180px;margin:28px auto 0;text-align:center;font-size:13px;">
    <a href="/work" style="margin:0 10px;">Work</a>
    <a href="/story" style="margin:0 10px;">Story</a>
    <a href="/studio" style="margin:0 10px;">Studio</a>
    <a href="/designers" style="margin:0 10px;">Designers</a>
    <a href="/qa" style="margin:0 10px;">Q&amp;A</a>
  </nav>
  <div class="legal">© Elizabeth Zab Art · Akron, OH</div>
</footer>
"""

COOKIE = """<div class="cookie-banner" id="cookieBanner" role="dialog" aria-label="Cookie notice" hidden>
  <div class="cookie-title">A note on cookies</div>
  <p class="cookie-body">This site uses a small set of cookies to keep the studio visit experience smooth. We don't sell your data and we don't run ad networks.</p>
  <div class="cookie-actions">
    <button type="button" class="cookie-btn cookie-decline" onclick="ezCookie('decline')">Decline</button>
    <button type="button" class="cookie-btn cookie-accept" onclick="ezCookie('accept')">Accept</button>
  </div>
</div>
<script>
(function(){
  try {
    if (!localStorage.getItem('ezart_cookie_v1')) {
      var b = document.getElementById('cookieBanner');
      if (b) b.hidden = false;
    }
  } catch (e) {}
})();
function ezCookie(v){
  try { localStorage.setItem('ezart_cookie_v1', v); } catch (e) {}
  var b = document.getElementById('cookieBanner');
  if (b) b.hidden = true;
}
</script>
"""


def hero_style(img):
    return f"background-image: {HERO_GRADIENT}, url('/assets/{img}');"


def studio_card():
    return f"""<div class="studio-card">
  <span class="eyebrow">Visit the studio</span>
  <h3>Salon Lofts, Akron.</h3>
  <p>My studio is open to walk-ins during my studio hours. Walk in from the Salon Lofts main lobby, see the work in person, ask about a commission, or pick up a piece you've reserved.</p>
  <p>I'm not in the studio the whole time the Salon Lofts lobby is open, so the hours below are when you'll find me there.</p>
  <p>To visit outside those hours, message me on Instagram and I'll arrange a time. Pickup for reserved pieces is easy and free.</p>
  <dl>
    <dt>Address</dt>
    <dd>3987 Medina Rd, Studio 3<br>Akron, OH 44333</dd>
    <dt>Studio</dt>
    <dd>Inside Salon Lofts, Studio 3 · walk in from the main lobby</dd>
    <dt>Studio hours</dt>
    <dd>Tue 11:30–3 · Wed 3–7 · Thu 11:30–3<br>Fri 11:30–3 · Sat 10–2 · Closed Sun &amp; Mon</dd>
    <dt>Reach me</dt>
    <dd><a href="{TEL}">{PHONE}</a> &nbsp;·&nbsp; <a href="{IG}" class="ig-link" target="_blank" rel="noopener" aria-label="Instagram @elizabethzabartllc" title="Instagram (@elizabethzabartllc)">{IG_SVG}</a></dd>
  </dl>
  <div class="card-actions" style="display:flex; gap:10px; flex-wrap:wrap; margin-top:4px;">
    <a href="https://maps.google.com/?q=3987+Medina+Rd+Akron+OH+44333" target="_blank" rel="noopener" class="btn">Get directions</a>
    <a href="{IG}" target="_blank" rel="noopener" class="btn btn-brand ig-btn">{IG_SVG}<span>Message me on Instagram</span></a>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# JSON-LD
# ---------------------------------------------------------------------------

def jsonld_block(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False)
            + '\n</script>\n')


def jsonld_index(base):
    obj = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Person",
                "@id": f"{base}/#person",
                "name": "Elizabeth Zab",
                "alternateName": "Elizabeth Zab Art",
                "url": f"{base}/",
                "image": f"{base}/assets/painting_1.jpg",
                "jobTitle": "Abstract Fluid Artist",
                "description": "Abstract artist working primarily in acrylic pouring and fluid art techniques.",
                "worksFor": {"@id": f"{base}/#org"},
                "sameAs": ["https://www.instagram.com/elizabethzabartllc"],
            },
            {
                "@type": "LocalBusiness",
                "@id": f"{base}/#org",
                "name": "Elizabeth Zab Art",
                "url": f"{base}/",
                "telephone": "+1-440-477-1972",
                "image": f"{base}/assets/painting_1.jpg",
                "founder": {"@id": f"{base}/#person"},
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "3987 Medina Rd, Studio 3",
                    "addressLocality": "Akron",
                    "addressRegion": "OH",
                    "postalCode": "44333",
                    "addressCountry": "US",
                },
                "geo": {"@type": "GeoCoordinates", "latitude": 41.0814, "longitude": -81.5190},
                "openingHoursSpecification": STUDIO_HOURS,
                "areaServed": ["Akron", "Cleveland", "Medina", "Hudson", "Northeast Ohio"],
                "priceRange": "$$",
            },
            {
                "@type": "WebSite",
                "@id": f"{base}/#website",
                "url": f"{base}/",
                "name": "Elizabeth Zab Art",
                "publisher": {"@id": f"{base}/#org"},
                "inLanguage": "en-US",
            },
        ],
    }
    return jsonld_block(obj)


QA_ITEMS = [
    ("What is pour painting?",
     "Pour painting is an acrylic technique where mixed paint is poured directly onto canvas and shaped by tilting, gravity, and movement. It produces flowing, organic patterns and cells that brushwork can't reproduce. Every piece is one-of-one — the paint never lays down the same way twice."),
    ("What is the hairdryer for?",
     "Warm air opens cells in the paint and helps me shape how the pigments settle. It's part of how each piece finds its breath. It's also how I keep the paint moving without losing its body."),
    ("Can I commission a custom piece?",
     "Yes. I take commissions for specific palettes, sizes, and rooms. Most commissions take two to four weeks depending on size and cure time. Reach out by phone or Instagram to start."),
    ("Can I pick up at the studio?",
     "Yes — local pickup at the Salon Lofts studio in Akron is the easiest way. Walk in during my studio hours, or message me on Instagram to schedule."),
    ("Do you ship?",
     "Shipping or pickup can be discussed when you inquire. Most local buyers (Akron, Cleveland, Medina, Hudson) pick up directly at the studio, which is the easiest option. International shipping is not offered at this time."),
    ("Do you offer Certificates of Authenticity?",
     "Every original ships with a signed Certificate of Authenticity that includes the piece's title, date, materials, and a brief note about the work."),
    ("Do you work with realtors or designers?",
     "Yes. I work with realtors and interior designers on staging listings with original work, commissioning palettes to match a room, and signed originals as client gifts. See the designers & realtors page, or call (440) 477-1972."),
    ("Where can I see the work in person?",
     "At my studio inside Salon Lofts, 3987 Medina Rd, Studio 3, Akron, OH 44333 — and at upcoming shows including the Boston Mills Artfest, June 27–28, Booth #88, North Tent."),
]


def jsonld_faq():
    obj = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in QA_ITEMS
        ],
    }
    return jsonld_block(obj)


def jsonld_studio(base):
    obj = {
        "@context": "https://schema.org",
        "@type": "Place",
        "@id": f"{base}/studio#place",
        "name": "Elizabeth Zab Art — Studio",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "3987 Medina Rd, Studio 3",
            "addressLocality": "Akron",
            "addressRegion": "OH",
            "postalCode": "44333",
            "addressCountry": "US",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 41.0814, "longitude": -81.5190},
        "hasMap": "https://maps.google.com/?q=3987+Medina+Rd+Akron+OH+44333",
        "telephone": "+1-440-477-1972",
        "openingHoursSpecification": STUDIO_HOURS,
    }
    return jsonld_block(obj)


def jsonld_designers(base):
    obj = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": "Art Staging and Commissioning",
        "provider": {"@type": "LocalBusiness", "@id": f"{base}/#org", "name": "Elizabeth Zab Art"},
        "areaServed": ["Akron", "Cleveland", "Medina", "Hudson", "Northeast Ohio"],
        "description": "Original pour paintings for staging listings, commissioned palettes to match a buyer's room, and signed originals as closing or client gifts.",
    }
    return jsonld_block(obj)


# ---------------------------------------------------------------------------
# page bodies
# ---------------------------------------------------------------------------

def wrap(proto, page, inner, jsonld=''):
    return (head(proto, page, jsonld)
            + '<body id="top">\n\n'
            + ARTFEST_STRIP + '\n'
            + header(proto) + '\n'
            + inner
            + '\n' + FOOTER + '\n'
            + COOKIE
            + '\n</body>\n</html>\n')


def featured(items, cols):
    cells = []
    for img, no, desc in items:
        cells.append(
            f"""    <div>
      <div class="media r-45" style="background-image:url('/assets/{img}');"></div>
      <div class="cap"><span class="no">{no}</span>{desc}</div>
    </div>""")
    return f'  <div class="feat feat-{cols}">\n' + "\n".join(cells) + "\n  </div>"


# ----- HOME PAGES -----

def home_b(proto):
    inner = f"""<section class="hero hero-b" style="padding:0;">
  <div class="hero-img" style="{hero_style('painting_1.jpg')}"></div>
  <div class="hero-content">
    <span class="eyebrow" style="color: var(--accent-wash);">Elizabeth Zab · Akron</span>
    <h1 style="margin-top:16px;">Pour paintings. Akron.</h1>
    <p class="lede">Original acrylic pour paintings, made and shown at Salon Lofts.</p>
    <div class="cta-row">
      <a href="/work" class="btn btn-ghost" style="border-color: var(--white); color: var(--white);">See the work ↓</a>
    </div>
  </div>
</section>

<section id="work" class="gallery-b-section">
  <div class="container">
    <span class="eyebrow">Recent work</span>
    <h2 style="margin: 12px 0 48px; max-width: 540px; font-weight: 300;">Four pieces.</h2>
{featured([
    ('painting_6.jpg', 'No. 01', 'Purple, silver, and yellow on a dark ground'),
    ('painting_3_c.jpg', 'No. 02', 'Rust, slate blue, and cream pour'),
    ('painting_7_c.jpg', 'No. 03', 'Black-and-white charcoal pour on canvas'),
    ('painting_8.jpg', 'No. 04', 'Black, yellow, and red, a bold vertical pour'),
], 4)}
    <div style="text-align:center; margin-top:48px;"><a href="/work" class="btn">View all work</a></div>
  </div>
</section>

<div class="band">
  <h2>Made in Akron. Seen at the studio.</h2>
  <p>Walk in from the Salon Lofts lobby to see originals in person.</p>
  <a href="/studio" class="btn">Visit the studio</a>
</div>
"""
    return wrap(proto, 'index', inner, jsonld_index(PROTOS[proto]['base']))


def home_c(proto):
    inner = f"""<section class="hero hero-c" style="padding:0;">
  <div class="hero-img" style="{hero_style('painting_1.jpg')}"></div>
  <div class="hero-content">
    <span class="eyebrow" style="color: var(--accent-wash);">Salon Lofts · Akron, OH</span>
    <h1 style="margin-top: 16px;">Walk in. See the work. Take one home.</h1>
    <p class="lede">Original pour paintings, made and shown at my studio inside Salon Lofts. Walk in from the main lobby during my studio hours.</p>
    <div class="cta-row">
      <a href="/studio" class="btn btn-brand">Plan a visit</a>
      <a href="{TEL}" class="btn btn-ghost">Call {PHONE}</a>
    </div>
  </div>
</section>

<div class="address-strip">
  <strong>3987 Medina Rd, Studio 3, Akron, OH 44333</strong> &nbsp;·&nbsp; Inside Salon Lofts &nbsp;·&nbsp; Walk-ins welcome during my studio hours
</div>

<section class="studio-pulled-up">
  <div class="container">
    <span class="eyebrow">The studio</span>
    <h2 style="margin: 12px 0 48px; max-width: 540px;">Walk in during my studio hours.</h2>
    <div class="studio-grid">
      <div class="media r-45" style="background-image:url('/assets/painting_8.jpg');"></div>
      {studio_card()}
    </div>
  </div>
</section>

<section class="container">
  <span class="eyebrow">Recent work</span>
  <h2 style="margin: 12px 0 48px; max-width: 540px;">A few recent pieces.</h2>
{featured([
    ('painting_6.jpg', 'No. 01', 'Purple, silver, and yellow on a dark ground'),
    ('painting_3_c.jpg', 'No. 02', 'Rust, slate blue, and cream pour'),
    ('painting_5_c.jpg', 'No. 03', 'Blue, black, and white pour, still wet'),
], 3)}
  <div style="text-align:center; margin-top:48px;"><a href="/work" class="btn btn-ghost">View all work</a></div>
</section>

<div class="final-cta-row">
  <h2>Come see them in person.</h2>
  <p>Walk in during my studio hours, or message me and I'll arrange a time at the studio.</p>
  <a href="/studio" class="btn btn-primary" style="background:var(--accent);border-color:var(--accent);color:var(--ink);">Plan a visit</a>
  <span class="phone-line">or call <a href="{TEL}">{PHONE}</a> &nbsp;·&nbsp; message me on <a href="{IG}" target="_blank" rel="noopener">Instagram</a></span>
</div>
"""
    return wrap(proto, 'index', inner, jsonld_index(PROTOS[proto]['base']))


HOME = {'b': home_b, 'c': home_c}

# ----- SHARED SUB-PAGES -----

GALLERY_ITEMS = [
    ('painting_6.jpg', 'gw-w-7', 'No. 01', 'Purple, silver, and yellow on a dark ground', '4/5'),
    ('painting_3_c.jpg', 'gw-w-5', 'No. 02', 'Rust, slate blue, and cream pour', '4/5'),
    ('painting_7_c.jpg', 'gw-w-5', 'No. 03', 'Black-and-white charcoal pour on canvas', '4/5'),
    ('painting_8.jpg', 'gw-w-7', 'No. 04', 'Black, yellow, and red, a bold vertical pour', '4/5'),
    ('painting_1.jpg', 'gw-w-6', 'No. 05', 'Pink, green, and silver pour', '4/5'),
    ('painting_5_c.jpg', 'gw-w-6', 'No. 06', 'Blue, black, and white pour, still wet', '4/5'),
]


def page_work(proto):
    cells = []
    for img, span, no, desc, ratio in GALLERY_ITEMS:
        cells.append(
            f"""    <div class="gw-wrap {span}">
      <div class="gw-pic" style="background-image: url('/assets/{img}'); aspect-ratio: {ratio};"></div>
      <div class="gw-caption"><span class="no">{no}</span>{desc}</div>
    </div>""")
    gallery = "\n".join(cells)
    inner = f"""<div class="page-head">
  <div class="container">
    <span class="eyebrow">Recent work</span>
    <h1>The work.</h1>
    <p class="sub">A selection of recent pieces, made one breath at a time.</p>
  </div>
</div>

<section class="container" style="padding-top:0;">
  <div class="gallery-wall">
{gallery}
  </div>
</section>

<div class="band">
  <h2>Come see them in person.</h2>
  <p>Every original is signed, dated, and shipped with a Certificate of Authenticity.</p>
  <a href="/studio" class="btn">Visit the studio</a>
</div>
"""
    return wrap(proto, 'work', inner)


def page_story(proto):
    inner = f"""<div class="page-head">
  <div class="container">
    <span class="eyebrow">The story</span>
    <h1>A painting is a kind of dance.</h1>
  </div>
</div>

<section class="container" style="padding-top:0;">
  <div class="story-grid">
    <div class="story-text">
      <p>I'm Elizabeth, an abstract artist working primarily in acrylic pouring and fluid art techniques, from a studio inside Salon Lofts in Akron. My work is guided by a deep connection to color, movement, and the organic flow of paint as it finds its own shape on canvas.</p>
      <div class="pull-quote">"The hairdryer is part of the process. It moves the paint, opens the cells, and gives each piece its breath."</div>
      <p>I approach painting as a kind of dance. Every piece begins with a poured palette and ends with a careful tilt, a quiet breath of warm air, and a long slow dry. No two are alike. Each is signed, dated, and finished by hand on the back of the canvas.</p>
    </div>
    <div class="media r-45" style="background-image:url('/assets/painting_5_c.jpg');"></div>
  </div>
</section>

<div class="band">
  <h2>Want to see the process in person?</h2>
  <p>Walk in from the Salon Lofts lobby in Akron to see how a pour painting comes together.</p>
  <a href="/studio" class="btn">Visit the studio</a>
</div>
"""
    return wrap(proto, 'story', inner)


def page_studio(proto):
    inner = f"""<div class="page-head">
  <div class="container">
    <span class="eyebrow">Visit</span>
    <h1>Visit the studio.</h1>
    <p class="sub">Walk in from the Salon Lofts lobby during my studio hours.</p>
  </div>
</div>

<section class="container" style="padding-top:0;">
  <div class="studio-grid">
    <div class="media r-45" style="background-image:url('/assets/painting_8.jpg');"></div>
    {studio_card()}
  </div>
</section>

<div class="artfest-callout">
  Find me at the <strong>Boston Mills Artfest</strong> · June 27–28 · Booth #88, North Tent · Cuyahoga Valley, OH
  <span class="shows">Around Northeast Ohio's art season — also the Tremont Arts Festival and Medina Art in the Park.</span>
</div>
"""
    return wrap(proto, 'studio', inner, jsonld_studio(PROTOS[proto]['base']))


def page_designers(proto):
    inner = f"""<section class="dark" style="padding-top: clamp(56px,8vw,104px);">
  <div class="container">
    <div class="realtor-grid">
      <div class="media r-43 viz" style="background-image:url('/assets/painting_4.jpg');" role="img" aria-label="Room visualization with an Elizabeth Zab pour painting"></div>
      <div>
        <span class="eyebrow">For designers &amp; realtors</span>
        <h1 style="color: var(--white); margin: 10px 0 8px;">Stage with originals.</h1>
        <p>An original pour painting lifts a listing or a client's room in a way that a print can't.</p>
        <p>I work with realtors and interior designers across Akron, Cleveland, Medina, and Hudson, on staging, commissioned palettes, and signed client gifts.</p>
        <p>Here's how that usually works:</p>
        <ol class="realtor-list">
          <li>Stage a listing with original work, with pickup or swap when the home sells</li>
          <li>Commission a palette to match a buyer's room or a client's space</li>
          <li>Signed originals as closing or client gifts</li>
        </ol>
        <p class="contact-line"><a href="{TEL}" style="color:inherit;">{PHONE}</a> &nbsp;·&nbsp; <a href="{IG}" class="ig-link" style="color:inherit;" target="_blank" rel="noopener" aria-label="Instagram @elizabethzabartllc" title="Instagram (@elizabethzabartllc)">{IG_SVG}</a></p>
      </div>
    </div>
  </div>
</section>

<div class="band">
  <h2>Tell me about your listing or your client.</h2>
  <p>Call or message and we'll find the right piece, palette, or commission for the space.</p>
  <a href="{TEL}" class="btn">Call {PHONE}</a>
  <div style="margin-top:16px;"><a href="{IG}" class="btn btn-ghost ig-btn" target="_blank" rel="noopener">{IG_SVG}<span>Message me on Instagram</span></a></div>
</div>
"""
    return wrap(proto, 'designers', inner, jsonld_designers(PROTOS[proto]['base']))


def page_qa(proto):
    items = []
    for i, (q, a) in enumerate(QA_ITEMS):
        op = ' open' if i == 0 else ''
        items.append(
            f"""  <details{op}>
    <summary>{q.replace('&', '&amp;')}</summary>
    <p>{a.replace('&', '&amp;')}</p>
  </details>""")
    accordion = "\n".join(items)
    inner = f"""<div class="page-head">
  <div class="container">
    <span class="eyebrow">Common questions</span>
    <h1>Good to know.</h1>
    <p class="sub">Common questions about the work, the studio, and how to buy.</p>
  </div>
</div>

<section class="container" style="padding-top:0;">
  <div class="qa-wrap qa">
{accordion}
  </div>
</section>

<div class="coa">
  <div class="seal">Every Original</div>
  <h3>Signed, dated, and shipped with a <span>Certificate of Authenticity.</span></h3>
</div>
"""
    return wrap(proto, 'qa', inner, jsonld_faq())


SUBPAGES = {
    'work': page_work,
    'story': page_story,
    'studio': page_studio,
    'designers': page_designers,
    'qa': page_qa,
}

# ---------------------------------------------------------------------------
# sitemap / robots / vercel.json
# ---------------------------------------------------------------------------

def sitemap(base):
    rows = [
        ('/', 'monthly', '1.0'),
        ('/work', 'monthly', '0.9'),
        ('/story', 'yearly', '0.7'),
        ('/studio', 'monthly', '0.9'),
        ('/designers', 'yearly', '0.6'),
        ('/qa', 'monthly', '0.8'),
    ]
    body = "\n".join(
        f"  <url><loc>{base}{p}</loc><changefreq>{c}</changefreq><priority>{pr}</priority></url>"
        for p, c, pr in rows)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + body + '\n</urlset>\n')


def robots(base):
    # Unlisted / partner-review only: keep crawlers out entirely.
    return "User-agent: *\nDisallow: /\n"


def vercel_json(slug):
    obj = {
        "cleanUrls": True,
        "trailingSlash": False,
        "headers": [
            {"source": "/(.*)",
             "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]},
            {"source": "/assets/(.*)",
             "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/(.*).html",
             "headers": [{"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"}]},
        ],
    }
    return json.dumps(obj, indent=2) + "\n"


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

CSS = base_css() + "\n" + EXTRA_CSS


def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def build():
    # sanity: paintings present
    missing = [p for p in PAINTINGS if not os.path.exists(os.path.join(PAINT_SRC, p))]
    if missing:
        raise SystemExit(f"Missing paintings in {PAINT_SRC}: {missing}")

    for proto, info in PROTOS.items():
        d = os.path.join(ROOT, info['slug'])
        base = info['base']
        assets = os.path.join(d, 'assets')
        os.makedirs(assets, exist_ok=True)

        # copy paintings
        for p in PAINTINGS:
            shutil.copy2(os.path.join(PAINT_SRC, p), os.path.join(assets, p))

        # client-supplied prototype C hero background (green/teal oval pour)
        hero_src = os.path.expanduser('~/Desktop/image for Elizabeth.jpeg')
        if os.path.exists(hero_src):
            shutil.copy2(hero_src, os.path.join(assets, 'hero_c.jpg'))

        # favicons / app icons at the project root
        brand = os.path.join(ROOT, '_brand')
        for fav in ('favicon.ico', 'favicon.svg', 'favicon-32.png', 'favicon-192.png', 'apple-touch-icon.png'):
            fsrc = os.path.join(brand, fav)
            if os.path.exists(fsrc):
                shutil.copy2(fsrc, os.path.join(d, fav))

        # home
        write(os.path.join(d, 'index.html'), HOME[proto](proto))
        # sub-pages
        for name, fn in SUBPAGES.items():
            write(os.path.join(d, f'{name}.html'), fn(proto))
        # seo files
        write(os.path.join(d, 'sitemap.xml'), sitemap(base))
        write(os.path.join(d, 'robots.txt'), robots(base))
        write(os.path.join(d, 'vercel.json'), vercel_json(info['slug']))

        print(f"built {info['slug']}: 6 pages + sitemap/robots/vercel.json + {len(PAINTINGS)} assets")


if __name__ == '__main__':
    build()
    print("DONE")
