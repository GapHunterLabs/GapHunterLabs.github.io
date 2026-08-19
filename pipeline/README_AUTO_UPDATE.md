# Auto-update del catálogo — cómo funciona

Desde 2026-08-19, `.github/workflows/update-catalog.yml` corre
`pipeline/auto_update_catalog.py` **automáticamente todos los días a
las 5:30am America/Bogota (10:30 UTC)**, sin intervención manual.

## Qué se actualiza solo

Datos en vivo, traídos de 2 APIs públicas en cada corrida:

- **JetBrains Marketplace** (`searchPlugins` + `/plugins/<id>/comments`):
  descargas, pricing model, reviews, rating.
- **GitHub** (`gh repo view --json stargazerCount`): estrellas de cada
  uno de los 34 repos `GapHunterLabs/*`.

Si esos datos cambiaron desde ayer, el workflow commitea y pushea
`index.html` (solo el bloque `<script id="catalog-data">` cambia,
mismo mecanismo de swap-in-place ya usado en cada refresh manual desde
2026-08-15) más `pipeline/catalog_daily_history.json` (histórico propio
de este repo, usado para calcular el % de crecimiento). Si nada cambió
de un día a otro, no hay commit vacío.

## Qué NO se actualiza solo (y por qué)

`pipeline/catalog_static_metadata.json` tiene 4 campos por plugin que
**casi nunca cambian**: `pitch`, `why`, `niche`, `xmlId`. Son texto
descriptivo curado a mano (el `niche` en particular es una
clasificación manual, no derivada de los tags genéricos de Marketplace)
— re-generarlos todos los días sería trabajo innecesario y agregaría
un punto de fallo (ese archivo depende de leer `plugin.xml`/`README.md`
de los 34 repos de plugins, que este repo del sitio no tiene clonados
localmente).

**Cuándo regenerarlo a mano:** solo si el pitch/why/niche de algún
plugin cambia de verdad (README reescrito, nuevo plugin agregado al
catálogo). No es una tarea diaria ni semanal.

**Cómo regenerarlo** (correr desde el repo raíz "Gap Hunter Labs", NO
desde este repo del sitio):

```bash
cd "Gap Hunter Labs"                      # el repo raíz, no este
python pipeline/28_catalog_report.py      # refresca out/catalog_report_latest.json
python3 - <<'EOF'
import json

with open('out/catalog_report_latest.json', encoding='utf-8') as f:
    report = json.load(f)

# Copiar el dict NICHE actual de pipeline/29_catalog_artifact_data.py aquí
# (o importarlo si se prefiere) antes de correr esto -- se omite en este
# snippet para no duplicar y desincronizar las 2 copias.
from importlib import import_module
import sys
sys.path.insert(0, "pipeline")
NICHE = import_module("29_catalog_artifact_data").NICHE  # ver nota abajo si el nombre de modulo con digito falla

static = {}
for repo, p in report["plugins"].items():
    static[repo] = {
        "xmlId": p["xmlId"],
        "name": p["name"],
        "pitch": p["pitch"],
        "why": p["why"],
        "niche": NICHE.get(repo, "—"),
        "githubUrl": p["github_url"],
        "firstPublished": p.get("first_published"),
    }

out = {
    "_comment": "Metadatos FIJOS por plugin (pitch/why/niche/xmlId) -- NO se regeneran automaticamente por el workflow diario, que solo trae metricas en vivo (descargas/reviews/stars/pricing). Si el pitch/why/niche de un plugin cambia, re-generar este archivo a mano corriendo el snippet documentado en README_AUTO_UPDATE.md del mismo directorio.",
    "generatedAt": report["generated_at"],
    "plugins": static,
}

with open("GapHunterLabs.github.io/pipeline/catalog_static_metadata.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"OK -- {len(static)} plugins escritos")
EOF
```

**Nota real, probada 2026-08-19:** `import_module("29_catalog_artifact_data")`
falla porque el nombre del módulo empieza con un dígito (no es un
identificador Python válido para `import` directo). Si el snippet de
arriba falla por eso, la forma que sí funciona es copiar el dict
`NICHE` completo (definido en `pipeline/29_catalog_artifact_data.py`,
sección superior del archivo) directamente dentro de este script en
vez de importarlo — exactamente lo que se hizo la primera vez que se
generó este archivo (2026-08-18), no probado el import dinámico en la
práctica todavía.

Después de regenerar, commitear y pushear `pipeline/catalog_static_metadata.json`
a este repo (`GapHunterLabs.github.io`) — el próximo cron diario ya lo
va a leer solo, no hace falta tocar nada más.

## Verificar que el workflow está corriendo

Pestaña **Actions** de `github.com/GapHunterLabs/GapHunterLabs.github.io`
— cada corrida (exitosa o fallida) queda listada ahí con su log
completo. También se puede disparar manualmente desde esa misma
pestaña (`workflow_dispatch`, botón "Run workflow") sin esperar al
cron, útil para probar un cambio sin esperar al día siguiente.

## Historia

Construido 2026-08-19 a pedido explícito del usuario: "tengo la
necesidad de hacer que los datos de cada plugin y del sitio en general
se actualicen directamente desde jetbrains marketplace y github. Esto
con la finalidad de no necesitar actualizar manualmente los datos."
Antes de esto, el catalog report se actualizaba manualmente corriendo
`pipeline/28_catalog_report.py` + `29_catalog_artifact_data.py` desde
el repo raíz y pegando el resultado a mano en `index.html` — ver
memoria `catalog_report_and_official_site` para el historial completo
de ese proceso manual (14 rondas de diseño del sitio, refreshes de
datos del 2026-08-15 al 2026-08-18).
