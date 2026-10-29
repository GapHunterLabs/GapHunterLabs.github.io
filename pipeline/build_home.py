#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_home.py -- pre-renderiza las dos piezas de la home (index.html) que
dependen de datos del catalogo:

  * TOOLS: las herramientas destacadas (lista curada a mano en TOOLS,
    con la brecha y la correccion de cada una). Nombre, precio y enlace
    salen de data/catalog-data.json.
  * CATALOG: la linea del catalogo completo, con los totales y la fecha
    del ultimo snapshot que actualiza el CI dos veces al dia.

Rediseno 2026-10-18 ("engineering notebook"): la home dejo de ser un
escaparate del catalogo. Se retiraron el subtitulo con cifras, las 4
metricas del hero, el slider de destacados, la barra de plataformas, las
categorias, la grilla de plugins de pago, los hubs y los facts del metodo,
y con ellos sus marcadores PRERENDER.

Reusa Sources de build_plugin_pages.py -- mismo parseo de
js/catalog-shared.js y mismos helpers de escape.

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
from build_plugin_pages import Sources, esc  # noqa: E402
from badges import badge, badge_row, badge_table, price_badge  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HOME_PAGE = ROOT / "index.html"
VSCODE_DATA = ROOT / "data" / "vscode-catalog-data.json"
RESEARCH_DATA = ROOT / "data" / "research.json"
PRICING_LABEL = {"FREE": "Free", "FREEMIUM": "Freemium", "PAID": "Paid"}

# (slug, brecha, correccion). Texto en ingles: build_i18n.py lo traduce
# con pipeline/i18n/es.json. Cada linea tiene que poder respaldarse con el
# pitch o la evidencia publicada del plugin.
TOOLS = (
    ("background-readaction-freeze-companion",
     "The freeze pattern that JetBrains&rsquo; Platform Blog names, a background task that reaches a "
     "blocking, non-cancellable read action, had no static check.",
     "An inspection for your plugin&rsquo;s own code. The same check found IDEA-393501 in IntelliJ itself."),
    ("openapi-companion",
     "Reviews of existing OpenAPI plugins report external <code>$ref</code> values that do not resolve, "
     "or editors that freeze the IDE on large specs.",
     "<code>$ref</code> navigation resolved entirely against local files, and a warning on every "
     "<code>$ref</code> that does not resolve."),
    ("ansible-companion",
     "Working with Ansible Vault files in the IDE depended on the <code>ansible-vault</code> command "
     "being installed.",
     "Encrypt and decrypt Ansible Vault (1.1, AES256) directly in the editor."),
    ("mermaid-companion",
     "Reviews of existing Mermaid tooling for JetBrains IDEs report false warnings and errors on valid "
     "diagrams, such as identifiers with non-ASCII characters.",
     "Syntax highlighting and syntax validation for <code>.mmd</code> and <code>.mermaid</code> files: "
     "flowchart, sequence and class diagrams."),
)


def sparkline(values, w=140, h=28):
    """Polilinea SVG (en linea, sin librerias) de una serie corta de enteros."""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    step = w / (len(values) - 1)
    pts = " ".join("%.0f,%.0f" % (i * step, h - 2 - (v - lo) * (h - 4) / span) for i, v in enumerate(values))
    label = "Downloads over the last %d days: %s to %s" % (len(values), format(values[0], ","), format(values[-1], ","))
    return ('<svg class="tw-mt-2 tw-h-7 tw-w-full" viewBox="0 0 %d %d" preserveAspectRatio="none" role="img" '
            'aria-label="%s"><polyline fill="none" stroke="var(--signal)" stroke-width="2" '
            'stroke-linejoin="round" stroke-linecap="round" points="%s"/></svg>' % (w, h, esc(label), pts))


def tile(label, value, sub_html, extra=""):
    return ('<div class="tw-bg-bg tw-p-5"><p class="tw-font-mono tw-text-xs tw-text-faint">%s</p>'
            '<p class="tw-mt-1 tw-text-3xl tw-font-bold tw-text-ink">%s</p>%s'
            '<p class="tw-mt-2 tw-text-xs tw-text-dim">%s</p></div>' % (label, value, extra, sub_html))


def sync_html(data):
    snap = (data.get("generatedAt") or "")[:10]
    return ('<span class="live-dot" aria-hidden="true"></span>'
            '<span>Catalog synced</span> <time datetime="%s">%s</time>' % (snap, snap))


def metrics_html(data, research, vscode_total):
    trend = [d["totalDownloads"] for d in data.get("trend7d", []) if "totalDownloads" in d]
    pr = research["upstreamPullRequests"]
    adv = research["advisoriesClosedUpstream"]
    tiles = [
        tile("JetBrains Marketplace downloads", format(data["totalDownloads"], ","),
             "Last 7 days", sparkline(trend) if len(trend) >= 2 else ""),
        tile("Tools in the catalog", str(data["totalPlugins"] + vscode_total),
             "<span>%d JetBrains plugins</span> &middot; <span>%d VS Code extensions</span>" % (data["totalPlugins"], vscode_total)),
        tile("Pull requests to IntelliJ", str(pr["total"]),
             "<b>%d</b> <span>integrated</span> &middot; <b>%d</b> <span>open</span>" % (pr["integrated"], pr["open"])),
        tile("Advisories closed upstream", str(adv["count"]),
             "<span>Fixed by the maintainers in</span> <code>reactive-commons-go</code>"),
    ]
    grid = ('<div class="tw-grid tw-grid-cols-2 tw-gap-px tw-overflow-hidden tw-rounded-lg tw-border tw-border-line '
            'tw-bg-line md:tw-grid-cols-4">%s</div>' % "".join(tiles))
    chips = badge_row([
        dict(label="JetBrains Marketplace", icon="jetbrains", variant="dark",
             href="https://plugins.jetbrains.com/vendor/gap-hunter-labs"),
        dict(label="GitHub", icon="github", variant="dark", href="https://github.com/GapHunterLabs"),
        dict(label="VS Code Marketplace", icon="vscode", variant="dark"),
    ])
    asof = research["asOf"]
    foot = ('<p class="tw-mt-3 tw-font-mono tw-text-xs tw-text-faint"><span>Counts as of</span> '
            '<time datetime="%s">%s</time></p>' % (asof, asof))
    return grid + '<div class="tw-mt-4">' + chips + "</div>" + foot


# Focus areas: shown in the hero card and as the "Disciplines" row of the stack table.
DISCIPLINES = [dict(label="Static analysis", icon="code", variant="dark"),
               dict(label="Performance", icon="gauge", variant="dark"),
               dict(label="Security research", icon="shield", variant="dark"),
               dict(label="Reliability", icon="layers", variant="dark")]


def focus_html():
    return badge_row(DISCIPLINES)


def stack_html():
    rows = [
        ("Platforms", [dict(label="JetBrains IDEs", icon="jetbrains", variant="dark"),
                       dict(label="IntelliJ IDEA", icon="intellij-idea", variant="dark"),
                       dict(label="VS Code", icon="vscode", variant="brand", hex6="007ACC"),
                       dict(label="Windows", icon="windows", variant="dark")]),
        ("Languages", [dict(label="Kotlin", icon="kotlin"), dict(label="Java", icon="java", variant="soft"),
                       dict(label="Python", icon="python")]),
        ("Disciplines", DISCIPLINES),
        ("Tooling", [dict(label="Gradle", icon="gradle", variant="soft"), dict(label="JUnit", icon="junit"),
                     dict(label="Git", icon="git"), dict(label="GitHub", icon="github", variant="dark"),
                     dict(label="GitHub Actions", icon="github-actions")]),
    ]
    return badge_table("Platforms, languages and tooling", rows, "stackCaption")


def die(msg: str) -> "NoReturn":  # noqa: F821
    sys.exit("[build_home] ERROR: " + msg)


def inject(html, start, end, content, label):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if len(pattern.findall(html)) != 1:
        die("marcador %s no encontrado (o duplicado) en index.html" % label)
    return pattern.sub(lambda _m: start + content + end, html, count=1)


def build(dry_run: bool = False) -> None:
    src = Sources()
    html = HOME_PAGE.read_text(encoding="utf-8")
    data = src.data
    by_slug = {p["repo"]: p for p in src.plugins}

    # ---- TOOLS: herramientas curadas -----------------------------------------
    rows = []
    for slug, gap, fix in TOOLS:
        p = by_slug.get(slug)
        if not p:
            die("la herramienta destacada %s ya no esta en el catalogo" % slug)
        pricing = p.get("pricing") or "FREE"
        rows.append(
            '<article class="tool">'
            '<div class="tool-head"><h3 class="tool-name"><a href="/catalog/%s/">%s</a></h3>'
            '<div class="badge-row tool-badges">%s%s</div></div>'
            '<dl class="tool-facts"><div><dt class="is-gap">Gap</dt><dd>%s</dd></div>'
            '<div><dt class="is-fix">Fix</dt><dd>%s</dd></div></dl>'
            '</article>'
            % (esc(slug), esc(p["name"]),
               badge("JetBrains IDEs", icon="jetbrains", variant="dark"),
               price_badge(pricing.lower(), PRICING_LABEL.get(pricing, "Free")), gap, fix)
        )
    tools_html = "".join(rows)

    # ---- CATALOG: totales y fecha del snapshot -------------------------------
    vscode_total = 0
    if VSCODE_DATA.exists():
        vscode_total = json.loads(VSCODE_DATA.read_text(encoding="utf-8")).get("totalExtensions") or 0
    snapshot = (data.get("generatedAt") or "")[:10]
    catalog_line = (
        "%d JetBrains plugins and %d VS Code extensions, each with its own page and a clear price: "
        "free, freemium or paid. Figures are synced twice a day from public JetBrains Marketplace "
        "and GitHub data (last snapshot: %s)." % (data["totalPlugins"], vscode_total, snapshot)
    )

    html = inject(html, "<!-- PRERENDER:TOOLS:START -->", "<!-- PRERENDER:TOOLS:END -->", tools_html, "TOOLS")
    research = json.loads(RESEARCH_DATA.read_text(encoding="utf-8"))
    html = inject(html, "<!-- PRERENDER:SYNC:START -->", "<!-- PRERENDER:SYNC:END -->", sync_html(data), "SYNC")
    html = inject(html, "<!-- PRERENDER:METRICS:START -->", "<!-- PRERENDER:METRICS:END -->",
                  metrics_html(data, research, vscode_total), "METRICS")
    html = inject(html, "<!-- PRERENDER:STACK:START -->", "<!-- PRERENDER:STACK:END -->", stack_html(), "STACK")
    html = inject(html, "<!-- PRERENDER:FOCUS:START -->", "<!-- PRERENDER:FOCUS:END -->", focus_html(), "FOCUS")
    html = inject(html, "<!-- PRERENDER:CATALOG:START -->", "<!-- PRERENDER:CATALOG:END -->", esc(catalog_line), "CATALOG")

    if dry_run:
        print("[dry-run] %d herramientas, catalogo: %s -- nada escrito" % (len(rows), catalog_line))
        return

    HOME_PAGE.write_text(html, encoding="utf-8")
    print("[build_home] index.html: %d herramientas destacadas + linea del catalogo (%s)" % (len(rows), snapshot))


def main():
    ap = argparse.ArgumentParser(description="Pre-renderiza la home (index.html)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    build(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
