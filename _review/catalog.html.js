
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
  'use strict';
  // Fase 2 del SuperPlan de SEO (2026-09-22): la grilla y la tabla ya
  // llegan pre-renderizadas en el HTML crudo -- pipeline/build_catalog_grid.py
  // escribe las 146 tarjetas/filas reales entre los marcadores
  // PRERENDER:*, cada una un <a href="/catalog/<repo>/"> real. Este script
  // NUNCA construye HTML de tarjetas/filas: solo oculta (hidden), reordena
  // (appendChild sobre nodos que ya existen) y pagina sobre esos nodos.
  // Filtrar/ordenar/paginar/buscar ya no dependen de data/catalog-data.json
  // ni de js/catalog-shared.js -- por eso esta pagina no los carga.
  var PAGE_SIZE = 15;
  var sortKey = 'downloads';
  var sortDir = -1; // desc
  var filterText = '';
  var filterPricing = '';
  var mode = 'field';
  var catalogPage = 1;

  var board = document.querySelector('.cat-board');
  var knownCats = board
    ? Array.prototype.map.call(board.querySelectorAll('[data-cat]'), function (b) { return b.getAttribute('data-cat'); })
    : [];
  var categoryParam = new URLSearchParams(location.search).get('category') || '';
  var filterCategory = knownCats.indexOf(categoryParam) !== -1 ? categoryParam : '';

  var gridEl = document.getElementById('catalogGrid');
  var gridPagerHost = document.getElementById('fieldPager');
  var gridCards = gridEl ? Array.prototype.slice.call(gridEl.children) : [];
  var tbody = document.getElementById('tbody');
  var tableRows = tbody ? Array.prototype.slice.call(tbody.children) : [];
  var noResults = document.getElementById('noResults');
  var tablePagerHost = document.getElementById('tablePager');

  var PREFERS_REDUCED_MOTION = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function numOrNull(str) {
    return (str === undefined || str === '') ? null : parseFloat(str);
  }

  function matches(el) {
    var isPending = el.hasAttribute('data-pending');
    if (filterPricing) {
      if (filterPricing === 'PENDING' && !isPending) return false;
      if (filterPricing !== 'PENDING' && (el.dataset.pricing || '') !== filterPricing) return false;
    }
    if (filterCategory && el.dataset.cat !== filterCategory) return false;
    if (!filterText) return true;
    return (el.dataset.search || '').indexOf(filterText) !== -1;
  }

  // Mismo criterio que el catalogo tenia en JS puro: un valor ausente
  // (null/undefined) siempre queda al final, sin importar la direccion.
  function cmp(a, b) {
    var av, bv;
    if (sortKey === 'name') {
      av = a.dataset.name; bv = b.dataset.name;
    } else if (sortKey === 'pricing') {
      av = a.dataset.pricing || null; bv = b.dataset.pricing || null;
    } else if (sortKey === 'firstPublished') {
      av = a.dataset.firstpublished || null; bv = b.dataset.firstpublished || null;
    } else {
      av = numOrNull(a.dataset[sortKey]); bv = numOrNull(b.dataset[sortKey]);
    }
    var an = (av === null || av === undefined || av === '');
    var bn = (bv === null || bv === undefined || bv === '');
    if (an && bn) return 0;
    if (an) return 1;
    if (bn) return -1;
    if (av < bv) return -1 * sortDir;
    if (av > bv) return 1 * sortDir;
    return 0;
  }

  function pagerHtml(total) {
    var pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (pages <= 1) return '';
    return '<nav class="catalog-pager" aria-label="Catalog pages">' +
      '<button type="button" class="btn catalog-pager-btn" data-page-dir="-1" aria-label="Previous page"' + (catalogPage <= 1 ? ' disabled' : '') + '>Previous</button>' +
      '<span class="catalog-pager-status" aria-live="polite">Page ' + catalogPage + ' of ' + pages + '</span>' +
      '<button type="button" class="btn catalog-pager-btn" data-page-dir="1" aria-label="Next page"' + (catalogPage >= pages ? ' disabled' : '') + '>Next</button>' +
      '</nav>';
  }

  function wirePager(host, total, onChange) {
    if (!host) return;
    host.innerHTML = pagerHtml(total);
    Array.prototype.forEach.call(host.querySelectorAll('[data-page-dir]'), function (btn) {
      btn.addEventListener('click', function () {
        var pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
        var dir = parseInt(btn.getAttribute('data-page-dir'), 10);
        catalogPage = Math.min(pages, Math.max(1, catalogPage + dir));
        onChange();
        scrollCatalogIntoView();
      });
    });
  }

  // Filtra (hidden), ordena (reordena los nodos YA existentes con
  // appendChild -- nunca reconstruye innerHTML) y pagina sobre una lista
  // de nodos pre-renderizados. Devuelve cuantos quedaron visibles tras el
  // filtro (antes de paginar), para el mensaje de "sin resultados" y el
  // paginador.
  function applyToNodes(container, allNodes) {
    var visible = allNodes.filter(matches);
    visible.sort(cmp);
    visible.forEach(function (el) { container.appendChild(el); });
    var pages = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
    if (catalogPage > pages) catalogPage = pages;
    if (catalogPage < 1) catalogPage = 1;
    var start = (catalogPage - 1) * PAGE_SIZE;
    allNodes.forEach(function (el) { el.hidden = true; });
    for (var i = start; i < Math.min(start + PAGE_SIZE, visible.length); i++) visible[i].hidden = false;
    return visible.length;
  }

  function renderGrid() {
    if (!gridEl) return;
    var total = applyToNodes(gridEl, gridCards);
    var noResultsEl = document.getElementById('fieldNoResults');
    if (noResultsEl) noResultsEl.hidden = total !== 0;
    wirePager(gridPagerHost, total, renderGrid);
  }

  function renderTable() {
    if (!tbody) return;
    var total = applyToNodes(tbody, tableRows);
    if (noResults) noResults.style.display = total === 0 ? 'block' : 'none';
    wirePager(tablePagerHost, total, renderTable);
  }

  function updateCategoryBoard() {
    if (!board) return;
    Array.prototype.forEach.call(board.querySelectorAll('.cat-cell'), function (btn) {
      var cat = btn.getAttribute('data-cat') || '';
      var active = cat === '' ? !filterCategory : filterCategory === cat;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
  }

  function renderAll() {
    var sel = document.getElementById('categoryFilter');
    if (sel) sel.value = filterCategory;
    updateCategoryBoard();
    document.getElementById('fieldView').style.display = mode === 'field' ? 'grid' : 'none';
    document.getElementById('tableView').style.display = mode === 'table' ? 'block' : 'none';
    if (mode === 'field') renderGrid();
    else renderTable();
  }

  function scrollCatalogIntoView() {
    var target = mode === 'table' ? document.getElementById('tableView') : document.getElementById('fieldMain');
    if (!target) return;
    target.scrollIntoView({ behavior: PREFERS_REDUCED_MOTION ? 'auto' : 'smooth', block: 'start' });
  }

  function switchMode(newMode, btn) {
    if (newMode === mode) return;
    Array.prototype.forEach.call(document.querySelectorAll('#modeToggle button'), function (b) {
      var isActive = b === btn || b.getAttribute('data-mode') === newMode;
      b.classList.toggle('active', isActive);
      b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });
    mode = newMode;
    catalogPage = 1;
    renderAll();
  }

  document.getElementById('modeToggle').addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-mode]');
    if (!btn) return;
    switchMode(btn.getAttribute('data-mode'), btn);
  });

  // Control bar compacta en mobile (a pedido explicito 2026-09-10): la
  // lupa expande/colapsa el campo de busqueda, "Filters" abre un popover
  // con los 2 <select> reales -- inerte fuera del breakpoint mobile.
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
      if (opening) searchInput.focus(); else searchInput.blur();
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

  Array.prototype.forEach.call(document.querySelectorAll('thead th[data-key]'), function (th) {
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
      if (tbody) {
        tbody.classList.remove('just-sorted');
        void tbody.offsetWidth; // fuerza el reflow para reiniciar la animacion CSS
        tbody.classList.add('just-sorted');
      }
    };
    th.addEventListener('click', sort);
    th.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); sort(); }
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
  var categoryFilterSelect = document.getElementById('categoryFilter');
  if (categoryFilterSelect) {
    categoryFilterSelect.addEventListener('change', function (e) {
      filterCategory = e.target.value;
      catalogPage = 1;
      renderAll();
    });
  }
  if (board) {
    board.addEventListener('click', function (e) {
      var btn = e.target.closest('.cat-cell');
      if (!btn || !board.contains(btn)) return;
      var cat = btn.getAttribute('data-cat') || '';
      filterCategory = (!cat || filterCategory === cat) ? '' : cat;
      catalogPage = 1;
      renderAll();
      // Este tablero vive pegado arriba de la grilla -- sin
      // scrollCatalogIntoView() a proposito, mismo criterio que antes.
    });
  }

  // Toda la fila navega al plugin (el nombre ya es un <a> real -- esto
  // solo extiende el area de click a la fila completa, por comodidad de
  // mouse). Ctrl/Cmd/Shift/click-derecho/click-de-rueda se dejan pasar
  // sin interferir para que abrir en pestaña nueva siga funcionando.
  if (tbody) {
    tbody.addEventListener('click', function (e) {
      if (e.defaultPrevented || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
      if (e.target.closest('a')) return;
      var row = e.target.closest('tr.row');
      if (!row) return;
      var repo = row.getAttribute('data-repo');
      if (repo) location.href = '/catalog/' + repo + '/';
    });
  }

  renderAll();

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
})();
