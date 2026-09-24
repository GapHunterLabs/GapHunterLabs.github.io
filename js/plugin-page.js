/* Runtime de las fichas de plugin (/catalog/<slug>/).
   Estas paginas se sirven ya renderizadas: este archivo solo activa las
   tres piezas interactivas que el shell comparte con el catalogo, nunca
   construye contenido. Si no se ejecuta, la ficha se lee entera igual. */
(function () {
  'use strict';

  // Menu movil del topbar -- mismo comportamiento que initCatalogTopbar()
  // en catalog/index.html (una clase en el topbar, nada mas).
  var burger = document.getElementById('topbarBurger');
  var topbar = document.getElementById('topbar');
  if (burger && topbar) {
    burger.addEventListener('click', function () {
      var open = topbar.classList.toggle('nav-open');
      burger.setAttribute('aria-expanded', String(open));
    });
  }

  // El GIF de demo vive en el repo del propio plugin
  // (raw.githubusercontent.com). Si alguna vez desaparece, se quita el
  // hueco en vez de dejar un icono de imagen rota.
  var gif = document.querySelector('.dossier-gif');
  if (gif) gif.addEventListener('error', function () { gif.remove(); });

  // Copiar el nombre del repo desde el panel de Facts.
  var copyBtn = document.querySelector('.copy-btn');
  if (copyBtn && navigator.clipboard && navigator.clipboard.writeText) {
    var CHECK = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8.5 6.2 12 13 4"/></svg>';
    copyBtn.addEventListener('click', function () {
      navigator.clipboard.writeText(copyBtn.getAttribute('data-copy')).then(function () {
        if (copyBtn.dataset.copied) return;
        var original = copyBtn.innerHTML;
        copyBtn.innerHTML = CHECK;
        copyBtn.classList.add('copied');
        copyBtn.dataset.copied = '1';
        setTimeout(function () {
          copyBtn.innerHTML = original;
          copyBtn.classList.remove('copied');
          delete copyBtn.dataset.copied;
        }, 1400);
      }).catch(function () {});
    });
  }

  // "Copy link" de la fila Share: el boton viene con [hidden] y solo se
  // muestra si hay clipboard, para no ofrecer un boton muerto.
  var shareCopy = document.querySelector('.share-copy');
  if (shareCopy && navigator.clipboard && navigator.clipboard.writeText) {
    shareCopy.hidden = false;
    var shareLabel = shareCopy.querySelector('span');
    shareCopy.addEventListener('click', function () {
      navigator.clipboard.writeText(shareCopy.getAttribute('data-copy')).then(function () {
        if (shareCopy.dataset.copied) return;
        var original = shareLabel.textContent;
        shareLabel.textContent = 'Copied';
        shareCopy.classList.add('copied');
        shareCopy.dataset.copied = '1';
        setTimeout(function () {
          shareLabel.textContent = original;
          shareCopy.classList.remove('copied');
          delete shareCopy.dataset.copied;
        }, 1400);
      }).catch(function () {});
    });
  }

  // Fade del logo al pie del sidebar cuando entra el <footer> real
  // (misma regla que ya aplica el catalogo, ver css/shell.css).
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
