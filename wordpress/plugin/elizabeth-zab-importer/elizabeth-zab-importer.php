<?php
/**
 * Plugin Name: Elizabeth Zab Migration Importer
 * Description: Imports the bundled artwork and seven editable pages without replacing existing content.
 * Version: 1.0.0
 * Requires at least: 6.5
 * Requires PHP: 8.1
 */
if (!defined('ABSPATH')) { exit; }
function ez_import_run() {
    if (!current_user_can('manage_options')) { return new WP_Error('permission','Administrator access is required.'); }
    if (!function_exists('ez_manifest') || get_template()!=='elizabeth-zab') { return new WP_Error('theme','Activate the Elizabeth Zab Art theme first.'); }
    $m=ez_manifest();$ids=array();$created=array();
    // Validate ALL collisions and source bytes before any mutation.
    foreach ($m['pages'] as $slug=>$page) {
        if ($slug==='404') { continue; }
        $existing=get_page_by_path($slug);
        if ($existing && get_post_meta($existing->ID,'_ez_import_commit',true)!==$m['source_commit']) { return new WP_Error('collision','Existing page slug “'.$slug.'” is not from this package. Import stopped without replacing content. Use an empty staging install.'); }
        if ($existing) { $ids[$slug]=$existing->ID; }
    }
    foreach ($m['assets'] as $asset) {
        $file=get_template_directory().'/assets/original/'.$asset['path'];
        if (!is_readable($file) || hash_file('sha256',$file)!==$asset['sha256']) { return new WP_Error('asset','Missing or changed bundled asset: '.$asset['path']); }
    }
    // Uploaded attachments give the owner a normal Media Library. Old URLs remain served by the theme.
    require_once ABSPATH.'wp-admin/includes/file.php';require_once ABSPATH.'wp-admin/includes/image.php';
    $media_count=0;
    foreach ($m['assets'] as $asset) {
        if (strpos($asset['path'],'assets/')!==0) { continue; }
        $found=get_posts(array('post_type'=>'attachment','post_status'=>'inherit','numberposts'=>1,'meta_key'=>'_ez_source_path','meta_value'=>$asset['path'],'fields'=>'ids'));
        if ($found) { continue; }
        $file=get_template_directory().'/assets/original/'.$asset['path'];
        $upload=wp_upload_bits(basename($file),null,file_get_contents($file));
        if ($upload['error']) { return new WP_Error('upload',$upload['error']); }
        $type=wp_check_filetype($upload['file']);
        $attachment=wp_insert_attachment(array('post_title'=>pathinfo($file,PATHINFO_FILENAME),'post_mime_type'=>$type['type'],'post_status'=>'inherit'),$upload['file'],0,true);
        if (is_wp_error($attachment)) { return $attachment; }
        update_post_meta($attachment,'_ez_source_path',$asset['path']);
        $metadata=wp_generate_attachment_metadata($attachment,$upload['file']);if (is_array($metadata)) { wp_update_attachment_metadata($attachment,$metadata); }
        foreach ($m['pages']['work']['gallery'] as $row) { if ($row['image']==='/'.$asset['path']) { update_post_meta($attachment,'_wp_attachment_image_alt',$row['alt']);wp_update_post(array('ID'=>$attachment,'post_title'=>$row['title'],'post_excerpt'=>$row['description']));break; } }
        $media_count++;
    }
    foreach ($m['pages'] as $slug=>$page) {
        if ($slug==='404' || isset($ids[$slug])) { continue; }
        $id=wp_insert_post(wp_slash(array('post_type'=>'page','post_status'=>'publish','post_title'=>$page['title'],'post_name'=>$slug,'post_content'=>'','comment_status'=>'closed','ping_status'=>'closed')),true);
        if (is_wp_error($id)) { return $id; }
        $ids[$slug]=$id;$created[]=$slug;
        update_post_meta($id,'_ez_layout',$slug);update_post_meta($id,'_wp_page_template','page-templates/migrated.php');
        update_post_meta($id,'_ez_fields_json',wp_slash(wp_json_encode(array_map(function($v) { return $v['default']; },$page['fields']),JSON_UNESCAPED_UNICODE)));
        update_post_meta($id,'_ez_gallery_json',wp_slash(wp_json_encode($page['gallery'],JSON_UNESCAPED_UNICODE)));
        update_post_meta($id,'_ez_seo_title',$page['seo_title']);update_post_meta($id,'_ez_description',$page['meta']['description']??'');
        $saved=wp_update_post(wp_slash(array('ID'=>$id,'post_content'=>ez_build_content($id))),true);
        if (is_wp_error($saved)) { return $saved; }
        update_post_meta($id,'_ez_import_commit',$m['source_commit']);
    }
    if (!get_option('ez_migration_initialized')) {
        update_option('show_on_front','page');update_option('page_on_front',$ids['home']);update_option('permalink_structure','/%postname%/');
        update_option('blogname','Elizabeth Zab Art');update_option('blogdescription','Original acrylic pour paintings in Akron, Ohio');update_option('blog_public',0);
        $loc=get_theme_mod('nav_menu_locations',array());
        foreach (array('primary'=>array('work','story','classes','designers','qa','studio'),'footer'=>array('work','story','classes','studio','designers','qa')) as $location=>$slugs) {
            if (!empty($loc[$location])) { continue; }
            $name='Elizabeth Zab '.ucfirst($location);$existing=wp_get_nav_menu_object($name);
            if ($existing) { $loc[$location]=$existing->term_id;continue; }
            $menu=wp_create_nav_menu($name);if (is_wp_error($menu)) { return $menu; }
            foreach ($slugs as $position=>$slug) { $item=wp_update_nav_menu_item($menu,0,array('menu-item-title'=>$location==='primary'&&$slug==='studio'?'Visit the studio':$m['pages'][$slug]['title'],'menu-item-object'=>'page','menu-item-object-id'=>$ids[$slug],'menu-item-type'=>'post_type','menu-item-status'=>'publish','menu-item-position'=>$position+1));if (is_wp_error($item)) { return $item; } }
            $loc[$location]=$menu;
        }
        set_theme_mod('nav_menu_locations',$loc);update_option('ez_migration_initialized',$m['source_commit']);
    }
    ez_routes();flush_rewrite_rules();
    return array('pages_created'=>$created,'pages_total'=>count($ids),'media_imported'=>$media_count,'source_commit'=>$m['source_commit']);
}
add_action('admin_menu',function() { add_management_page('Elizabeth Zab migration','Elizabeth Zab migration','manage_options','ez-migration','ez_import_screen'); });
function ez_import_screen() {
    if (!current_user_can('manage_options')) { return; }
    echo '<div class="wrap"><h1>Elizabeth Zab migration</h1><p>Use a backed-up, empty staging WordPress installation with the Elizabeth Zab Art theme active. This imports seven pages, bundled artwork and menus; sets the static homepage and clean permalinks; and discourages indexing. It does not change DNS, send invitations or enable production indexing.</p>';
    if (isset($_POST['ez_import_nonce'])) {
        check_admin_referer('ez_import','ez_import_nonce');$result=ez_import_run();
        if (is_wp_error($result)) { echo '<div class="notice notice-error"><p>'.esc_html($result->get_error_message()).'</p><p>If an upload failed, fix it and rerun. Previously imported pages and media are retained.</p></div>'; }
        else { echo '<div class="notice notice-success"><p>Imported '.esc_html(count($result['pages_created'])).' new pages and '.esc_html($result['media_imported']).' media items. Total migration pages: '.esc_html($result['pages_total']).'.</p></div>'; }
    }
    echo '<form method="post">';wp_nonce_field('ez_import','ez_import_nonce');submit_button('Import into staging');echo '</form><p>After verification, deactivate this importer. The theme supplies editing controls, legacy URLs, analytics and SEO.</p></div>';
}
if (defined('WP_CLI') && WP_CLI) {
    WP_CLI::add_command('ez migrate',function() { $r=ez_import_run();if (is_wp_error($r)) { WP_CLI::error($r->get_error_message()); }WP_CLI::success(wp_json_encode($r)); });
}
