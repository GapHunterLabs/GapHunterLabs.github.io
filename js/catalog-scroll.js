/* Flujo de scroll del catalogo (2026-10-05): un solo criterio para paginar,
   buscar y filtrar, en la grilla JetBrains y en la de VS Code.
   - Paginar: lleva al inicio de los resultados y mueve el foco ahi (teclado
     y lector de pantalla siguen desde la pagina nueva; el estado "Pagina X de
     Y" ya se anuncia con aria-live).
   - Buscar / filtrar: solo desplaza si los resultados quedaron fuera de vista
     (arriba, o casi debajo del pliegue), sin perder de vista el control que se
     esta usando (campo de busqueda o barra de filtros).
   El margen sale del alto real del topbar, no de un numero fijo: con 72px fijos
   la primera tarjeta quedaba 7px debajo del topbar en movil. */
(function () {
  'use strict';
  var REDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function offset() {
    var header = document.getElementById('topbar');
    return Math.round((header ? header.getBoundingClientRect().bottom : 0) + 12);
  }

  function scrollToY(y) {
    y = Math.max(0, Math.round(y));
    if (Math.abs(y - window.scrollY) < 4) return;
    window.scrollTo({ top: y, behavior: REDUCED ? 'auto' : 'smooth' });
  }

  window.GHLCatalogScroll = {
    toResults: function (el) {
      if (!el) return;
      scrollToY(window.scrollY + el.getBoundingClientRect().top - offset());
      if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1');
      try { el.focus({ preventScroll: true }); } catch (e) { el.focus(); }
    },
    reveal: function (el, keep) {
      if (!el) return;
      var off = offset();
      var top = el.getBoundingClientRect().top;
      if (top < off - 1) {
        // los resultados quedaron arriba (p. ej. se filtro estando abajo en la lista)
        scrollToY(window.scrollY + top - off);
      } else if (top > window.innerHeight * 0.62) {
        // casi no se ven: subirlos, pero sin esconder el control en uso
        var y = window.scrollY + top - off;
        if (keep) y = Math.min(y, window.scrollY + keep.getBoundingClientRect().top - off);
        scrollToY(y);
      }
    }
  };
})();
