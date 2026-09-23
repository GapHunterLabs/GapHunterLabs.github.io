
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
  var PREFERS_REDUCED_MOTION = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  GapCatalog.ready.then(function (shared) {
    var data = shared.data;
    var plugins = shared.plugins;
    var CATEGORIES = shared.CATEGORIES;
    var CAT_BY_KEY = shared.CAT_BY_KEY;
    var ICONS = shared.ICONS;
    var GIF_URL = shared.GIF_URL;
    var esc = shared.esc;
    var statsDecoded = false;

    function renderStats() {
      document.getElementById('heroSubtitle').textContent = 'We hunt real, evidence-based gaps in developer tooling and ship focused IntelliJ-family plugins to fix them. Every one of the ' + data.totalPlugins + ' products in this catalog exists because of a documented complaint, its fix traces to a real diff, and its traction to real download numbers pulled straight from JetBrains Marketplace and GitHub — nothing here is estimated.';
      var base = 0, current = 0;
      plugins.forEach(function (p) { if (p.growthFrom != null && p.downloads != null) { base += p.growthFrom; current += p.downloads; } });
      var growth = base > 0 ? '<span class="stat-growth">▲ ' + (((current - base) / base) * 100).toFixed(1) + '%</span>' : '';
      document.getElementById('stats').innerHTML =
        '<div class="tele-row"><span class="tele-icon" style="color:var(--accent)">' + ICONS.plugins + '</span><div class="tele-body"><div class="tele-num accent">' + data.totalPlugins + '</div><div class="tele-label">Plugins active</div></div></div>' +
        '<div class="tele-row"><span class="tele-icon" style="color:var(--good)">' + ICONS.downloads + '</span><div class="tele-body"><div class="tele-num">' + data.totalDownloads.toLocaleString('en-US') + growth + '</div><div class="tele-label">Downloads</div></div></div>';
      var facts = [];
      if (data.totalReviews > 0) facts.push([data.totalReviews, 'Reviews total']);
      if (data.avgRating != null) facts.push([data.avgRating.toFixed(2), 'Avg rating']);
      if (data.totalStars > 0) facts.push([data.totalStars, 'GitHub stars']);
      document.getElementById('methodFacts').innerHTML = facts.map(function (f) { return '<div class="method-fact"><div class="method-fact-num">' + f[0] + '</div><div class="method-fact-label">' + f[1] + '</div></div>'; }).join('');

      var footerStatus = document.getElementById('footerStatusText');
      if (footerStatus) footerStatus.textContent = data.totalPlugins + ' plugins tracked';
    }

    function renderCategories() {
      var counts = {};
      plugins.forEach(function (p) { counts[p.categoryKey] = (counts[p.categoryKey] || 0) + 1; });
      document.getElementById('categoryPreview').innerHTML = CATEGORIES.filter(function (c) { return c.key !== 'other'; }).map(function (c) {
        return '<a class="cat-cell" href="/catalog/?category=' + c.key + '" style="--cat:' + c.color + '"><span class="cat-cell-icon">' + shared.catIconHtml(c.key) + '</span><span class="cat-cell-copy"><strong>' + esc(c.label) + '</strong><span class="cat-cell-count">' + (counts[c.key] || 0) + ' plugins</span></span><span class="cat-cell-arrow" aria-hidden="true">&rarr;</span></a>';
      }).join('');
    }

    function initHeroSlider() {
      var root = document.getElementById('heroSlider'), track = document.getElementById('heroSliderTrack'), dots = document.getElementById('heroSliderDots');
      var prev = document.getElementById('heroSliderPrev'), next = document.getElementById('heroSliderNext');
      if (!root || !track || !dots || !prev || !next) return;
      var featured = plugins.filter(function (p) { return GIF_URL[p.repo]; }).sort(function (a,b) { return (b.downloads || 0) - (a.downloads || 0); }).slice(0,5);
      var index = 0, timer;
      track.innerHTML = featured.map(function (p,i) { return '<a class="hs-slide" href="/catalog/#' + encodeURIComponent(p.repo) + '"' + (i ? ' tabindex="-1"' : '') + '><span class="hs-media"><img src="' + esc(GIF_URL[p.repo]) + '" alt="" width="640" height="360"></span><span class="hs-copy"><span class="hs-kicker">Featured</span><span class="hs-name">' + esc(p.name) + '</span><span class="hs-niche">' + esc(p.niche || '') + '</span></span></a>'; }).join('');
      dots.innerHTML = featured.map(function (p,i) { return '<button type="button" class="hs-dot' + (i ? '' : ' is-active') + '" aria-label="Show ' + esc(p.name) + '"></button>'; }).join('');
      function go(n) { index = (n + featured.length) % featured.length; track.style.transform = 'translateX(-' + index * 100 + '%)'; Array.prototype.forEach.call(track.children,function(el,i){el.tabIndex=i===index?0:-1;}); Array.prototype.forEach.call(dots.children,function(el,i){el.classList.toggle('is-active',i===index);}); }
      function play(){ clearInterval(timer); if(!PREFERS_REDUCED_MOTION) timer=setInterval(function(){go(index+1);},5500); }
      prev.addEventListener('click',function(){go(index-1);play();}); next.addEventListener('click',function(){go(index+1);play();});
      dots.addEventListener('click',function(e){var i=Array.prototype.indexOf.call(dots.children,e.target);if(i>=0){go(i);play();}}); play();
      // Zoom que sigue al mouse (a pedido explícito 2026-09-10) -- el
      // origen del scale() de arriba (--hs-ox/--hs-oy, default 50%/18%
      // en CSS) se sobreescribe por elemento según la posición real del
      // cursor dentro de esa imagen, para que el zoom 1.75x quede
      // centrado donde está el mouse en vez de un punto fijo. Delegado
      // en `track` (estable -- innerHTML solo se arma una vez arriba,
      // go() solo cambia su transform) en vez de por-slide. Se salta
      // por completo si el usuario pidió reduced motion, mismo criterio
      // que play() ya usa arriba.
      if (!PREFERS_REDUCED_MOTION) {
        track.addEventListener('mousemove', function (e) {
          var media = e.target.closest('.hs-media');
          if (!media) return;
          var rect = media.getBoundingClientRect();
          if (!rect.width || !rect.height) return;
          var ox = Math.min(100, Math.max(0, (e.clientX - rect.left) / rect.width * 100));
          var oy = Math.min(100, Math.max(0, (e.clientY - rect.top) / rect.height * 100));
          media.style.setProperty('--hs-ox', ox + '%');
          media.style.setProperty('--hs-oy', oy + '%');
        });
        track.addEventListener('mouseleave', function () {
          Array.prototype.forEach.call(track.querySelectorAll('.hs-media'), function (media) {
            media.style.removeProperty('--hs-ox');
            media.style.removeProperty('--hs-oy');
          });
        });
      }
    }

    renderStats();
    renderCategories();
    initHeroSlider();
  }).catch(function () {
    var subtitle = document.getElementById('heroSubtitle');
    var stats = document.getElementById('stats');
    if (subtitle) {
      subtitle.setAttribute('role', 'alert');
      subtitle.textContent = 'Catalog data could not be loaded. You can retry or browse the plugins on JetBrains Marketplace.';
    }
    if (stats) {
      stats.innerHTML =
        '<button type="button" class="btn primary" id="homeCatalogRetry">Retry</button>' +
        '<a class="btn" href="https://plugins.jetbrains.com/vendor/gap-hunter-labs">Open JetBrains Marketplace ↗</a>';
    }
    var retry = document.getElementById('homeCatalogRetry');
    if (retry) retry.addEventListener('click', function () { location.reload(); });
  });

  var burger = document.getElementById('topbarBurger'), topbar = document.getElementById('topbar');
  if (burger && topbar) burger.addEventListener('click', function () { var open = topbar.classList.toggle('nav-open'); burger.setAttribute('aria-expanded', String(open)); });

  // Fade el logo del pie del sidebar cuando el <footer> real entra en
  // viewport (ver comentario en css/shell.css).
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
