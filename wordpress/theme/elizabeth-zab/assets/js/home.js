
/* Poured-paint motion for the home artwork cards: scroll reveal + pointer tilt */
(function(){
  var cards = [].slice.call(document.querySelectorAll('.art-card'));
  if (!cards.length) return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Staggered scroll reveal (stagger handled in CSS via --motion-delay) */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(en){ if (en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
    cards.forEach(function(c){ io.observe(c); });
  } else {
    cards.forEach(function(c){ c.classList.add('in'); });
  }

  /* Pointer parallax tilt — desktop fine-pointer only, never on touch or reduced-motion */
  var fine = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (!fine || reduce) return;

  cards.forEach(function(card){
    var frame = card.querySelector('.art-frame');
    if (!frame) return;
    var max = parseFloat(card.getAttribute('data-tilt-max')) || 6;
    var raf = null, rx = 0, ry = 0;

    function apply(){ raf = null; frame.style.setProperty('--rx', rx.toFixed(2) + 'deg'); frame.style.setProperty('--ry', ry.toFixed(2) + 'deg'); }
    function onMove(ev){
      var r = frame.getBoundingClientRect();
      var px = (ev.clientX - r.left) / r.width - 0.5;
      var py = (ev.clientY - r.top) / r.height - 0.5;
      ry = px * max;        /* horizontal cursor -> rotateY */
      rx = -py * max;       /* vertical cursor -> rotateX (inverted for natural feel) */
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
