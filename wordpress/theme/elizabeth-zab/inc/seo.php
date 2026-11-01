<?php
if (!defined('ABSPATH')) { exit; }
function ez_is_public() {
    $o=ez_options();
    return (int)get_option('blog_public') === 1 && $o['production_ready'] === '1' && in_array(wp_parse_url(home_url('/'),PHP_URL_HOST),array('elizabethzab.art','www.elizabethzab.art'),true);
}
function ez_seo_plugin() { return defined('WPSEO_VERSION') || defined('RANK_MATH_VERSION') || defined('AIOSEO_VERSION'); }
add_filter('pre_get_document_title', function($title) {
    if (ez_seo_plugin()) { return $title; }
    $data=ez_page_data(); if (!$data) { return $title; }
    return get_post_meta(get_queried_object_id(),'_ez_seo_title',true) ?: $data['seo_title'];
});
add_filter('wp_robots', function($robots) {
    if (!ez_is_public() || is_404() || is_search()) { $robots['noindex']=true; unset($robots['index']); }
    else { unset($robots['noindex'],$robots['nofollow']); $robots['index']=true; $robots['follow']=true; }
    return $robots;
});
add_action('send_headers',function() { if (!ez_is_public()) { header('X-Robots-Tag: noindex, nofollow',true); } });
add_action('wp',function() { if (ez_page_data() && !ez_seo_plugin()) { remove_action('wp_head','rel_canonical'); } });
function ez_schema_update($value) {
    if (!is_array($value)) { return is_string($value) ? str_replace('https://elizabethzab.art/',trailingslashit(home_url('/')),$value) : $value; }
    $o=ez_options();
    if (($value['@type'] ?? '') === 'PostalAddress') { $value=array('@type'=>'PostalAddress','streetAddress'=>$o['street'],'addressLocality'=>$o['city'],'addressRegion'=>$o['region'],'postalCode'=>$o['postal'],'addressCountry'=>'US'); }
    if (isset($value['telephone'])) { $value['telephone']=$o['telephone']; }
    if (isset($value['openingHoursSpecification'])) { $value['openingHoursSpecification']=ez_hours_schema(); }
    if (isset($value['hasMap'])) { $value['hasMap']='https://maps.google.com/?q='.rawurlencode($o['street'].' '.$o['city'].' '.$o['region'].' '.$o['postal']); }
    if (isset($value['sameAs'])) { $value['sameAs']=array($o['instagram']); }
    foreach ($value as $k=>$v) { $value[$k]=ez_schema_update($v); }
    return $value;
}
function ez_schemas($id,$data) {
    $schemas=$data['schema']; $layout=ez_layout($id);
    if ($layout==='qa') {
        $entities=array(); $content=ez_display(ez_build_content($id));
        preg_match_all('~<details\b[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>~s',$content,$matches,PREG_SET_ORDER);
        foreach ($matches as $m) { $entities[]=array('@type'=>'Question','name'=>html_entity_decode(wp_strip_all_tags($m[1]),ENT_QUOTES,'UTF-8'),'acceptedAnswer'=>array('@type'=>'Answer','text'=>html_entity_decode(trim(preg_replace('/\s+/',' ',wp_strip_all_tags($m[2]))),ENT_QUOTES,'UTF-8'))); }
        foreach ($schemas as &$schema) { if (($schema['@type'] ?? '')==='FAQPage') { $schema['mainEntity']=$entities; } } unset($schema);
    }
    if ($layout==='work') {
        $items=array(); foreach (ez_gallery($id,$data) as $i=>$r) { $items[]=array('@type'=>'ListItem','position'=>$i+1,'item'=>array('@type'=>'VisualArtwork','name'=>$r['title'],'description'=>$r['description'],'image'=>strpos($r['image'],'/')===0?home_url($r['image']):$r['image'],'artform'=>'Painting','artMedium'=>'Acrylic pour on canvas','artworkSurface'=>'Canvas','creator'=>array('@id'=>home_url('/#person'),'name'=>'Elizabeth Zab'))); }
        foreach ($schemas as &$schema) { if (isset($schema['@graph'])) { foreach ($schema['@graph'] as &$node) { if (($node['@type'] ?? '')==='CollectionPage') { $node['mainEntity']=array('@type'=>'ItemList','numberOfItems'=>count($items),'itemListElement'=>$items); } } unset($node); } } unset($schema);
    }
    return ez_schema_update($schemas);
}
add_action('wp_head',function() {
    $data=ez_page_data(); if (!$data || ez_seo_plugin()) { return; }
    $id=get_queried_object_id(); $meta=$data['meta'];
    $title=get_post_meta($id,'_ez_seo_title',true) ?: $data['seo_title'];
    $desc=get_post_meta($id,'_ez_description',true) ?: ($meta['description'] ?? '');
    $image=get_post_meta($id,'_ez_social_image',true) ?: ($meta['og:image'] ?? '');
    if (strpos($image,'/')===0) { $image=home_url($image); }
    $image=str_replace('https://elizabethzab.art/',trailingslashit(home_url('/')),$image);
    $canonical=is_404()?'':get_permalink($id);
    if ($canonical) { echo '<link rel="canonical" href="'.esc_url($canonical).'">' . "\n"; }
    $meta['description']=$desc;
    foreach (array('og:title','twitter:title') as $key) { $meta[$key]=$title; }
    foreach (array('og:description','twitter:description') as $key) { $meta[$key]=$desc; }
    foreach (array('og:image','twitter:image') as $key) { if ($image) { $meta[$key]=$image; } }
    if ($canonical) { $meta['og:url']=$canonical; } else { unset($meta['og:url']); }
    if (get_post_meta($id,'_ez_social_image',true)) { unset($meta['og:image:width'],$meta['og:image:height']); }
    foreach ($meta as $key=>$value) {
        if (in_array($key,array('viewport','robots','googlebot','theme-color'),true)) { continue; }
        echo '<meta '.(strpos($key,'og:')===0?'property':'name').'="'.esc_attr($key).'" content="'.esc_attr($value).'">' . "\n";
    }
    foreach (ez_schemas($id,$data) as $schema) { echo '<script type="application/ld+json">'.wp_json_encode($schema, JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT|JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE).'</script>' . "\n"; }
    if ($image && is_front_page()) { echo '<link rel="preload" as="image" href="'.esc_url($image).'" fetchpriority="high">'; }
},5);
