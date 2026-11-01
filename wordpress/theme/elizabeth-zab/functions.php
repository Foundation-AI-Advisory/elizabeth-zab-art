<?php
/** Elizabeth Zab Art. Content lives in WordPress pages and page metadata. */
if (!defined('ABSPATH')) { exit; }
define('EZ_VERSION', '1.0.0');
function ez_manifest() {
    static $data;
    if ($data === null) { $data = json_decode(file_get_contents(__DIR__ . '/inc/data/manifest.json'), true); }
    return $data;
}
function ez_layout($id = 0) {
    if (!$id && is_404()) { return '404'; }
    return get_post_meta($id ?: get_queried_object_id(), '_ez_layout', true);
}
function ez_page_data($id = 0) { $all = ez_manifest(); return $all['pages'][ez_layout($id)] ?? null; }
function ez_json_meta($id, $key, $default = array()) {
    $value = json_decode(get_post_meta($id, $key, true), true);
    return is_array($value) ? $value : $default;
}
function ez_values($id, $data) {
    return array_merge(array_map(function($v) { return $v['default']; }, $data['fields']), ez_json_meta($id, '_ez_fields_json'));
}
function ez_gallery($id, $data) { return ez_json_meta($id, '_ez_gallery_json', $data['gallery']); }
function ez_inline_allowed() {
    return array('a'=>array('href'=>true,'title'=>true,'target'=>true,'rel'=>true,'class'=>true), 'span'=>array('class'=>true), 'strong'=>array(), 'em'=>array(), 'b'=>array(), 'i'=>array(), 'br'=>array());
}
function ez_field_clean($value, $type) {
    if (!is_scalar($value)) { return ''; }
    if ($type === 'rich') { return wp_kses((string)$value, ez_inline_allowed()); }
    if (in_array($type, array('url','image'), true)) { return esc_url_raw((string)$value); }
    return sanitize_text_field((string)$value);
}
function ez_field_html($value, $type) {
    if ($type === 'rich') { return wp_kses($value, ez_inline_allowed()); }
    if ($type === 'image') { return esc_url(str_replace(array("'",'(',')'),array('%27','%28','%29'),$value)); }
    if ($type === 'url') { return esc_url($value); }
    return $type === 'attribute' ? esc_attr($value) : esc_html($value);
}
function ez_gallery_html($rows) {
    ob_start();
    foreach ($rows as $i=>$row) {
        $num = sprintf('%02d', $i + 1); ?>
    <article class="plate reveal">
      <figure class="plate-media">
        <span class="plate-index" aria-hidden="true"><?php echo esc_html($num); ?></span>
        <button type="button" class="plate-open js-open" data-idx="<?php echo (int)$i; ?>" aria-label="<?php echo esc_attr('Open full view: ' . $row['title']); ?>">
          <img src="<?php echo esc_url($row['image']); ?>" width="<?php echo absint($row['width']) ?: 1000; ?>" height="<?php echo absint($row['height']) ?: 1000; ?>" loading="<?php echo $i ? 'lazy' : 'eager'; ?>" <?php if (!$i) { echo 'fetchpriority="high"'; } ?> decoding="async" alt="<?php echo esc_attr($row['alt']); ?>">
        </button>
      </figure>
      <div class="plate-text">
        <span class="plate-no">No. <?php echo esc_html($num); ?></span>
        <h2 class="plate-title"><?php echo esc_html($row['title']); ?></h2>
        <p class="plate-meta"><?php echo esc_html($row['medium']); ?></p>
        <p class="plate-note"><?php echo esc_html($row['description']); ?></p>
        <button type="button" class="plate-cue js-open" data-idx="<?php echo (int)$i; ?>">View full piece <span class="ar" aria-hidden="true">→</span></button>
      </div>
    </article>
    <?php }
    return ob_get_clean();
}
function ez_build_content($id, $values = null, $gallery = null) {
    $data = ez_page_data($id); if (!$data) { return get_post_field('post_content', $id); }
    $layout = ez_layout($id);
    $template = file_get_contents(__DIR__ . '/inc/data/' . $layout . '.html');
    $values = $values ?? ez_values($id, $data);
    $template = str_replace('{{ez:gallery}}', ez_gallery_html($gallery ?? ez_gallery($id, $data)), $template);
    $map = array();
    foreach ($data['fields'] as $key=>$field) { $map['{{ez:' . $key . '}}'] = ez_field_html($values[$key] ?? $field['default'], $field['type']); }
    return strtr($template, $map);
}
function ez_options() {
    return array_merge(array('phone'=>'(440) 477-1972','telephone'=>'+14404771972','instagram'=>'https://www.instagram.com/elizabethzabartllc?igsh=MXY0MHR5dWs1bWlk','street'=>'3987 Medina Rd, Studio 3','city'=>'Akron','region'=>'OH','postal'=>'44333','location'=>'Inside Salon Lofts','footer_tagline'=>'Pour paintings, made in Akron, seen at the studio.','ga_id'=>'G-F039HJSL10','analytics'=>'1','production_ready'=>'0','wed_open'=>'15:00','wed_close'=>'19:00','thu_open'=>'12:00','thu_close'=>'16:00','fri_open'=>'11:00','fri_close'=>'14:00','sat_open'=>'10:00','sat_close'=>'14:00'), get_option('ez_site_details', array()));
}
function ez_hours_schema() {
    $o=ez_options(); $out=array();
    foreach (array('sun'=>'Sunday','mon'=>'Monday','tue'=>'Tuesday','wed'=>'Wednesday','thu'=>'Thursday','fri'=>'Friday','sat'=>'Saturday') as $k=>$day) {
        if (!empty($o[$k.'_open']) && !empty($o[$k.'_close'])) { $out[]=array('@type'=>'OpeningHoursSpecification','dayOfWeek'=>$day,'opens'=>$o[$k.'_open'],'closes'=>$o[$k.'_close']); }
    } return $out;
}
function ez_hours_html() {
    $open=array(); $closed=array(); $o=ez_options();
    foreach (array('wed'=>'Wed','thu'=>'Thu','fri'=>'Fri','sat'=>'Sat','sun'=>'Sun','mon'=>'Mon','tue'=>'Tue') as $k=>$label) {
        if (!empty($o[$k.'_open']) && !empty($o[$k.'_close'])) {
            $fmt=function($t) { $p=explode(':',$t); return ((int)$p[0]%12 ?: 12) . ($p[1]==='00' ? '' : ':'.$p[1]); };
            $open[]=$label.' '.$fmt($o[$k.'_open']).'–'.$fmt($o[$k.'_close']);
        } else { $closed[]=$label; }
    }
    $tail=''; if ($closed) { $last=array_pop($closed); $tail='Closed '.($closed ? implode(', ', $closed).' & ' : '').$last; }
    return esc_html(implode(' · ', $open)) . ($tail ? '<br>'.esc_html($tail) : '');
}
function ez_global_html($html) {
    $o=ez_options();
    $from=array('Wed 3–7 · Thu 12–4 · Fri 11–2 · Sat 10–2<br>Closed Sun, Mon &amp; Tue','(440) 477-1972','tel:+14404771972','3987 Medina Rd, Studio 3','Akron, OH 44333','Inside Salon Lofts','Pour paintings, made in Akron, seen at the studio.','https://www.instagram.com/elizabethzabartllc?igsh=MXY0MHR5dWs1bWlk','https://maps.google.com/?q=3987+Medina+Rd+Akron+OH+44333');
    $to=array(ez_hours_html(),esc_html($o['phone']),esc_attr('tel:'.$o['telephone']),esc_html($o['street']),esc_html($o['city'].', '.$o['region'].' '.$o['postal']),esc_html($o['location']),esc_html($o['footer_tagline']),esc_url($o['instagram']),esc_url('https://maps.google.com/?q='.rawurlencode($o['street'].' '.$o['city'].' '.$o['region'].' '.$o['postal'])));
    return str_replace($from,$to,$html);
}
function ez_local_urls($html) {
    // Root-relative references work on staging domains and WordPress subdirectories.
    $html = str_replace('https://elizabethzab.art/', trailingslashit(home_url('/')), $html);
    $html = preg_replace_callback('~\b(href|src)=([\'"])(/[^/][^\'"]*|/)\2~', function($m) { return $m[1].'='.$m[2].esc_url(home_url($m[3])).$m[2]; }, $html);
    return preg_replace_callback('~url\(([\'"]?)(/assets/[^)\'"\s]+)\1\)~', function($m) { return 'url('.$m[1].esc_url(home_url($m[2])).$m[1].')'; }, $html);
}
function ez_display($html) { return ez_local_urls(ez_global_html($html)); }
add_action('after_setup_theme', function() {
    add_theme_support('title-tag'); add_theme_support('post-thumbnails'); add_theme_support('html5', array('style','script','gallery','caption'));
    register_nav_menus(array('primary'=>'Primary navigation','footer'=>'Footer navigation'));
});
add_action('wp_enqueue_scripts', function() {
    $layout=ez_layout() ?: 'story';
    wp_enqueue_style('ez-font','https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500&display=swap',array(),null);
    wp_enqueue_style('ez-page',get_template_directory_uri().'/assets/css/'.$layout.'.css',array('ez-font'),EZ_VERSION);
    wp_enqueue_style('ez-access',get_template_directory_uri().'/assets/css/wordpress.css',array('ez-page'),EZ_VERSION);
    wp_enqueue_script('ez-page',get_template_directory_uri().'/assets/js/'.$layout.'.js',array(),EZ_VERSION,true);
    if ($layout !== '404') {
        wp_enqueue_script('ez-site',get_template_directory_uri().'/assets/js/site.js',array(),EZ_VERSION,true);
        $o=ez_options(); $host=wp_parse_url(home_url('/'),PHP_URL_HOST);
        $ga=($o['analytics']==='1' && $o['production_ready']==='1' && (int)get_option('blog_public')===1 && in_array($host,array('elizabethzab.art','www.elizabethzab.art'),true)) ? $o['ga_id'] : '';
        wp_add_inline_script('ez-site','window.ezAnalyticsId='.wp_json_encode($ga).';','before');
    }
});
function ez_nav($location) {
    $items=array();$loc=get_nav_menu_locations();
    if (!empty($loc[$location])) { $items=wp_get_nav_menu_items($loc[$location]); }
    if (!$items) {
        $slugs=$location==='primary'?array('work','story','classes','designers','qa','studio'):array('work','story','classes','studio','designers','qa');
        foreach ($slugs as $slug) { $p=get_page_by_path($slug); if (!$p || $p->post_status!=='publish') { continue; } $items[]=(object)array('url'=>get_permalink($p),'title'=>$slug==='studio'&&$location==='primary'?'Visit the studio':$p->post_title,'object_id'=>$p->ID,'classes'=>array()); }
    }
    foreach ($items as $item) {
        $slug=get_post_field('post_name',$item->object_id); $classes=$item->classes ?: array();
        if ($location==='primary' && $slug==='qa') { $classes[]='hide-sm'; }
        if ($location==='primary' && $slug==='studio') { $classes[]='visit-cta'; }
        echo '<a href="'.esc_url($item->url).'" class="'.esc_attr(implode(' ',$classes)).'"'.((int)$item->object_id===get_queried_object_id()?' aria-current="page"':'').'>'.esc_html($item->title).'</a>';
    }
}
require_once __DIR__.'/inc/seo.php';
require_once __DIR__.'/inc/routes.php';
if (is_admin()) { require_once __DIR__.'/inc/admin.php'; }
