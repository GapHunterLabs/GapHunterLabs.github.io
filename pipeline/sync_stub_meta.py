#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_stub_meta.py -- copia el <title>/description/OG de cada pagina real a su
stub de redireccion (catalog.html, methodology.html, ...).

Por que existe: un stub es solo `meta refresh` + JS. Los scrapers sociales
(Slack, Discord, LinkedIn, WhatsApp) NO siguen ese redirect: leen el propio
stub, y el stub decia "Redirecting... - Gap Hunter Labs" sin ningun og:*,
asi que un enlace viejo compartido salia como una tarjeta vacia que dice
"Redirecting...". Con estas etiquetas la tarjeta sale igual que la de la
pagina real (og:url apunta a la URL limpia, asi que Facebook re-escrapea
directamente esa).

No pone noindex a proposito (ver verify_static.py): un meta refresh de 0s ya
se trata como redireccion y noindex junto a canonical son senales
contradictorias.

Idempotente: reescribe el bloque entre <!--STUBMETA--> y <!--/STUBMETA-->.
Correr despues de cambiar el title/description de una pagina real.

Uso:  python pipeline/sync_stub_meta.py
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://gaphunterlabs.github.io"
OG_IMAGE = SITE + "/og-image.png"
OG_ALT = "Gap Hunter Labs — Plugin Intelligence Catalog Report"

STUBS = (
    ("catalog.html", "catalog/index.html", "/catalog/"),
    ("methodology.html", "methodology/index.html", "/methodology/"),
    ("contact.html", "contact/index.html", "/contact/"),
    ("security.html", "security/index.html", "/security/"),
    ("laboratorio.html", "laboratorio/index.html", "/laboratorio/"),
)
OPEN, CLOSE = "<!--STUBMETA-->", "<!--/STUBMETA-->"


def die(msg: str) -> "NoReturn":  # noqa: F821
    sys.exit("[sync_stub_meta] ERROR: " + msg)


def grab(pattern: str, text: str, what: str, rel: str) -> str:
    m = re.search(pattern, text, re.S)
    if not m:
        die("no encontre %s en %s" % (what, rel))
    return m.group(1)


def main() -> None:
    for stub_name, target_rel, url_path in STUBS:
        target = (ROOT / target_rel).read_text(encoding="utf-8")
        title = grab(r"<title>(.*?)</title>", target, "<title>", target_rel).strip()
        desc = grab(r'<meta name="description" content="([^"]*)"', target, "description", target_rel)
        url = SITE + url_path
        # Los og:* van con el caracter real (em dash), no con &mdash;: los
        # scrapers sociales no siempre decodifican entidades con nombre.
        title_attr = html.escape(html.unescape(title), quote=True)
        desc = html.escape(html.unescape(desc), quote=True)
        block = "\n".join([
            OPEN,
            '<meta name="description" content="%s">' % desc,
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="Gap Hunter Labs">',
            '<meta property="og:url" content="%s">' % url,
            '<meta property="og:title" content="%s">' % title_attr,
            '<meta property="og:description" content="%s">' % desc,
            '<meta property="og:image" content="%s">' % OG_IMAGE,
            '<meta property="og:image:type" content="image/png">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            '<meta property="og:image:alt" content="%s">' % OG_ALT,
            '<meta property="og:locale" content="en_US">',
            '<meta name="twitter:card" content="summary_large_image">',
            '<meta name="twitter:site" content="@GapHunterLabs">',
            '<meta name="twitter:title" content="%s">' % title_attr,
            '<meta name="twitter:description" content="%s">' % desc,
            '<meta name="twitter:image" content="%s">' % OG_IMAGE,
            '<meta name="twitter:image:alt" content="%s">' % OG_ALT,
            CLOSE,
        ])

        path = ROOT / stub_name
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"<title>.*?</title>", lambda m: "<title>%s</title>" % title, text, count=1, flags=re.S)
        if '<meta name="viewport"' not in text:
            text = text.replace('<meta charset="UTF-8">',
                                '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">', 1)
        if OPEN in text:
            text = re.sub(re.escape(OPEN) + r".*?" + re.escape(CLOSE), lambda m: block, text, count=1, flags=re.S)
        else:
            text = text.replace("</title>", "</title>\n" + block, 1)
        path.write_text(text, encoding="utf-8", newline="\n")
        print("[sync_stub_meta] %s <- %s" % (stub_name, target_rel))


if __name__ == "__main__":
    main()
