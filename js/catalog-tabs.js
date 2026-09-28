/* Pestanas de plataforma del catalogo (2026-09-27): JetBrains IDEs | VS Code.
   Sin JavaScript las dos secciones se ven una debajo de la otra y las
   pestanas funcionan como anclas. Con JavaScript se muestra una sola y la
   eleccion queda en la URL (?platform=vscode) para poder compartirla.
   Tambien acepta el ancla vieja #vsxSection. */
(function () {
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.platform-tab'));
  if (!tabs.length) return;

  function panelOf(tab) { return document.getElementById(tab.getAttribute('aria-controls')); }

  function select(name, updateUrl) {
    tabs.forEach(function (tab) {
      var on = tab.getAttribute('data-platform') === name;
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      tab.tabIndex = on ? 0 : -1;
      var panel = panelOf(tab);
      if (panel) panel.hidden = !on;
    });
    if (!updateUrl) return;
    try {
      var url = new URL(location.href);
      if (name === 'vscode') url.searchParams.set('platform', 'vscode'); else url.searchParams.delete('platform');
      history.replaceState(null, '', url.pathname + url.search);
    } catch (e) { /* sin History API: la pestana igual cambia */ }
  }

  var params = new URLSearchParams(location.search);
  var wantsVsx = params.get('platform') === 'vscode' || location.hash === '#vsxSection' || location.hash === '#vscode';
  select(wantsVsx ? 'vscode' : 'jetbrains', false);

  tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function (e) {
      e.preventDefault();
      select(tab.getAttribute('data-platform'), true);
    });
    tab.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      e.preventDefault();
      var next = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
      next.focus();
      select(next.getAttribute('data-platform'), true);
    });
  });
})();
