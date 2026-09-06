# Gap Hunter Labs website architecture

This repository is the static GitHub Pages site for Gap Hunter Labs. It has no build step and uses self-hosted fonts, plain HTML/CSS/JavaScript, and a small scheduled Python updater.

## Public pages

- `index.html` — home page, featured plugins, category previews, and the public identity section.
- `catalog.html` — full searchable/filterable catalog, table and field views, plugin dossiers, JSON-LD, and a no-script crawler list.
- `methodology.html` — public decision model and catalog data disclosures.
- `contact.html` — support and contact channels.

All four pages use the same destination navigation: Catalog, Methodology, and Contact. The logo returns home. Only destination pages set `aria-current="page"`; home does not.

## Catalog data

The browser-facing source of truth is `data/catalog-data.json`. Both home and catalog load it through `js/catalog-shared.js`.

`pipeline/catalog_static_metadata.json` contains curated public product fields. `pipeline/auto_update_catalog.py` combines those fields with live Marketplace and GitHub metrics, writes `data/catalog-data.json`, refreshes the catalog SEO blocks, updates first-paint counts, and records catalog history.

The full catalog's structured data belongs in `catalog.html`, because that is the page containing the listing. The home page keeps only organization/site structured data.

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
