# Elizabeth Zab Art — WordPress migration package

Status: built for staging installation; production migration is NOT complete.
Source: Foundation-AI-Advisory/elizabeth-zab-art, commit 6e85ac6c2b80cd6b7972dec2fd121f09def39a82, retrieved October 21, 2026.

The live site remains on GitHub Pages. No production DNS, hosting account, user account or access permission has been changed.

## Included

- `elizabeth-zab-theme.zip`: installable classic WordPress theme, original artwork, CSS and page interactions; no page builder or paid plugin required.
- `elizabeth-zab-importer.zip`: administrator-only, repeatable staging importer. Creates seven pages, imports 20 artwork image files into the Media Library, creates menus and sets the Home page and clean permalinks. Existing unrelated pages are never replaced. Deactivate after a successful import.
- `elizabeth-zab-pages.xml`: alternative WordPress WXR export with seven pages and editing metadata. Prefer the bundled importer, which also handles local media and menus. Do not use both paths unless intentionally continuing a partial import.
- `elizabeth-zab-root-assets.zip`: optional exact legacy image/icon files for the web root. Helpful if the host handles static file requests without passing missing files to WordPress. Does not contain a static robots.txt or sitemap.xml that could override WordPress indexing controls.
- `theme/`, `plugin/`, `tools/`: complete editable source, deterministic conversion and static validation tools.
- `validation-static.json` and `VALIDATION.md`: checks completed and remaining tests.
- `DEPLOYMENT.md`: staging installation, GoDaddy cutover, rollback and access handoff.

## Preserved

Seven page routes: `/`, `/work/`, `/story/`, `/studio/`, `/designers/`, `/qa/`, `/classes/`. Custom 404 artwork animation is included. The existing color palette, Quicksand font, artwork, text, responsive CSS, gallery navigation/swipe/keyboard controls, card motion, Q&A disclosures, phone links, Instagram links and map directions are carried over. Classes retains its actual coming-soon message; no dates, prices or booking system are invented.

Page titles, descriptions, social metadata and structured data are seeded from source. Gallery and FAQ structured data follow their editable content. Studio contact details and opening hours update shared displays and business schema. `/sitemap.xml` is generated from published WordPress pages; legacy `/assets/*`, icon and `llms.txt` URLs are served from the bundled files. Explicit legacy `index.html` variants redirect to the unchanged clean page routes.

GA4 property `G-F039HJSL10` is retained. The old site's Decline button only hid a notice while GA had already loaded. The conversion loads GA only after Accept, on the production hostname, with indexing enabled and the administrator launch control checked. No new analytics account is created.

## Editing after import

| Change | WordPress location |
|---|---|
| Headings, paragraphs, button labels/links, page images and alt text | Pages → select page → Page copy and artwork → Update |
| Add/remove/reorder gallery pieces, descriptions, dimensions and images | Pages → Work → Gallery pieces → Update |
| Homepage featured artwork and captions | Pages → Home → Page copy and artwork |
| Classes announcements, description and link | Pages → Classes |
| Q&A questions and answers | Pages → Q&A |
| Phone, Instagram, address, hours, footer introduction | Studio details → Save studio details |
| Page search title, description and social image | Pages → select page → Search and social preview |
| Menu labels/order | Appearance → Menus, administrator |
| New images | Media → Add New or Choose from Media Library |

Use the supplied page fields for migrated pages. Their layouts are intentionally protected; this is not a freeform Site Editor theme. New ordinary pages use the normal WordPress editor. The Work gallery is repeatable. Adding entirely new homepage sections or additional FAQ rows requires a template extension; editing the existing ones does not. Do not change existing slugs during routine edits.

Full page HTML is also stored in `post_content` for portability. The JSON editing metadata, page template and theme preserve editing structure. Keep the database and theme in backups. Site settings and menus require a database backup; WXR alone is not a full-site backup.

## Required before launch

A WordPress installation that allows uploading a custom theme and plugin; temporary staging URL; Administrator access; HTTPS; supported PHP and database; a backup and restore facility; and access to the hosting provider's domain/SSL configuration. If using WordPress.com, confirm the chosen plan permits custom themes and plugins. GoDaddy DNS registration alone is not WordPress hosting.

No hosting purchase or provider selection is assumed. The website manager's identity and permissions remain to be confirmed separately. Do not put passwords or recovery codes in this package or send them in chat.
