/* Contact desk: los formularios arman un enlace de "nuevo issue" de GitHub prellenado (sin backend).
   Movido desde un <script> inline el 2026-09-24 para poder quitar
   'unsafe-inline' del script-src de la CSP (ver DOCUMENTATION.md). */
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
  // 2026-09-27: bilingue -- la version en espanol (/es/contacto/) usa este
  // mismo script; el idioma sale de <html lang>.
  var ES = document.documentElement.lang === 'es';
  function t(en, es) { return ES ? es : en; }
  var CATEGORY_OPTIONS = ES
    ? ['API', 'DevOps', 'Seguridad', 'Datos', 'Calidad de código', 'Generación de código', 'Pruebas', 'Editor', 'Otra']
    : ['API', 'DevOps', 'Security', 'Data', 'Code Quality', 'Codegen', 'Testing', 'Editor', 'Other'];
  var PLATFORM_OPTIONS = [t('JetBrains (IntelliJ family)', 'JetBrains (familia IntelliJ)'), 'VS Code', t('Other', 'Otra')];
  var TEAM_OPTION = t('Team licenses for a paid plugin', 'Licencias de equipo para un plugin de pago');

  var CONFIGS = {
    gap: {
      label: 'gap-report',
      title: t('Submit a gap', 'Proponer una brecha'),
      sub: t('What are you missing? The more detail, the better.', '¿Qué te falta? Cuanto más detalle, mejor.'),
      submitLabel: t('Submit a gap', 'Proponer una brecha'),
      fields: [
        { name: 'category', label: t('Category', 'Categoría'), prompt: t('Select a category', 'Elige una categoría'), type: 'select', options: CATEGORY_OPTIONS, required: true, half: true },
        { name: 'platform', label: t('Platform', 'Plataforma'), prompt: t('Select a platform', 'Elige una plataforma'), type: 'select', options: PLATFORM_OPTIONS, required: true, half: true },
        { name: 'problem', label: t("What's the problem?", '¿Cuál es el problema?'), type: 'textarea', max: 1000, required: true, placeholder: t('Describe the issue, friction or missing capability…', 'Describe el problema, la fricción o la capacidad que falta…') },
        { name: 'existing', label: t('Existing solution', 'Solución existente'), type: 'textarea', max: 500, required: false, placeholder: t('Have you tried any existing tools or workarounds?', '¿Probaste alguna herramienta o solución alternativa?') },
        { name: 'evidence', label: t('Evidence / references', 'Evidencia / referencias'), type: 'textarea', max: 500, required: false, placeholder: t('Links, examples, or relevant documentation…', 'Enlaces, ejemplos o documentación relevante…') }
      ]
    },
    plugin: {
      label: 'plugin-feedback',
      title: t('Report a plugin', 'Reportar un plugin'),
      sub: t('Tell us which plugin and what happened.', 'Cuéntanos qué plugin y qué pasó.'),
      submitLabel: t('Report a plugin', 'Reportar un plugin'),
      fields: [
        { name: 'plugin', label: t('Plugin name', 'Nombre del plugin'), type: 'text', required: true, placeholder: t('e.g. GitLab CI Companion', 'p. ej. GitLab CI Companion') },
        { name: 'problem', label: t('What happened?', '¿Qué pasó?'), type: 'textarea', max: 1000, required: true, placeholder: t('Bug, missing feature, or unexpected behavior…', 'Error, función que falta o comportamiento inesperado…') }
      ]
    },
    // 2026-09-27: "hire" y "partnership" son leads privados -- van por
    // correo (mailto:) y NUNCA como issue publico de GitHub.
    hire: {
      label: 'hire',
      mail: true,
      title: t('Work with Joel', 'Trabaja con Joel'),
      sub: t('Custom static-analysis rules, CI/CD integration, private plugin distribution or team licenses. Joel replies personally by email.',
             'Reglas de análisis estático a medida, integración en CI/CD, distribución privada de plugins o licencias de equipo. Joel responde personalmente por correo.'),
      submitLabel: t('Email Joel', 'Escribir a Joel'),
      fields: [
        { name: 'org', label: t('Company', 'Empresa'), type: 'text', required: true, placeholder: t('Your company or team', 'Tu empresa o equipo') },
        { name: 'service', label: t('What do you need?', '¿Qué necesitas?'), prompt: t('Select one', 'Elige una opción'), type: 'select', required: true,
          options: [t('Custom static-analysis rules', 'Reglas de análisis estático a medida'), t('CI/CD integration', 'Integración en CI/CD'),
                    t('Private plugin distribution', 'Distribución privada de plugins'), TEAM_OPTION, t('Something else', 'Otra cosa')] },
        { name: 'message', label: t('Details', 'Detalles'), type: 'textarea', max: 1500, required: true, placeholder: t('Your stack, what the tool should catch or do, and any timeline…', 'Tu stack, qué debe detectar o hacer la herramienta y los plazos…') }
      ]
    },
    partnership: {
      label: 'partnership',
      mail: true,
      title: t('Partnership', 'Alianzas'),
      sub: t('Tell us about your organization and what you have in mind. This goes by email, never as a public issue.',
             'Cuéntanos sobre tu organización y lo que tienes en mente. Esto va por correo, nunca como un issue público.'),
      submitLabel: t('Send by email', 'Enviar por correo'),
      fields: [
        { name: 'org', label: t('Organization', 'Organización'), type: 'text', required: true, placeholder: t('Your company or project', 'Tu empresa o proyecto') },
        { name: 'message', label: t('Message', 'Mensaje'), type: 'textarea', max: 1000, required: true, placeholder: t('What kind of partnership are you thinking of?', '¿Qué tipo de alianza tienes en mente?') }
      ]
    }
  };
  var CONTACT_EMAIL = 'gaphunterlabs@gmail.com';

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
    var reqMark = f.required ? ' <span class="req">*</span>' : ' <span style="color:var(--text-faint);font-weight:400">' + t('(optional)', '(opcional)') + '</span>';
    var label = '<label for="cf-' + f.name + '">' + esc(f.label) + reqMark + '</label>';
    var body = '';
    if (f.type === 'select') {
      body = '<select id="cf-' + f.name + '" name="' + f.name + '"' + (f.required ? ' required' : '') + '>' +
        '<option value="">' + esc(f.prompt || t('Select one', 'Elige una opción')) + '</option>' +
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

  function track(path) {
    try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: path, event: true }); } catch (err) { /* opcional */ }
  }

  function copyText(text, btn) {
    function done(ok) {
      if (!btn) return;
      var original = btn.getAttribute('data-label') || btn.textContent;
      btn.setAttribute('data-label', original);
      btn.textContent = ok ? t('Copied', 'Copiado') : t('Select and copy manually', 'Selecciona y copia a mano');
      setTimeout(function () { btn.textContent = original; }, 2000);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
    } else {
      done(false);
    }
  }

  // Respaldo del mailto: en equipos sin cliente de correo el clic puede no
  // hacer nada, asi que el mensaje armado queda visible para copiarlo.
  function showFallback(subject, body) {
    var host = document.getElementById('cfFallback');
    if (!host) return;
    host.innerHTML =
      '<p><strong>' + t('If your mail app didn\u2019t open,', 'Si tu app de correo no se abri\u00f3,') + '</strong> ' +
      t('copy this message and send it to ', 'copia este mensaje y env\u00edalo a ') +
      '<a href="mailto:' + CONTACT_EMAIL + '">' + CONTACT_EMAIL + '</a>.</p>' +
      '<textarea readonly rows="8" aria-label="' + t('Prepared message', 'Mensaje preparado') + '">' + esc(t('Subject: ', 'Asunto: ') + subject + '\n\n' + body) + '</textarea>' +
      '<div class="cf-fallback-actions">' +
      '<button type="button" class="btn" data-copy-kind="email">' + t('Copy email', 'Copiar correo') + '</button>' +
      '<button type="button" class="btn primary" data-copy-kind="message">' + t('Copy message', 'Copiar mensaje') + '</button></div>';
    host.hidden = false;
    host.querySelector('[data-copy-kind="email"]').addEventListener('click', function (ev) { copyText(CONTACT_EMAIL, ev.currentTarget); track('contact-copy-email'); });
    host.querySelector('[data-copy-kind="message"]').addEventListener('click', function (ev) { copyText(t('Subject: ', 'Asunto: ') + subject + '\n\n' + body, ev.currentTarget); track('contact-copy-message'); });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var cfg = CONFIGS[currentKey];
    var data = new FormData(form);
    var titleSeed = data.get(cfg.fields[0].name) || cfg.title;
    if (cfg.mail) {
      var subject = (cfg.label === 'hire' ? t('Work with Joel: ', 'Trabaja con Joel: ') : t('Partnership: ', 'Alianza: ')) + String(titleSeed).slice(0, 80);
      var body = cfg.fields.map(function (f) {
        var v = data.get(f.name);
        return f.label + ':\n' + (v ? String(v) : t('(not provided)', '(sin completar)'));
      }).join('\n\n');
      showFallback(subject, body);
      track('contact-' + cfg.label + '-send');
      window.location.href = 'mailto:' + CONTACT_EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      return;
    }
    var issueTitle = '[' + cfg.label + '] ' + String(titleSeed).slice(0, 80);
    var bodyLines = cfg.fields.map(function (f) {
      var v = data.get(f.name);
      return '**' + f.label + '**\n' + (v ? String(v) : '_(not provided)_');
    });
    var issueBody = bodyLines.join('\n\n');
    var url = REPO_ISSUES + '?title=' + encodeURIComponent(issueTitle) +
      '&body=' + encodeURIComponent(issueBody) +
      '&labels=' + encodeURIComponent(cfg.label);
    track('contact-' + cfg.label + '-send');
    window.open(url, '_blank', 'noopener');
  });

  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () { copyText(btn.getAttribute('data-copy'), btn); track('contact-copy-email'); });
  });

  // ?intent=hire|partnership|plugin|gap, con ?plugin=<slug> o ?need=<texto>
  // para precargar el mensaje (llegan desde la home, las fichas y la
  // busqueda sin resultados del catalogo).
  var params = new URLSearchParams(window.location.search);
  var intent = params.get('intent');
  activate(CONFIGS[intent] ? intent : 'gap');
  var prefill = params.get('plugin') ? t('About the plugin: ', 'Sobre el plugin: ') + params.get('plugin') + '\n\n'
    : params.get('need') ? t('I searched the catalog for "', 'Busqué en el catálogo "') + params.get('need').slice(0, 120) + t('" and found nothing.\n\n', '" y no encontré nada.\n\n') : '';
  if (prefill) {
    var ta = fieldsHost.querySelector('textarea');
    if (ta) { ta.value = prefill; ta.dispatchEvent(new Event('input')); }
    if (params.get('plugin') && intent === 'hire') {
      var sel = fieldsHost.querySelector('select[name="service"]');
      if (sel) sel.value = TEAM_OPTION;
    }
  }
})();
