
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
  // El diagrama "se dibuja" una vez al entrar en viewport. Respeta
  // prefers-reduced-motion desde el arranque -- si el usuario lo
  // pidió, ni siquiera se agrega .diagram-anim-ready, así que el
  // diagrama nunca pasa por un estado oculto en ningún momento.
  var figure = document.querySelector('.decision-figure');
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (figure && !reduceMotion && 'IntersectionObserver' in window) {
    figure.classList.add('diagram-anim-ready');
    var seq = figure.querySelectorAll('.node, .node-built, .connector');
    seq.forEach(function (el, i) { el.style.transitionDelay = (i * 55) + 'ms'; });
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          figure.classList.add('is-visible');
          obs.disconnect();
        }
      });
    }, { threshold: 0.25 });
    io.observe(figure);
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
