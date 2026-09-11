(function () {
  'use strict';
  var loaderStarted = Date.now();
  var domReady = new Promise(function (resolve) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', resolve, { once: true });
    else resolve();
  });

  function finishLoader(ok, count) {
    var loader = document.getElementById('siteLoader');
    if (!loader) return;
    var status = loader.querySelector('.sl-status');
    if (status) status.textContent = ok ? count + ' plugins loaded' : 'Catalog data unavailable';
    loader.classList.toggle('is-error', !ok);
    var remaining = Math.max(0, 400 - (Date.now() - loaderStarted));
    Promise.all([domReady, new Promise(function (resolve) { setTimeout(resolve, remaining); })]).then(function () {
      setTimeout(function () {
        loader.classList.add('is-done');
        loader.setAttribute('aria-busy', 'false');
        loader.setAttribute('aria-hidden', 'true');
        document.documentElement.classList.remove('boot');
        setTimeout(function () { if (loader.parentNode) loader.remove(); }, 450);
      }, ok ? 80 : 500);
    });
  }

  var ready = fetch('/data/catalog-data.json', { credentials: 'same-origin' })
    .then(function (response) {
      if (!response.ok) throw new Error('Catalog request failed: ' + response.status);
      return response.json();
    })
    .then(function (data) {
      if (!data || !Array.isArray(data.plugins)) throw new Error('Catalog response is invalid');
      var plugins = data.plugins;
  // ---- category model -----------------------------------------------
  // Hand-curated grouping of each plugin's real `niche` string into
  // top-level catalog categories. If a future niche is not mapped, it
  // falls into "Other" rather than breaking the catalog.
  var CAT_BY_KEY = {};
  function tokenColor(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }
  var CATEGORIES = [
    { key: 'api', label: 'API', colorToken: '--accent' },
    { key: 'devops', label: 'DevOps', colorToken: '--good' },
    { key: 'security', label: 'Security', colorToken: '--bad' },
    { key: 'data', label: 'Data', colorToken: '--purple' },
    { key: 'quality', label: 'Code Quality', colorToken: '--amber' },
    { key: 'codegen', label: 'Codegen', colorToken: '--cyan' },
    { key: 'testing', label: 'Testing', colorToken: '--teal' },
    { key: 'editor', label: 'Editor', colorToken: '--pending' },
    { key: 'other', label: 'Other', colorToken: '--text-faint' }
  ];
  CATEGORIES.forEach(function (c) {
    c.color = tokenColor(c.colorToken);
    CAT_BY_KEY[c.key] = c;
  });

  // Same stroke icons as the Hunting Field category board -- reused on
  // each plugin card's top-right badge so the board and the grid share
  // one visual language.
  var CAT_ICON_INNER = {
    api: '<path d="M-4.5-6.5v3M-1.5-6.5v3M-6-3.5h7a2 2 0 0 1 2 2v1a2 2 0 0 0 2 2h1M6 6.5v-3M1.5 6.5v-3M6 3.5H-1a2 2 0 0 1-2-2v-1a2 2 0 0 0-2-2h-1" stroke-linecap="round" stroke-linejoin="round"/>',
    devops: '<path d="M-6 0a3 3 0 1 0 6 0 3 3 0 1 1 6 0 3 3 0 1 1-6 0 3 3 0 1 0-6 0Z" stroke-linejoin="round"/>',
    security: '<path d="M0-6.5 5.5-4v4.2C5.5 3.8 2.8 6 0 6.5-2.8 6-5.5 3.8-5.5.2V-4Z" stroke-linejoin="round"/>',
    data: '<path d="M-5-3c0-1.4 2.2-2.5 5-2.5s5 1.1 5 2.5v6c0 1.4-2.2 2.5-5 2.5s-5-1.1-5-2.5Z"/><path d="M-5-3c0 1.4 2.2 2.5 5 2.5s5-1.1 5-2.5"/>',
    quality: '<path d="M0-6.5v13M-5.5-3.5h11M-5.5-3.5 -6.5 0M-5.5-3.5-4.5 0M5.5-3.5 4.5 0M5.5-3.5 6.5 0M-6.5 0a1.5 1.5 0 0 0 3 0M3.5 0a1.5 1.5 0 0 0 3 0M-2.5 6.5h5" stroke-linecap="round" stroke-linejoin="round"/>',
    codegen: '<path d="M-6-2.5-3 0-6 2.5M6-2.5 3 0 6 2.5M.8-6 -1.3-.5h2.6L-.8 6" stroke-linecap="round" stroke-linejoin="round"/>',
    testing: '<path d="M-2-6.5v4.2l-3.3 6.6a1.6 1.6 0 0 0 1.4 2.2h7.8a1.6 1.6 0 0 0 1.4-2.2L1-2.3v-4.2M-3.3-6.5h6.6M-3-1.5h6" stroke-linecap="round" stroke-linejoin="round"/>',
    editor: '<rect x="-6" y="-5" width="12" height="10" rx="1.5"/><path d="M-3.5-2h4M-3.5 0.5h2.5M2-2v2.5" stroke-linecap="round"/>',
    other: '<path d="M0-6.5v13M-6.5 0h13M-4.6-4.6 4.6 4.6M4.6-4.6-4.6 4.6" stroke-linecap="round"/>'
  };
  function catIconHtml(key) {
    var inner = CAT_ICON_INNER[key] || CAT_ICON_INNER.other;
    return '<svg viewBox="-8 -8 16 16" aria-hidden="true">' + inner + '</svg>';
  }

  // Shared line-icon set -- used by both the hero telemetry column
  // (renderStats()) and the Hunting Field plugin cards (pluginCardHtml(),
  // just the download icon) so the same visual language for "this is a
  // count" reads consistently in both places, one definition.
  var ICONS = {
    plugins: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M10 1.5 17.5 6v8L10 18.5 2.5 14V6Z"/><path d="M10 10 17.5 6M10 10v8.5M10 10 2.5 6"/></svg>',
    downloads: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2.5v10M6 9l4 4 4-4M3.5 15.5v2a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-2"/></svg>',
    visitors: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M2 10s2.8-5.5 8-5.5S18 10 18 10s-2.8 5.5-8 5.5S2 10 2 10Z"/><circle cx="10" cy="10" r="2.3"/></svg>',
    reviews: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"><path d="M3 4.5h14a1 1 0 0 1 1 1V13a1 1 0 0 1-1 1H8l-4 3.5V14H3a1 1 0 0 1-1-1V5.5a1 1 0 0 1 1-1Z"/></svg>',
    rating: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><path d="M10 2.2 12.4 7.4 18 8.1 13.9 12 15 17.6 10 14.8 5 17.6 6.1 12 2 8.1 7.6 7.4Z"/></svg>',
    github: '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>',
    // The repository copy action uses the same outline style as the
    // other icons. A separate checkmark confirms a successful copy.
    copy: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"><rect x="5.5" y="5.5" width="8.5" height="8.5" rx="1.3"/><path d="M10.5 5.5V3.3a1.3 1.3 0 0 0-1.3-1.3H3.3A1.3 1.3 0 0 0 2 3.3v5.9a1.3 1.3 0 0 0 1.3 1.3h2.2"/></svg>',
    copyCheck: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8.5 6.2 12 13 4"/></svg>',
    // A generic plugin puzzle icon stays legible at button size and
    // matches the currentColor outline language used by the icon set.
    jetbrains: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"><path d="M7.5 3.5h3v1.75a1.25 1.25 0 0 0 2.5 0V3.5h3v3h-1.75a1.25 1.25 0 0 0 0 2.5h1.75v3h-3v-1.75a1.25 1.25 0 0 0-2.5 0V12h-3V9h1.75a1.25 1.25 0 0 0 0-2.5H7.5Z"/></svg>',
    // 2026-09-11: real VS Code logo mark, same path already used
    // elsewhere on the site (vsx section header, footer "VS Code
    // Marketplace" link) -- reused here so the new "Download for VS
    // Code" dossier button matches those exactly instead of a
    // different approximation.
    vscode: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.15 2.587L18.21.21a1.494 1.494 0 0 0-1.705.29l-9.46 8.63-4.12-3.128a.999.999 0 0 0-1.276.057L.327 7.261A1 1 0 0 0 .326 8.74L3.899 12 .326 15.26a1 1 0 0 0 .001 1.479L1.65 17.94a.999.999 0 0 0 1.276.057l4.12-3.128 9.46 8.63a1.492 1.492 0 0 0 1.704.29l4.942-2.377A1.5 1.5 0 0 0 24 20.06V3.939a1.5 1.5 0 0 0-.85-1.352zm-5.146 14.861L10.826 12l7.178-5.448v10.896z"/></svg>'
  };

  var NICHE_TO_CATEGORY = {
    'Ansible / DevOps': 'devops',
    'React Native Tooling': 'devops',
    'GitLab CI/CD': 'devops',
    'Jenkins CI/CD': 'devops',
    'Git Tooling': 'devops',
    'Nginx Config': 'devops',
    'CMake / Build Tooling': 'devops',
    'Env Config Tooling': 'devops',
    'OpenAPI/Swagger Tooling': 'api',
    'AsyncAPI Tooling': 'api',
    'GraphQL Tooling': 'api',
    'JSON Schema Tooling': 'api',
    'XSD/WSDL Tooling': 'api',
    'API Security': 'security',
    'Certificates / X.509': 'security',
    'JWT / Auth Tooling': 'security',
    'Dependency / SCA Security': 'security',
    'Firestore / Database': 'data',
    'CSV/XLSX Tooling': 'data',
    'Data Format Conversion': 'data',
    'Code Complexity': 'quality',
    'Refactoring Tools': 'quality',
    'Code Review': 'quality',
    'Inline Diagnostics': 'quality',
    'Java/Kotlin Codegen': 'codegen',
    'Codegen': 'codegen',
    'Debugging / Codegen': 'codegen',
    'Load Testing': 'testing',
    'Testing / Codegen': 'testing',
    'Diagrams': 'editor',
    'Editor Theme': 'editor',
    'Editor Productivity': 'editor',
    'JS/TS Tooling': 'editor',
    'Regex Tooling': 'editor',
    // 7 niches added 2026-08-23 -- audited and found missing (fell
    // through to 'other' via the `|| 'other'` fallback below, even
    // though every one of these clearly belongs in an existing
    // category by name alone). All 7 plugins were added 2026-08-19 as
    // part of the plan-B batch, after this map was last updated.
    'Build Tooling / Architecture': 'devops',
    'Code Quality / Feature Flags': 'quality',
    'Code Quality / Logging': 'quality',
    'Code Quality / Security': 'quality',
    'Docker / DevOps': 'devops',
    'Node.js / npm Tooling': 'devops',
    'VCS / Git Workflow': 'devops',
    // 23 niches added 2026-08-27 -- 67 of 101 plugins (2/3 of the whole
    // catalog) had their `niche` field stuck at "—" (a placeholder that
    // was never filled in when those plugins were added, mostly the
    // 2026-08-19+ "factory" batches) in catalog_static_metadata.json,
    // so ALL of them fell through the `|| 'other'` fallback below --
    // this is the actual root cause behind the "Other" node in the
    // Hunting Field always looking disproportionately large/"expanded"
    // (user report, 2026-08-27): it wasn't a CSS/animation bug, the
    // These values keep plugins with specific niches in their intended
    // categories rather than falling through to "Other".
    'HTTP Client Reuse': 'devops',
    'Cloud SDK Client Reuse': 'devops',
    'Database Client Reuse': 'devops',
    'Search Client Reuse': 'devops',
    'Messaging Client Reuse': 'devops',
    'Object Mapper Reuse': 'quality',
    'Cache Client Reuse': 'devops',
    'Connection Pool Tuning': 'devops',
    'API Deprecation Tooling': 'api',
    'Spring Framework Pitfalls': 'quality',
    'Distributed Tracing': 'devops',
    'Resilience Tooling': 'devops',
    'API Reliability': 'api',
    'Secrets Detection': 'security',
    'PHP Security': 'security',
    'Ruby Security': 'security',
    'SQL Injection Detection': 'security',
    'PII / Compliance': 'security',
    'Kubernetes Tooling': 'devops',
    'Observability Tooling': 'devops',
    'gRPC Tooling': 'api',
    'Database Performance': 'quality',
    // 13 niches added 2026-09-02 for the 22-plugin batch published and
    // approved that same day (confirmed live via the Marketplace API,
    // sequential ids 33995-34018). Same discipline as the 2026-08-27
    // fix: every one of these 22 plugins got a real niche assigned
    // before this map was touched, so none of them can fall through
    // to 'other' even transiently.
    'Concurrency / Async Bugs': 'quality',
    'Caching Bugs': 'quality',
    'Exception Handling': 'quality',
    'SSRF Detection': 'security',
    'Deserialization Security': 'security',
    'Kafka / Messaging Bugs': 'quality',
    'JPA / ORM Pitfalls': 'quality',
    'Numeric Safety': 'quality',
    'Distributed Locking': 'quality',
    'IAM / Cloud Security': 'security',
    'Kubernetes Security': 'security',
    'AWS Security': 'security',
    'ReDoS Detection': 'security',
    // 9 niches added 2026-09-03 for the 20-plugin batch built that day
    // (Tier 0 through Tier -4 escalation) -- uploaded to Marketplace the
    // same day but pending JetBrains' manual review, added here on
    // purpose so none of the 20 falls through to 'other' even while
    // pending (same discipline as the 2026-08-27/2026-09-02 batches
    // above -- every plugin gets a real niche BEFORE this map is
    // touched, never after).
    'SpEL Injection Detection': 'security',
    'CI/CD Security': 'security',
    'Log Injection Detection': 'security',
    'XPath Injection Detection': 'security',
    'Resource Leak Detection': 'quality',
    'Code Quality / Encapsulation': 'quality',
    'LDAP Injection Detection': 'security',
    'Lucene Injection Detection': 'security',
    'Web Session Security': 'security'
  };

  plugins.forEach(function (p) {
    p.categoryKey = NICHE_TO_CATEGORY[p.niche] || 'other';
  });

  // Hand-written per-plugin "Gap" openings (2026-08-15 request) -- the
  // raw `why` field is real, verified evidence (never touched), but
  // ~25 of the 34 plugins share the exact same boilerplate opening
  // ("Born from real evidence in JetBrains Marketplace reviews, not
  // assumptions:" or the "Ports a pattern that's genuinely popular
  // elsewhere..." variant for the 7 "proven concept" plugins), which
  // reads as templated when you look at more than one card. Every
  // override below keeps 100% of the original facts (competitor name,
  // download counts, %, verbatim complaints) -- only the framing
  // sentence changes, so nothing here is a new claim, just a different
  // way of leading with the same evidence. The ~9 plugins NOT in this
  // map already had a distinct opening (usually a bolded competitor
  // name) and fall through to the raw `why` text unchanged.
  var GAP_OVERRIDES = {
    'ansible-companion': 'Ansible tooling\'s existing incumbents — paid and free alike — draw concrete, repeated complaints in their own JetBrains Marketplace reviews: price, YAML the plugin shouldn\'t be touching, and badly parsed Jinja2. Vault encrypt/decrypt stands out as one of the features users value most in the paid incumbent, and one of the few pieces buildable without an external language server.',
    'react-native-companion': 'React Native Console — the leading paid alternative (~430K downloads, $19-24/year) — has a recent, severe, reproducible complaint on record: "severely impacting IDE performance... frequently becomes unresponsive... thread dumps are required." Older reports add buggy iOS simulator integration and unreliable buttons. Tellingly, the same vendor\'s own free tier is rated higher than their paid one — the problem is implementation quality in the paid extras, not the feature set itself.',
    'api-security-companion': 'The market-leading security scanners carry real, recent problems on record in their own reviews — not assumptions.',
    'cert-companion': 'The leading paid certificate/keystore explorer plugin (308K downloads) has 83% of its reviews sitting at 3 stars or fewer — a documented pattern, not a guess.',
    'highlight-companion': 'Better Highlights (1.03M downloads, freemium) looks fine at a glance — but its raw aggregate rating is contaminated by unrelated products that happen to share the word "better." Filtering down to the actual review text turns up independent, recent (2026-02) complaints:',
    'gitlab-ci-companion': '"GitLab CICD — Pipelines & Jobs, Builds Run Cancel Retry View Log" (26,891 downloads, paid) is the closest existing tool here — its own reviews are the evidence:',
    'theme-companion': 'A paid Monokai theme plugin with 2.47M downloads still has 85%+ of its reviews at 3 stars or below — the complaints are specific, not just noise:',
    'openapi-companion': 'Four independent sources in the OpenAPI/Swagger tooling space point at the same gap:',
    'spreadsheet-companion': 'The leading paid spreadsheet plugin ($39/year, ~307K downloads) has half its reviews at 3 stars or fewer. Paying users report they can\'t add or delete rows, can\'t copy/paste cells, that the plugin forcibly takes over CSV files with no opt-out, that its license prompt freezes the whole IDE, and that it corrupted XLSX files on save.',
    'jwt-companion': 'JWT (JSON Web Token) Analyzer (74,353 downloads) is the incumbent here — its own reviews spell out the problem:',
    'git-hygiene-companion': 'GitToolBox (~10.2M downloads, 4.7★ freemium, the largest install base found in this niche) is popular for a reason — but its own public issue tracker tells a more specific story:',
    'asyncapi-companion': 'The leading AsyncAPI plugin (freemium, actively developed) has 55% of its reviews at 3 stars or fewer — a higher negative-review rate than most of the competitors that anchored other plugins in this catalog. Paying and free users alike report:',
    'xsd-companion': 'A paid XSD/WSDL visualizer plugin charges ~$10/month and still draws 69% of its reviews at 3 stars or fewer:',
    'graphql-companion': 'JetBrains\'s own official GraphQL plugin has millions of downloads — and a real gap even it doesn\'t cover:',
    'nginx-companion': 'The leading nginx plugin\'s paid tier (254K+ downloads) has recent complaints of locking up the IDE "even on non-nginx related edits." Its free tier repeatedly prompts for analytics/tracking consent on every startup, no matter how many times a user declines — and the historical free alternative has been abandoned since 2019.',
    'jenkinsfile-companion': 'Two independent signals point at the same Jenkinsfile-tooling gap in JetBrains Marketplace:',
    'review-companion': 'Bito AI Code Reviews (~864K downloads, freemium) is the closest incumbent — its own reviews make the case:',
    'material-companion': 'The leading Material-style theme plugin has 18.6M downloads and is still actively developed — yet 80% of its recent reviews sit at 3 stars or fewer:',
    'change-case-companion': 'VS Code has multiple "change case" extensions with millions of combined installs — JetBrains Marketplace had no real equivalent (confirmed by search before building this). Not a competitor-complaint build; a deliberate bet on a pattern already proven popular elsewhere.',
    'env-diff-companion': 'Env-diff/env-sync tooling already exists across other editors and CLI tools — JetBrains Marketplace had no real equivalent (confirmed by search before building this). A deliberate bet on an already-proven pattern, not a competitor-complaint build.',
    'error-lens-companion': 'VS Code\'s Error Lens extension has 10M+ installs and is one of that ecosystem\'s most-used tools — confirmed before building this that JetBrains Marketplace had no equivalent yet.',
    'import-cost-companion': 'The closest existing plugin in this space (135K downloads) has 75% of its reviews at 3 stars or fewer — a documented, years-long pattern of severe CPU spikes and IDE freezes:',
    'json-to-code-companion': '"Paste JSON as Code"-style tools are widely used across other editors — JetBrains Marketplace had no real equivalent (confirmed by search before building this).',
    'regex-preview-companion': 'Standalone regex testers are a daily tool for many developers — but JetBrains Marketplace had no real equivalent living directly in the IDE (confirmed by search before building this).',
    'turbo-log-companion': 'VS Code\'s Turbo Console Log has millions of installs — a search before building this turned up zero results for "turbo console log," "turbo log," or "console log" as a code-generation concept anywhere in JetBrains Marketplace.'
  };

  function gapText(p) {
    return GAP_OVERRIDES[p.repo] || p.why || '—';
  }

  // Real demo GIFs already living in each plugin's own repo
  // (docs/screenshots/demo.gif), referenced via raw.githubusercontent.com
  // instead of copied into this repo -- one source of truth, updates
  // automatically if a plugin's own gif is ever replaced. Every URL
  // below was verified live (HTTP HEAD, 2026-08-15) before being added,
  // branch name included since it's `main` for some repos and `master`
  // for others. react-native-companion added 2026-08-21 -- its file is
  // a real screenshot PNG (screenshot_1.png), not a .gif; the key name
  // is historical (this map originally only held demo GIFs) but the
  // <img> rendering it doesn't care about format, so no code change was
  // needed, only that one new entry, verified live (HTTP HEAD, 200)
  // before adding.
  //
  // 2026-08-23 audit note: 10 plugins currently have NO entry here, not
  // 1 as an earlier version of this comment said -- review-companion
  // (the original, genuinely-deliberate omission) plus the 9 plan-B
  // plugins shipped 2026-08-19 (dockerfile-layer-size-companion,
  // circular-dependency-companion, commit-message-convention-companion,
  // feature-flag-reference-companion, http-status-inline-companion,
  // log-format-string-companion, sql-concatenation-companion,
  // unused-npm-script-companion, env-var-missing-companion). Checked
  // live via HTTP HEAD before writing this note: none of the 9 have a
  // docs/screenshots/{demo.gif,screenshot_1.png,demo.png} in either
  // main or master yet -- there is genuinely no real asset to link to
  // for any of them, so nothing was added to the map (the dossier's
  // onerror="this.remove()" already degrades gracefully either way).
  // Next step when this gets revisited: add real demo images to those
  // 9 repos first, THEN add their entries here -- not the other way
  // around.
  var GIF_URL = {
    'dependency-vulnerability-companion': 'https://raw.githubusercontent.com/GapHunterLabs/dependency-vulnerability-companion/main/docs/screenshots/demo.gif',
    'react-native-companion': 'https://raw.githubusercontent.com/GapHunterLabs/react-native-companion/main/docs/screenshots/screenshot_1.png',
    'ansible-companion': 'https://raw.githubusercontent.com/GapHunterLabs/ansible-companion/main/docs/screenshots/demo.gif',
    'api-security-companion': 'https://raw.githubusercontent.com/GapHunterLabs/api-security-companion/main/docs/screenshots/demo.gif',
    'cert-companion': 'https://raw.githubusercontent.com/GapHunterLabs/cert-companion/main/docs/screenshots/demo.gif',
    'highlight-companion': 'https://raw.githubusercontent.com/GapHunterLabs/highlight-companion/main/docs/screenshots/demo.gif',
    'gitlab-ci-companion': 'https://raw.githubusercontent.com/GapHunterLabs/gitlab-ci-companion/main/docs/screenshots/demo.gif',
    'mermaid-companion': 'https://raw.githubusercontent.com/GapHunterLabs/mermaid-companion/master/docs/screenshots/demo.gif',
    'theme-companion': 'https://raw.githubusercontent.com/GapHunterLabs/theme-companion/main/docs/screenshots/demo.gif',
    'openapi-companion': 'https://raw.githubusercontent.com/GapHunterLabs/openapi-companion/master/docs/screenshots/demo.gif',
    'spreadsheet-companion': 'https://raw.githubusercontent.com/GapHunterLabs/spreadsheet-companion/main/docs/screenshots/demo.gif',
    'refactor-simulator': 'https://raw.githubusercontent.com/GapHunterLabs/refactor-simulator/master/docs/screenshots/demo.gif',
    'jwt-companion': 'https://raw.githubusercontent.com/GapHunterLabs/jwt-companion/main/docs/screenshots/demo.gif',
    'firestore-companion': 'https://raw.githubusercontent.com/GapHunterLabs/firestore-companion/master/docs/screenshots/demo.gif',
    'git-hygiene-companion': 'https://raw.githubusercontent.com/GapHunterLabs/git-hygiene-companion/main/docs/screenshots/demo.gif',
    'asyncapi-companion': 'https://raw.githubusercontent.com/GapHunterLabs/asyncapi-companion/master/docs/screenshots/demo.gif',
    'xsd-companion': 'https://raw.githubusercontent.com/GapHunterLabs/xsd-companion/master/docs/screenshots/demo.gif',
    'graphql-companion': 'https://raw.githubusercontent.com/GapHunterLabs/graphql-companion/main/docs/screenshots/demo.gif',
    'k6-companion': 'https://raw.githubusercontent.com/GapHunterLabs/k6-companion/master/docs/screenshots/demo.gif',
    'nginx-companion': 'https://raw.githubusercontent.com/GapHunterLabs/nginx-companion/main/docs/screenshots/demo.gif',
    'format-converter-companion': 'https://raw.githubusercontent.com/GapHunterLabs/format-converter-companion/master/docs/screenshots/demo.gif',
    'cmake-companion': 'https://raw.githubusercontent.com/GapHunterLabs/cmake-companion/master/docs/screenshots/demo.gif',
    'jenkinsfile-companion': 'https://raw.githubusercontent.com/GapHunterLabs/jenkinsfile-companion/master/docs/screenshots/demo.gif',
    'material-companion': 'https://raw.githubusercontent.com/GapHunterLabs/material-companion/master/docs/screenshots/demo.gif',
    'json-schema-companion': 'https://raw.githubusercontent.com/GapHunterLabs/json-schema-companion/master/docs/screenshots/demo.gif',
    'test-scaffold-companion': 'https://raw.githubusercontent.com/GapHunterLabs/test-scaffold-companion/master/docs/screenshots/demo.gif',
    'bean-copy-companion': 'https://raw.githubusercontent.com/GapHunterLabs/bean-copy-companion/main/docs/screenshots/demo.gif',
    'change-case-companion': 'https://raw.githubusercontent.com/GapHunterLabs/change-case-companion/main/docs/screenshots/demo.gif',
    'env-diff-companion': 'https://raw.githubusercontent.com/GapHunterLabs/env-diff-companion/main/docs/screenshots/demo.gif',
    'error-lens-companion': 'https://raw.githubusercontent.com/GapHunterLabs/error-lens-companion/main/docs/screenshots/demo.gif',
    'import-cost-companion': 'https://raw.githubusercontent.com/GapHunterLabs/import-cost-companion/main/docs/screenshots/demo.gif',
    'json-to-code-companion': 'https://raw.githubusercontent.com/GapHunterLabs/json-to-code-companion/main/docs/screenshots/demo.gif',
    'regex-preview-companion': 'https://raw.githubusercontent.com/GapHunterLabs/regex-preview-companion/main/docs/screenshots/demo.gif',
    'turbo-log-companion': 'https://raw.githubusercontent.com/GapHunterLabs/turbo-log-companion/main/docs/screenshots/demo.gif'
  };

  // Real, derivable technical facts (2026-08-15 Facts-panel rework) --
  // never fabricated: platform is parsed straight from the plugin's own
  // pitch (nearly every one starts "IntelliJ... plugin."), Marketplace
  // ID is parsed from its own marketplaceUrl.
  function platformOf(p) {
    var m = (p.pitch || '').match(/^(IntelliJ[^.]*?plugin)\s*[.(]/);
    return m ? m[1] : 'IntelliJ-family';
  }
  function marketplaceId(p) {
    if (!p.marketplaceUrl) return null;
    var m = p.marketplaceUrl.match(/\/plugin\/(\d+)-/);
    return m ? m[1] : null;
  }
  function growthFactLine(p) {
    if (p.growth == null || p.growthFrom == null || p.downloads == null) return 'New listing';
    var arrow = p.growth > 0 ? '▲ +' : p.growth < 0 ? '▼ ' : '';
    return arrow + p.growth.toFixed(1) + '% since ' + p.growthSince + ' (' + p.growthFrom + '→' + p.downloads + ')';
  }

  // ---- shared helpers ---------------------------------------------
  function esc(s) {
    if (s == null) return '';
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  // esc() only neutralizes HTML metacharacters -- it does NOT validate a
  // URL's scheme, so on its own `esc(p.marketplaceUrl)` would still render
  // a working `href="javascript:..."` if that field ever arrived malformed.
  // Every dynamic href/src on this page goes
  // through this gate first: only http(s) survives, anything else
  // (javascript:, data:, vbscript:, a bare "//host" scheme-relative link)
  // is replaced with '#' instead of ever reaching the DOM.
  function safeUrl(s) {
    if (s == null) return '#';
    var str = String(s).trim();
    return /^https?:\/\//i.test(str) ? str : '#';
  }

  function mdInline(s) {
    var out = esc(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Convert complete backtick pairs to code and preserve an unmatched
    // trailing backtick as literal text.
    var parts = out.split('`');
    if (parts.length < 3) return out;
    var rebuilt = parts[0];
    var i = 1;
    for (; i + 1 < parts.length; i += 2) rebuilt += '<code>' + parts[i] + '</code>' + parts[i + 1];
    if (i < parts.length) rebuilt += '`' + parts[i];
    return rebuilt;
  }

  function byRepo(repo) {
    for (var i = 0; i < plugins.length; i++) if (plugins[i].repo === repo) return plugins[i];
    return null;
  }

  function pricingLabel(p, isPending) {
    if (isPending) return { cls: 'pending', text: 'Pending' };
    if (p === 'FREE') return { cls: 'free', text: 'Free' };
    if (p === 'FREEMIUM') return { cls: 'freemium', text: 'Freemium' };
    if (p === 'PAID') return { cls: 'paid', text: 'Paid' };
    // Unknown upstream pricing values remain displayable; every caller
    // escapes this text before inserting it into HTML.
    return { cls: 'free', text: p || '—' };
  }

  // Below this baseline, a percentage badge is more misleading than
  // informative -- 2026-08-23 audit finding: 1->20 downloads reads as
  // "▲ 1900.0%", and six unrelated plugins all show the identical
  // "▲ 300.0%" purely because they all happened to go 2->8. The
  // arithmetic is correct, but the badge visually overstates what's
  // really a handful of raw downloads. Below this floor, show the raw
  // delta instead ("+18") -- still real signal, without implying a
  // growth rate that a tiny sample can't actually support.
  var GROWTH_PERCENT_MIN_BASELINE = 10;

  function growthMarkup(p) {
    var g = p.growth;
    var title = p.growthSince ? ('Since ' + p.growthSince + ': ' + p.growthFrom + ' → ' + p.downloads) : 'No earlier snapshot';
    var titleAttr = ' title="' + esc(title) + '"';
    if (g === null || g === undefined) return '<span class="growth flat"' + titleAttr + '>—</span>';
    if (p.growthFrom != null && p.growthFrom < GROWTH_PERCENT_MIN_BASELINE && p.downloads != null) {
      var delta = p.downloads - p.growthFrom;
      if (delta > 0) return '<span class="growth up"' + titleAttr + '>▲ +' + delta + '</span>';
      if (delta < 0) return '<span class="growth down"' + titleAttr + '>▼ ' + delta + '</span>';
      return '<span class="growth flat"' + titleAttr + '>±0</span>';
    }
    if (g > 0) return '<span class="growth up"' + titleAttr + '>▲ ' + g.toFixed(1) + '%</span>';
    if (g < 0) return '<span class="growth down"' + titleAttr + '>▼ ' + Math.abs(g).toFixed(1) + '%</span>';
    return '<span class="growth flat"' + titleAttr + '>0%</span>';
  }


      var api = {
        data: data,
        plugins: plugins,
        CATEGORIES: CATEGORIES,
        CAT_BY_KEY: CAT_BY_KEY,
        ICONS: ICONS,
        GIF_URL: GIF_URL,
        esc: esc,
        safeUrl: safeUrl,
        mdInline: mdInline,
        pricingLabel: pricingLabel,
        growthMarkup: growthMarkup,
        byRepo: byRepo,
        catIconHtml: catIconHtml,
        gapText: gapText,
        platformOf: platformOf,
        marketplaceId: marketplaceId,
        growthFactLine: growthFactLine
      };
      finishLoader(true, plugins.length);
      return api;
    })
    .catch(function (error) {
      finishLoader(false, 0);
      document.dispatchEvent(new CustomEvent('catalogerror', { detail: error }));
      throw error;
    });

  window.GapCatalog = { ready: ready };
})();
