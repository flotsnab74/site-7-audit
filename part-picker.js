// Интерактивные блоки страницы «Наши работы» (gallery.html):
//   1) точки на реальном фото деталей (.rp-hot);
//   2) подбор по типу детали (.pp-tile).
// Наведение мыши / фокус / нажатие открывает карточку справа (.pp-panel).
// Все карточки лежат в HTML (текст виден поисковикам), скрипт только переключает их.
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var canHover = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  function init(root) {
    var tiles = [].slice.call(root.querySelectorAll('.pp-tile, .rp-hot'));
    var panels = [].slice.call(root.querySelectorAll('.pp-panel'));
    if (!tiles.length || !panels.length) { initGal(root); return; }
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

    // На телефоне карточка лежит под плитками/фото: после нажатия прокручиваем минимально,
    // чтобы карточка стала видна целиком, а фото или плитки остались частично на экране.
    function showPanel() {
      var p = root.querySelector('.pp-panel:not([hidden])');
      if (!p) return;
      var r = p.getBoundingClientRect();
      if (r.bottom > window.innerHeight - 8 || r.top < 70) {
        p.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'nearest' });
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

    initGal(root);
    select(tiles[0].getAttribute('data-part'));
  }

  // Мини-галереи внутри карточек (несколько фото одной детали)
  function initGal(root) {
    [].slice.call(root.querySelectorAll('[data-gal]')).forEach(function (gal) {
      var main = gal.querySelector('.pp-gal-main');
      var btns = [].slice.call(gal.querySelectorAll('.pp-gal-btn'));
      var gtimer = null;
      function show(btn) {
        if (btn.classList.contains('is-on')) return;
        btns.forEach(function (b) { b.classList.toggle('is-on', b === btn); });
        var panel = gal.closest('.pp-panel');
        if (gal.closest('.pp-solo')) panel = gal.closest('.rp').querySelector('.pp-body').closest('.pp-panel');
        var cap = btn.getAttribute('data-caption');
        if (cap !== null) {
          var capEl = panel && panel.querySelector('.pp-caption');
          if (capEl) capEl.textContent = cap;
        }
        // характеристики именно этого изделия: строки с data-spec обновляются, строки без данных скрываются
        var raw = btn.getAttribute('data-specs');
        if (raw && panel) {
          var specs = null;
          try { specs = JSON.parse(raw); } catch (e) { specs = null; }
          if (specs) {
            [].slice.call(panel.querySelectorAll('[data-spec]')).forEach(function (row) {
              var v = specs[row.getAttribute('data-spec')];
              var vEl = row.querySelector('.v');
              if (v && vEl) { vEl.textContent = v; row.hidden = false; } else { row.hidden = true; }
            });
          }
        }
        main.classList.add('is-swapping');
        setTimeout(function () {
          main.src = btn.getAttribute('data-src');
          main.alt = btn.getAttribute('data-alt') || '';
          main.classList.remove('is-swapping');
        }, reduce ? 0 : 150);
      }
      btns.forEach(function (btn) {
        btn.addEventListener('click', function () { show(btn); });
        if (canHover) {
          btn.addEventListener('mouseenter', function () { clearTimeout(gtimer); gtimer = setTimeout(function () { show(btn); }, 90); });
          btn.addEventListener('mouseleave', function () { clearTimeout(gtimer); });
        }
      });
    });
  }

  [].slice.call(document.querySelectorAll('[data-part-picker]')).forEach(init);
})();
