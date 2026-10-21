(function () {
  'use strict';
  var loaded = false;
  function analytics() {
    var id = window.ezAnalyticsId;
    if (loaded || !/^G-[A-Z0-9]+$/.test(id || '')) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date()); window.gtag('config', id);
    var tag = document.createElement('script'); tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(tag);
  }
  var choice = '';
  try { choice = localStorage.getItem('ezart_cookie_v1') || ''; } catch (e) {}
  var banner = document.getElementById('cookieBanner');
  if (banner) banner.hidden = choice === 'accept' || choice === 'decline';
  if (choice === 'accept') analytics();
  window.ezCookie = function (value) {
    if (value !== 'accept' && value !== 'decline') return;
    try { localStorage.setItem('ezart_cookie_v1', value); } catch (e) {}
    if (banner) banner.hidden = true;
    if (value === 'accept') analytics();
  };
  // Keep keyboard focus within the existing artwork viewer.
  var box = document.getElementById('lightbox');
  if (box) box.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab' || box.getAttribute('aria-hidden') !== 'false') return;
    var controls = Array.from(box.querySelectorAll('button'));
    var first = controls[0], last = controls[controls.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });
})();
