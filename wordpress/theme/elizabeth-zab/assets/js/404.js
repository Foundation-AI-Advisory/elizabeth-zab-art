
(function(){
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var imgs = [].slice.call(document.querySelectorAll('.reveal img'));
  if (reduce || imgs.length < 2) return;
  var i = 0;
  // Hold the first painting through the pour, then let it "become" the others.
  setTimeout(function cycle(){
    imgs[i].classList.remove('active');
    i = (i + 1) % imgs.length;
    imgs[i].classList.add('active');
    setTimeout(cycle, 5200);
  }, 4600);
})();
