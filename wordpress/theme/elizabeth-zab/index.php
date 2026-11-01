<?php get_header(); ?>
<main id="ez-main" class="container" style="padding-top:60px;padding-bottom:60px">
<?php if (have_posts()) { while (have_posts()) { the_post(); ?>
<article><h1><?php the_title(); ?></h1><?php the_content(); ?></article>
<?php } } else { ?><h1>Nothing here yet.</h1><?php } ?>
</main>
<?php get_footer(); ?>
