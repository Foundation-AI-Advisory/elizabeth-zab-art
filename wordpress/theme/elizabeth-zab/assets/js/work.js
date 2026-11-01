
/* Lightbox viewer for the gallery plates */
(function(){
  var lb = document.getElementById('lightbox');
  if (!lb) return;
  var plates = Array.prototype.slice.call(document.querySelectorAll('.plate-open'));
  if (!plates.length) return;

  var img = lb.querySelector('.lb-img');
  var cap = lb.querySelector('.lb-cap');
  var count = lb.querySelector('.lb-count');
  var btnPrev = lb.querySelector('.lb-prev');
  var btnNext = lb.querySelector('.lb-next');

  var items = plates.map(function(btn){
    var im = btn.querySelector('img');
    var t = (btn.getAttribute('aria-label') || '').replace(/^Open full view:\s*/, '');
    return { src: im.getAttribute('src'), alt: im.getAttribute('alt'), no: 'No. ' + ('0' + (plates.indexOf(btn) + 1)).slice(-2), title: t };
  });
  var idx = 0, lastFocus = null;

  function render(){
    var it = items[idx];
    img.setAttribute('src', it.src);
    img.setAttribute('alt', it.alt);
    cap.innerHTML = '<span class="no"></span>';
    cap.querySelector('.no').textContent = it.no;
    cap.appendChild(document.createTextNode(' ' + it.title));
    count.textContent = (idx + 1) + ' / ' + items.length;
  }
  function open(i){
    idx = i; lastFocus = document.activeElement; render();
    lb.setAttribute('aria-hidden', 'false');
    document.body.classList.add('lb-open');
    lb.querySelector('.lb-close').focus();
  }
  function close(){
    lb.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('lb-open');
    img.setAttribute('src', '');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  function step(d){ idx = (idx + d + items.length) % items.length; render(); }

  document.querySelectorAll('.js-open').forEach(function(el){
    el.addEventListener('click', function(){ open(parseInt(el.getAttribute('data-idx'), 10) || 0); });
  });
  btnPrev.addEventListener('click', function(){ step(-1); });
  btnNext.addEventListener('click', function(){ step(1); });
  lb.querySelectorAll('[data-close]').forEach(function(el){ el.addEventListener('click', close); });
  document.addEventListener('keydown', function(e){
    if (lb.getAttribute('aria-hidden') !== 'false') return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') step(-1);
    else if (e.key === 'ArrowRight') step(1);
  });

  /* basic swipe on touch */
  var x0 = null;
  lb.addEventListener('touchstart', function(e){ x0 = e.changedTouches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function(e){
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 45) step(dx < 0 ? 1 : -1);
    x0 = null;
  }, { passive: true });
})();

/* Scroll reveal for plates */
(function(){
  var els = document.querySelectorAll('.reveal');
  if (!els.length) return;
  if (!('IntersectionObserver' in window)) { els.forEach(function(e){ e.classList.add('in'); }); return; }
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){ if (en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); } });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
  els.forEach(function(e){ io.observe(e); });
})();

/* Pointer parallax tilt on each plate image — desktop fine-pointer only */
(function(){
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (!fine || reduce) return;
  var plates = [].slice.call(document.querySelectorAll('.plate'));
  plates.forEach(function(plate){
    var frame = plate.querySelector('.plate-open');
    if (!frame) return;
    var max = parseFloat(getComputedStyle(plate).getPropertyValue('--tilt-max')) || 6;
    var raf = null, rx = 0, ry = 0;
    function apply(){ raf = null; frame.style.setProperty('--rx', rx.toFixed(2) + 'deg'); frame.style.setProperty('--ry', ry.toFixed(2) + 'deg'); }
    function onMove(ev){
      var r = frame.getBoundingClientRect();
      var px = (ev.clientX - r.left) / r.width - 0.5;
      var py = (ev.clientY - r.top) / r.height - 0.5;
      ry = px * max; rx = -py * max;
      if (!raf) raf = requestAnimationFrame(apply);
    }
    function onEnter(){ frame.classList.add('is-tilting'); frame.style.willChange = 'transform'; }
    function onLeave(){
      frame.classList.remove('is-tilting');
      frame.style.setProperty('--rx', '0deg');
      frame.style.setProperty('--ry', '0deg');
      frame.style.willChange = '';
    }
    frame.addEventListener('pointerenter', onEnter);
    frame.addEventListener('pointermove', onMove);
    frame.addEventListener('pointerleave', onLeave);
  });
})();
