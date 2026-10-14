/* TRPL Labs — search, filtering, and on-demand live previews.
   No dependencies, no build step. */
(function () {
  'use strict';

  /* ---------------------------------------------------------- index page */
  var grid = document.getElementById('grid');
  if (grid) {
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
    var q = document.getElementById('q');
    var wrap = document.getElementById('searchWrap');
    var clearBtn = document.getElementById('clearQ');
    var count = document.getElementById('count');
    var empty = document.getElementById('empty');
    var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
    var cat = 'all';
    var sortSel = document.getElementById('sort');
    var sort = 'featured';
    var SORTS = ['featured', 'newest', 'name', 'category'];
    var catOrder = (grid.dataset.catOrder || '').split('|');

    // The build writes cards in featured order, so DOM position is the baseline.
    cards.forEach(function (c, i) { c.dataset.i = i; });

    function byIndex(a, b) { return a.dataset.i - b.dataset.i; }

    function reorder() {
      var list = cards.slice();
      if (sort === 'newest') {
        list.sort(function (a, b) { return b.dataset.added.localeCompare(a.dataset.added) || byIndex(a, b); });
      } else if (sort === 'name') {
        list.sort(function (a, b) { return a.dataset.name.localeCompare(b.dataset.name); });
      } else if (sort === 'category') {
        list.sort(function (a, b) {
          return (catOrder.indexOf(a.dataset.cat) - catOrder.indexOf(b.dataset.cat)) || byIndex(a, b);
        });
      } else {
        list.sort(byIndex);
      }
      Array.prototype.slice.call(grid.querySelectorAll('.group-head')).forEach(function (h) { h.remove(); });
      var last = null;
      list.forEach(function (c) {
        if (sort === 'category' && c.dataset.cat !== last) {
          last = c.dataset.cat;
          var h = document.createElement('li');
          h.className = 'group-head';
          h.dataset.cat = last;
          h.textContent = last;
          grid.appendChild(h);
        }
        grid.appendChild(c);
      });
    }

    function terms(s) {
      return s.toLowerCase().split(/\s+/).filter(Boolean);
    }

    function apply() {
      var words = terms(q.value);
      var shown = 0;
      cards.forEach(function (c) {
        var okCat = cat === 'all' || c.dataset.cat === cat;
        var hay = c.dataset.search;
        var okText = words.every(function (w) { return hay.indexOf(w) !== -1; });
        var vis = okCat && okText;
        c.classList.toggle('is-hidden', !vis);
        if (vis) shown++;
      });
      Array.prototype.slice.call(grid.querySelectorAll('.group-head')).forEach(function (h) {
        h.hidden = !cards.some(function (c) { return c.dataset.cat === h.dataset.cat && !c.classList.contains('is-hidden'); });
      });
      count.textContent = shown + (shown === 1 ? ' project' : ' projects');
      empty.hidden = shown !== 0;
      wrap.classList.toggle('has-value', q.value.length > 0);
      var url = new URL(location.href);
      if (q.value) { url.searchParams.set('q', q.value); } else { url.searchParams.delete('q'); }
      if (cat !== 'all') { url.searchParams.set('cat', cat); } else { url.searchParams.delete('cat'); }
      if (sort !== 'featured') { url.searchParams.set('sort', sort); } else { url.searchParams.delete('sort'); }
      history.replaceState(null, '', url.pathname + url.search + url.hash);
    }

    q.addEventListener('input', apply);
    clearBtn.addEventListener('click', function () { q.value = ''; q.focus(); apply(); });
    q.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && q.value) { q.value = ''; apply(); }
    });

    sortSel.addEventListener('change', function () {
      sort = SORTS.indexOf(sortSel.value) !== -1 ? sortSel.value : 'featured';
      reorder();
      apply();
    });

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        cat = chip.dataset.cat;
        chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)); });
        apply();
      });
    });

    // "/" focuses search, the way a developer expects it to.
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement !== q && !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) {
        e.preventDefault();
        q.focus();
      }
    });

    // Restore state from the URL so a filtered view is shareable.
    var params = new URLSearchParams(location.search);
    if (params.get('q')) q.value = params.get('q');
    if (SORTS.indexOf(params.get('sort')) !== -1) { sort = params.get('sort'); sortSel.value = sort; reorder(); }
    if (params.get('cat')) {
      var match = chips.filter(function (c) { return c.dataset.cat === params.get('cat'); })[0];
      if (match) { cat = match.dataset.cat; chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c === match)); }); }
    }
    apply();

  }

  /* ------------------------------------------------------ reduced motion */
  // Looping animations hold on their poster frame for visitors who ask for less motion.
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('video[autoplay]').forEach(function (v) {
      v.removeAttribute('autoplay'); v.pause(); v.controls = true;
    });
  }

  /* -------------------------------------------------------- detail page */
  var loadDemo = document.getElementById('loadDemo');
  if (loadDemo) {
    loadDemo.addEventListener('click', function () {
      var box = document.getElementById('demoFrame');
      var frame = document.createElement('iframe');
      frame.src = loadDemo.dataset.src;
      frame.title = 'Live demo';
      frame.setAttribute('referrerpolicy', 'no-referrer-when-downgrade');
      frame.setAttribute('allow', 'accelerometer; gyroscope; magnetometer; camera; fullscreen');
      frame.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-popups allow-forms allow-downloads');
      box.appendChild(frame);
      box.classList.add('is-live');
    });
  }

  /* ------------------------------------------------------------- copy */
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var text = btn.parentNode.textContent.replace(/^\s*Copy\s*/, '').trim();
      if (navigator.clipboard) navigator.clipboard.writeText(text);
      var was = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = was; }, 1300);
    });
  });
})();
