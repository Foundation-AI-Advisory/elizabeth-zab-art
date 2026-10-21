# Validation record

Build date: October 21, 2026. Source commit: 6e85ac6c2b80cd6b7972dec2fd121f09def39a82.

## Completed

- Inspected the complete repository file tree and all HTML/CSS/JavaScript, structured metadata, crawler files and SEO audit script; retrieved and hash-verified every source blob.
- 107 static migration checks passed: seven page records, nine gallery records, exact default content/structure reconstruction, exact CSS preservation, valid JSON-LD records, all referenced artwork present, 27 original asset checksums and seven WXR items.
- Existing SEO audit passed: seven public routes and seven sitemap URLs. The audit was narrowly updated to exclude WordPress package fragments from its scan of public static pages.
- All 10 JavaScript files passed `node --check`.
- All 10 PHP files parsed successfully with php-parser 3.7.0 in PHP 8.3 mode (upstream commit 94f6b40fa502e7e8e07d0dc2f8a7f13be65cd98c). This is a syntax parse, not execution by PHP or WordPress.
- The importer and saving code include capability checks, nonces, input sanitization, escaped field output, source-asset checksum preflight and existing-page collision protection.

## Not completed — required before production

No verified WordPress host/staging login is available. The local environment has no PHP/WordPress runtime. Package and runtime installation attempts were unavailable. The browser preview stalled and was cancelled, so there is no completed screenshot, responsive visual, or interactive browser test. Do not interpret static checks as a live staging acceptance test.

The following are release gates:

1. PHP lint and runtime: `find wp-content/themes/elizabeth-zab wp-content/plugins/elizabeth-zab-importer -name '*.php' -exec php -l {} \;`. Activate theme/plugin under WP_DEBUG_LOG and resolve any errors.
2. Import on an empty backed-up staging site; verify seven pages, 20 artwork attachments, primary/footer menus and the Home setting. Rerun importer and confirm no duplicate pages/media or overwritten edits. Test collision handling against a disposable unrelated page before importing the real site.
3. Edit a paragraph, a background image/alt text and a gallery item through wp-admin; save, reload front end and confirm persistence. Test add/remove/reorder, then restore the intended content. Confirm Editor can edit Pages/Media/Studio details but cannot change launch/analytics settings or install plugins. Verify revisions and backup restore.
4. Compare every page with GitHub Pages at desktop and 390px/768px mobile widths. Verify fonts, hero crop, all artwork, navigation wrap, no horizontal overflow, and reduced-motion behavior. Confirm the custom 404 returns HTTP 404, not 200.
5. Gallery: open first/last images; previous/next wrapping; arrow keys; Escape; backdrop close; restored focus; Tab focus containment; touch swipe. Q&A disclosures expand/collapse. Check phone, Instagram and map links without sending messages or placing calls.
6. URL/SEO: seven clean page routes return 200; `/home/` resolves consistently to `/`; legacy index.html variants reach the clean routes; all `/assets/*`, favicons and llms.txt resolve; unknown routes return 404. Check root and subdirectory staging installations if the selected host uses a subdirectory.
7. Head/indexing: one title, canonical and description per page; valid social image and JSON-LD; live sitemap and robots behavior. Staging must remain noindex with analytics suppressed. After approved cutover, production must be indexable with the correct domain and without duplicate SEO-plugin tags.
8. Consent/analytics: fresh visit shows banner; Decline persists and does not load GA; Accept loads GA once only on approved production; no GA on staging regardless of saved choice. Verify using GA4 Realtime/DebugView and browser network tools.
9. Hosting: HTTPS and certificate renewal, www redirect, IPv4/IPv6, static-file rewrites, cache invalidation, upload limits, backups/restore and post-migration performance. Confirm email DNS is unaffected.

## Known scope limits

- Original homepage images painting_14/15/16.webp are the repository's upscaled client transit images. They are preserved, not represented as higher-detail originals; replace through the image picker when camera originals arrive.
- No ecommerce checkout, class registration, payment processing or contact-form backend exists in the source, so none is invented.
- Existing page layouts are protected, field-based editing interfaces. New layout sections and additional FAQ rows require template work. Work gallery entries are repeatable.
- A successful initial deployment and the manager's editing walkthrough are still needed before calling the migration complete.
