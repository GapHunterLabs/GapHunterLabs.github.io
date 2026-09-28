/* Aplica el tema elegido (Light/Dark) ANTES del primer pintado para que no
   haya destello. Se carga sin defer en el <head>. "System" = sin atributo:
   el CSS sigue a prefers-color-scheme. Ver /css/theme.css. */
(function () {
  try {
    var t = localStorage.getItem('ghl-theme');
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
  } catch (e) { /* almacenamiento bloqueado: se queda en System */ }
})();
