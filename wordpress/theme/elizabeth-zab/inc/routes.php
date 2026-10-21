<?php
if (!defined('ABSPATH')) { exit; }
function ez_routes() {
    $m=ez_manifest();
    foreach ($m['assets'] as $asset) { add_rewrite_rule('^'.preg_quote($asset['path'],'~').'$', 'index.php?ez_asset='.rawurlencode($asset['path']), 'top'); }
    add_rewrite_rule('^sitemap\.xml$','index.php?ez_sitemap=1','top');
}
add_action('init','ez_routes');
add_filter('query_vars',function($vars) { $vars[]='ez_asset';$vars[]='ez_sitemap';return $vars; });
add_action('after_switch_theme',function() { ez_routes();flush_rewrite_rules(); });
add_filter('redirect_canonical',function($url) { return get_query_var('ez_asset') || get_query_var('ez_sitemap') ? false : $url; });
add_filter('robots_txt',function($text,$public) {
    if (!ez_is_public()) { return "User-agent: *\nDisallow: /\n"; }
    return "User-agent: *\nAllow: /\nDisallow: /wp-admin/\nAllow: /wp-admin/admin-ajax.php\n\nSitemap: ".home_url('/sitemap.xml')."\n";
},20,2);
add_action('template_redirect',function() {
    $asset=rawurldecode((string)get_query_var('ez_asset'));
    if ($asset) {
        $m=ez_manifest(); $paths=array_column($m['assets'],'path');
        if (!in_array($asset,$paths,true)) { return; }
        $file=get_template_directory().'/assets/original/'.$asset;
        if (!is_file($file)) { status_header(404);exit; }
        $ext=strtolower(pathinfo($file,PATHINFO_EXTENSION));
        $types=array('jpg'=>'image/jpeg','webp'=>'image/webp','png'=>'image/png','ico'=>'image/x-icon','svg'=>'image/svg+xml','txt'=>'text/plain; charset=utf-8');
        status_header(200); header('Content-Type: '.($types[$ext] ?? 'application/octet-stream'));header('X-Content-Type-Options: nosniff');
        if ($ext==='txt') { header('Cache-Control: public, max-age=300');echo ez_display(file_get_contents($file)); }
        else { header('Cache-Control: public, max-age=86400');header('Content-Length: '.filesize($file));readfile($file); } exit;
    }
    if (get_query_var('ez_sitemap')) {
        status_header(200); header('Content-Type: application/xml; charset=utf-8');
        echo '<?xml version="1.0" encoding="UTF-8"?>';
        echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">';
        if (ez_is_public()) {
            foreach (get_pages(array('post_status'=>'publish')) as $page) {
                echo '<url><loc>'.esc_xml(get_permalink($page)).'</loc><lastmod>'.esc_xml(get_post_modified_time('c',true,$page)).'</lastmod>';
                $html=ez_display(ez_build_content($page->ID));
                preg_match_all('~(?:src=[\'"]|url\([\'"]?)(https?://[^\'"\s)]+\.(?:jpg|png|webp))~i',$html,$matches);
                foreach (array_unique($matches[1]) as $image) { echo '<image:image><image:loc>'.esc_xml($image).'</image:loc></image:image>'; }
                echo '</url>';
            }
        } echo '</urlset>';exit;
    }
    if (is_attachment()) { $url=wp_get_attachment_url(get_queried_object_id());if ($url) { wp_safe_redirect($url,301);exit; } }
    // Legacy index.html variants remain one-hop redirects to the unchanged clean URL.
    $path=wp_parse_url(wp_unslash($_SERVER['REQUEST_URI'] ?? ''),PHP_URL_PATH);
    $base=wp_parse_url(home_url('/'),PHP_URL_PATH) ?: '/';
    $relative=substr($path,strlen(rtrim($base,'/')));
    if ($relative==='/index.html') { wp_safe_redirect(home_url('/'),301);exit; }
    foreach (array('work','story','studio','designers','qa','classes') as $slug) {
        if ($relative==='/'.$slug.'/index.html') { wp_safe_redirect(home_url('/'.$slug.'/'),301);exit; }
    }
},0);
