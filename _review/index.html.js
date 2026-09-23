
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
  'use strict';
  // Fase 2 del SuperPlan de SEO (2026-09-22): el subtitulo del hero, los
  // contadores, los facts, las categorias y el slider de destacados ya
  // llegan pre-renderizados (pipeline/build_home.py, mismos datos que
  // catalog-data.json pero escritos como HTML real en vez de pedidos por
  // fetch). Esta pagina ya no carga js/catalog-shared.js ni depende de
  // GapCatalog -- lo unico que queda en JS es interactividad sobre nodos
  // que ya existen: el slider (dots/flechas/autoplay/zoom) y el burger
  // del topbar.
  var PREFERS_REDUCED_MOTION = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  (function initHeroSlider() {
    var track = document.getElementById('heroSliderTrack');
    var dots = document.getElementById('heroSliderDots');
    var prev = document.getElementById('heroSliderPrev');
    var next = document.getElementById('heroSliderNext');
    if (!track || !dots || !prev || !next) return;
    var slides = Array.prototype.slice.call(track.children);
    var dotEls = Array.prototype.slice.call(dots.children);
    if (!slides.length) return;
    var index = 0, timer;

    function go(n) {
      index = (n + slides.length) % slides.length;
      track.style.transform = 'translateX(-' + index * 100 + '%)';
      slides.forEach(function (el, i) { el.tabIndex = i === index ? 0 : -1; });
      dotEls.forEach(function (el, i) { el.classList.toggle('is-active', i === index); });
    }
    function play() {
      clearInterval(timer);
      if (!PREFERS_REDUCED_MOTION) timer = setInterval(function () { go(index + 1); }, 5500);
    }
    prev.addEventListener('click', function () { go(index - 1); play(); });
    next.addEventListener('click', function () { go(index + 1); play(); });
    dots.addEventListener('click', function (e) {
      var dot = e.target.closest('.hs-dot');
      var i = dot ? dotEls.indexOf(dot) : -1;
      if (i >= 0) { go(i); play(); }
    });
    play();

    // Zoom que sigue al mouse (a pedido explicito 2026-09-10) -- el
    // origen del scale() (--hs-ox/--hs-oy, default 50%/18% en CSS) se
    // sobreescribe por elemento segun la posicion real del cursor.
    // Delegado en `track` (estable) en vez de por-slide.
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
  })();

  var burger = document.getElementById('topbarBurger'), topbar = document.getElementById('topbar');
  if (burger && topbar) {
    burger.addEventListener('click', function () {
      var open = topbar.classList.toggle('nav-open');
      burger.setAttribute('aria-expanded', String(open));
    });
  }

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
