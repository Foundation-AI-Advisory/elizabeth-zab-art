<?php
$footer=file_get_contents(__DIR__.'/inc/data/'.(is_404()?'footer-404.html':'footer.html'));
if (!is_404()) {
    ob_start(); ez_nav('footer'); $nav=ob_get_clean();
    $footer=preg_replace_callback('~(<nav class="legal-nav"[^>]*>).*?(</nav>)~s',function($m) use ($nav) { return $m[1].$nav.$m[2]; },$footer);
}
echo ez_display($footer); // Trusted theme layout; editable values escaped by ez_display.
if (!is_404()) { echo file_get_contents(__DIR__.'/inc/data/cookie.html'); }
wp_footer();
?>
</body>
</html>
