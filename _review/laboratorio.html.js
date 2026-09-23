
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
