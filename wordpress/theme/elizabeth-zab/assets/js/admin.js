(function () {
  'use strict';
  var nextIndex = 1000;
  document.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    if (b.classList.contains('ez-media')) {
      var input = document.getElementById(b.dataset.target);
      var picker = wp.media({ title: 'Choose artwork', library: { type: 'image' }, multiple: false });
      picker.on('select', function () {
        var media = picker.state().get('selection').first().toJSON(); input.value = media.url;
        var row = b.closest('.ez-piece');
        if (row) {
          row.querySelector('[name$="[width]"]').value = media.width || '';
          row.querySelector('[name$="[height]"]').value = media.height || '';
          var alt = row.querySelector('[name$="[alt]"]'); if (media.alt) alt.value = media.alt;
        }
      }); picker.open();
    }
    if (b.id === 'ez-add-piece') {
      var template = document.getElementById('ez-piece-template').innerHTML.replace(/__INDEX__/g, String(nextIndex++));
      document.getElementById('ez-gallery').insertAdjacentHTML('beforeend', template);
    }
    var row = b.closest('.ez-piece'); if (!row) return;
    if (b.classList.contains('ez-remove') && window.confirm('Remove this artwork from the gallery? The media file is kept.')) row.remove();
    if (b.classList.contains('ez-up') && row.previousElementSibling) row.parentNode.insertBefore(row, row.previousElementSibling);
    if (b.classList.contains('ez-down') && row.nextElementSibling) row.parentNode.insertBefore(row.nextElementSibling, row);
  });
})();
