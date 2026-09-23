
(function () {
  var topbar = document.getElementById('topbar');
  var burger = document.getElementById('topbarBurger');
  if (!topbar || !burger) return;
  burger.addEventListener('click', function () {
    var open = topbar.classList.toggle('nav-open');
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  document.querySelectorAll('#appSidebar a').forEach(function (link) {
    link.addEventListener('click', function () {
      topbar.classList.remove('nav-open');
      burger.setAttribute('aria-expanded', 'false');
    });
  });
  // Fade el logo del pie del sidebar cuando el <footer> real entra en
  // viewport -- evita que ambas marcas queden casi superpuestas al
  // llegar abajo de la página (ver comentario en css/shell.css).
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


// Contact desk: 3 quick actions (Submit a gap / Report a plugin /
// Partnership) cada uno con su propio set de campos -- "Security
// report" NO es un form, es un link directo a security.html#sec-report
// (esa página ya instruye no abrir un issue público de seguridad, así
// que este form nunca debe generar uno). Sin backend: el submit arma
// un link de "crear issue" en el repo del sitio con los campos
// prellenados en título/cuerpo -- llega por notificación default de
// GitHub a la cuenta que ya opera el repo (gaphunterlabs@gmail.com).
(function () {
  var REPO_ISSUES = 'https://github.com/GapHunterLabs/GapHunterLabs.github.io/issues/new';
  var CATEGORY_OPTIONS = ['API', 'DevOps', 'Security', 'Data', 'Code Quality', 'Codegen', 'Testing', 'Editor', 'Other'];
  var PLATFORM_OPTIONS = ['JetBrains (IntelliJ family)', 'VS Code', 'Other'];

  var CONFIGS = {
    gap: {
      label: 'gap-report',
      title: 'Submit a gap',
      sub: "What are you missing? The more detail, the better.",
      submitLabel: 'Submit a gap',
      fields: [
        { name: 'category', label: 'Category', type: 'select', options: CATEGORY_OPTIONS, required: true, half: true },
        { name: 'platform', label: 'Platform', type: 'select', options: PLATFORM_OPTIONS, required: true, half: true },
        { name: 'problem', label: "What's the problem?", type: 'textarea', max: 1000, required: true, placeholder: 'Describe the issue, friction or missing capability…' },
        { name: 'existing', label: 'Existing solution', type: 'textarea', max: 500, required: false, placeholder: 'Have you tried any existing tools or workarounds?' },
        { name: 'evidence', label: 'Evidence / references', type: 'textarea', max: 500, required: false, placeholder: 'Links, examples, or relevant documentation…' }
      ]
    },
    plugin: {
      label: 'plugin-feedback',
      title: 'Report a plugin',
      sub: 'Tell us which plugin and what happened.',
      submitLabel: 'Report a plugin',
      fields: [
        { name: 'plugin', label: 'Plugin name', type: 'text', required: true, placeholder: 'e.g. GitLab CI Companion' },
        { name: 'problem', label: 'What happened?', type: 'textarea', max: 1000, required: true, placeholder: 'Bug, missing feature, or unexpected behavior…' }
      ]
    },
    partnership: {
      label: 'partnership',
      title: 'Partnership',
      sub: 'Tell us about your organization and what you have in mind.',
      submitLabel: 'Send',
      fields: [
        { name: 'org', label: 'Organization', type: 'text', required: true, placeholder: 'Your company or project' },
        { name: 'message', label: 'Message', type: 'textarea', max: 1000, required: true, placeholder: 'What kind of partnership are you thinking of?' }
      ]
    }
  };

  var fieldsHost = document.getElementById('cfFields');
  var titleEl = document.getElementById('cfTitle');
  var subEl = document.getElementById('cfSub');
  var submitBtn = document.getElementById('cfSubmit');
  var form = document.getElementById('contactForm');
  var qaItems = document.querySelectorAll('.qa-item[data-target]');
  var currentKey = 'gap';
  if (!fieldsHost || !form) return;

  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : s; return d.innerHTML; }

  function renderFields(key) {
    var cfg = CONFIGS[key];
    var html = '';
    var i = 0;
    while (i < cfg.fields.length) {
      var f = cfg.fields[i];
      if (f.half && cfg.fields[i + 1] && cfg.fields[i + 1].half) {
        html += '<div class="cf-row">' + fieldHtml(f) + fieldHtml(cfg.fields[i + 1]) + '</div>';
        i += 2;
      } else {
        html += fieldHtml(f);
        i += 1;
      }
    }
    fieldsHost.innerHTML = html;
    fieldsHost.querySelectorAll('textarea[data-max]').forEach(wireCounter);
  }

  function fieldHtml(f) {
    var reqMark = f.required ? ' <span class="req">*</span>' : ' <span style="color:var(--text-faint);font-weight:400">(optional)</span>';
    var label = '<label for="cf-' + f.name + '">' + esc(f.label) + reqMark + '</label>';
    var body = '';
    if (f.type === 'select') {
      body = '<select id="cf-' + f.name + '" name="' + f.name + '"' + (f.required ? ' required' : '') + '>' +
        '<option value="">Select ' + (f.label === 'Category' ? 'a category' : 'a platform') + '</option>' +
        f.options.map(function (o) { return '<option value="' + esc(o) + '">' + esc(o) + '</option>'; }).join('') +
        '</select>';
    } else if (f.type === 'textarea') {
      body = '<textarea id="cf-' + f.name + '" name="' + f.name + '" data-max="' + f.max + '" placeholder="' + esc(f.placeholder || '') + '"' + (f.required ? ' required' : '') + '></textarea>' +
        '<span class="cf-counter" data-counter-for="cf-' + f.name + '">0/' + f.max + '</span>';
    } else {
      body = '<input type="text" id="cf-' + f.name + '" name="' + f.name + '" placeholder="' + esc(f.placeholder || '') + '"' + (f.required ? ' required' : '') + '>';
    }
    return '<div class="cf-field">' + label + body + '</div>';
  }

  function wireCounter(ta) {
    var max = parseInt(ta.getAttribute('data-max'), 10);
    var counter = fieldsHost.querySelector('[data-counter-for="' + ta.id + '"]');
    if (!counter) return;
    function update() {
      var len = ta.value.length;
      counter.textContent = Math.min(len, max) + '/' + max;
      counter.style.color = len > max ? 'var(--warn, #FFB020)' : '';
    }
    ta.addEventListener('input', update);
    update();
  }

  function activate(key) {
    currentKey = key;
    var cfg = CONFIGS[key];
    titleEl.textContent = cfg.title;
    subEl.textContent = cfg.sub;
    submitBtn.childNodes[0].nodeValue = cfg.submitLabel + ' ';
    renderFields(key);
    qaItems.forEach(function (btn) {
      var on = btn.getAttribute('data-target') === key;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  qaItems.forEach(function (btn) {
    btn.addEventListener('click', function () { activate(btn.getAttribute('data-target')); });
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var cfg = CONFIGS[currentKey];
    var data = new FormData(form);
    var titleSeed = data.get(cfg.fields[0].name) || cfg.title;
    var issueTitle = '[' + cfg.label + '] ' + String(titleSeed).slice(0, 80);
    var bodyLines = cfg.fields.map(function (f) {
      var v = data.get(f.name);
      return '**' + f.label + '**\n' + (v ? String(v) : '_(not provided)_');
    });
    var issueBody = bodyLines.join('\n\n');
    var url = REPO_ISSUES + '?title=' + encodeURIComponent(issueTitle) +
      '&body=' + encodeURIComponent(issueBody) +
      '&labels=' + encodeURIComponent(cfg.label);
    window.open(url, '_blank', 'noopener');
  });

  activate('gap');
})();
