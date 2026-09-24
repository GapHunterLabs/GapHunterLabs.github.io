/* Seccion de extensiones de VS Code del catalogo (paginada, lee GapVSCode de vscode-catalog.js).
   Movido desde un <script> inline el 2026-09-24 para poder quitar
   'unsafe-inline' del script-src de la CSP (ver DOCUMENTATION.md). */
(function () {
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  // 2026-09-11: paginated at the user's explicit request (31 extensions
  // made the section a very long unbroken scroll) -- same
  // .catalog-pager/.catalog-pager-btn/.catalog-pager-status classes the
  // JetBrains grid's own pager uses above, for one consistent pager
  // look site-wide, but with its own local page state: this section is
  // a separate IIFE/data source (GapVSCode, not GapCatalog) so it can't
  // share that pager's catalogPage variable.
  var VSX_PAGE_SIZE = 10;
  var vsxPage = 1;
  var reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  GapVSCode.ready.then(function (data) {
    var section = document.getElementById('vsxSection');
    var grid = document.getElementById('vsxGrid');
    var subtitle = document.getElementById('vsxSubtitle');
    var pagerHost = document.getElementById('vsxPager');
    if (!section || !grid || !data.extensions.length) return;
    var extensions = data.extensions;
    subtitle.textContent = extensions.length + ' extensions published for VS Code -- same evidence-driven approach, a different editor.';

    function pageCount() { return Math.max(1, Math.ceil(extensions.length / VSX_PAGE_SIZE)); }
    function cardHtml(e) {
      return '<div class="vsx-card">' +
        '<div class="vsx-card-name">' + esc(e.displayName) + '</div>' +
        '<div class="vsx-card-niche">' + esc(e.niche) + '</div>' +
        '<div class="vsx-card-pitch">' + esc(e.pitch) + '</div>' +
        '<a class="vsx-card-link" href="' + esc(e.marketplaceUrl) + '" target="_blank" rel="noopener">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12l7 7 7-7"/></svg>' +
        'View on VS Code Marketplace</a>' +
        '</div>';
    }
    function pagerHtml() {
      var pages = pageCount();
      if (pages <= 1) return '';
      return '<nav class="catalog-pager" aria-label="VS Code extension pages">' +
        '<button type="button" class="btn catalog-pager-btn" data-vsx-dir="-1" aria-label="Previous page"' + (vsxPage <= 1 ? ' disabled' : '') + '>Previous</button>' +
        '<span class="catalog-pager-status" aria-live="polite">Page ' + vsxPage + ' of ' + pages + '</span>' +
        '<button type="button" class="btn catalog-pager-btn" data-vsx-dir="1" aria-label="Next page"' + (vsxPage >= pages ? ' disabled' : '') + '>Next</button>' +
        '</nav>';
    }
    function render() {
      var pages = pageCount();
      if (vsxPage > pages) vsxPage = pages;
      if (vsxPage < 1) vsxPage = 1;
      var start = (vsxPage - 1) * VSX_PAGE_SIZE;
      grid.innerHTML = extensions.slice(start, start + VSX_PAGE_SIZE).map(cardHtml).join('');
      if (!pagerHost) return;
      pagerHost.innerHTML = pagerHtml();
      Array.prototype.forEach.call(pagerHost.querySelectorAll('[data-vsx-dir]'), function (btn) {
        btn.addEventListener('click', function () {
          vsxPage = Math.min(pageCount(), Math.max(1, vsxPage + parseInt(btn.getAttribute('data-vsx-dir'), 10)));
          render();
          section.scrollIntoView({ block: 'start', behavior: reducedMotion ? 'auto' : 'smooth' });
        });
      });
    }
    render();
    section.hidden = false;
  }).catch(function (error) {
    // Non-fatal: this section is additive to the page, never gates it
    // the way GapCatalog.ready gates the main catalog grid above.
    console.error('VS Code catalog failed to load', error);
  });
})();
