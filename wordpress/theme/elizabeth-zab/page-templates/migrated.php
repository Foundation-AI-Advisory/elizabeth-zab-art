<?php
/* Template Name: Elizabeth Zab — preserved layout */
get_header();
while (have_posts()) { the_post(); ?>
<main id="ez-main" tabindex="-1"><?php echo ez_display(ez_build_content(get_the_ID())); ?></main>
<?php }
get_footer();
