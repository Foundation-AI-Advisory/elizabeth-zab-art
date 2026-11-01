<!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.add('js');</script>
<link rel="icon" href="<?php echo esc_url(home_url('/favicon.ico')); ?>" sizes="any">
<link rel="icon" type="image/svg+xml" href="<?php echo esc_url(home_url('/favicon.svg')); ?>">
<link rel="icon" type="image/png" sizes="32x32" href="<?php echo esc_url(home_url('/favicon-32.png')); ?>">
<link rel="apple-touch-icon" href="<?php echo esc_url(home_url('/apple-touch-icon.png')); ?>">
<meta name="theme-color" content="#2D4434">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<?php wp_head(); ?>
</head>
<body id="top" <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="ez-skip" href="#ez-main">Skip to content</a>
<header class="site-header"><div class="row">
<a href="<?php echo esc_url(home_url('/')); ?>" class="wordmark">Elizabeth Zab <span>· Art</span></a>
<nav class="nav-right" aria-label="Main navigation"><?php ez_nav('primary'); ?></nav>
</div></header>
