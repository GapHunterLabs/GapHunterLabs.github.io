# Gap Hunter Labs website architecture

This repository is the static GitHub Pages site for Gap Hunter Labs. It has no build step and uses self-hosted fonts, plain HTML/CSS/JavaScript, and a small scheduled Python updater.

## Public pages

2026-09-10: migrated to clean (extensionless) URLs. Real content now
lives at `<page>/index.html` so GitHub Pages serves it at `/<page>/`
with no `.html` in the address bar; the home page is the one
exception (`index.html` at the repo root already serves `/`). The old
top-level `catalog.html`/`methodology.html`/`contact.html`/
`security.html`/`laboratorio.html` files still exist, but each is now
a tiny client-side redirect stub (meta refresh + `location.replace`,
preserving query/hash) pointing at the new clean URL — kept working
rather than removed, since search engines had already indexed the old
URLs.

- `index.html` — home page, featured plugins, category previews, and the public identity section. Served at `/`.
- `catalog/index.html` — searchable/filterable catalog, table and field views, JSON-LD. Its grid and table are pre-rendered real HTML (146 `<a href="/catalog/<slug>/">` cards and `<tr>` rows, see "Catalog page rendering" below), not built by JS from a fetch. Served at `/catalog/`.
- `catalog/<slug>/index.html` — one real, indexable page per plugin (146 and counting): full dossier (gap, fix, facts, similar plugins), its own canonical/OG/JSON-LD. Generated, not hand-written — see "Per-plugin pages" below. Served at `/catalog/<slug>/`.
- `methodology/index.html` — public decision model and catalog data disclosures. Served at `/methodology/`.
- `security/index.html` — security posture, vulnerability reporting, certification disclosures. Served at `/security/`.
- `laboratorio/index.html` — curated case studies from the catalog. Served at `/laboratorio/`.
- `contact/index.html` — support and contact channels. Served at `/contact/`.

All pages share the same sidebar navigation: Home, Catalog, Methodology, Laboratorie, Contact (`security/index.html` has no sidebar entry of its own — it's reached via the footer nav and the "Security Report" link on Contact). Only the page a visitor is on sets `aria-current="page"` in that nav.

Because these pages now live one directory below the repo root, every asset reference (`css/shell.css`, `js/catalog-shared.js`, `js/vscode-catalog.js`, `fonts/*`) and `js/catalog-shared.js`'s own `fetch('/data/catalog-data.json', ...)` call must be **absolute** (`/css/...`, `/js/...`, `/fonts/...`, `/data/...`), not relative — a relative reference resolves against the subdirectory and 404s. `_review/verify_static.py` guards this regression explicitly.

## Catalog data

The browser-facing source of truth is `data/catalog-data.json`. `js/catalog-shared.js` fetches it and is used by the **home page** (category previews, featured slider, hero stats) and by the **VS Code section** cross-reference. `catalog/index.html` no longer loads it or `js/catalog-shared.js` at all — its own grid/table/stats/category options are pre-rendered HTML, and its small remaining script only filters (hides), sorts (reorders existing nodes) and paginates over that HTML; it never fetches or builds markup from JSON.

`pipeline/catalog_static_metadata.json` contains curated public product fields. `pipeline/auto_update_catalog.py` combines those fields with live Marketplace and GitHub metrics, writes `data/catalog-data.json`, refreshes the catalog page's JSON-LD, updates first-paint counts, and records catalog history.

Each plugin's own structured data (`SoftwareApplication` + `BreadcrumbList`) lives on its own `/catalog/<slug>/` page. `catalog/index.html`'s JSON-LD is a lighter `ItemList` of `{position, url, name}` pointing at those 146 real pages — no nested entity data, and deliberately no `aggregateRating` (Marketplace reviews are a different site's data; Google's guidelines don't allow marking up a third party's aggregate rating as your own). The home page keeps only organization/site structured data.

## Per-plugin pages (`catalog/<slug>/`)

`pipeline/build_plugin_pages.py` generates one real, indexable page per plugin from `data/catalog-data.json`. It does not reimplement the dossier or the page shell by hand: it reads the topbar/sidebar/footer/`<head>` and the CSS straight out of `catalog/index.html` via stable markers, and the category/gap/demo-media maps straight out of `js/catalog-shared.js` (a small tolerant JS-literal parser, since those are real `var X = {...}` maps, not JSON). One source of truth; nothing hand-duplicated. `pipeline/build_plugin_pages.py --inspect` prints the real schema and what it couldn't resolve.

## Demo media (`media/<slug>/`)

Fase 3 (2026-09-23): the 34 plugin demos (33 animated GIFs + 1 static screenshot) were downloaded from each plugin's own repo, converted with ffmpeg, and re-hosted under `media/<slug>/` in this repo — a deliberate, explicit trade-off (user decision, 2026-09-23) of performance over the "one source of truth in each plugin's own repo" principle the codebase otherwise follows. `js/catalog-shared.js`'s `DEMO_MEDIA` map (parsed by `Sources` the same way as everything else) is the only place these paths are recorded: `{poster, mp4, webm}` for a real demo, `{poster}` only for a static screenshot (`react-native-companion`).

Conversion isn't a straight re-encode: several of these GIFs only have 2–4 real frames with long hold delays (a "scene A → scene B → scene C" slideshow, not smooth motion) — an `fps=12` resample in the ffmpeg filter chain is what makes the output preserve the source's real total duration instead of collapsing those holds into under a second. Output is 960px wide, H.264 MP4 + VP9 WebM (a browser only ever fetches one, via `<video><source>` fallback) plus a WebP poster (shown instantly, before the video buffers). `PluginRenderer.demo_media_html()` in `build_plugin_pages.py` is the one place that turns a `DEMO_MEDIA` entry into markup — `<video muted loop playsinline autoplay>` when a real demo exists, `<img>` when it's a static screenshot, empty string when neither — reused by both `build_plugin_pages.py` (the plugin's own dossier) and `build_home.py` (the featured slider), so the two never diverge.

The CSP's `media-src 'self'` (added the same day) is required for these `<video>` elements to load at all under `default-src 'none'`; `img-src` no longer needs `raw.githubusercontent.com` now that nothing on these pages fetches from it.

To convert a new demo (or re-convert one that changed): `python pipeline/convert_demo_media.py <slug> <path-or-url-to-gif-or-png>` writes `media/<slug>/` and prints the `DEMO_MEDIA` entry to paste into `js/catalog-shared.js` (it refuses to finish if the output duration doesn't match the source's, catching the fps-collapse failure mode above). Rebuild after: `build_catalog_grid.py`, `build_home.py`, `build_plugin_pages.py --sitemap --inject`.

## Catalog page rendering (`catalog/index.html`'s own grid/table)

`pipeline/build_catalog_grid.py` pre-renders `catalog/index.html`'s own Field grid (146 `<a class="plugin-card" href="/catalog/<slug>/" data-cat="…" data-downloads="…" …>`) and Table rows, plus the hero stats and category `<select>`/board counts, between `<!-- PRERENDER:*:START/END -->` markers. Reuses the same `Sources`/`PluginRenderer` helpers as `build_plugin_pages.py` (same repo, imported directly — not duplicated).

The page's own inline script never builds HTML or fetches JSON for this content: it filters by toggling `hidden` on the already-rendered nodes, sorts by reordering them (`appendChild` on an existing child moves it), and paginates the same way. A dossier "click a card, see details in a panel" experience used to live on this page (`dossierBodyHtml()` et al.) — removed 2026-09-22 now that every plugin has its own real page; a card/row click is a normal navigation to `/catalog/<slug>/`.

## Common maintenance

Refresh live data and all generated catalog surfaces:

```bash
python pipeline/auto_update_catalog.py
python pipeline/build_catalog_grid.py      # catalog/index.html's own grid/table/stats
python pipeline/build_plugin_pages.py --sitemap --inject   # the 146 per-plugin pages + sitemap + hash shim
```

Refresh the catalog page's JSON-LD without network calls:

```bash
python pipeline/auto_update_catalog.py --seo-from-data
```

After editing the catalog payload or generated SEO, verify that `totalPlugins`, `plugins.length`, JSON-LD `numberOfItems`, the pre-rendered card count and the pre-rendered row count are all equal (`_review/verify_static.py` and `_review/verify_seo.py` both check this, plus per-plugin-page canonicalization).

After editing page scripts, extract inline executable scripts and check them with `node --check`. Serving the repository over HTTP is still useful for visual testing, but no longer required to see the home page's or the catalog page's real content — the catalog's own grid/table render with JavaScript disabled; only the home page's category previews/featured slider still depend on `js/catalog-shared.js`'s `fetch('/data/catalog-data.json', ...)`.

## Deployment

GitHub Pages serves the repository directly. The scheduled workflow commits only generated catalog data, catalog/home static counts, catalog JSON-LD, the catalog page's own pre-rendered grid/table, the 146 per-plugin pages, sitemap, and history files when they actually change.
