/* Aplica el tema elegido (Light/Dark) ANTES del primer pintado para que no
   haya destello. Se carga sin defer en el <head>. "System" (elegido a mano y
   guardado como 'system') = sin atributo: el CSS sigue a prefers-color-scheme.
   Sin eleccion guardada, la primera visita es oscura. Ver /css/theme.css. */
(function () {
  try {
    var t = localStorage.getItem('ghl-theme');
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
    else if (t !== 'system') document.documentElement.setAttribute('data-theme', 'dark'); // primera visita: oscuro
  } catch (e) { document.documentElement.setAttribute('data-theme', 'dark'); }
})();
