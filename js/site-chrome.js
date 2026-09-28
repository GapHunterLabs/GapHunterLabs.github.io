/* Encabezado y pie compartidos (2026-09-27): menus desplegables del
   encabezado, selector de tema System/Light/Dark (encabezado + pie) y
   cierre del menu movil al elegir un enlace. El burger lo siguen
   manejando los scripts de cada pagina (#topbar.nav-open). */
(function () {
  var root = document.documentElement;
  var KEY = 'ghl-theme';

  function currentChoice() {
    var t = root.getAttribute('data-theme');
    return t === 'light' || t === 'dark' ? t : 'system';
  }

  function syncThemeControls() {
    var choice = currentChoice();
    document.querySelectorAll('[data-theme-choice]').forEach(function (btn) {
      btn.setAttribute('aria-pressed', btn.getAttribute('data-theme-choice') === choice ? 'true' : 'false');
    });
  }

  function applyTheme(choice) {
    if (choice === 'light' || choice === 'dark') root.setAttribute('data-theme', choice);
    else root.removeAttribute('data-theme');
    try {
      if (choice === 'system') localStorage.removeItem(KEY); else localStorage.setItem(KEY, choice);
    } catch (e) { /* sin almacenamiento: vale para esta visita */ }
    syncThemeControls();
  }

  document.querySelectorAll('[data-theme-choice]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      applyTheme(btn.getAttribute('data-theme-choice'));
      closeAllMenus();
    });
  });
  syncThemeControls();

  // ---- menus desplegables (patron disclosure: boton + panel) ----------
  var menus = Array.prototype.slice.call(document.querySelectorAll('.gh-menu'));

  function closeAllMenus(except) {
    menus.forEach(function (menu) {
      if (menu === except) return;
      var toggle = menu.querySelector('[data-menu-toggle]');
      var panel = menu.querySelector('[data-menu]');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
      if (panel) panel.hidden = true;
    });
  }

  menus.forEach(function (menu) {
    var toggle = menu.querySelector('[data-menu-toggle]');
    var panel = menu.querySelector('[data-menu]');
    if (!toggle || !panel) return;
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = panel.hidden;
      closeAllMenus(menu);
      panel.hidden = !open;
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) {
        var first = panel.querySelector('button, a');
        if (first) first.focus();
      }
    });
    panel.addEventListener('click', function (e) { e.stopPropagation(); });
  });

  document.addEventListener('click', function () { closeAllMenus(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var openMenu = menus.filter(function (m) { var p = m.querySelector('[data-menu]'); return p && !p.hidden; })[0];
    closeAllMenus();
    if (openMenu) {
      var t = openMenu.querySelector('[data-menu-toggle]');
      if (t) t.focus();
    }
    var header = document.getElementById('topbar');
    var burger = document.getElementById('topbarBurger');
    if (header && header.classList.contains('nav-open')) {
      header.classList.remove('nav-open');
      if (burger) { burger.setAttribute('aria-expanded', 'false'); burger.focus(); }
    }
  });

  // ---- menu movil: cerrar al elegir un enlace ------------------------
  var header = document.getElementById('topbar');
  var burger = document.getElementById('topbarBurger');
  document.querySelectorAll('#siteNav a').forEach(function (link) {
    link.addEventListener('click', function () {
      if (header) header.classList.remove('nav-open');
      if (burger) burger.setAttribute('aria-expanded', 'false');
    });
  });
})();
