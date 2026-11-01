# Deployment and handoff

## 1. Stage the replacement — owner: Ben

Objective: verify an editable replacement before moving public traffic. Next action: identify the existing WordPress host/staging URL, or provision one after a hosting decision. Start installation once access is available; allow 1–2 working days for host-specific testing and corrections, subject to findings. Benefit: preserve visitor access and reduce SEO disruption.

1. Use a backed-up, empty WordPress staging installation. Recommended platform baseline from WordPress: PHP 8.3+, MariaDB 10.11+ or MySQL 8.0+, HTTPS, and Apache/Nginx permalink support. Set an upload limit above 10 MB and sufficient image-processing memory (256 MB is a practical target). Use the host's password protection in addition to noindex; robots directives are not access controls.
2. Appearance → Themes → Add New → Upload: install and activate `elizabeth-zab-theme.zip`.
3. Plugins → Add New → Upload: install and activate `elizabeth-zab-importer.zip`.
4. Tools → Elizabeth Zab migration → Import into staging. This changes WordPress homepage/permalink settings and sets “Discourage search engines.” It does not touch DNS. A collision with an unrelated page slug stops import. Successful imported pages/media are retained on reruns; review partial errors before retrying.
5. Confirm seven pages, 20 original artwork media items and both navigation menus. Remove the host's sample page/post only after confirming they are disposable.
6. Settings → Permalinks → Save Changes. Confirm each clean URL resolves. If old `/assets/` or icon paths return 404 because the host intercepts static extensions, copy `elizabeth-zab-root-assets.zip` contents to the WordPress web root through the host's file manager/SFTP, without overwriting different existing files. Otherwise allow unknown static paths to reach WordPress. The root-assets archive contains exact originals. Keep it unchanged unless intentionally replacing the legacy image.
7. Leave Studio details → “Cutover approved and production verified” unchecked. GA is suppressed on staging. No SEO plugin is required. If adding Yoast, Rank Math or AIOSEO, migrate metadata into that plugin and retest; the theme suppresses its SEO output for those plugins to avoid duplicate tags.
8. Complete every test in VALIDATION.md. Deactivate the importer after a successful import and record a restorable database/files backup.

Alternative WXR route: activate the theme, use Tools → Import → WordPress to import `elizabeth-zab-pages.xml`, assign content to an existing account, then run the bundled importer to import local images and initialize menus/settings. Matching package pages are retained. Without the importer, manually set Home as the front page, clean permalinks and both menus; WXR does not create the Media Library or shared settings.

Optional WP-CLI: after installing/activating both packages, run `wp --user=<existing-administrator-login> ez migrate`. The importer requires an actual administrator context. Run only against the intended staging install.

## 2. GoDaddy cutover — owner: Ben; approval required

Objective: move web traffic without disrupting email or losing a rollback path. Next action: review tested staging with Elizabeth and approve the exact DNS change. Execute only after the validation gate passes, in an agreed low-traffic window. Benefit: controlled transition with the existing search URLs preserved.

1. Export/screenshot the actual current GoDaddy DNS zone immediately before cutover. Record A, AAAA, CNAME, MX, TXT, CAA and TTL values. The repository verifies GoDaddy → GitHub Pages but is not an authoritative current zone export. No replacement IP or record value is supplied in this package because the target host is not known.
2. Confirm target hostname, required web DNS records, www behavior and an SSL certificate plan with the WordPress host. Prefer certificate provisioning through DNS validation or a host-supported pre-cutover domain preview. Do not bypass certificate warnings. Test the production hostname against the new origin before switching if the host supports it.
3. Preserve nameservers, MX records, email verification records, SPF, DKIM, DMARC and unrelated TXT/CNAME records. Change only the web-routing records the selected host requires. Check old AAAA records so IPv6 visitors do not continue reaching the old origin. Do not transfer the domain or change nameservers merely to migrate the site.
4. If useful, lower only affected web-record TTLs at least one existing TTL interval before the approved cutover. Keep GitHub Pages and its CNAME binding active during propagation and rollback coverage.
5. Freeze content edits for the final copy. Back up staging and update WordPress home/site URLs to `https://elizabethzab.art`. Use a serialized-data-aware WordPress/host migration method, not raw SQL string replacement. Replace staging URLs in media and menus; inspect the result. Configure www to redirect to the apex domain and HTTPS.
6. After explicit approval, change the agreed GoDaddy web records to the host-provided values. Do not invent IPs or apply generic GitHub/GoDaddy values.
7. Verify HTTPS, both IPv4/IPv6 paths, every page and representative images on the public domain. In WordPress, uncheck “Discourage search engines,” then check Studio details → “Cutover approved and production verified.” Verify no noindex meta or X-Robots-Tag remains on public content, robots allows crawling, the sitemap contains all seven intended URLs, and canonicals use the production HTTPS domain.
8. Accept cookies in a test browser and verify the original GA4 property receives the visit; verify Decline does not load GA. Confirm phone/Instagram/directions, gallery and Q&A.
9. Submit the existing `/sitemap.xml` in Search Console if the owner has access. This is the same domain and same page paths: do not use a Change of Address request. Monitor 404s, indexing, analytics and performance for 7–14 days.

## 3. Rollback — owner: Ben

If the new origin fails materially, restore the exact saved web DNS records. Keep the GitHub Pages site and domain binding available until the new site has been stable through the monitoring period. DNS rollback is subject to cached TTLs; zero downtime cannot be guaranteed. Restore WordPress files/database if the failure is within WordPress, preserving any edits made since the backup. Do not delete the original repository as part of migration.

## 4. Website manager access — owner: Ben; recipient and scope unconfirmed

Objective: give the manager enough access for her actual responsibilities while Ben retains ownership and recovery. Next action: confirm the person's name/email and whether she handles content only or hosting/updates/backups too. Establish named accounts before handoff and verify access together. Benefit: maintainability without shared passwords or unnecessary purchasing/transfer authority.

| Confirmed responsibilities | WordPress account | GoDaddy access |
|---|---|---|
| Content, artwork, classes and hours | Editor; theme Studio details supports edit_pages | No domain rights needed for WordPress content. If GoDaddy connection is desired without current access, Accounts Connection Only |
| Theme/plugin updates, backups and full website management | Administrator, own named login | Products & Domains only if she must manage GoDaddy hosting; this level is broader than content access |
| DNS management without hosting/product administration | WordPress role based on the content/technical scope above | Domains Only; folder restricted to elizabethzab.art, Management Access on, Transfer Access off |

Do not grant Products, Domains & Purchase by default. Keep domain ownership, billing and recovery with the account owner. Use GoDaddy Delegate Access with her own login rather than sharing Ben's password. Confirm whether product-level delegation would expose unrelated account products before choosing Products & Domains. Prefer an isolated account/product arrangement if the provider cannot scope access adequately.

No invitation or account has been sent/created. After identity and scope are confirmed, create the WordPress named account, send the approved GoDaddy invitation, require/enable available MFA, and test her page editing, image upload and any agreed maintenance responsibilities. Retain a separate owner administrator; document backup ownership, renewals and escalation.

## Provider references checked October 21, 2026

- https://wordpress.org/about/requirements/
- https://wordpress.org/documentation/article/roles-and-capabilities/
- https://developer.wordpress.org/themes/
- https://www.godaddy.com/en-ca/help/delegate-access-levels-of-permission-12374
- https://www.godaddy.com/en-ca/help/what-is-delegate-access-12378
