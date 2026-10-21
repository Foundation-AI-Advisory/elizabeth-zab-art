<?php
if (!defined('ABSPATH')) { exit; }
add_filter('use_block_editor_for_post',function($use,$post) { return get_post_meta($post->ID,'_ez_layout',true) ? false : $use; },10,2);
add_action('add_meta_boxes_page',function($post) {
    if (!ez_page_data($post->ID)) { return; }
    remove_post_type_support('page','editor');
    add_meta_box('ez-content','Page copy and artwork','ez_content_box','page','normal','high');
    add_meta_box('ez-seo','Search and social preview','ez_seo_box','page','normal');
});
function ez_input($name,$value,$type,$label,$id='') {
    $id=$id ?: 'ez-'.substr(md5($name),0,12);
    echo '<div class="ez-field"><label for="'.esc_attr($id).'"><strong>'.esc_html($label).'</strong></label>';
    if ($type==='rich') {
        wp_editor($value,$id,array('textarea_name'=>$name,'textarea_rows'=>3,'media_buttons'=>false,'teeny'=>true,'wpautop'=>false,'quicktags'=>false,'tinymce'=>array('toolbar1'=>'bold italic link unlink undo redo','toolbar2'=>'','forced_root_block'=>false)));
    } elseif ($type==='long') {
        echo '<textarea rows="4" class="widefat" id="'.esc_attr($id).'" name="'.esc_attr($name).'">'.esc_textarea($value).'</textarea>';
    } else {
        echo '<input class="widefat" id="'.esc_attr($id).'" type="'.($type==='time'?'time':'text').'" name="'.esc_attr($name).'" value="'.esc_attr($value).'">';
        if ($type==='image') { echo '<button type="button" class="button ez-media" data-target="'.esc_attr($id).'">Choose from Media Library</button>'; }
    }
    echo '</div>';
}
function ez_content_box($post) {
    wp_nonce_field('ez_save_page','ez_page_nonce');
    $data=ez_page_data($post->ID);$values=ez_values($post->ID,$data);
    echo '<p>Edit text and artwork below, then click Update. Layout and mobile styling remain intact. Shared phone, address and hours are under <a href="'.esc_url(admin_url('admin.php?page=ez-details')).'">Studio details</a>. Page revisions contain the rendered content.</p>';
    foreach ($data['fields'] as $key=>$field) { ez_input('ez_fields['.$key.']',$values[$key],$field['type'],$field['label'],'ezfield'.$key); }
    if (ez_layout($post->ID)==='work') {
        echo '<h2>Gallery pieces</h2><p>Add, remove or reorder entries. Titles, descriptions and images also update the artwork viewer and structured data.</p><div id="ez-gallery">';
        foreach (ez_gallery($post->ID,$data) as $i=>$row) { ez_gallery_editor_row($i,$row); }
        echo '</div><button type="button" class="button" id="ez-add-piece">Add artwork</button><template id="ez-piece-template">';
        ez_gallery_editor_row('__INDEX__',array_fill_keys(array('title','medium','description','image','alt','width','height'),''));echo '</template>';
    }
}
function ez_gallery_editor_row($i,$row) {
    echo '<fieldset class="ez-piece"><legend><strong>Artwork</strong></legend>';
    foreach (array('title'=>'Title','image'=>'Image','alt'=>'Image description (accessibility)','medium'=>'Medium and dimensions','description'=>'Description','width'=>'Image width in pixels','height'=>'Image height in pixels') as $key=>$label) {
        ez_input('ez_gallery['.$i.']['.$key.']',$row[$key] ?? '',$key==='image'?'image':($key==='description'?'long':'text'),$label,'ezpiece'.$i.$key);
    }
    echo '<p><button type="button" class="button ez-up">Move up</button> <button type="button" class="button ez-down">Move down</button> <button type="button" class="button ez-remove">Remove artwork</button></p></fieldset>';
}
function ez_seo_box($post) {
    $data=ez_page_data($post->ID);
    ez_input('ez_seo_title',get_post_meta($post->ID,'_ez_seo_title',true) ?: $data['seo_title'],'text','Search title');
    ez_input('ez_description',get_post_meta($post->ID,'_ez_description',true) ?: ($data['meta']['description'] ?? ''),'long','Description');
    ez_input('ez_social_image',get_post_meta($post->ID,'_ez_social_image',true) ?: ($data['meta']['og:image'] ?? ''),'image','Social preview image');
    echo '<p>The canonical URL follows this page’s permalink. Keep the existing slug. If an SEO plugin is activated, move these fields into it before launch; the theme suppresses its own SEO output to avoid duplicates.</p>';
}
function ez_save_page($id) {
    if (empty($_POST['ez_page_nonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['ez_page_nonce'])),'ez_save_page') || !current_user_can('edit_post',$id) || wp_is_post_revision($id) || (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE)) { return; }
    $data=ez_page_data($id);if (!$data) { return; }
    $values=ez_values($id,$data);$raw=isset($_POST['ez_fields']) && is_array($_POST['ez_fields'])?wp_unslash($_POST['ez_fields']):array();
    foreach ($data['fields'] as $key=>$field) { if (array_key_exists($key,$raw)) { $values[$key]=ez_field_clean($raw[$key],$field['type']); } }
    update_post_meta($id,'_ez_fields_json',wp_slash(wp_json_encode($values,JSON_UNESCAPED_UNICODE)));
    if (ez_layout($id)==='work') {
        $gallery=array();$rows=isset($_POST['ez_gallery']) && is_array($_POST['ez_gallery'])?wp_unslash($_POST['ez_gallery']):array();
        foreach (array_slice($rows,0,100) as $row) {
            if (!is_array($row) || empty($row['title']) || empty($row['image'])) { continue; }
            $clean=array();foreach (array('title','image','alt','medium','description','width','height') as $key) { $v=$row[$key]??''; $clean[$key]=in_array($key,array('width','height'),true)?absint($v):($key==='image'?esc_url_raw($v):sanitize_textarea_field($v)); }
            $gallery[]=$clean;
        }
        update_post_meta($id,'_ez_gallery_json',wp_slash(wp_json_encode($gallery,JSON_UNESCAPED_UNICODE)));
    }
    foreach (array('ez_seo_title','ez_description','ez_social_image') as $name) {
        if (isset($_POST[$name]) && is_scalar($_POST[$name])) { $v=wp_unslash($_POST[$name]);update_post_meta($id,'_'.$name,$name==='ez_social_image'?esc_url_raw($v):sanitize_textarea_field($v)); }
    }
    // A complete HTML copy remains portable through WordPress export and theme changes.
    remove_action('save_post_page','ez_save_page');
    wp_update_post(wp_slash(array('ID'=>$id,'post_content'=>ez_build_content($id))));
    add_action('save_post_page','ez_save_page');
}
add_action('save_post_page','ez_save_page');
add_action('init',function() {
    foreach (array('_ez_fields_json','_ez_gallery_json','_ez_seo_title','_ez_description','_ez_social_image') as $key) {
        register_post_meta('page',$key,array('type'=>'string','single'=>true,'show_in_rest'=>false,'revisions_enabled'=>true,'auth_callback'=>function($allowed,$key,$id) { return current_user_can('edit_post',$id); }));
    }
});
add_action('admin_menu',function() { add_menu_page('Studio details','Studio details','edit_pages','ez-details','ez_details_screen','dashicons-art',21); });
function ez_details_screen() {
    if (!current_user_can('edit_pages')) { return; }
    $o=ez_options();
    if (isset($_POST['ez_details_nonce'])) {
        check_admin_referer('ez_details','ez_details_nonce');
        $raw=isset($_POST['ez_details']) && is_array($_POST['ez_details'])?wp_unslash($_POST['ez_details']):array();
        foreach (array('phone','telephone','instagram','street','city','region','postal','location','footer_tagline') as $key) { if (isset($raw[$key]) && is_scalar($raw[$key])) { $o[$key]=$key==='instagram'?esc_url_raw($raw[$key]):sanitize_text_field($raw[$key]); } }
        foreach (array('sun','mon','tue','wed','thu','fri','sat') as $day) { foreach (array('open','close') as $part) { $key=$day.'_'.$part;$v=$raw[$key]??'';$o[$key]=is_string($v)&&preg_match('/^(?:[01][0-9]|2[0-3]):[0-5][0-9]$/',$v)?$v:''; } }
        if (current_user_can('manage_options')) {
            $o['ga_id']=isset($raw['ga_id'])&&is_string($raw['ga_id'])&&preg_match('/^G-[A-Z0-9]+$/',$raw['ga_id'])?$raw['ga_id']:$o['ga_id'];
            $o['analytics']=!empty($raw['analytics'])?'1':'0';$o['production_ready']=!empty($raw['production_ready'])?'1':'0';
        }
        update_option('ez_site_details',$o);echo '<div class="notice notice-success"><p>Studio details saved.</p></div>';
    }
    echo '<div class="wrap"><h1>Studio details</h1><p>Shared contact information and studio hours update across the site and its structured data.</p><form method="post">';wp_nonce_field('ez_details','ez_details_nonce');
    foreach (array('phone'=>'Phone displayed','telephone'=>'Phone link (international format, e.g. +14404771972)','instagram'=>'Instagram URL','street'=>'Street and studio number','city'=>'City','region'=>'State','postal'=>'ZIP code','location'=>'Studio location','footer_tagline'=>'Footer introduction') as $key=>$label) { ez_input('ez_details['.$key.']',$o[$key],'text',$label); }
    echo '<h2>Studio hours</h2><p>Use 24-hour times. Leave both times blank for closed days.</p>';
    foreach (array('sun'=>'Sunday','mon'=>'Monday','tue'=>'Tuesday','wed'=>'Wednesday','thu'=>'Thursday','fri'=>'Friday','sat'=>'Saturday') as $day=>$label) { echo '<div class="ez-hours">';foreach (array('open'=>'opens','close'=>'closes') as $part=>$word) { ez_input('ez_details['.$day.'_'.$part.']',$o[$day.'_'.$part]??'','time',$label.' '.$word); }echo '</div>'; }
    if (current_user_can('manage_options')) {
        echo '<h2>Administrator: launch and analytics</h2>';ez_input('ez_details[ga_id]',$o['ga_id'],'text','GA4 measurement ID');
        echo '<p><label><input type="checkbox" name="ez_details[analytics]" value="1" '.checked($o['analytics'],'1',false).'> Enable GA4 after the visitor accepts cookies</label></p>';
        echo '<p><label><input type="checkbox" name="ez_details[production_ready]" value="1" '.checked($o['production_ready'],'1',false).'> Cutover approved and production verified</label></p><p>Keep unchecked on staging. Public indexing also requires the production domain and Settings → Reading → “Discourage search engines” unchecked. This control does not change DNS.</p>';
    }
    submit_button('Save studio details');echo '</form></div>';
}
add_action('admin_enqueue_scripts',function($hook) {
    if (!in_array($hook,array('post.php','post-new.php','toplevel_page_ez-details'),true)) { return; }
    wp_enqueue_media();wp_enqueue_script('ez-admin',get_template_directory_uri().'/assets/js/admin.js',array(),EZ_VERSION,true);
    wp_enqueue_style('ez-admin',get_template_directory_uri().'/assets/css/admin.css',array(),EZ_VERSION);
});
