
/* Enlaces antiguos al dossier por hash (#mermaid-companion) -> su URL real
   (/catalog/mermaid-companion/). Corre antes de cualquier CSS o fetch para
   que el salto ocurra sin primer pintado. La lista de slugs la escribe
   pipeline/build_plugin_pages.py entre los marcadores; no editar a mano. */
(function () {
  var h = location.hash.slice(1).toLowerCase();
  if (!h) return;
  var slugs = /*SLUGS*/["ansible-companion","apache-httpclient-reuse-companion","api-deprecation-header-companion","api-security-companion","async-self-invocation-companion","asyncapi-companion","aws-s3-public-acl-sdk-companion","aws-sdk-client-reuse-companion","background-readaction-freeze-companion","bean-copy-companion","binding-result-position-companion","cache-invalidation-companion","cassandra-cqlsession-reuse-companion","cert-companion","change-case-companion","changelog-fragment-companion","circular-dependency-companion","cmake-companion","commit-message-convention-companion","completablefuture-cancellation-companion","config-secrets-file-companion","connection-pool-config-companion","correlation-id-propagation-companion","cors-policy-companion","deadlock-lock-order-companion","dependency-vulnerability-companion","dockerfile-layer-size-companion","dockerfile-missing-user-companion","dockerfile-unused-stage-companion","elasticsearch-client-reuse-companion","enum-ordinal-persistence-companion","env-diff-companion","env-var-missing-companion","environment-specific-constant-companion","error-lens-companion","exception-escape-chain-companion","feature-flag-reference-companion","feign-fallback-config-companion","firestore-companion","flaky-test-marker-companion","format-converter-companion","gcp-client-reuse-companion","git-hygiene-companion","github-actions-pwn-request-companion","gitlab-ci-companion","go-timer-leak-companion","gradle-task-graph-companion","graphql-companion","grpc-error-status-companion","grpc-missing-deadline-companion","grpc-streamobserver-contract-companion","highlight-companion","http-status-inline-companion","idempotency-key-companion","import-cost-companion","integer-overflow-widening-companion","interface-exception-divergence-companion","interface-resource-close-divergence-companion","interface-sink-divergence-companion","interprocedural-resource-leak-companion","jdbc-double-close-companion","jenkinsfile-companion","json-path-builder-companion","json-schema-companion","json-to-code-companion","jwt-companion","jwt-signature-verification-companion","jwt-webhook-timing-safe-companion","k6-companion","k8s-label-selector-exposure-companion","k8s-readiness-liveness-probe-companion","k8s-resource-limit-companion","kafka-premature-offset-commit-companion","kafka-producer-reuse-companion","kafka-topic-feedback-loop-companion","kafka-topic-schema-companion","ktor-httpclient-reuse-companion","kubernetes-rbac-wildcard-companion","ldap-injection-sink-companion","log-format-string-companion","log-injection-companion","lucene-query-injection-companion","material-companion","merge-conflict-leftover-companion","mermaid-companion","micrometer-timer-sample-companion","micronaut-httpclient-create-companion","mismatched-lock-object-companion","module-boundary-leak-companion","mongo-client-reuse-companion","mutable-state-leak-companion","n-plus-one-query-companion","nginx-companion","npm-peer-dependency-companion","object-mapper-reuse-companion","okhttp-client-reuse-companion","openapi-companion","otel-span-naming-companion","php-composer-script-companion","php-file-inclusion-companion","php-function-injection-companion","php-open-redirect-companion","php-shell-injection-companion","php-sql-injection-companion","pii-field-annotation-companion","pii-tostring-leak-companion","postman-openapi-drift-companion","prometheus-metric-naming-companion","prometheus-metric-registration-companion","rabbitmq-channel-reuse-companion","rails-mass-assignment-companion","rate-limiter-fallback-companion","react-native-companion","redis-lock-missing-ttl-companion","redisson-client-reuse-companion","redos-catastrophic-backtracking-companion","refactor-simulator","regex-named-group-companion","regex-preview-companion","resilience-self-invocation-companion","retry-backoff-jitter-companion","review-companion","ruby-gemfile-group-companion","ruby-nethttp-reuse-companion","ruby-shell-injection-companion","rxjava-disposable-leak-companion","second-order-sqli-field-companion","semver-bump-mismatch-companion","session-attribute-type-confusion-companion","spel-injection-sink-companion","spreadsheet-companion","sql-concatenation-companion","ssrf-allowlist-bypass-companion","ssrf-unsanitized-url-companion","terraform-iam-privesc-companion","terraform-iam-wildcard-companion","test-scaffold-companion","theme-companion","thread-confinement-escape-companion","trycatch-consistency-companion","turbo-log-companion","unsafe-deserialization-sink-companion","unused-npm-script-companion","webhook-signature-companion","xpath-injection-sink-companion","xsd-companion"]/*ENDSLUGS*/;
  if (slugs.indexOf(h) !== -1) location.replace('/catalog/' + h + '/');
})();


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


(function () {
Promise.all([
  GapCatalog.ready,
  // 2026-09-11: cross-reference for the dossier's "Download for VS
  // Code" button -- additive only, same non-fatal contract as the vsx
  // section below (js/vscode-catalog.js's own header comment): if this
  // fetch fails, the JetBrains catalog still renders exactly as
  // before, it just never matches a VS Code port (empty map) instead
  // of blocking the whole page on a second marketplace's outage.
  GapVSCode.ready.then(function (d) { return d.extensions; }).catch(function () { return []; })
]).then(function (results) {
  var shared = results[0];
  var vsxByRepo = {};
  results[1].forEach(function (e) { vsxByRepo[e.name] = e; });
  var data = shared.data;
  var plugins = shared.plugins;
  var CATEGORIES = shared.CATEGORIES;
  var CAT_BY_KEY = shared.CAT_BY_KEY;
  var ICONS = shared.ICONS;
  // Ícono local (no vive en catalog-shared.js porque ningún otro
  // consumidor lo necesita hoy) -- mismo lenguaje visual que
  // ICONS.downloads (viewBox 20x20, stroke, stroke-width 1.4), usado
  // para el stat "Published" del dossier. 2026-09-10.
  var ICON_CALENDAR = '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="14" height="13" rx="1.5"/><path d="M3 8h14M7 2.5v3M13 2.5v3"/></svg>';
  var GIF_URL = shared.GIF_URL;
  var esc = shared.esc;
  var safeUrl = shared.safeUrl;
  var mdInline = shared.mdInline;
  var pricingLabel = shared.pricingLabel;
  var growthMarkup = shared.growthMarkup;
  var byRepo = shared.byRepo;
  var catIconHtml = shared.catIconHtml;
  var gapText = shared.gapText;
  var platformOf = shared.platformOf;
  var marketplaceId = shared.marketplaceId;
  var growthFactLine = shared.growthFactLine;
  var mode = 'field';
  var sortKey = 'downloads';
  var sortDir = -1; // desc
  var filterText = '';
  var filterPricing = '';
  var categoryParam = new URLSearchParams(location.search).get('category') || '';
  var filterCategory = shared.CAT_BY_KEY[categoryParam] && categoryParam !== 'other' ? categoryParam : (categoryParam === 'other' ? 'other' : '');
  var selectedRepo = null;
  var PAGE_SIZE = 15;
  var catalogPage = 1;
  function setSelectedRepo(repo, scrollAfter) {
    selectedRepo = repo || null;
    renderAll();
    if (scrollAfter && selectedRepo) scrollSelectedIntoView();
  }
  function matches(p) {
    var isPending = p.downloads === null;
    if (filterPricing) {
      if (filterPricing === 'PENDING' && !isPending) return false;
      if (filterPricing !== 'PENDING' && p.pricing !== filterPricing) return false;
    }
    if (filterCategory && p.categoryKey !== filterCategory) return false;
    if (!filterText) return true;
    var hay = (p.name + ' ' + p.niche + ' ' + p.repo).toLowerCase();
    return hay.indexOf(filterText) !== -1;
  }

  function sortedFiltered() {
    var rows = plugins.filter(matches);
    rows.sort(function (a, b) {
      var av = a[sortKey], bv = b[sortKey];
      if (sortKey === 'name') { av = a.name.toLowerCase(); bv = b.name.toLowerCase(); }
      var an = (av === null || av === undefined);
      var bn = (bv === null || bv === undefined);
      if (an && bn) return 0;
      if (an) return 1;
      if (bn) return -1;
      if (av < bv) return -1 * sortDir;
      if (av > bv) return 1 * sortDir;
      return 0;
    });
    return rows;
  }

  function catalogPageCount(n) {
    return Math.max(1, Math.ceil(n / PAGE_SIZE));
  }
  function clampCatalogPage(n) {
    var pages = catalogPageCount(n);
    if (catalogPage > pages) catalogPage = pages;
    if (catalogPage < 1) catalogPage = 1;
    return pages;
  }
  function ensurePageForRepo(rows, repo) {
    if (!repo) return;
    var i;
    for (i = 0; i < rows.length; i++) {
      if (rows[i].repo === repo) {
        catalogPage = Math.floor(i / PAGE_SIZE) + 1;
        return;
      }
    }
  }
  function pagedRows(rows) {
    clampCatalogPage(rows.length);
    var start = (catalogPage - 1) * PAGE_SIZE;
    return rows.slice(start, start + PAGE_SIZE);
  }
  function pagerHtml(total) {
    var pages = catalogPageCount(total);
    if (pages <= 1) return '';
    return '<nav class="catalog-pager" aria-label="Catalog pages">' +
      '<button type="button" class="btn catalog-pager-btn" data-page-dir="-1" aria-label="Previous page"' + (catalogPage <= 1 ? ' disabled' : '') + '>Previous</button>' +
      '<span class="catalog-pager-status" aria-live="polite">Page ' + catalogPage + ' of ' + pages + '</span>' +
      '<button type="button" class="btn catalog-pager-btn" data-page-dir="1" aria-label="Next page"' + (catalogPage >= pages ? ' disabled' : '') + '>Next</button>' +
      '</nav>';
  }
  function wirePager(container, total) {
    if (!container) return;
    Array.prototype.forEach.call(container.querySelectorAll('[data-page-dir]'), function (btn) {
      btn.addEventListener('click', function () {
        var dir = parseInt(btn.getAttribute('data-page-dir'), 10);
        var pages = catalogPageCount(total);
        catalogPage = Math.min(pages, Math.max(1, catalogPage + dir));
        selectedRepo = null;
        renderAll();
        scrollCatalogIntoView();
      });
    });
  }

  function similarCardHtml(s, cls) {
    var sCat = CAT_BY_KEY[s.categoryKey] || CAT_BY_KEY.other;
    return '<div class="' + cls + '" data-repo="' + esc(s.repo) + '" role="button" tabindex="0" aria-label="' + esc(s.name) + ' details">' +
      '<span class="card-cat" style="--cat:' + sCat.color + '" title="' + esc(sCat.label) + '" aria-hidden="true">' + catIconHtml(s.categoryKey) + '</span>' +
      '<div class="sc-name">' + esc(s.name) + '</div>' +
      '<div class="sc-niche">' + esc(s.niche) + '</div>' +
      '<div class="sc-dl">' + (s.downloads == null ? 'Pending' : s.downloads.toLocaleString('en-US') + ' downloads') + '</div></div>';
  }

  var PREFERS_REDUCED_MOTION = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function decodeNumber(el, finalText, extraHtml) {
    if (el) el.innerHTML = finalText + (extraHtml || '');
  }

  // Stats reales arriba del Hunting Field (reemplazo del sidebar, a
  // pedido explícito 2026-09-10) -- mismos campos que ya usa
  // renderStats() en index.html, mismos íconos compartidos.
  function renderCatalogStats() {
    var el = document.getElementById('catalogStats');
    if (!el) return;
    var catCount = CATEGORIES.filter(function (c) { return c.key !== 'other'; }).length;
    el.innerHTML =
      '<div class="cs-item"><span class="cs-icon" style="color:var(--accent)">' + ICONS.plugins + '</span><div><div class="cs-num">' + data.totalPlugins + '</div><div class="cs-label">Active plugins</div></div></div>' +
      '<div class="cs-item"><span class="cs-icon" style="color:var(--good)">' + ICONS.downloads + '</span><div><div class="cs-num">' + data.totalDownloads.toLocaleString('en-US') + '</div><div class="cs-label">Total downloads</div></div></div>' +
      '<div class="cs-item"><span class="cs-icon" style="color:var(--purple)"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="3" y="3" width="6" height="6" rx="1"/><rect x="11" y="3" width="6" height="6" rx="1"/><rect x="3" y="11" width="6" height="6" rx="1"/><rect x="11" y="11" width="6" height="6" rx="1"/></svg></span><div><div class="cs-num">' + catCount + '</div><div class="cs-label">Categories</div></div></div>';
  }

  function populateCategorySelect() {
    var counts = {};
    CATEGORIES.forEach(function (c) { counts[c.key] = 0; });
    plugins.forEach(function (p) { counts[p.categoryKey] = (counts[p.categoryKey] || 0) + 1; });
    var active = CATEGORIES.filter(function (c) { return c.key !== 'other' || counts.other > 0; });

    var sel = document.getElementById('categoryFilter');
    var html = '<option value="">All categories (' + plugins.length + ')</option>';
    active.forEach(function (c) {
      html += '<option value="' + c.key + '">' + esc(c.label) + ' (' + (counts[c.key] || 0) + ')</option>';
    });
    sel.innerHTML = html;
  }

  function wireCategorySelect() {
    var sel = document.getElementById('categoryFilter');
    if (sel.dataset.wired) return;
    sel.dataset.wired = '1';
    sel.addEventListener('change', function (e) {
      filterCategory = e.target.value;
      selectedRepo = null;
      catalogPage = 1;
      renderAll();
      // Mismo criterio que wireCategoryBoard() -- este <select> vive en
      // la barra de controles, ya pegado arriba de la grilla; el salto
      // de scrollCatalogIntoView() rompía la misma vista quieta pedida
      // para el tablero de categorías. 2026-09-10.
    });
  }

  function categoryCounts() {
    var counts = {};
    CATEGORIES.forEach(function (c) { counts[c.key] = 0; });
    plugins.forEach(function (p) { counts[p.categoryKey] = (counts[p.categoryKey] || 0) + 1; });
    return counts;
  }

  function updateCategoryBoard() {
    var board = document.querySelector('.cat-board');
    if (!board) return;
    var counts = categoryCounts();
    Array.prototype.forEach.call(board.querySelectorAll('.cat-cell'), function (btn) {
      var cat = btn.getAttribute('data-cat') || '';
      var active = cat === '' ? !filterCategory : filterCategory === cat;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
      var countEl = btn.querySelector('.cat-cell-count');
      if (!countEl) return;
      if (cat === '') {
        countEl.textContent = plugins.length + (plugins.length === 1 ? ' plugin' : ' plugins');
        return;
      }
      var n = counts[cat] || 0;
      countEl.textContent = n === 1 ? '1 plugin' : n + ' plugins';
      if (cat === 'other') {
        if (n > 0) btn.removeAttribute('hidden');
        else btn.setAttribute('hidden', '');
      }
    });
  }

  function wireCategoryBoard() {
    var board = document.querySelector('.cat-board');
    if (!board || board.dataset.wired) return;
    board.dataset.wired = '1';
    board.addEventListener('click', function (e) {
      var btn = e.target.closest('.cat-cell');
      if (!btn || !board.contains(btn)) return;
      var cat = btn.getAttribute('data-cat') || '';
      filterCategory = (!cat || filterCategory === cat) ? '' : cat;
      selectedRepo = null;
      catalogPage = 1;
      renderAll();
      // A diferencia de wireCategorySelect() (el <select> de la barra de
      // controles, lejos de la grilla), este tablero vive pegado arriba
      // de la grilla -- no hace falta scrollCatalogIntoView() y, peor,
      // el salto rompía la vista que el usuario pidió: el tablero de
      // categorías quieto arriba, la grilla filtrada apareciendo justo
      // debajo, sin mover el scroll. 2026-09-10.
    });
  }

  // ---- Field main: grid or dossier -----------------------------------
  function pluginCardHtml(p) {
    var isPending = p.downloads === null;
    var cat = CAT_BY_KEY[p.categoryKey] || CAT_BY_KEY.other;
    // Pricing tier on the card face (Free/Freemium/Paid/Pending), not
    // growth% -- growth still lives one click away in the dossier's own
    // stat row (dossierBodyHtml()), which has room for the "since
    // <date>" tooltip context that a compact card face doesn't.
    var pr = pricingLabel(p.pricing, isPending);
    return '<div class="plugin-card" data-repo="' + esc(p.repo) + '" role="button" tabindex="0" aria-label="' + esc(p.name) + ' details">' +
      '<div class="card-header">' +
      '<span class="card-cat" style="--cat:' + cat.color + '" title="' + esc(cat.label) + '" aria-hidden="true">' + catIconHtml(p.categoryKey) + '</span>' +
      '<div class="card-top">' +
      '<div class="card-name">' + esc(p.name) + (p.verified ? '<span class="verified-mark" role="img" aria-label="Verified vendor" title="Verified vendor">✓</span>' : '') + '</div>' +
      '<div class="card-niche">' + esc(p.niche) + '</div>' +
      '</div>' +
      '</div>' +
      '<div class="card-metrics">' +
      (isPending
        ? '<span class="chip pending">Pending</span>'
        : '<span class="card-dl-wrap"><span class="dl-icon">' + ICONS.downloads + '</span><span class="card-dl">' + p.downloads.toLocaleString('en-US') + '</span></span>' +
          '<span class="card-pricing ' + pr.cls + '">' + esc(pr.text) + '</span>') +
      '</div></div>';
  }

  function renderGrid() {
    var rows = sortedFiltered();
    var main = document.getElementById('fieldMain');
    if (rows.length === 0) {
      main.innerHTML = '<div class="no-results" aria-live="polite">No results for that filter.</div>';
      return;
    }
    var pageRows = pagedRows(rows);
    main.innerHTML = '<div class="plugin-grid">' + pageRows.map(pluginCardHtml).join('') + '</div>' + pagerHtml(rows.length);
    wirePager(main, rows.length);
    Array.prototype.forEach.call(main.querySelectorAll('.plugin-card'), function (card) {
      var open = function () {
        setSelectedRepo(card.getAttribute('data-repo'), true);
      };
      card.addEventListener('click', open);
      // Added 2026-08-21: these cards are role="button"/tabindex="0" (see
      // pluginCardHtml) but a real <button> would have gotten Enter/Space
      // activation for free from the browser -- a plain focusable <div>
      // does not, so a keyboard-only visitor could Tab to a card but
      // never actually open it before this. Space also scrolls the page
      // by default on a focused element; preventDefault stops that so
      // the key does what the visible "button" role promises instead.
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          open();
        }
      });
    });
  }

  // Full rich content of a plugin's dossier -- header card (back,
  // name/chips/pitch, stats, gif/links), Gap+Fix+Facts, similar plugins.
  // Field-mode full-page dossier only. The table row uses
  // tableDossierBodyHtml(). Caller must call wireDossierInteractions()
  // on the container afterward for similar-card clicks.
  function dossierBodyHtml(p) {
    var isPending = p.downloads === null;
    var pr = pricingLabel(p.pricing, isPending);
    var cat = CAT_BY_KEY[p.categoryKey];
    var gifUrl = GIF_URL[p.repo];
    var mpId = marketplaceId(p);

    var similar = plugins
      .filter(function (o) { return o.repo !== p.repo && o.categoryKey === p.categoryKey; })
      .sort(function (a, b) { return (b.downloads || 0) - (a.downloads || 0); })
      .slice(0, 4);

    var html = '<div class="dossier-sheet"><div class="dossier-card">';
    html += '<button type="button" class="dossier-back" id="dossierBack">✕ Close</button>';
    html += '<div class="dossier-top">';
    html += '<div class="dossier-intro"><div class="dossier-title-row"><h2>' + esc(p.name) + '</h2>' +
      '<span class="chip ' + pr.cls + '">' + esc(pr.text) + '</span>' +
      '<span class="chip" style="background:color-mix(in srgb, ' + cat.color + ' 20%, transparent); color:' + cat.color + '">' + esc(cat.label) + '</span></div>' +
      '<div class="dossier-niche">' + esc(p.niche) + '</div>' +
      '<div class="dossier-pitch">' + mdInline(p.pitch || '—') + '</div>';
    html += '<div class="dossier-stats">';
    html += '<div class="stat"><span class="stat-icon">' + ICONS.downloads + '</span><div><div class="num" id="dossierDlNum">' + (isPending ? '—' : p.downloads.toLocaleString('en-US')) + '</div><div class="label">Downloads' + (isPending ? '' : ' ' + growthMarkup(p)) + '</div></div></div>';
    html += '<div class="stat"><span class="stat-icon">' + ICONS.github + '</span><div><div class="num">' + (p.stars != null ? p.stars : '—') + '</div><div class="label">GitHub stars</div></div></div>';
    html += '<div class="stat"><span class="stat-icon">' + ICON_CALENDAR + '</span><div><div class="num">' + (p.firstPublished || '—') + '</div><div class="label">Published</div></div></div>';
    html += '</div></div>';
    html += '<div class="dossier-side">';
    html += '<div class="dossier-links">';
    if (p.marketplaceUrl) html += '<a class="btn primary" href="' + esc(safeUrl(p.marketplaceUrl)) + '" target="_blank" rel="noopener"><span class="btn-icon">' + ICONS.jetbrains + '</span>Install on JetBrains ↗</a>';
    html += '<a class="btn" href="' + esc(safeUrl(p.githubUrl)) + '" target="_blank" rel="noopener"><span class="btn-icon">' + ICONS.github + '</span>View on GitHub ↗</a>';
    // 2026-09-11: real cross-reference (vsxByRepo, keyed by the same
    // repo slug both marketplaces share, e.g. "cert-companion") -- only
    // ports that actually exist and are live on the VS Code Marketplace
    // get this button, never every plugin.
    var vsxMatch = vsxByRepo[p.repo];
    if (vsxMatch) html += '<a class="btn" href="' + esc(safeUrl(vsxMatch.marketplaceUrl)) + '" target="_blank" rel="noopener"><span class="btn-icon">' + ICONS.vscode + '</span>Download for VS Code ↗</a>';
    html += '</div>';
    if (gifUrl) {
      // onerror moved to a real addEventListener in
      // wireDossierInteractions() so this markup stays free of inline
      // handlers (script-src unsafe-inline).
      html += '<img class="dossier-gif" src="' + esc(gifUrl) + '" alt="' + esc(p.name) + ' in action" loading="lazy">';
    }
    html += '</div></div></div>';

    html += '<div class="dossier-body">';
    html += '<div class="info-block"><div class="ib-head"><span class="ib-icon gap">!</span><span class="ib-title">The Gap</span></div>' +
      '<div class="ib-body">' + mdInline(gapText(p)) + '</div></div>';
    html += '<div class="info-block"><div class="ib-head"><span class="ib-icon fix">✓</span><span class="ib-title">The Fix</span></div>' +
      '<div class="ib-body">' + mdInline(p.pitch || '—') + '</div></div>';
    html += '</div>';

    html += '<div class="info-block facts-block"><div class="ib-head"><span class="ib-icon facts">⚙</span><span class="ib-title">Facts</span></div><ul class="facts-list">' +
      '<li><span class="fk">Category</span><span class="fv">' + esc(cat.label) + '</span></li>' +
      '<li><span class="fk">Pricing</span><span class="fv">' + esc(pr.text) + '</span></li>' +
      '<li><span class="fk">Platform</span><span class="fv">' + esc(platformOf(p)) + '</span></li>' +
      '<li><span class="fk">First published</span><span class="fv">' + (p.firstPublished || '—') + '</span></li>' +
      '<li><span class="fk">Marketplace ID</span><span class="fv">' + (mpId ? '#' + esc(mpId) : (isPending ? 'Pending' : '—')) + '</span></li>' +
      '<li><span class="fk">Repository</span><span class="fv"><code>' + esc(p.repo) + '</code><button type="button" class="copy-btn" data-copy="' + esc(p.repo) + '" aria-label="Copy repository name">' + ICONS.copy + '</button></span></li>' +
      '<li><span class="fk">Growth</span><span class="fv">' + esc(growthFactLine(p)) + '</span></li>' +
      '</ul></div>';

    if (similar.length) {
      html += '<div class="similar-section"><div class="similar-title">Similar plugins you might like</div><div class="similar-grid">';
      similar.forEach(function (s) {
        html += similarCardHtml(s, 'similar-card');
      });
      html += '</div></div>';
    }
    html += '</div>';
    return html;
  }

  // Compact, table-row-scale dossier -- its own function rather than a
  // CSS-only restyle of dossierBodyHtml(), because the reference layout
  // (inline header, Details panel pinned right, small stat tiles) isn't
  // just a smaller version of the Field-mode page, it's a different
  // arrangement. Same real fields, same helpers (gapText/growthMarkup/
  // growthFactLine/marketplaceId/platformOf/pricingLabel/CAT_BY_KEY) --
  // no new data invented for this. Deliberately omits: the demo GIF
  // (would dominate a table row), and anything the reference image
  // showed that isn't real curated data here (tags, a screenshot, a
  // Key Features checklist, Resources links) -- see the CSS comment
  // above .tbl-dossier for the full reasoning.
  function tableDossierBodyHtml(p) {
    var isPending = p.downloads === null;
    var pr = pricingLabel(p.pricing, isPending);
    var cat = CAT_BY_KEY[p.categoryKey];
    var mpId = marketplaceId(p);

    var similar = plugins
      .filter(function (o) { return o.repo !== p.repo && o.categoryKey === p.categoryKey; })
      .sort(function (a, b) { return (b.downloads || 0) - (a.downloads || 0); })
      .slice(0, 4);

    var html = '<div class="tbl-dossier">';

    html += '<div class="tbl-head">';
    html += '<div class="tbl-intro"><div class="tbl-title-row"><h3>' + esc(p.name) + '</h3>' +
      '<span class="chip ' + pr.cls + '">' + esc(pr.text) + '</span>' +
      '<span class="chip" style="background:color-mix(in srgb, ' + cat.color + ' 20%, transparent); color:' + cat.color + '">' + esc(cat.label) + '</span></div>' +
      '<div class="tbl-niche">' + esc(p.niche) + '</div>' +
      '<div class="tbl-pitch">' + mdInline(p.pitch || '—') + '</div></div>';
    html += '<div class="tbl-links">';
    if (p.marketplaceUrl) html += '<a class="btn primary" href="' + esc(safeUrl(p.marketplaceUrl)) + '" target="_blank" rel="noopener"><span class="btn-icon">' + ICONS.jetbrains + '</span>Install on JetBrains ↗</a>';
    html += '<a class="btn" href="' + esc(safeUrl(p.githubUrl)) + '" target="_blank" rel="noopener"><span class="btn-icon">' + ICONS.github + '</span>View on GitHub ↗</a>';
    var vsxMatchTbl = vsxByRepo[p.repo];
    if (vsxMatchTbl) html += '<a class="btn" href="' + esc(safeUrl(vsxMatchTbl.marketplaceUrl)) + '" target="_blank" rel="noopener"><span class="btn-icon">' + ICONS.vscode + '</span>Download for VS Code ↗</a>';
    html += '</div>';
    html += '</div>';

    html += '<div class="tbl-stats">';
    html += '<div class="tbl-stat"><div class="ts-icon">↓</div><div><div class="ts-num">' + (isPending ? '—' : p.downloads.toLocaleString('en-US')) + (isPending ? '' : growthMarkup(p)) + '</div><div class="ts-label">Downloads</div></div></div>';
    html += '<div class="tbl-stat"><div class="ts-icon">⌥</div><div><div class="ts-num">' + (p.stars != null ? p.stars : '—') + '</div><div class="ts-label">GitHub ★</div></div></div>';
    html += '<div class="tbl-stat"><div class="ts-icon">▤</div><div><div class="ts-num">' + (p.firstPublished || '—') + '</div><div class="ts-label">Published</div></div></div>';
    html += '</div>';

    html += '<div class="tbl-body">';
    html += '<div class="tbl-block"><div class="ib-head"><span class="ib-icon gap">!</span><span class="ib-title">The Gap</span></div>' +
      '<div class="ib-body">' + mdInline(gapText(p)) + '</div></div>';
    html += '<div class="tbl-block"><div class="ib-head"><span class="ib-icon fix">✓</span><span class="ib-title">The Fix</span></div>' +
      '<div class="ib-body">' + mdInline(p.pitch || '—') + '</div></div>';
    html += '</div>';

    html += '<div class="tbl-block tbl-details"><div class="ib-head"><span class="ib-icon facts">⚙</span><span class="ib-title">Details</span></div><ul class="tbl-details-list">' +
      '<li><span class="fk">Category</span><span class="fv">' + esc(cat.label) + '</span></li>' +
      '<li><span class="fk">Pricing</span><span class="fv">' + esc(pr.text) + '</span></li>' +
      '<li><span class="fk">Platform</span><span class="fv">' + esc(platformOf(p)) + '</span></li>' +
      '<li><span class="fk">First published</span><span class="fv">' + (p.firstPublished || '—') + '</span></li>' +
      '<li><span class="fk">Marketplace ID</span><span class="fv">' + (mpId ? '#' + esc(mpId) : (isPending ? 'Pending' : '—')) + '</span></li>' +
      '<li><span class="fk">Repository</span><span class="fv"><code>' + esc(p.repo) + '</code><button type="button" class="copy-btn" data-copy="' + esc(p.repo) + '" aria-label="Copy repository name">' + ICONS.copy + '</button></span></li>' +
      '<li><span class="fk">Growth</span><span class="fv">' + esc(growthFactLine(p)) + '</span></li>' +
      '</ul></div>';

    if (similar.length) {
      html += '<div class="tbl-similar"><div class="tbl-similar-title">Similar plugins you might like</div><div class="tbl-similar-grid">';
      similar.forEach(function (s) {
        html += similarCardHtml(s, 'tbl-similar-card');
      });
      html += '</div></div>';
    }

    html += '</div>';
    return html;
  }

  // Wires the "similar plugin" cards inside a just-rendered dossier --
  // Field mode's full-page dossier uses .similar-card, the table row's
  // own compact layout uses .tbl-similar-card (2026-08-16, since the
  // table row expand stopped sharing markup with Field mode); both are
  // wired here since the click behavior is identical either way.
  // Switching to a similar plugin from EITHER context just changes
  // selectedRepo and re-renders in the CURRENT mode, so from a table
  // row it re-opens as a different table row rather than jumping the
  // user into Field mode.
  function wireDossierInteractions(container, p) {
    var gif = container.querySelector('.dossier-gif');
    if (gif) gif.addEventListener('error', function () { gif.remove(); });
    if (p && p.downloads !== null) {
      var dlNum = container.querySelector('#dossierDlNum');
      if (dlNum) decodeNumber(dlNum, p.downloads.toLocaleString('en-US'));
    }
    var copyBtn = container.querySelector('.copy-btn');
    if (copyBtn && navigator.clipboard && navigator.clipboard.writeText) {
      copyBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        var text = copyBtn.getAttribute('data-copy');
        navigator.clipboard.writeText(text).then(function () {
          if (copyBtn.dataset.copied) return;
          var original = copyBtn.innerHTML;
          copyBtn.innerHTML = ICONS.copyCheck;
          copyBtn.classList.add('copied');
          copyBtn.dataset.copied = '1';
          setTimeout(function () {
            copyBtn.innerHTML = original;
            copyBtn.classList.remove('copied');
            delete copyBtn.dataset.copied;
          }, 1400);
        }).catch(function () {});
      });
    }
    Array.prototype.forEach.call(container.querySelectorAll('.similar-card, .tbl-similar-card'), function (card) {
      var open = function (e) {
        if (e) e.stopPropagation(); // don't also trigger the table row's own click-to-toggle
        setSelectedRepo(card.getAttribute('data-repo'), true);
      };
      card.addEventListener('click', open);
      // Bug fixed 2026-08-23 (audit finding): these cards were mouse-only
      // -- role="button"/tabindex="0" now added in the markup (see
      // dossierBodyHtml) but that alone doesn't give a plain <div> real
      // button activation, same gap .plugin-card had until 2026-08-21
      // (see its own keydown handler above). Space also preventDefault's
      // its default page-scroll behavior here for the same reason.
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          open(e);
        }
      });
    });
  }

  // Panel de detalle fijo (Fase 5b) -- ya no reemplaza #fieldMain,
  // se monta en #fieldDetail al lado de la grilla. wireDossierInteractions()
  // y el resto del contenido (dossierBodyHtml()) no cambiaron.
  function renderDossier(p) {
    var html = '<div class="dossier-enter">' + dossierBodyHtml(p) + '</div>';
    var detail = document.getElementById('fieldDetail');
    var row = document.getElementById('fieldRow');
    detail.innerHTML = html;
    detail.hidden = false;
    if (row) row.classList.add('has-detail');

    document.getElementById('dossierBack').addEventListener('click', function () {
      setSelectedRepo(null, false);
    });
    wireDossierInteractions(detail, p);
  }

  function closeDossier() {
    var detail = document.getElementById('fieldDetail');
    var row = document.getElementById('fieldRow');
    if (detail) { detail.hidden = true; detail.innerHTML = ''; }
    if (row) row.classList.remove('has-detail');
  }

  function renderField() {
    // renderGrid() corre siempre ahora -- antes selectedRepo hacía que
    // renderDossier() reemplazara la grilla entera; el hash routing
    // (setSelectedRepo/syncHashToState) no se tocó, "cerrar" el panel
    // ya es la conducta correcta sin cambios ahí.
    renderGrid();
    if (selectedRepo) {
      var p = byRepo(selectedRepo);
      if (p) { renderDossier(p); return; }
    }
    closeDossier();
  }

  // ---- Table mode (unchanged logic, restyled) -------------------------
  function renderTable() {
    var rows = sortedFiltered();
    var tbody = document.getElementById('tbody');
    var noResults = document.getElementById('noResults');
    var pagerHost = document.getElementById('tablePager');

    if (rows.length === 0) {
      tbody.innerHTML = '';
      noResults.style.display = 'block';
      if (pagerHost) pagerHost.innerHTML = '';
      return;
    }
    noResults.style.display = 'none';
    if (selectedRepo) ensurePageForRepo(rows, selectedRepo);
    var pageRows = pagedRows(rows);

    var html = '';
    pageRows.forEach(function (p) {
      var isPending = p.downloads === null;
      var pr = pricingLabel(p.pricing, isPending);
      var isOpen = selectedRepo === p.repo;
      html += '<tr class="row" data-repo="' + esc(p.repo) + '" role="button" tabindex="0" aria-expanded="' + (isOpen ? 'true' : 'false') + '" aria-label="' + esc(p.name) + ' details">';
      html += '<td class="name-cell"><div class="plugin-name">' + esc(p.name) + (p.verified ? '<span class="verified-mark" role="img" aria-label="Verified vendor" title="Verified vendor">✓</span>' : '') + '</div><div class="niche">' + esc(p.niche) + '</div></td>';
      html += '<td class="num-cell" data-label="Downloads">' + (isPending ? '—' : p.downloads.toLocaleString('en-US')) + (isPending ? '' : growthMarkup(p)) + '</td>';
      html += '<td class="num-cell tbl-optional" data-label="Reviews">' + (p.reviews === null ? '—' : p.reviews) + '</td>';
      html += '<td class="num-cell tbl-optional" data-label="Rating">' + (p.rating != null ? p.rating.toFixed(2) : '—') + '</td>';
      html += '<td class="num-cell" data-label="GitHub ★">' + (p.stars != null ? p.stars : '—') + '</td>';
      html += '<td data-label="Pricing"><span class="chip ' + pr.cls + '">' + esc(pr.text) + '</span></td>';
      html += '<td class="num-cell" data-label="Published" style="text-align:left">' + (p.firstPublished || '—') + '</td>';
      html += '</tr>';
      html += '<tr class="expand-row"><td colspan="7"><div class="expand-inner' + (isOpen ? ' open' : '') + '" id="exp-' + esc(p.repo) + '">';
      // Own compact layout (tableDossierBodyHtml, 2026-08-16), not the
      // Field-mode dossier -- only actually built for the currently
      // OPEN row (isOpen), so closed rows stay cheap even with all 34
      // present in the table.
      if (isOpen) {
        html += '<button type="button" class="dossier-close" data-repo="' + esc(p.repo) + '" aria-label="Close">✕</button>';
        html += tableDossierBodyHtml(p);
      }
      html += '</div></td></tr>';
    });
    tbody.innerHTML = html;

    Array.prototype.forEach.call(tbody.querySelectorAll('tr.row'), function (tr) {
      var toggle = function () {
        var repo = tr.getAttribute('data-repo');
        var opening = selectedRepo !== repo; // false when this click is closing an already-open row
        setSelectedRepo(opening ? repo : null, opening);
      };
      tr.addEventListener('click', toggle);
      // Same keyboard-activation gap as .plugin-card above (role="button"
      // tabindex="0" on a <tr> doesn't get free Enter/Space handling the
      // way a real <button> would) -- added 2026-08-21 alongside that fix.
      tr.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggle();
        }
      });
    });
    Array.prototype.forEach.call(tbody.querySelectorAll('.dossier-close'), function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        setSelectedRepo(null, false);
      });
    });
    wireDossierInteractions(tbody, selectedRepo ? byRepo(selectedRepo) : null);
    if (pagerHost) {
      pagerHost.innerHTML = pagerHtml(rows.length);
      wirePager(pagerHost, rows.length);
    }
  }

  // Added 2026-08-21: opening a plugin (Field dossier, a Table row's
  // inline expand, or jumping to a "similar" plugin from either) used to
  // leave the viewport wherever it already was -- if that plugin's card/
  // row sat low on the page, its dossier content rendered mostly or
  // fully below the fold, so the info the click was FOR wasn't visible
  // without an extra manual scroll. Called right after renderAll() at
  // every real "open" site (never on close/toggle-off), once the new
  // DOM for that repo actually exists. 'nearest' (not 'start') so an
  // element already fully in view doesn't jump unnecessarily -- only
  // scrolls when the top of the newly-opened content isn't visible.
  function scrollCatalogIntoView() {
    var target = mode === 'table'
      ? document.getElementById('tableView')
      : document.getElementById('fieldMain');
    if (!target) return;
    target.scrollIntoView({
      behavior: PREFERS_REDUCED_MOTION ? 'auto' : 'smooth',
      block: 'start'
    });
  }

  function scrollSelectedIntoView(instant) {
    if (!selectedRepo) return;
    var behavior = (instant || PREFERS_REDUCED_MOTION) ? 'auto' : 'smooth';
    // Field mode: renderDossier() replaces #fieldMain's ENTIRE contents
    // with the opened plugin's dossier, so #fieldMain itself is the
    // unambiguous target -- a plain [data-repo=...] selector would be
    // ambiguous here (a "similar plugin" card inside that same dossier
    // carries the SAME data-repo value as the card that opened it once
    // the user later reopens it from elsewhere).
    // block:'start' (not 'nearest') -- 'nearest' only scrolls when the
    // element is judged off-screen, and even then doesn't promise the
    // element's own top lands under the sticky topbar; it can stop
    // wherever "nearest" happens to be. 'start' + the scroll-margin-top
    // above (72px, matching .topbar's real height) is what actually
    // guarantees the opened dossier/row's top sits flush under the
    // header on both desktop and phone, every time -- the exact
    // alignment bug reported live via screenshot. 2026-08-23.
    var fieldMain = document.getElementById('fieldMain');
    if (mode === 'field' && fieldMain) {
      fieldMain.scrollIntoView({ behavior: behavior, block: 'start' });
      return;
    }
    // Table mode: the row itself IS the right anchor, and tr.row is the
    // one place data-repo is guaranteed unique per repo in this view.
    var row = document.querySelector('tr.row[data-repo="' + selectedRepo + '"]');
    if (row) row.scrollIntoView({ behavior: behavior, block: 'start' });
  }

  // Added 2026-08-21: the browser tab title never changed from the
  // static "Gap Hunter Labs — Plugin Intelligence" no matter what was
  // open -- with several plugin dossiers or catalog tabs open at once,
  // every tab read identically, so there was no way to tell them apart
  // without clicking through each one. Driven from renderAll() (the one
  // real state-sync point every open/close/filter action already routes
  // through) instead of being set at each individual open/close call
  // site -- guarantees the title can never drift from the real
  // selectedRepo state, and Table mode's toggle-closed case (which
  // reuses the same click handler as toggle-open) doesn't need its own
  // separate title-reset logic.
  var BASE_TITLE = document.title;
  function updateDocumentTitle() {
    if (selectedRepo) {
      var p = byRepo(selectedRepo);
      document.title = p ? (p.name + ' — Gap Hunter Labs') : BASE_TITLE;
    } else {
      document.title = BASE_TITLE;
    }
  }

  // Deep-linking via URL hash, added 2026-08-23 (indexing audit): before
  // this, opening a plugin's dossier only mutated in-memory JS state
  // (selectedRepo) and document.title -- the URL never changed, so
  // there was no way to bookmark, share, or crawl-link to a specific
  // plugin; every one of the 43 possible dossier states was invisible
  // to search and impossible to reload back into. history.replaceState
  // (not pushState) is deliberate: this just keeps the CURRENT url in
  // sync with state, it does not create a new back-button history entry
  // per click -- the existing "Back to catalog"/dossier-close controls
  // already handle in-app navigation, stacking a pushState per open
  // would make the browser back button behave unexpectedly (one step
  // per plugin viewed, not one step per real navigation action).
  // Repository slugs use the page fragment so dossier links remain
  // bookmarkable and shareable without adding another route.
  function syncHashToState() {
    var target = selectedRepo ? ('#' + selectedRepo) : (location.pathname + location.search);
    if (location.hash !== (selectedRepo ? '#' + selectedRepo : '')) {
      history.replaceState(null, '', target);
    }
  }

  function renderAll() {
    updateDocumentTitle();
    syncHashToState();

    document.getElementById('categoryFilter').value = filterCategory;
    updateCategoryBoard();

    document.getElementById('fieldView').style.display = mode === 'field' ? 'grid' : 'none';
    document.getElementById('tableView').style.display = mode === 'table' ? 'block' : 'none';

    if (mode === 'field') renderField();
    else renderTable();
  }

  // Field <-> Table: switch immediately. No loading overlay.
  function switchMode(newMode, btn) {
    if (newMode === mode) return;
    Array.prototype.forEach.call(document.querySelectorAll('#modeToggle button'), function (b) {
      var isActive = b === btn || b.getAttribute('data-mode') === newMode;
      b.classList.toggle('active', isActive);
      b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });
    mode = newMode;
    renderAll();
    if (selectedRepo) scrollSelectedIntoView();
  }

  document.getElementById('modeToggle').addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-mode]');
    if (!btn) return;
    switchMode(btn.getAttribute('data-mode'), btn);
  });

  // Control bar compacta en mobile (a pedido explícito 2026-09-10):
  // la lupa expande/colapsa el campo de búsqueda (el resto se
  // desvanece mientras está abierto), el botón "Filters" abre un
  // popover con los 2 <select> reales -- ninguno de los dos hace nada
  // en escritorio (ambos botones son display:none ahí, ver CSS), así
  // que este bloque es inerte fuera del breakpoint mobile.
  (function () {
    var controls = document.getElementById('controls');
    var searchToggle = document.getElementById('searchToggle');
    var searchInput = document.getElementById('searchInput');
    var filtersToggle = document.getElementById('filtersToggle');
    var filtersPanel = document.getElementById('filtersPanel');
    if (!controls || !searchToggle || !filtersToggle || !filtersPanel) return;

    function closeFilters() {
      filtersPanel.classList.remove('is-open');
      filtersToggle.setAttribute('aria-expanded', 'false');
    }
    function closeSearch() {
      controls.classList.remove('is-searching');
      searchToggle.setAttribute('aria-expanded', 'false');
    }

    searchToggle.addEventListener('click', function () {
      var opening = !controls.classList.contains('is-searching');
      controls.classList.toggle('is-searching', opening);
      searchToggle.setAttribute('aria-expanded', opening ? 'true' : 'false');
      closeFilters();
      if (opening) {
        searchInput.focus();
      } else {
        searchInput.blur();
      }
    });

    filtersToggle.addEventListener('click', function () {
      var opening = !filtersPanel.classList.contains('is-open');
      filtersPanel.classList.toggle('is-open', opening);
      filtersToggle.setAttribute('aria-expanded', opening ? 'true' : 'false');
      if (opening) closeSearch();
    });

    document.addEventListener('click', function (e) {
      if (!controls.contains(e.target)) closeFilters();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      if (controls.classList.contains('is-searching')) closeSearch();
      if (filtersPanel.classList.contains('is-open')) closeFilters();
    });
  })();

  Array.prototype.forEach.call(document.querySelectorAll('thead th'), function (th) {
    var sort = function () {
      var key = th.getAttribute('data-key');
      if (sortKey === key) {
        sortDir *= -1;
      } else {
        sortKey = key;
        sortDir = (key === 'name' || key === 'pricing' || key === 'firstPublished') ? 1 : -1;
      }
      Array.prototype.forEach.call(document.querySelectorAll('thead th'), function (t) {
        t.classList.remove('sorted');
        t.querySelector('.arrow') && t.querySelector('.arrow').remove();
        t.setAttribute('aria-sort', 'none');
      });
      th.classList.add('sorted');
      th.setAttribute('aria-sort', sortDir === 1 ? 'ascending' : 'descending');
      var arrow = document.createElement('span');
      arrow.className = 'arrow';
      arrow.textContent = sortDir === 1 ? '▲' : '▼';
      th.appendChild(arrow);
      renderAll();
      var tbody = document.getElementById('tbody');
      if (tbody) {
        tbody.classList.remove('just-sorted');
        void tbody.offsetWidth; // Force reflow so the CSS animation restarts.
        tbody.classList.add('just-sorted');
      }
    };
    th.addEventListener('click', sort);
    th.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        sort();
      }
    });
  });

  var searchDebounceTimer = null;
  document.getElementById('searchInput').addEventListener('input', function (e) {
    var val = e.target.value;
    if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(function () {
      filterText = val.trim().toLowerCase();
      catalogPage = 1;
      renderAll();
    }, 120);
  });
  document.getElementById('pricingFilter').addEventListener('change', function (e) {
    filterPricing = e.target.value;
    catalogPage = 1;
    renderAll();
  });

  // one-time: build the category <select> options + attach its change
  // listener. NOT called from renderAll()/renderField() -- the option
  // list is static (same 8 categories every render), only the SELECTED
  // value needs to stay in sync on every render, handled separately in
  // renderAll() via categoryFilter.value = filterCategory. Populating +
  // re-attaching a listener on every render would stack duplicate
  // 'change' handlers instead of replacing them.
  renderCatalogStats();
  populateCategorySelect();
  wireCategorySelect();
  wireCategoryBoard();

  // Initial deep-link read: if the page was loaded/reloaded/shared with
  // a #repo-slug hash already in the URL, open straight to that
  // plugin's dossier instead of always starting on the plain catalog.
  // byRepo() is the same lookup renderDossier()/etc already use
  // elsewhere -- an unrecognized or empty hash just leaves
  // selectedRepo null, same as today's default.
  (function initialHashRepo() {
    var slug = location.hash.replace(/^#/, '');
    if (slug && byRepo(slug)) selectedRepo = slug;
  })();

  // Back/forward + externally-changed hash support: if something other
  // than this page's own syncHashToState() changes location.hash (the
  // browser's own back/forward buttons after a deep link, or a user
  // manually editing the URL), reflect it into selectedRepo and
  // re-render. Guarded against re-triggering our OWN replaceState calls
  // by checking the hash actually still differs from the current state
  // -- replaceState doesn't fire 'hashchange' by spec, but this guard
  // keeps the handler correct even if that ever changes.
  window.addEventListener('hashchange', function () {
    var slug = location.hash.replace(/^#/, '');
    // Only touch selectedRepo when the hash is empty or a real plugin
    // repository slug. Unknown fragments are left alone.
    if (slug !== '' && !byRepo(slug)) return;
    var next = slug ? slug : null;
    if (next !== selectedRepo) {
      selectedRepo = next;
      renderAll();
      if (selectedRepo) scrollSelectedIntoView();
    }
  });

  renderAll();
  if (selectedRepo) {
    scrollSelectedIntoView(true);
    window.addEventListener('load', function () {
      if (selectedRepo) scrollSelectedIntoView(true);
    });
  }

  (function initCatalogTopbar() {


    var burger = document.getElementById('topbarBurger');
    var topbar = document.getElementById('topbar');
    if (burger && topbar) {
      burger.addEventListener('click', function () {
        var open = topbar.classList.toggle('nav-open');
        burger.setAttribute('aria-expanded', String(open));
      });
    }
  })();

  // Fade el logo del pie del sidebar cuando el <footer> real entra en
  // viewport (ver comentario en css/shell.css).
  (function () {
    var siteFooter = document.querySelector('.site-footer');
    var sidebarFooter = document.querySelector('.sidebar-footer');
    if (siteFooter && sidebarFooter && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          sidebarFooter.classList.toggle('is-near-footer', entry.isIntersecting);
        });
      }).observe(siteFooter);
    }
  })();

}).catch(function () {
  var main = document.getElementById('fieldMain');
  if (!main) return;
  main.innerHTML =
    '<section class="load-error" role="alert" aria-labelledby="catalogLoadErrorTitle">' +
      '<h2 id="catalogLoadErrorTitle">Catalog data could not be loaded</h2>' +
      '<p>Retry this page, or browse all Gap Hunter Labs plugins on JetBrains Marketplace.</p>' +
      '<div class="load-error-actions">' +
        '<button type="button" class="btn primary" id="catalogRetry">Retry</button>' +
        '<a class="btn" href="https://plugins.jetbrains.com/vendor/gap-hunter-labs">Open JetBrains Marketplace ↗</a>' +
      '</div>' +
    '</section>';
  var retry = document.getElementById('catalogRetry');
  if (retry) retry.addEventListener('click', function () { location.reload(); });
});
})();
