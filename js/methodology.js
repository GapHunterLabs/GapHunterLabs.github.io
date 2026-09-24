/* /methodology/: el diagrama de decision "se dibuja" una vez al entrar en viewport (respeta prefers-reduced-motion).
   Movido desde un <script> inline el 2026-09-24 para poder quitar
   'unsafe-inline' del script-src de la CSP (ver DOCUMENTATION.md). */
(function () {
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
})();
