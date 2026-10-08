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
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_plugin_pages import Sources, PluginRenderer, esc, thousands, pitch_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HOME_PAGE = ROOT / "index.html"
VSCODE_DATA = ROOT / "data" / "vscode-catalog-data.json"
HUBS_DATA = ROOT / "data" / "hubs.json"
PRICING_LABEL = {"FREE": "Free", "FREEMIUM": "Freemium", "PAID": "Paid"}
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
    vscode_total = 0
    if VSCODE_DATA.exists():
        vscode_total = json.loads(VSCODE_DATA.read_text(encoding="utf-8")).get("totalExtensions") or 0
    # 2026-10-05: sin "nothing here is estimated" (una auditoria externa la marco
    # como afirmacion fragil); en su lugar, la fecha real del snapshot.
    snapshot = (data.get("generatedAt") or "")[:10]
    subtitle = (
        "Every plugin is built for a documented gap in developer tooling and has a clear "
        "price: free, freemium or paid. Figures are synced twice a day from public JetBrains "
        "Marketplace and GitHub data (last snapshot: %s)." % snapshot
    )

    # ---- stats: 2 tele-rows (plugins, downloads+growth) --------------------
    # 2026-09-27: el % de crecimiento agregado se retiro del hero -- cada
    # plugin empezo a medirse en una fecha distinta (growthSince), asi que
    # la suma no tiene un periodo honesto que mostrar.
    growth_html = ""
    n_paid = sum(1 for p in plugins if p.get("pricing") in ("FREEMIUM", "PAID"))
    stats_html = "".join(
        '<div class="hdr-stat"><span class="hdr-stat-num">%s</span><span class="hdr-stat-label">%s</span></div>'
        % (num, label)
        for num, label in ((data["totalPlugins"], "JetBrains plugins"), (vscode_total, "VS Code extensions"),
                           (thousands(data["totalDownloads"]), "JetBrains downloads"), (n_paid, "Paid &amp; Pro plugins")))
    _ = growth_html

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
        % (c["key"], src.cat_var[c["key"]], renderer.cat_icon_html(c["key"]),
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
            '<span class="hs-copy"><span class="hs-kicker"><span class="price-badge price-%s">%s</span>Featured plugin</span>'
            '<span class="hs-name">%s</span><span class="hs-niche">%s</span></span></a>'
            % (esc(p["repo"]), '' if i == 0 else ' tabindex="-1"',
               media_html, (p.get("pricing") or "FREE").lower(), PRICING_LABEL.get(p.get("pricing"), "Free"),
               esc(p["name"]), esc(p.get("niche")))
        )
        dots.append(
            '<button type="button" class="hs-dot%s" aria-label="Show %s"></button>'
            % (' is-active' if i == 0 else '', esc(p["name"]))
        )

    # ---- plugins de pago (FREEMIUM/PAID) desde el campo pricing ----------
    def clean(text):
        """Texto de la tarjeta: el mismo que usan el catalogo y las fichas (pitch_text en build_plugin_pages.py)."""
        return pitch_text(text)

    paid = sorted((p for p in plugins if p.get("pricing") in ("FREEMIUM", "PAID")),
                  key=lambda p: p.get("downloads") or 0, reverse=True)
    paid_html = "".join(
        '<article class="paid-card">'
        '<header class="paid-card-head"><span class="price-badge price-%s">%s</span>'
        '<span class="paid-niche">%s</span></header>'
        '<h3 class="paid-card-title"><a href="/catalog/%s/">%s</a></h3><p class="paid-card-desc">%s</p>'
        '<div class="paid-actions">'
        '<a class="btn primary" href="%s" target="_blank" rel="noopener" data-goatcounter-click="out-trial-%s">Start free trial &#8599;</a>'
        '<a class="btn" href="/catalog/%s/">Details</a></div></article>'
        % (p["pricing"].lower(), PRICING_LABEL[p["pricing"]], esc(p.get("niche")),
           esc(p["repo"]), esc(p["name"]), esc(clean(p.get("pitch"))),
           esc(p.get("marketplaceUrl") or ("/catalog/%s/" % p["repo"])), esc(p["repo"]), esc(p["repo"]))
        for p in paid
    )
    if not paid_html:
        die("ningun plugin FREEMIUM/PAID -- la seccion de pago quedaria vacia")

    # ---- hubs: data/hubs.json (vacio hasta que exista el primero) ----------
    hubs = json.loads(HUBS_DATA.read_text(encoding="utf-8")) if HUBS_DATA.exists() else []
    hubs_html = ""
    if hubs:
        cards = "".join(
            '<article class="paid-card"><div class="paid-card-head">'
            '<span class="price-badge price-%s">%s</span><span class="paid-niche">%d plugins</span></div>'
            '<h3>%s</h3><p>%s</p><div class="paid-actions">'
            '<a class="btn primary" href="%s" target="_blank" rel="noopener" data-goatcounter-click="out-hub-%s">Get the hub &#8599;</a>'
            '</div></article>'
            % (h.get("pricing", "PAID").lower(), PRICING_LABEL.get(h.get("pricing", "PAID"), "Paid"),
               len(h.get("plugins", [])), esc(h["name"]), esc(h.get("pitch")),
               esc(h["marketplaceUrl"]), esc(h["slug"]))
            for h in hubs
        )
        hubs_html = ('<section class="paid-section" id="hubs" aria-labelledby="hubsTitle">'
                     '<div class="section-head"><div><p class="eyebrow">Hubs</p>'
                     '<h2 id="hubsTitle">Plugin hubs: one install per tool family</h2></div></div>'
                     '<div class="paid-grid">%s</div></section>' % cards)

    # ---- barra de plataformas (2026-09-27): "disponible en", no patrocinio ----
    JB_MARK = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M2.345 23.997A2.347 2.347 0 0 1 0 21.652V10.988C0 9.665.535 8.37 1.473 7.433l5.965-5.961A5.01 5.01 0 0 1 10.989 0h10.666A2.347 2.347 0 0 1 24 2.345v10.664a5.056 5.056 0 0 1-1.473 3.554l-5.965 5.965A5.017 5.017 0 0 1 13.007 24v-.003H2.345Zm8.969-6.854H5.486v1.371h5.828v-1.371ZM3.963 6.514h13.523v13.519l4.257-4.257a3.936 3.936 0 0 0 1.146-2.767V2.345c0-.678-.552-1.234-1.234-1.234H10.989a3.897 3.897 0 0 0-2.767 1.145L3.963 6.514Zm-.192.192L2.256 8.22a3.944 3.944 0 0 0-1.145 2.768v10.664c0 .678.552 1.234 1.234 1.234h10.666a3.9 3.9 0 0 0 2.767-1.146l1.512-1.511H3.771V6.706Z"/></svg>')
    VS_MARK = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23.15 2.587L18.21.21a1.494 1.494 0 0 0-1.705.29l-9.46 8.63-4.12-3.128a.999.999 0 0 0-1.276.057L.327 7.261A1 1 0 0 0 .326 8.74L3.899 12 .326 15.26a1 1 0 0 0 .001 1.479L1.65 17.94a.999.999 0 0 0 1.276.057l4.12-3.128 9.46 8.63a1.492 1.492 0 0 0 1.704.29l4.942-2.377A1.5 1.5 0 0 0 24 20.06V3.939a1.5 1.5 0 0 0-.85-1.352zm-5.146 14.861L10.826 12l7.178-5.448v10.896z"/></svg>')
    GH_MARK = ('<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>')
    platforms_html = (
        '<p class="plat-label">Available on</p><div class="plat-logos">%s</div>' % "".join(
            '<a class="plat-item" href="%s" target="_blank" rel="noopener" data-goatcounter-click="%s">'
            '<span class="plat-mark">%s</span><span class="plat-text"><strong>%s</strong><span>%s</span></span></a>'
            % row for row in (
                ("https://plugins.jetbrains.com/vendor/gap-hunter-labs", "out-vendor-jetbrains", JB_MARK,
                 "JetBrains Marketplace", "%d plugins" % data["totalPlugins"]),
                ("https://marketplace.visualstudio.com/publishers/GapHunterLabs", "out-vendor-vscode", VS_MARK,
                 "VS Code Marketplace", "%d extensions" % vscode_total),
                ("https://github.com/GapHunterLabs", "out-vendor-github", GH_MARK,
                 "GitHub", "Open source, Apache-2.0"))))
    html = inject(html, "<!-- PRERENDER:PLATFORMS:START -->", "<!-- PRERENDER:PLATFORMS:END -->", platforms_html, "PLATFORMS")

    html = inject(html, "<!-- PRERENDER:SUBTITLE:START -->", "<!-- PRERENDER:SUBTITLE:END -->", esc(subtitle), "SUBTITLE")
    html = inject(html, "<!-- PRERENDER:STATS:START -->", "<!-- PRERENDER:STATS:END -->", stats_html, "STATS")
    html = inject(html, "<!-- PRERENDER:METHODFACTS:START -->", "<!-- PRERENDER:METHODFACTS:END -->", facts_html, "METHODFACTS")
    html = inject(html, "<!-- PRERENDER:CATPREVIEW:START -->", "<!-- PRERENDER:CATPREVIEW:END -->", cat_html, "CATPREVIEW")
    html = inject(html, "<!-- PRERENDER:SLIDES:START -->", "<!-- PRERENDER:SLIDES:END -->", "".join(slides), "SLIDES")
    html = inject(html, "<!-- PRERENDER:DOTS:START -->", "<!-- PRERENDER:DOTS:END -->", "".join(dots), "DOTS")
    html = inject(html, "<!-- PRERENDER:PAIDPLUGINS:START -->", "<!-- PRERENDER:PAIDPLUGINS:END -->", paid_html, "PAIDPLUGINS")
    html = inject(html, "<!-- PRERENDER:HUBS:START -->", "<!-- PRERENDER:HUBS:END -->", hubs_html, "HUBS")

    if dry_run:
        print("[dry-run] %d categorias, %d destacados -- nada escrito" % (len(src.categories) - 1, len(featured)))
        return

    HOME_PAGE.write_text(html, encoding="utf-8")
    print("[build_home] index.html: subtitulo + stats + %d facts + %d categorias + %d destacados + %d de pago + %d hubs"
          % (len(facts), len(src.categories) - 1, len(featured), len(paid), len(hubs)))


def main():
    ap = argparse.ArgumentParser(description="Pre-renderiza la home (index.html)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    build(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
