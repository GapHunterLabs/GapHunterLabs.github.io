#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_og_images.py -- genera media/<slug>/og.png (1200x630) para cada
plugin, sustituyendo pipeline/og_plugin_template.html y renderizandolo
con Chromium headless via Playwright (mismo motor que _review/render_og.py
para la home/services -- un solo renderizador en todo el sitio).

Reusa Sources/PluginRenderer de build_plugin_pages.py -- misma fuente de
verdad de categoria/color/icono/pricing que ya usa el resto del sitio,
nada duplicado a mano.

Migrado 2026-10-12 de puppeteer-core/Edge (que exigia un Edge/Chrome del
sistema, ausente en esta maquina) a Playwright, que trae su propio
Chromium. Un unico navegador renderiza los 146 en una sola sesion.

Requiere:
  * playwright instalado (`pip install playwright` +
    `python -m playwright install chromium`).

Uso:
    python pipeline/build_og_images.py --limit 3         # prueba rapida
    python pipeline/build_og_images.py --slug mermaid-companion
    python pipeline/build_og_images.py                   # los 146
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "pipeline"
sys.path.insert(0, str(PIPELINE))

from build_plugin_pages import Sources, PluginRenderer, esc, thousands, truncate, plain_text  # noqa: E402

TEMPLATE = PIPELINE / "og_plugin_template.html"
MEDIA_DIR = ROOT / "media"
FONT_SANS = (ROOT / "fonts" / "IBMPlexSans-Latin.woff2").resolve()
FONT_MONO = (ROOT / "fonts" / "JetBrainsMono-Latin.woff2").resolve()

PRICING_DOT = {
    "free": "#34D5C7",
    "freemium": "#B98CFF",
    "paid": "#FFB020",
    "pending": "#8DACE0",
}


def die(msg: str) -> "NoReturn":  # noqa: F821
    sys.exit("[build_og_images] ERROR: " + msg)


def name_font_size(name: str) -> int:
    n = len(name)
    if n <= 18:
        return 58
    if n <= 26:
        return 50
    if n <= 34:
        return 42
    return 36


def file_url(path: Path) -> str:
    return "file:///" + str(path).replace("\\", "/")


def platform_badges(src, p, icons) -> str:
    badges = []
    if p.get("marketplaceUrl"):
        badges.append('<div class="badge">%s JetBrains</div>' % icons["jetbrains"])
    vsx = src.vsx_by_repo.get(p["repo"])
    if vsx and vsx.get("marketplaceUrl"):
        badges.append('<div class="badge">%s VS Code</div>' % icons["vscode"])
    return "\n        ".join(badges)


def stat_pair(p):
    if p.get("downloads") is not None:
        stat1 = (thousands(p["downloads"]), "Downloads")
    else:
        stat1 = ("New", "Listing")
    if p.get("rating") is not None:
        stat2 = ("%.1f ★" % p["rating"], "Rating")
    elif p.get("stars"):
        stat2 = (thousands(p["stars"]), "GitHub stars")
    else:
        stat2 = (esc(p.get("firstPublished") or "—"), "Published")
    return stat1, stat2


def build_html(renderer: PluginRenderer, src: Sources, p: dict) -> str:
    icons = src.icons
    is_pending = p.get("downloads") is None
    pr_cls, pr_text = renderer.pricing_label(p.get("pricing"), is_pending)
    cat = src.cat_by_key.get(p["categoryKey"], src.cat_by_key["other"])
    color = src.cat_color[cat["key"]]
    # description() ya es el mismo texto que usan meta description/og:description
    # de la propia ficha -- pitch real, acotado y sin markdown, no el "why"
    # de investigacion (que suele terminar en "...complaints:" sin cerrar).
    tagline = truncate(renderer.description(p), 150)
    stat1, stat2 = stat_pair(p)

    tpl = TEMPLATE.read_text(encoding="utf-8")
    subs = {
        "@@FONT_SANS@@": file_url(FONT_SANS),
        "@@FONT_MONO@@": file_url(FONT_MONO),
        "@@NAME_FONT_SIZE@@": str(name_font_size(p["name"])),
        "@@NAME@@": esc(p["name"]),
        "@@NICHE@@": esc(p.get("niche") or ""),
        "@@TAGLINE@@": esc(tagline),
        "@@PRICING_DOT@@": PRICING_DOT[pr_cls],
        "@@PRICING_LABEL@@": esc(pr_text),
        "@@PLATFORM_BADGES@@": platform_badges(src, p, icons),
        "@@CAT_COLOR@@": color,
        "@@CAT_ICON@@": src.cat_icon_inner.get(p["categoryKey"]) or src.cat_icon_inner["other"],
        "@@CAT_LABEL@@": esc(cat["label"]),
        "@@STAT1_VALUE@@": esc(stat1[0]),
        "@@STAT1_LABEL@@": esc(stat1[1]),
        "@@STAT2_VALUE@@": esc(stat2[0]),
        "@@STAT2_LABEL@@": esc(stat2[1]),
    }
    for token, value in subs.items():
        tpl = tpl.replace(token, value)
    leftover = re.findall(r"@@[A-Z0-9_]+@@", tpl)
    if leftover:
        die("quedaron tokens sin resolver para %s: %s" % (p["repo"], sorted(set(leftover))))
    return tpl


def render_batch(pairs):
    """Renderiza todos los (slug, html) en una sola sesion de Chromium."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        die("falta playwright -- `pip install playwright` + `python -m playwright install chromium`")

    outputs = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
            for slug, html in pairs:
                out_dir = MEDIA_DIR / slug
                out_dir.mkdir(parents=True, exist_ok=True)
                out_png = out_dir / "og.png"
                with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
                    f.write(html)
                    tmp_path = Path(f.name)
                try:
                    page.goto(tmp_path.resolve().as_uri(), wait_until="load")
                    page.evaluate("() => document.fonts.ready")
                    page.wait_for_timeout(300)
                    page.screenshot(path=str(out_png), type="png")
                finally:
                    tmp_path.unlink(missing_ok=True)
                if not out_png.exists() or out_png.stat().st_size < 5000:
                    die("PNG de salida sospechosamente chico o ausente para %s" % slug)
                outputs.append((slug, out_png))
        finally:
            browser.close()
    return outputs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--slug", default=None, help="generar solo este repo")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        die("falta pipeline/og_plugin_template.html")

    src = Sources()
    renderer = PluginRenderer(src)

    rows = src.plugins
    if args.slug:
        rows = [p for p in rows if p["repo"] == args.slug]
        if not rows:
            die("no existe el repo %r" % args.slug)
    elif args.limit:
        rows = rows[: args.limit]

    pairs = [(p["repo"], build_html(renderer, src, p)) for p in rows]
    results = render_batch(pairs)
    for slug, out_png in results:
        size_kb = out_png.stat().st_size / 1024
        print("  %-40s -> %s (%.0f KB)" % (slug, out_png.relative_to(ROOT), size_kb))

    print("\nOK -- %d imagen(es) OG generada(s)." % len(results))


if __name__ == "__main__":
    main()
