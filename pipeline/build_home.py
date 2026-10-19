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

ROOT = Path(__file__).resolve().parents[1]
HOME_PAGE = ROOT / "index.html"
VSCODE_DATA = ROOT / "data" / "vscode-catalog-data.json"
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
            '<p class="tool-meta">JetBrains IDEs &middot; %s</p></div>'
            '<dl class="tool-facts"><div><dt class="is-gap">Gap</dt><dd>%s</dd></div>'
            '<div><dt class="is-fix">Fix</dt><dd>%s</dd></div></dl>'
            '</article>'
            % (esc(slug), esc(p["name"]), PRICING_LABEL.get(pricing, "Free"), gap, fix)
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
