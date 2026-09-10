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
- `catalog/index.html` — full searchable/filterable catalog, table and field views, plugin dossiers, JSON-LD, and a no-script crawler list. Served at `/catalog/`.
- `methodology/index.html` — public decision model and catalog data disclosures. Served at `/methodology/`.
- `security/index.html` — security posture, vulnerability reporting, certification disclosures. Served at `/security/`.
- `laboratorio/index.html` — curated case studies from the catalog. Served at `/laboratorio/`.
- `contact/index.html` — support and contact channels. Served at `/contact/`.

All pages share the same sidebar navigation: Home, Catalog, Methodology, Laboratorie, Contact (`security/index.html` has no sidebar entry of its own — it's reached via the footer nav and the "Security Report" link on Contact). Only the page a visitor is on sets `aria-current="page"` in that nav.

Because these pages now live one directory below the repo root, every asset reference (`css/shell.css`, `js/catalog-shared.js`, `js/vscode-catalog.js`, `fonts/*`) and the two shared JS modules' own `fetch('data/catalog-data.json', ...)` calls must be **absolute** (`/css/...`, `/js/...`, `/fonts/...`, `/data/...`), not relative — a relative reference resolves against the subdirectory and 404s. `_review/verify_static.py` guards this regression explicitly.

## Catalog data

The browser-facing source of truth is `data/catalog-data.json`. Both home and catalog load it through `js/catalog-shared.js`.

`pipeline/catalog_static_metadata.json` contains curated public product fields. `pipeline/auto_update_catalog.py` combines those fields with live Marketplace and GitHub metrics, writes `data/catalog-data.json`, refreshes the catalog SEO blocks, updates first-paint counts, and records catalog history.

The full catalog's structured data belongs in `catalog/index.html`, because that is the page containing the listing. The home page keeps only organization/site structured data.

## Common maintenance

Refresh live data and all generated catalog surfaces:

```bash
python pipeline/auto_update_catalog.py
```

Refresh JSON-LD and the no-script listing without network calls:

```bash
python pipeline/auto_update_catalog.py --seo-from-data
```

After editing the catalog payload or generated SEO, verify that `totalPlugins`, `plugins.length`, JSON-LD `numberOfItems`, and the no-script `<li>` count are equal.

After editing page scripts, extract inline executable scripts and check them with `node --check`. Serve the repository over HTTP for browser testing because the shared catalog loader fetches `data/catalog-data.json`.

## Deployment

GitHub Pages serves the repository directly. The scheduled workflow commits only generated catalog data, catalog/home static counts, catalog SEO, sitemap date, and history files when they actually change.
