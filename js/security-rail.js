/* Rail "Platform Insights" de /security/ (usa GapCatalog de catalog-shared.js).
   Movido desde un <script> inline el 2026-09-24 para poder quitar
   'unsafe-inline' del script-src de la CSP (ver DOCUMENTATION.md).
   Corregido el mismo dia: leia el export GIF_URL (renombrado a DEMO_MEDIA en la
   Fase 3, {poster,mp4,webm} en vez de una URL), lo que lanzaba un TypeError que
   el .catch se tragaba y dejaba el rail oculto para siempre. */
// Rail liviano de "Platform Insights" -- reusa GapCatalog.ready (ya
// cargado por catalog-shared.js) para stats/categorías/destacado
// reales. Si el fetch falla, el rail se queda oculto (atributo
// `hidden` en el markup) en vez de mostrar ceros o un placeholder
// falso.
(function () {
  if (typeof GapCatalog === 'undefined') return;
  GapCatalog.ready.then(function (shared) {
    var data = shared.data, plugins = shared.plugins, CATEGORIES = shared.CATEGORIES;
    var esc = shared.esc, catIconHtml = shared.catIconHtml, DEMO_MEDIA = shared.DEMO_MEDIA;
    var rail = document.getElementById('pageInsights');
    if (!rail) return;
    document.getElementById('piPlugins').textContent = data.totalPlugins;
    document.getElementById('piDownloads').textContent = data.totalDownloads.toLocaleString('en-US');
    var counts = {};
    plugins.forEach(function (p) { counts[p.categoryKey] = (counts[p.categoryKey] || 0) + 1; });
    document.getElementById('piCategories').innerHTML = CATEGORIES.filter(function (c) { return c.key !== 'other'; }).map(function (c) {
      return '<a class="pi-cat" href="/catalog/?category=' + c.key + '" style="--cat:' + c.color + '">' + catIconHtml(c.key) + '<span>' + esc(c.label) + '</span><b>' + (counts[c.key] || 0) + '</b></a>';
    }).join('');
    var featured = plugins.filter(function (p) { return DEMO_MEDIA[p.repo]; }).sort(function (a, b) { return (b.downloads || 0) - (a.downloads || 0); })[0];
    if (featured) {
      var card = document.getElementById('piFeaturedCard');
      card.hidden = false;
      var link = document.getElementById('piFeatured');
      link.href = '/catalog/' + encodeURIComponent(featured.repo) + '/';
      link.innerHTML = '<img src="' + esc(DEMO_MEDIA[featured.repo].poster) + '" alt="" width="300" height="169" loading="lazy">' +
        '<strong>' + esc(featured.name) + '</strong><span>' + esc(featured.niche || '') + '</span>';
    }
    rail.hidden = false;
  }).catch(function () { /* rail stays hidden -- no fake/empty state shown */ });
})();
