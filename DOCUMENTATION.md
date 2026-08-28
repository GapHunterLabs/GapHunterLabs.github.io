# Gap Hunter Labs — sitio oficial, mapa de arquitectura y trazabilidad

Este documento existe porque el repo nunca tuvo un README en la raíz —
toda la lógica de decisiones vivía dispersa en comentarios inline dentro
de `index.html` (384KB+, muy bien comentado línea a línea, pero sin un
mapa general). Sirve como punto de entrada: qué archivo hace qué, dónde
vive cada dato, y cómo se relaciona este repo con el repo raíz privado
`Gap Hunter Labs/`.

## 1. Qué es este repo

`GapHunterLabs.github.io` es el sitio público de GitHub Pages —
único archivo real de contenido: **`index.html`** (una SPA de un solo
archivo, HTML+CSS+JS inline, sin build step, sin dependencias externas
salvo GoatCounter para analytics). Todo lo demás en la raíz es soporte
(favicons, manifest, robots/sitemap, `404.html`).

## 2. Dónde vive cada dato del catálogo — las 3 capas

Esta es la parte que causó el incidente real documentado en la §4 —
entenderla bien evita que se repita.

```
Gap Hunter Labs/ (repo raíz, PRIVADO, sin remote git)
  pipeline/28_catalog_report.py       -> lee plugin.xml/README.md de
                                          cada uno de los 100+ repos de
                                          plugin hermanos, produce
                                          out/catalog_report_latest.json
  pipeline/29_catalog_artifact_data.py -> agrega el dict NICHE (curado
                                          A MANO, no derivado de nada) a
                                          ese report, produce
                                          out/catalog_artifact_data.json
                                          (consumido por un dashboard
                                          interno, workstream-1-catalogo/)
        │
        │  (proceso MANUAL, sin automatizar — ver §3)
        ▼
GapHunterLabs.github.io/ (este repo, PÚBLICO)
  pipeline/catalog_static_metadata.json  -> snapshot congelado de
                                          {xmlId, name, pitch, why,
                                          niche, githubUrl,
                                          firstPublished} por plugin.
                                          Fuente de verdad para estos
                                          campos DENTRO de este repo.
  pipeline/auto_update_catalog.py     -> corre en cron diario (ver
                                          .github/workflows/
                                          update-catalog.yml), trae
                                          downloads/stars/pricing/
                                          reviews EN VIVO desde
                                          JetBrains Marketplace + GitHub
                                          API, los combina con
                                          catalog_static_metadata.json,
                                          y hace swap-in-place del
                                          bloque <script id="catalog-data">
                                          dentro de index.html.
  index.html
    <script id="catalog-data">        -> JSON final embebido que el JS
                                          de la pagina lee en runtime
                                          (fusion de static+live, la
                                          UNICA copia que el navegador
                                          ve de verdad)
    NICHE_TO_CATEGORY (en el <script> -> mapea cada `niche` (string
    principal)                           libre, ej. "API Security") a
                                          una de las 9 categorias del
                                          Hunting Field (api/devops/
                                          security/data/quality/
                                          codegen/testing/editor/other)
```

**3 copias reales del mismo dato `niche` existen a propósito**
(`29_catalog_artifact_data.py.NICHE` en el repo raíz →
`catalog_static_metadata.json.niche` en este repo →
`index.html`'s embedded `catalog-data` JSON), cada una con un rol
distinto documentado en `pipeline/README_AUTO_UPDATE.md` (léelo antes
de tocar cualquiera de las 3). El auto-update diario **nunca** toca la
1ª ni la 2ª — solo refresca métricas vivas sobre la 3ª. Si el
`niche`/`pitch`/`why` de un plugin cambia de verdad, hay que
regenerar a mano siguiendo ese README, empezando siempre por la 1ª
capa (el repo raíz).

## 3. El punto ciego real: nada valida que las 3 capas estén sincronizadas

No existe ningún check automático que compare `NICHE` (repo raíz) contra
`catalog_static_metadata.json` (este repo) contra el `niche` real
embebido en `index.html`. Si se agrega un plugin nuevo al catálogo sin
pasar por el proceso completo de las 3 capas (por ejemplo, agregándolo
directo a `catalog_static_metadata.json` con un placeholder porque el
niche "se completaría después"), **nada avisa** — el sitio sigue
funcionando, sin error visible, el plugin simplemente cae en la
categoría catch-all "Other" del Hunting Field. Así se llegó al
incidente real de la §4: 67 de 101 plugins (2/3 del catálogo) llevaban
semanas con `niche="—"` sin que nadie lo notara hasta que el tamaño
desproporcionado del nodo "Other" en el Hunting Field lo hizo visible.

**Chequeo rápido para confirmar que esto no está pasando ahora mismo**
(correr desde este repo):

```bash
python3 -c "
import json
with open('pipeline/catalog_static_metadata.json', encoding='utf-8') as f:
    data = json.load(f)
bad = [k for k, v in data['plugins'].items() if len(v.get('niche','')) <= 2]
print(len(bad), 'plugins con niche vacio:', bad)
"
```

Si esto devuelve algo distinto de 0, el mismo bug volvió — casi
seguro porque se agregó un plugin nuevo sin pasar por
`29_catalog_artifact_data.py.NICHE` del repo raíz primero.

## 4. Caso de estudio: el bug del nodo "Other" siempre expandido (2026-08-27)

**Síntoma reportado por el usuario:** "el nodo Other [del Hunting
Field] se mantiene expandido siempre" — visualmente notorio, mucho más
grande que el resto y con apariencia distinta.

**Hipótesis descartadas, en orden, con evidencia real de por qué:**
1. *¿Estado `.active`/`.merged` pegado?* — Se auditó todo el flujo
   `setNodeMerged()`/`currentDockedCategory()`/`renderAll()`. El DOM
   inicial (confirmado con un dump headless real, ver §5) no tiene NUNCA
   la clase `.active` en ningún nodo al cargar. Descartado con evidencia,
   no por suposición.
2. *¿Bug de CSS/animación en el nodo en sí?* — Se revisaron todas las
   reglas de `.hunting-svg .node`/`.dot`/`.dot-ring`. Nada trataba a
   "other" como caso especial.
3. **Causa real, confirmada extrayendo el DOM renderizado real:** el
   radio del `circle.dot-ring` de "other" era `50.6px` contra `25-31px`
   del resto — casi el doble. La fórmula del radio
   (`(12 + sqrt(count)*3) * FIELD_SCALE * 1.04`) es proporcional al
   número de plugins de esa categoría — retro-calculando el `count` real
   a partir del radio dio **~100 de 101 plugins** en "Other". Confirmado
   exacto contando: **67 de 101** plugins tenían `niche: "—"` en
   `catalog_static_metadata.json`, cayendo todos en el fallback
   `NICHE_TO_CATEGORY[niche] || 'other'`.

**No era un bug de renderizado — era un bug de datos** que el
renderizado estaba mostrando correctamente. El nodo "Other" se veía
"siempre expandido" porque genuinamente tenía 67 plugins reales, no un
estado de UI atascado.

**Cómo se llegó a esa confirmación** (técnica reusable para la próxima
vez que un bug visual dependa de datos runtime reales en vez de código
estático — ver §5): el análisis de código estático solo llegó hasta
"nada en el código sesga a Other explícitamente". La confirmación real
requirió renderizar la página con JS ejecutado de verdad y leer los
atributos `r=` de los `<circle>` reales del DOM.

**Fix aplicado, en las 3 capas de la §2:**
1. `pipeline/29_catalog_artifact_data.py` (repo raíz): 67 entradas
   nuevas agregadas al dict `NICHE`.
2. `pipeline/catalog_static_metadata.json` (este repo): mismo fix
   aplicado directo (ver `pipeline/fix_missing_niches_2026_08_27.py`,
   conservado como registro histórico, no es parte del pipeline
   recurrente).
3. `index.html`: el `catalog-data` embebido actualizado con los 67
   niches nuevos (swap dirigido, sin tocar downloads/stars/growth ya
   frescos) + 23 entradas nuevas agregadas a `NICHE_TO_CATEGORY` (los
   niches recién asignados que no eran uno de los ~34 preexistentes).

**Resultado verificado:** distribución de categorías pasó de
`{other: 67, devops: 8, editor: 6, api: 5, quality: 4, security: 3,
codegen: 3, testing: 2}` a `{devops: 43, security: 16, quality: 13,
api: 11, editor: 8, data: 4, testing: 3, codegen: 3}` — "Other" queda
en 0 y desaparece del Hunting Field (el filtro `activeCategories()` ya
excluye categorías con count 0).

## 5. Cómo depurar este sitio cuando el bug depende de datos runtime

Aprendizaje real de la sesión que motivó este documento — dos técnicas
que sí funcionaron después de que otras fallaron:

- **`file://` no sirve para debug headless de esta página.**
  `msedge --headless --dump-dom file:///.../index.html` devuelve el DOM
  SIN que el JS haya corrido (probablemente por cómo el navegador trata
  fetch/recursos bajo `file://`). **Servir por HTTP local sí funciona**:
  `python3 -m http.server 8973` desde este repo, después
  `msedge --headless --dump-dom http://localhost:8973/index.html` —
  ahí el DOM sale completo, con el SVG del Hunting Field ya construido
  y las clases/atributos reales. Recordar cerrar el server después
  (`Stop-Process` sobre el PID que quedó escuchando el puerto).
- **Cuando el bug es "algo se ve desproporcionado", extraer los
  atributos numéricos reales del SVG en vez de mirar solo la clase CSS**
  — en este caso, comparar los `r=` de los `circle.dot-ring` de cada
  nodo fue lo que reveló el desbalance real de conteo, mucho antes que
  cualquier inspección del código de animación/estado.
- **Validar sintaxis después de editar `index.html`:** no hay build
  step ni linter en CI para este archivo. Antes de considerar un cambio
  terminado, correr:
  ```bash
  python3 -c "import re,json; c=open('index.html',encoding='utf-8').read(); \
    m=re.search(r'<script id=\"catalog-data\"[^>]*>(.*?)</script>', c, re.DOTALL); \
    json.loads(m.group(1)); print('catalog-data JSON OK')"
  # extraer el <script> principal (sin atributos, buscar con grep -n "^<script>$")
  # y validarlo con: node --check <archivo-extraido>.js
  ```
  Ambos chequeos son rápidos y habrían detectado cualquier JSON roto o
  error de sintaxis JS antes de publicar.

## 6. Convenciones de comentarios ya establecidas en `index.html`

El archivo ya sigue una disciplina real de comentarios que vale la pena
mantener en cualquier edición nueva — no es solo estilo, es lo que
permite reconstruir el "por qué" de una decisión meses después sin
tener que preguntar:

- Cada fix real cita la **fecha** (`2026-08-27`) y, cuando aplica, si
  fue **pedido explícito del usuario** (con las palabras textuales
  cuando ayuda) vs. un hallazgo propio.
- Cuando se revierte o corrige un intento anterior, el comentario dice
  **qué se intentó antes y por qué no funcionó** (ver los 4-5 rounds
  documentados sobre `transform-origin`/`fill-box` en las reglas del
  Hunting Field) — no solo la versión final.
- Los números "mágicos" (paddings, radios, umbrales de breakpoint)
  casi siempre traen al lado **de dónde salió ese número** (medido
  contra un viewport real, una fórmula, un porcentaje pedido
  explícitamente).

## 7. Índice rápido de zonas del código (`index.html`)

Referencia de dónde buscar cada pieza, para no tener que grep-ear todo
el archivo de cero cada vez (números de línea aproximados, van a
correrse con cada edición — usar como punto de partida, no como
verdad fija):

| Zona | Qué hace | Punto de entrada aproximado |
|---|---|---|
| `CATEGORIES` | Las 9 categorías del Hunting Field (key/label/color) | buscar `var CATEGORIES = [` |
| `NICHE_TO_CATEGORY` | Mapa niche-string → categoría | buscar `var NICHE_TO_CATEGORY = {` |
| `buildHuntingSvg()` | Construye el SVG del Hunting Field UNA SOLA VEZ | buscar `function buildHuntingSvg` |
| `updateHuntingSvg()` / `setNodeMerged()` | Toggle de estado activo/merge por render | buscar `function setNodeMerged` |
| `attachHubDrag()` | Drag del hub central (mouse + touch/pointer events) | buscar `function attachHubDrag` |
| `<script id="catalog-data">` | JSON embebido, única fuente runtime del catálogo | buscar `id="catalog-data"` |
| `.telemetry` / `.tele-row` | Box de estadísticas (stats), incluye breakpoints mobile | buscar `.telemetry {` |
| `renderAll()` | Punto de entrada de cada re-render (filtro/búsqueda/modo) | buscar `function renderAll` |

## 8. Herramienta correcta para cada tarea

Este repo mezcla varios tipos de trabajo (dato, HTML/CSS/JS estático,
automatización cron) que cada uno tiene su propia forma correcta de
tocarse — usar la equivocada es lo que hizo que este bug tardara
semanas en detectarse. Tabla de referencia:

| Tarea | Herramienta correcta | Por qué / qué evitar |
|---|---|---|
| Agregar/editar el `niche`, `pitch`, `why` de un plugin | Editar `Gap Hunter Labs/pipeline/29_catalog_artifact_data.py` (dict `NICHE`) **primero**, después regenerar `catalog_static_metadata.json` siguiendo `pipeline/README_AUTO_UPDATE.md` | Nunca editar `catalog_static_metadata.json` directo sin tocar la capa de arriba — eso es exactamente lo que dejó las 3 capas desincronizadas (§3) |
| Refrescar downloads/stars/pricing/reviews | No tocar nada a mano — corre solo vía cron (`update-catalog.yml`), o disparar manual desde la pestaña **Actions** de GitHub (`workflow_dispatch`) | `auto_update_catalog.py` hace llamadas reales a JetBrains Marketplace + `gh` CLI; correrlo local sin necesidad gasta cuota de esas APIs sin motivo |
| Editar HTML/CSS/JS de `index.html` | `Edit` directo sobre el archivo (no hay build step) | El archivo es grande (380KB+) — usar `Grep`/búsqueda por patrón para ubicar la zona (ver tabla de §7) en vez de `Read` completo, que excede el límite de tokens de una sola lectura |
| Validar que un cambio a `index.html` no rompió nada | Ver snippets exactos en §5 (`json.loads()` sobre el bloque `catalog-data`, `node --check` sobre el `<script>` principal extraído) | No hay linter/CI para este archivo — estas 2 validaciones son las únicas red de seguridad real antes de publicar |
| Ver el comportamiento REAL de la página (JS ya ejecutado, no solo el HTML fuente) | `python3 -m http.server <puerto>` desde este repo + `msedge --headless --dump-dom http://localhost:<puerto>/index.html` | `--dump-dom` sobre `file://` no ejecuta el JS de esta página (confirmado, ver §5) — servir por HTTP local es la diferencia real. Cerrar el server (`Stop-Process` sobre el PID del puerto) al terminar |
| Confirmar un bug visual que depende de conteos/tamaños reales (no de código estático) | Extraer atributos numéricos reales del DOM renderizado (`grep -oE` sobre el dump, o inspeccionar en vivo) — nunca asumir el valor leyendo solo la fórmula en el código | El propio código puede ser 100% correcto y aun así producir un resultado visual roto por datos de entrada malos (exactamente el caso de §4) |
| Publicar un cambio | `git add`/`commit`/`push` normal a este repo — GitHub Pages sirve directo desde la rama configurada, sin paso de deploy separado | — |
| Verificar que el cron diario sigue vivo | Pestaña **Actions** de `github.com/GapHunterLabs/GapHunterLabs.github.io` | Cada corrida (éxito o falla) queda listada con su log completo ahí, no hace falta adivinar |

## 9. Historia — sesiones de diseño previas

El proceso manual de 14 rondas de diseño del sitio (2026-08-15 al
2026-08-18, antes del auto-update) y el resto del historial operativo
vive en la memoria persistente del asistente
(`catalog_report_and_official_site` y memorias relacionadas con
`workstream3`/`site_seo`) — no duplicado aquí a propósito, para no
tener 2 fuentes de verdad sobre lo mismo. Este documento cubre
arquitectura y trazabilidad de datos; la memoria cubre decisiones de
producto/diseño puntuales sesión por sesión.
