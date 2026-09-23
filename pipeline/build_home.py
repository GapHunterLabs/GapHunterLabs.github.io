#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_home.py -- Fase 2 del SuperPlan de SEO: pre-renderiza el subtitulo
del hero, los contadores, los facts del metodo, las categorias y el
slider de destacados en index.html (la home), en vez de dejar que el
navegador los pinte tras un fetch de data/catalog-data.json.

Con esto, la home deja de cargar js/catalog-shared.js: nada en esta
pagina depende ya de GapCatalog.ready (era su unico consumidor). El
script que queda solo hace interactividad sobre nodos que ya existen
(el slider, el burger del topbar).

Reusa Sources/PluginRenderer de build_plugin_pages.py -- mismo parseo
de js/catalog-shared.js, mismos helpers de escape/color/icono.

Uso:
    python pipeline/build_home.py
    python pipeline/build_home.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_plugin_pages import Sources, PluginRenderer, esc, thousands  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HOME_PAGE = ROOT / "index.html"
FEATURED_MAX = 5


def die(msg: str) -> "NoReturn":  # noqa: F821
    sys.exit("[build_home] ERROR: " + msg)


def inject(html, start, end, content, label):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if len(pattern.findall(html)) != 1:
        die("marcador %s no encontrado (o duplicado) en index.html" % label)
    return pattern.sub(lambda _m: start + content + end, html, count=1)


def build(dry_run: bool = False) -> None:
    src = Sources()
    renderer = PluginRenderer(src)
    html = HOME_PAGE.read_text(encoding="utf-8")
    data = src.data
    plugins = src.plugins

    # ---- heroSubtitle: misma frase que renderStats() escribia en runtime ----
    subtitle = (
        "We hunt real, evidence-based gaps in developer tooling and ship "
        "focused IntelliJ-family plugins to fix them. Every one of the %d "
        "products in this catalog exists because of a documented complaint, "
        "its fix traces to a real diff, and its traction to real download "
        "numbers pulled straight from JetBrains Marketplace and GitHub — "
        "nothing here is estimated." % data["totalPlugins"]
    )

    # ---- stats: 2 tele-rows (plugins, downloads+growth) --------------------
    base = sum(p["growthFrom"] for p in plugins if p.get("growthFrom") is not None and p.get("downloads") is not None)
    current = sum(p["downloads"] for p in plugins if p.get("growthFrom") is not None and p.get("downloads") is not None)
    growth_html = (
        '<span class="stat-growth">▲ %.1f%%</span>' % (((current - base) / base) * 100)
        if base > 0 else ""
    )
    stats_html = (
        '<div class="tele-row"><span class="tele-icon" style="color:var(--accent)">%s</span>'
        '<div class="tele-body"><div class="tele-num accent">%d</div>'
        '<div class="tele-label">Plugins active</div></div></div>'
        '<div class="tele-row"><span class="tele-icon" style="color:var(--good)">%s</span>'
        '<div class="tele-body"><div class="tele-num">%s%s</div>'
        '<div class="tele-label">Downloads</div></div></div>'
    ) % (src.icons["plugins"], data["totalPlugins"], src.icons["downloads"],
         thousands(data["totalDownloads"]), growth_html)

    # ---- methodFacts: mismas 3 condiciones que renderStats() -----------------
    facts = []
    if data.get("totalReviews", 0) > 0:
        facts.append((data["totalReviews"], "Reviews total"))
    if data.get("avgRating") is not None:
        facts.append(("%.2f" % data["avgRating"], "Avg rating"))
    if data.get("totalStars", 0) > 0:
        facts.append((data["totalStars"], "GitHub stars"))
    facts_html = "".join(
        '<div class="method-fact"><div class="method-fact-num">%s</div>'
        '<div class="method-fact-label">%s</div></div>' % (f[0], esc(f[1]))
        for f in facts
    )

    # ---- categoryPreview: 8 tiles reales, mismo <a href> que ya usaba JS ----
    counts = {c["key"]: 0 for c in src.categories}
    for p in plugins:
        counts[p["categoryKey"]] = counts.get(p["categoryKey"], 0) + 1
    cat_html = "".join(
        '<a class="cat-cell" href="/catalog/?category=%s" style="--cat:%s">'
        '<span class="cat-cell-icon">%s</span>'
        '<span class="cat-cell-copy"><strong>%s</strong>'
        '<span class="cat-cell-count">%d plugins</span></span>'
        '<span class="cat-cell-arrow" aria-hidden="true">→</span></a>'
        % (c["key"], src.cat_color[c["key"]], renderer.cat_icon_html(c["key"]),
           esc(c["label"]), counts.get(c["key"], 0))
        for c in src.categories if c["key"] != "other"
    )

    # ---- hero slider: 5 destacados reales, ya con su URL /catalog/<slug>/ --
    featured = sorted(
        (p for p in plugins if p["repo"] in src.demo_media),
        key=lambda p: p.get("downloads") or 0, reverse=True,
    )[:FEATURED_MAX]
    if not featured:
        die("ningun plugin con DEMO_MEDIA -- el slider quedaria vacio")

    slides, dots = [], []
    for i, p in enumerate(featured):
        # Solo el primer slide es eager (visible sin interactuar, LCP);
        # el resto queda detras de un click/autoplay del propio slider.
        # decorative=True: el nombre/niche ya son texto real justo al
        # lado (.hs-copy), no hace falta repetirlo en alt/aria-label.
        media_html = renderer.demo_media_html(
            p["repo"], "", p["name"], eager=(i == 0), decorative=True)
        slides.append(
            '<a class="hs-slide" href="/catalog/%s/"%s>'
            '<span class="hs-media">%s</span>'
            '<span class="hs-copy"><span class="hs-kicker">Featured</span>'
            '<span class="hs-name">%s</span><span class="hs-niche">%s</span></span></a>'
            % (esc(p["repo"]), '' if i == 0 else ' tabindex="-1"',
               media_html, esc(p["name"]), esc(p.get("niche")))
        )
        dots.append(
            '<button type="button" class="hs-dot%s" aria-label="Show %s"></button>'
            % (' is-active' if i == 0 else '', esc(p["name"]))
        )

    html = inject(html, "<!-- PRERENDER:SUBTITLE:START -->", "<!-- PRERENDER:SUBTITLE:END -->", esc(subtitle), "SUBTITLE")
    html = inject(html, "<!-- PRERENDER:STATS:START -->", "<!-- PRERENDER:STATS:END -->", stats_html, "STATS")
    html = inject(html, "<!-- PRERENDER:METHODFACTS:START -->", "<!-- PRERENDER:METHODFACTS:END -->", facts_html, "METHODFACTS")
    html = inject(html, "<!-- PRERENDER:CATPREVIEW:START -->", "<!-- PRERENDER:CATPREVIEW:END -->", cat_html, "CATPREVIEW")
    html = inject(html, "<!-- PRERENDER:SLIDES:START -->", "<!-- PRERENDER:SLIDES:END -->", "".join(slides), "SLIDES")
    html = inject(html, "<!-- PRERENDER:DOTS:START -->", "<!-- PRERENDER:DOTS:END -->", "".join(dots), "DOTS")

    if dry_run:
        print("[dry-run] %d categorias, %d destacados -- nada escrito" % (len(src.categories) - 1, len(featured)))
        return

    HOME_PAGE.write_text(html, encoding="utf-8")
    print("[build_home] index.html: subtitulo + stats + %d facts + %d categorias + %d destacados pre-renderizados"
          % (len(facts), len(src.categories) - 1, len(featured)))


def main():
    ap = argparse.ArgumentParser(description="Pre-renderiza la home (index.html)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    build(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
