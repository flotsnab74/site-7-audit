// Интерактивный подбор по типу детали (products.html).
// Наведение мыши / фокус / нажатие на плитку открывает карточку изделия справа.
// Все карточки лежат в HTML (текст виден поисковикам), скрипт только переключает их.
(function () {
  var root = document.querySelector('[data-part-picker]');
  if (!root) return;
  var tiles = [].slice.call(root.querySelectorAll('.pp-tile'));
  var panels = [].slice.call(root.querySelectorAll('.pp-panel'));
  if (!tiles.length || !panels.length) return;

  var canHover = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var current = null, timer = null;

  function select(id) {
    if (id === current) return;
    current = id;
    tiles.forEach(function (t) {
      var on = t.getAttribute('data-part') === id;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
    });
    panels.forEach(function (p) {
      var on = p.getAttribute('data-part') === id;
      p.hidden = !on;
      p.classList.remove('is-active');
      if (on) { void p.offsetWidth; p.classList.add('is-active'); }
    });
  }

  // На телефоне карточка лежит под плитками: после нажатия прокручиваем к ней, если её не видно.
  function showPanel() {
    var p = root.querySelector('.pp-panel:not([hidden])');
    if (!p) return;
    var r = p.getBoundingClientRect();
    if (r.top > window.innerHeight * 0.55 || r.bottom < 0) {
      p.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    }
  }

  tiles.forEach(function (tile, i) {
    var id = tile.getAttribute('data-part');
    tile.addEventListener('click', function () { clearTimeout(timer); select(id); if (!canHover) showPanel(); });
    tile.addEventListener('focus', function () { select(id); });
    if (canHover) {
      tile.addEventListener('mouseenter', function () {
        clearTimeout(timer);
        timer = setTimeout(function () { select(id); }, 90);   // небольшая задержка, чтобы не мелькало при быстром движении мыши
      });
      tile.addEventListener('mouseleave', function () { clearTimeout(timer); });
    }
    tile.addEventListener('keydown', function (e) {
      var n = tiles.length, to = null;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') to = (i + 1) % n;
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') to = (i - 1 + n) % n;
      else if (e.key === 'Home') to = 0;
      else if (e.key === 'End') to = n - 1;
      if (to !== null) { e.preventDefault(); tiles[to].focus(); }
    });
  });

  select(tiles[0].getAttribute('data-part'));
})();
