
// Rail liviano de "Platform Insights" -- reusa GapCatalog.ready (ya
// cargado por catalog-shared.js) para stats/categorías/destacado
// reales. Si el fetch falla, el rail se queda oculto (atributo
// `hidden` en el markup) en vez de mostrar ceros o un placeholder
// falso.
(function () {
  if (typeof GapCatalog === 'undefined') return;
  GapCatalog.ready.then(function (shared) {
    var data = shared.data, plugins = shared.plugins, CATEGORIES = shared.CATEGORIES;
    var esc = shared.esc, catIconHtml = shared.catIconHtml, GIF_URL = shared.GIF_URL;
    var rail = document.getElementById('pageInsights');
    if (!rail) return;
    document.getElementById('piPlugins').textContent = data.totalPlugins;
    document.getElementById('piDownloads').textContent = data.totalDownloads.toLocaleString('en-US');
    var counts = {};
    plugins.forEach(function (p) { counts[p.categoryKey] = (counts[p.categoryKey] || 0) + 1; });
    document.getElementById('piCategories').innerHTML = CATEGORIES.filter(function (c) { return c.key !== 'other'; }).map(function (c) {
      return '<a class="pi-cat" href="/catalog/?category=' + c.key + '" style="--cat:' + c.color + '">' + catIconHtml(c.key) + '<span>' + esc(c.label) + '</span><b>' + (counts[c.key] || 0) + '</b></a>';
    }).join('');
    var featured = plugins.filter(function (p) { return GIF_URL[p.repo]; }).sort(function (a, b) { return (b.downloads || 0) - (a.downloads || 0); })[0];
    if (featured) {
      var card = document.getElementById('piFeaturedCard');
      card.hidden = false;
      var link = document.getElementById('piFeatured');
      link.href = '/catalog/#' + encodeURIComponent(featured.repo);
      link.innerHTML = '<img src="' + esc(GIF_URL[featured.repo]) + '" alt="" width="300" height="169" loading="lazy">' +
        '<strong>' + esc(featured.name) + '</strong><span>' + esc(featured.niche || '') + '</span>';
    }
    rail.hidden = false;
  }).catch(function () { /* rail stays hidden -- no fake/empty state shown */ });
})();


(function () {
  var topbar = document.getElementById('topbar');
  var burger = document.getElementById('topbarBurger');
  if (topbar && burger) {
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
  }
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
