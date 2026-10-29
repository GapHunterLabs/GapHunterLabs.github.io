# Catalog auto-update

The scheduled update in `.github/workflows/update-catalog.yml` runs twice daily: at 06:00 UTC and 00:00 UTC.

## Data flow

1. `pipeline/auto_update_catalog.py` reads the curated product fields in `pipeline/catalog_static_metadata.json`.
2. It retrieves current downloads, pricing, reviews, ratings, and repository stars from the public JetBrains Marketplace and GitHub interfaces.
3. It writes the browser-facing payload to `data/catalog-data.json` with `json.dump()`.
4. It refreshes the JSON-LD and no-script list in `catalog/index.html` from that payload.
5. It updates static plugin counts in `index.html` and `catalog/index.html`, records the daily history, and updates the catalog entry's sitemap date.

The browser loads `data/catalog-data.json` from `js/catalog-shared.js`; catalog data is not embedded in either HTML page.

## Commands

Run a complete live refresh from the repository root:

```bash
python pipeline/auto_update_catalog.py
```

Regenerate only the catalog page's SEO blocks from the existing external JSON:

```bash
python pipeline/auto_update_catalog.py --seo-from-data
```

`--seo-from-index` remains accepted as a backwards-compatible alias, but it reads the external JSON just like `--seo-from-data`.

## Curated fields

`pipeline/catalog_static_metadata.json` owns fields that do not come from live metrics: `xmlId`, `name`, `pitch`, `why`, `niche`, `githubUrl`, and `firstPublished`. Update those entries when a plugin is added or its public description changes. The next complete refresh merges them with live metrics.

## Verification

A successful update requires the same plugin count in:

- `data/catalog-data.json` (`totalPlugins` and `plugins.length`)
- `catalog/index.html` JSON-LD (`numberOfItems`)
- `catalog/index.html` no-script list (`<li>` count`)

The workflow checks this parity before committing generated changes. It skips the commit when no tracked generated file changed.

## Frontend build (Tailwind and badges)

The site needs no CDN. `css/tw.css` is compiled from `pipeline/css-src/tailwind.css` by the Tailwind CLI and committed, so the CI does not need Node:

```
cd pipeline
npm install          # once: tailwindcss, axe-core, simple-icons (all devDependencies)
npm run build:css    # rewrites ../css/tw.css (~2 s)
python _review/verify_tailwind.py   # fails if tw.css is stale
```

Utilities use the `tw-` prefix and read the colors from the CSS tokens in `css/theme.css`, so the light, dark and system themes keep working. Badges and the badge table come from `pipeline/badges.py` as inline SVG (brand marks from `pipeline/icons.json`, extracted from simple-icons, CC0, by `build_icons.py`). Rebuild `tw.css` after adding a `tw-*` class to a generator or a page.

Accessibility check on a sample of pages, with the site served locally: `python _review/axe_check.py`.
