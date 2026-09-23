#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_catalog_grid.py -- Fase 2 del SuperPlan de SEO: pre-renderiza
/catalog/'s propia grilla (Field) y tabla, en vez de dejar que el
navegador las pinte tras un fetch de data/catalog-data.json.

Escribe HTML real -- 146 <a class="plugin-card" href="/catalog/<repo>/">
y 146 <tr> de tabla, cada uno con sus data-* -- entre los marcadores
PRERENDER:* que pipeline/build_plugin_pages.py's Shell NO toca (viven
dentro de <main class="wrap">, que ese script reemplaza entero al
generar cada ficha; los dos scripts son independientes entre si).

Con esto, catalog/index.html deja de necesitar JS para pintar su
contenido principal: el script inline que queda en esa pagina solo
oculta (hidden)/reordena (appendChild) nodos que YA existen -- nunca
construye HTML ni hace fetch. Ver el propio <script> de la pagina para
el detalle de esa hidratacion.

Reusa Sources/PluginRenderer de build_plugin_pages.py (mismo parseo de
js/catalog-shared.js, mismos helpers de escape/color/icono) -- ningun
dato ni mapa se mantiene por duplicado.

Uso:
    python pipeline/build_catalog_grid.py
    python pipeline/build_catalog_grid.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_plugin_pages import Sources, PluginRenderer, esc, thousands, die  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PAGE = ROOT / "catalog" / "index.html"


def marker_span(html, start, end, label):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if len(pattern.findall(html)) != 1:
        die("marcador %s no encontrado (o duplicado) en catalog/index.html" % label)
    return pattern


def inject(html, start, end, content, label):
    pattern = marker_span(html, start, end, label)
    return pattern.sub(lambda _m: start + content + end, html, count=1)


def plugin_count_text(n: int) -> str:
    return "1 plugin" if n == 1 else "%d plugins" % n


def card_html(p, renderer: PluginRenderer, src: Sources) -> str:
    is_pending = p.get("downloads") is None
    cat = src.cat_by_key.get(p["categoryKey"], src.cat_by_key["other"])
    color = src.cat_color[cat["key"]]
    pr_cls, pr_text = renderer.pricing_label(p.get("pricing"), is_pending)
    search = (p["name"] + " " + (p.get("niche") or "") + " " + p["repo"]).lower()

    attrs = [
        'data-repo="%s"' % esc(p["repo"]),
        'data-cat="%s"' % esc(p["categoryKey"]),
        'data-pricing="%s"' % esc(p.get("pricing") or ""),
        'data-name="%s"' % esc(p["name"].lower()),
        'data-search="%s"' % esc(search),
    ]
    if is_pending:
        attrs.append('data-pending="1"')
    else:
        attrs.append('data-downloads="%d"' % p["downloads"])
    if p.get("reviews") is not None:
        attrs.append('data-reviews="%d"' % p["reviews"])
    if p.get("rating") is not None:
        attrs.append('data-rating="%s"' % p["rating"])
    if p.get("stars") is not None:
        attrs.append('data-stars="%d"' % p["stars"])
    if p.get("firstPublished"):
        attrs.append('data-firstpublished="%s"' % esc(p["firstPublished"]))

    metrics = (
        '<span class="chip pending">Pending</span>' if is_pending else
        '<span class="card-dl-wrap"><span class="dl-icon">%s</span>'
        '<span class="card-dl">%s</span></span>'
        '<span class="card-pricing %s">%s</span>' % (
            src.icons["downloads"], thousands(p["downloads"]), pr_cls, esc(pr_text))
    )
    return (
        '<a class="plugin-card" href="/catalog/%s/" aria-label="%s details" %s>'
        '<div class="card-header">'
        '<span class="card-cat" style="--cat:%s" title="%s" aria-hidden="true">%s</span>'
        '<div class="card-top"><div class="card-name">%s</div>'
        '<div class="card-niche">%s</div></div></div>'
        '<div class="card-metrics">%s</div></a>'
    ) % (esc(p["repo"]), esc(p["name"]), " ".join(attrs), color, esc(cat["label"]),
         renderer.cat_icon_html(p["categoryKey"]), esc(p["name"]), esc(p.get("niche")), metrics)


def table_row_html(p, renderer: PluginRenderer, src: Sources) -> str:
    is_pending = p.get("downloads") is None
    pr_cls, pr_text = renderer.pricing_label(p.get("pricing"), is_pending)
    search = (p["name"] + " " + (p.get("niche") or "") + " " + p["repo"]).lower()

    attrs = [
        'data-repo="%s"' % esc(p["repo"]),
        'data-cat="%s"' % esc(p["categoryKey"]),
        'data-pricing="%s"' % esc(p.get("pricing") or ""),
        'data-name="%s"' % esc(p["name"].lower()),
        'data-search="%s"' % esc(search),
    ]
    if is_pending:
        attrs.append('data-pending="1"')
    else:
        attrs.append('data-downloads="%d"' % p["downloads"])
    if p.get("reviews") is not None:
        attrs.append('data-reviews="%d"' % p["reviews"])
    if p.get("rating") is not None:
        attrs.append('data-rating="%s"' % p["rating"])
    if p.get("stars") is not None:
        attrs.append('data-stars="%d"' % p["stars"])
    if p.get("firstPublished"):
        attrs.append('data-firstpublished="%s"' % esc(p["firstPublished"]))

    dl_cell = "—" if is_pending else (thousands(p["downloads"]) + renderer.growth_markup(p))
    return (
        '<tr class="row" %s>'
        '<td class="name-cell"><a href="/catalog/%s/"><div class="plugin-name">%s</div>'
        '<div class="niche">%s</div></a></td>'
        '<td class="num-cell" data-label="Downloads">%s</td>'
        '<td class="num-cell tbl-optional" data-label="Reviews">%s</td>'
        '<td class="num-cell tbl-optional" data-label="Rating">%s</td>'
        '<td class="num-cell" data-label="GitHub ★">%s</td>'
        '<td data-label="Pricing"><span class="chip %s">%s</span></td>'
        '<td class="num-cell" data-label="Published" style="text-align:left">%s</td>'
        '</tr>'
    ) % (" ".join(attrs), esc(p["repo"]), esc(p["name"]), esc(p.get("niche")), dl_cell,
         "—" if p.get("reviews") is None else p["reviews"],
         "—" if p.get("rating") is None else ("%.2f" % p["rating"]),
         "—" if p.get("stars") is None else p["stars"],
         pr_cls, esc(pr_text), esc(p.get("firstPublished") or "—"))


def sort_default(plugins):
    """Mismo default que el JS: sortKey='downloads', sortDir=-1 (desc),
    ausentes siempre al final sin importar la direccion."""
    def key(p):
        d = p.get("downloads")
        return (d is None, -(d or 0))
    return sorted(plugins, key=key)


def update_category_board(html: str, src: Sources) -> str:
    counts = {c["key"]: 0 for c in src.categories}
    for p in src.plugins:
        counts[p["categoryKey"]] = counts.get(p["categoryKey"], 0) + 1
    total = len(src.plugins)

    # Celda "All categories" (data-cat="").
    pattern = re.compile(r'(data-cat=""[^>]*>.*?<span class="cat-cell-count">)([^<]*)(</span>)', re.S)
    html, n = pattern.subn(lambda m: m.group(1) + plugin_count_text(total) + m.group(3), html, count=1)
    if n != 1:
        die("celda 'All categories' del cat-board no encontrada")

    for cat in src.categories:
        key = cat["key"]
        n_count = counts.get(key, 0)
        pattern = re.compile(
            r'(data-cat="%s"[^>]*>.*?<span class="cat-cell-count">)([^<]*)(</span>)' % re.escape(key), re.S)
        html, n = pattern.subn(lambda m: m.group(1) + plugin_count_text(n_count) + m.group(3), html, count=1)
        if n != 1:
            die("celda de categoria '%s' no encontrada en el cat-board" % key)

    # La celda 'other' se oculta si nunca hay ningun plugin sin categoria
    # mapeada -- mismo criterio que updateCategoryBoard() tenia en JS.
    other_button = re.compile(r'(<button type="button" class="cat-cell" data-cat="other"[^>]*?)(\s*hidden)?(>)')
    m = other_button.search(html)
    if not m:
        die("celda 'other' del cat-board no encontrada")
    replacement = m.group(1) + ("" if counts.get("other", 0) > 0 else " hidden") + m.group(3)
    html = html[:m.start()] + replacement + html[m.end():]
    return html


def build(dry_run: bool = False) -> None:
    src = Sources()
    renderer = PluginRenderer(src)
    html = CATALOG_PAGE.read_text(encoding="utf-8")

    rows = sort_default(src.plugins)

    total_downloads = src.data.get("totalDownloads", sum(p.get("downloads") or 0 for p in src.plugins))
    cat_count = len([c for c in src.categories if c["key"] != "other"])
    stats_html = (
        '<div class="cs-item"><span class="cs-icon" style="color:var(--accent)">%s</span>'
        '<div><div class="cs-num">%d</div><div class="cs-label">Active plugins</div></div></div>'
        '<div class="cs-item"><span class="cs-icon" style="color:var(--good)">%s</span>'
        '<div><div class="cs-num">%s</div><div class="cs-label">Total downloads</div></div></div>'
        '<div class="cs-item"><span class="cs-icon" style="color:var(--purple)">'
        '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true">'
        '<rect x="3" y="3" width="6" height="6" rx="1"/><rect x="11" y="3" width="6" height="6" rx="1"/>'
        '<rect x="3" y="11" width="6" height="6" rx="1"/><rect x="11" y="11" width="6" height="6" rx="1"/>'
        '</svg></span><div><div class="cs-num">%d</div><div class="cs-label">Categories</div></div></div>'
    ) % (src.icons["plugins"], len(src.plugins), src.icons["downloads"], thousands(total_downloads), cat_count)

    counts = {c["key"]: 0 for c in src.categories}
    for p in src.plugins:
        counts[p["categoryKey"]] = counts.get(p["categoryKey"], 0) + 1
    active_cats = [c for c in src.categories if c["key"] != "other" or counts.get("other", 0) > 0]
    options_html = "".join(
        '<option value="%s">%s (%d)</option>' % (c["key"], esc(c["label"]), counts.get(c["key"], 0))
        for c in active_cats
    )

    grid_html = "".join(card_html(p, renderer, src) for p in rows)
    table_html = "".join(table_row_html(p, renderer, src) for p in rows)

    html = inject(html, "<!-- PRERENDER:STATS:START -->", "<!-- PRERENDER:STATS:END -->", stats_html, "STATS")
    html = inject(html, "<!-- PRERENDER:CATOPTIONS:START -->", "<!-- PRERENDER:CATOPTIONS:END -->",
                  options_html, "CATOPTIONS")
    html = inject(html, "<!-- PRERENDER:GRID:START -->", "<!-- PRERENDER:GRID:END -->", grid_html, "GRID")
    html = inject(html, "<!-- PRERENDER:TABLE:START -->", "<!-- PRERENDER:TABLE:END -->", table_html, "TABLE")
    html = update_category_board(html, src)

    if dry_run:
        print("[dry-run] %d tarjetas, %d filas, %d opciones de categoria -- nada escrito"
              % (len(rows), len(rows), len(active_cats)))
        return

    CATALOG_PAGE.write_text(html, encoding="utf-8")
    print("[build_catalog_grid] catalog/index.html: %d tarjetas + %d filas pre-renderizadas"
          % (len(rows), len(rows)))


def main():
    ap = argparse.ArgumentParser(description="Pre-renderiza la grilla/tabla de /catalog/")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    build(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
