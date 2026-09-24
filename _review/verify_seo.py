#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_seo.py -- guardarraíles de las fichas por plugin (/catalog/<slug>/).

Complementa a verify_static.py: aquel cuida el shell y los stubs, este
cuida la canonicalización y el contenido indexable de las 146 fichas que
genera pipeline/build_plugin_pages.py.

Falla con exit != 0 y una lista concreta de problemas. Pensado para correr
en el workflow justo después del build, antes de commitear.

Uso:  python _review/verify_seo.py
"""

from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://gaphunterlabs.github.io"
MIN_WORDS = 110          # contenido real en el HTML crudo, sin JS
TITLE_MAX = 70
DESC_MAX = 160
SLUG_MARK = "/*SLUGS*/"
SLUG_MARK_END = "/*ENDSLUGS*/"
SHIM_TARGETS = ("catalog/index.html", "index.html", "catalog.html")
STATIC_URLS = (
    SITE + "/", SITE + "/catalog/", SITE + "/methodology/",
    SITE + "/security/", SITE + "/contact/", SITE + "/laboratorio/",
)

problems: list[str] = []


def fail(where: str, msg: str) -> None:
    problems.append("%s: %s" % (where, msg))


def text_of(html: str) -> str:
    """Palabras visibles del <main>, sin etiquetas ni SVG."""
    m = re.search(r'<main class="wrap">(.*?)</main>', html, re.S)
    if not m:
        return ""
    body = re.sub(r"<svg.*?</svg>", " ", m.group(1), flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", body).strip()


def one(pattern: str, html: str, where: str, label: str):
    found = re.findall(pattern, html, re.S)
    if len(found) != 1:
        fail(where, "se esperaba 1 %s, hay %d" % (label, len(found)))
        return None
    return found[0]


def main() -> int:
    data = json.loads((ROOT / "data" / "catalog-data.json").read_text(encoding="utf-8"))
    plugins = data["plugins"]
    slugs = [p["repo"] for p in plugins]
    by_slug = {p["repo"]: p for p in plugins}

    if len(set(slugs)) != len(slugs):
        dupes = [s for s, c in Counter(slugs).items() if c > 1]
        fail("data", "slugs duplicados: %s" % dupes)
    if data.get("totalPlugins") != len(plugins):
        fail("data", "totalPlugins=%s pero hay %d plugins" % (data.get("totalPlugins"), len(plugins)))

    # ---- 1. una ficha por plugin, y ninguna de mas ------------------------
    present = {d.name for d in (ROOT / "catalog").iterdir()
               if d.is_dir() and (d / "index.html").exists()}
    missing = sorted(set(slugs) - present)
    orphan = sorted(present - set(slugs))
    if missing:
        fail("fichas", "faltan %d: %s" % (len(missing), missing[:8]))
    if orphan:
        fail("fichas", "sobran %d (plugin retirado sin borrar su pagina): %s" % (len(orphan), orphan[:8]))

    titles, descs = defaultdict(list), defaultdict(list)

    for slug in sorted(present & set(slugs)):
        where = "catalog/%s/" % slug
        p = by_slug[slug]
        url = "%s/catalog/%s/" % (SITE, slug)
        # Nombre distinto del modulo `html` importado arriba (html.unescape
        # se usa mas abajo) -- una sombra aca haria fallar esas llamadas.
        page_html = (ROOT / "catalog" / slug / "index.html").read_text(encoding="utf-8")

        # ---- canonicalización, coherente en los cuatro sitios -------------
        canonical = one(r'<link rel="canonical" href="([^"]*)">', page_html, where, "canonical")
        if canonical and canonical != url:
            fail(where, "canonical %r != %r" % (canonical, url))
        og_url = one(r'<meta property="og:url" content="([^"]*)">', page_html, where, "og:url")
        if og_url and og_url != url:
            fail(where, "og:url %r != canonical" % og_url)

        # ---- og:image por plugin (Fase 3b) ---------------------------------
        # media/<slug>/og.png lo genera pipeline/build_og_images.py aparte
        # (Chromium headless, no corre en cada build). Si existe en disco,
        # el <head> generado por build_plugin_pages.py tiene que apuntarle
        # -- si todavia no existe, debe caer a la og-image.png generica,
        # nunca a una URL de media/ inexistente.
        has_own_og = (ROOT / "media" / slug / "og.png").exists()
        expected_og = "%s/media/%s/og.png" % (SITE, slug) if has_own_og else "%s/og-image.png" % SITE
        for prop, label in ((r'<meta property="og:image" content="([^"]*)">', "og:image"),
                             (r'<meta property="og:image:secure_url" content="([^"]*)">', "og:image:secure_url"),
                             (r'<meta name="twitter:image" content="([^"]*)">', "twitter:image")):
            found = one(prop, page_html, where, label)
            if found and found != expected_og:
                fail(where, "%s %r != %r esperado" % (label, found, expected_og))
        if has_own_og:
            alt = one(r'<meta property="og:image:alt" content="([^"]*)">', page_html, where, "og:image:alt")
            if alt and alt == "Gap Hunter Labs - Plugin Intelligence Catalog Report":
                fail(where, "og:image:alt sigue siendo el generico aunque tiene imagen propia")

        title = one(r"<title>(.*?)</title>", page_html, where, "title")
        if title:
            titles[title].append(slug)
            # Se mide el texto DECODIFICADO (lo que un lector/crawler ve
            # de verdad), no los bytes de la fuente con entidades HTML.
            rendered = html.unescape(title)
            if len(rendered) > TITLE_MAX:
                fail(where, "title de %d chars visibles (max %d): %r" % (len(rendered), TITLE_MAX, rendered))
        desc = one(r'<meta name="description" content="([^"]*)">', page_html, where, "description")
        if desc:
            descs[desc].append(slug)
            rendered = html.unescape(desc)
            if len(rendered) > DESC_MAX:
                fail(where, "description de %d chars visibles (max %d): %r" % (len(rendered), DESC_MAX, rendered))
            if not desc.strip():
                fail(where, "description vacia")

        h1s = re.findall(r"<h1[ >]", page_html)
        if len(h1s) != 1:
            fail(where, "se esperaba 1 <h1>, hay %d" % len(h1s))

        if 'name="robots"' in page_html and "noindex" in page_html:
            fail(where, "una ficha indexable no puede llevar noindex")

        # ---- contenido real sin JS ----------------------------------------
        words = len(text_of(page_html).split())
        if words < MIN_WORDS:
            fail(where, "solo %d palabras en el HTML crudo (minimo %d)" % (words, MIN_WORDS))
        if 'class="boot"' in page_html or "site-loader" in page_html:
            fail(where, "la ficha arrastra el loader del catalogo")
        if "catalog-data.json" in page_html:
            fail(where, "la ficha pide el JSON del catalogo; deberia venir ya renderizada")

        # ---- datos estructurados ------------------------------------------
        blocks = re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', page_html, re.S)
        graph = None
        for raw in blocks:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                fail(where, "JSON-LD invalido: %s" % exc)
                continue
            if isinstance(parsed, dict) and "@graph" in parsed:
                graph = parsed["@graph"]
        if graph is None:
            fail(where, "falta el bloque JSON-LD @graph de la ficha")
        else:
            app = next((n for n in graph if n.get("@type") == "SoftwareApplication"), None)
            crumbs = next((n for n in graph if n.get("@type") == "BreadcrumbList"), None)
            if not app:
                fail(where, "JSON-LD sin SoftwareApplication")
            else:
                if app.get("url") != url:
                    fail(where, "JSON-LD url %r != canonical" % app.get("url"))
                if app.get("name") != p["name"]:
                    fail(where, "JSON-LD name %r != %r" % (app.get("name"), p["name"]))
                if "aggregateRating" in app:
                    fail(where, "aggregateRating de un tercero: Google no admite "
                                "ratings agregados de otro sitio")
            if not crumbs:
                fail(where, "JSON-LD sin BreadcrumbList")
            elif crumbs["itemListElement"][-1].get("name") != p["name"]:
                fail(where, "la ultima miga no es el plugin")

        # ---- enlaces internos ----------------------------------------------
        for href in re.findall(r'href="(/[^"]*)"', page_html):
            path = href.split("#")[0].split("?")[0]
            if path.endswith((".css", ".js", ".png", ".json", ".xml", ".svg", ".ico", ".txt",
                              ".woff2", ".woff", ".ttf")):
                continue
            if path and not path.endswith("/"):
                fail(where, "enlace interno sin barra final: %s" % href)
            if path.endswith(".html"):
                fail(where, "enlace interno a un stub .html: %s" % href)
        for href in re.findall(r'href="#([a-z0-9-]+)"', page_html):
            if href in by_slug:
                fail(where, "enlace a una ficha por hash en vez de su ruta: #%s" % href)

    for title, owners in titles.items():
        if len(owners) > 1:
            fail("titles", "duplicado en %s: %r" % (owners, title))
    for desc, owners in descs.items():
        if len(owners) > 1:
            fail("descriptions", "duplicada en %s" % owners)

    # ---- 2. sitemap -------------------------------------------------------
    sitemap_path = ROOT / "sitemap.xml"
    ElementTree.parse(sitemap_path)
    sitemap = sitemap_path.read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    if len(locs) != len(set(locs)):
        fail("sitemap", "hay <loc> repetidos")
    for static in STATIC_URLS:
        if static not in locs:
            fail("sitemap", "falta la URL estatica %s" % static)
    for slug in slugs:
        if "%s/catalog/%s/" % (SITE, slug) not in locs:
            fail("sitemap", "falta la ficha %s" % slug)
    if ".html" in sitemap:
        fail("sitemap", "hay URLs .html")
    # auto_update_catalog.py reescribe el <lastmod> de /catalog/ con este
    # patron exacto; si se rompe, ese script aborta el workflow entero.
    if not re.search(r"<loc>%s/catalog/</loc>\s*<lastmod>" % re.escape(SITE), sitemap):
        fail("sitemap", "la entrada de /catalog/ perdio la forma que espera auto_update_catalog.py")

    # ---- 3. shim hash -> ruta ---------------------------------------------
    for rel in SHIM_TARGETS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        m = re.search(re.escape(SLUG_MARK) + r"(\[.*?\])" + re.escape(SLUG_MARK_END), text, re.S)
        if not m:
            fail(rel, "no tiene el bloque de slugs del shim")
            continue
        try:
            listed = json.loads(m.group(1))
        except json.JSONDecodeError as exc:
            fail(rel, "la lista de slugs no parsea: %s" % exc)
            continue
        if sorted(listed) != sorted(slugs):
            fail(rel, "la lista del shim tiene %d slugs y el catalogo %d"
                 % (len(listed), len(slugs)))

    # ---- 4. CSS compartido -------------------------------------------------
    if not (ROOT / "css" / "plugin.css").exists():
        fail("css/plugin.css", "no existe; correr pipeline/build_plugin_pages.py")

    # ---- 5. catalog/index.html pre-renderizado (Fase 2) --------------------
    # El grid/tabla del propio catalogo dejaron de depender de un fetch a
    # data/catalog-data.json (pipeline/build_catalog_grid.py los escribe
    # como HTML real) -- estos chequeos fallan si esa garantia se rompe.
    catalog_text = (ROOT / "catalog" / "index.html").read_text(encoding="utf-8")
    # Substring-only checks would also flag harmless leftovers (a comment
    # mentioning the old behaviour, dead .site-loader CSS rules with no
    # matching element) -- these look for the actual code/markup that
    # would mean the page is fetching or waiting on something again.
    if re.search(r"""fetch\(\s*['"]/data/catalog-data\.json""", catalog_text):
        fail("catalog/index.html", "vuelve a hacer fetch de catalog-data.json; el grid deberia venir pre-renderizado")
    if re.search(r'<script src="/js/catalog-shared\.js"', catalog_text):
        fail("catalog/index.html", "todavia carga catalog-shared.js (solo lo necesitaba el dossier, ya removido)")
    if re.search(r'id="siteLoader"|<html[^>]*\bclass="boot"', catalog_text):
        fail("catalog/index.html", "volvio el loader (markup real, no solo la CSS muerta que queda)")
    n_cards = len(re.findall(r'class="plugin-card"', catalog_text))
    n_rows = len(re.findall(r'<tr class="row"', catalog_text))
    if n_cards != len(slugs) or n_rows != len(slugs):
        fail("catalog/index.html", "%d tarjetas / %d filas pre-renderizadas, se esperaban %d de cada una "
             "(correr pipeline/build_catalog_grid.py)" % (n_cards, n_rows, len(slugs)))
    href_slugs = set(re.findall(r'/catalog/([a-z0-9-]+)/"', catalog_text))
    missing_hrefs = set(slugs) - href_slugs
    if missing_hrefs:
        fail("catalog/index.html", "%d plugins sin <a href> real en el grid/tabla: %s"
             % (len(missing_hrefs), sorted(missing_hrefs)[:5]))

    # ---- 6. index.html pre-renderizado (Fase 2) -----------------------------
    # Mismo contrato que catalog/index.html: el hero/stats/categorias/slider
    # ya son HTML real, no un fetch -- estos chequeos fallan si esa garantia
    # se rompe.
    home_text = (ROOT / "index.html").read_text(encoding="utf-8")
    if re.search(r"""fetch\(\s*['"]/data/catalog-data\.json""", home_text):
        fail("index.html", "vuelve a hacer fetch de catalog-data.json; el hero/stats/categorias deberian venir pre-renderizados")
    if re.search(r'<script src="/js/catalog-shared\.js"', home_text):
        fail("index.html", "todavia carga catalog-shared.js (nada en esta pagina lo necesita ya)")
    if re.search(r'id="siteLoader"|<html[^>]*\bclass="boot"', home_text):
        fail("index.html", "volvio el loader (markup real, no solo la CSS muerta que queda)")
    n_slides = len(re.findall(r'class="hs-slide"', home_text))
    if n_slides == 0:
        fail("index.html", "el slider de destacados no tiene diapositivas pre-renderizadas")
    for slide_href in re.findall(r'<a class="hs-slide" href="([^"]+)"', home_text):
        if not re.match(r"^/catalog/[a-z0-9-]+/$", slide_href):
            fail("index.html", "diapositiva del hero con href no canonico: %s" % slide_href)

    # ---- 7. demos re-alojadas en /media/ (Fase 3) --------------------------
    # Las 34 demos migraron de raw.githubusercontent.com a media/<slug>/ en
    # este mismo repo (decision explicita del usuario, 2026-09-23, ver
    # DOCUMENTATION.md "Demo media") -- estos chequeos fallan si algo vuelve
    # a depender del host externo, o si <video> queda sin la CSP que
    # necesita para cargar bajo default-src 'none'.
    def csp_value(text):
        m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)"', text)
        return m.group(1) if m else ""

    # https://raw... (con el esquema) para no marcar el comentario del
    # <head> que solo MENCIONA el hostname al explicar por que ya no se usa;
    # media-src se busca DENTRO del valor real de la CSP, no en cualquier
    # parte del archivo (un comentario explicando la CSP tambien contiene
    # la frase "media-src 'self'" como prosa).
    for text, where in ((catalog_text, "catalog/index.html"), (home_text, "index.html")):
        if "https://raw.githubusercontent.com" in text:
            fail(where, "referencia real a raw.githubusercontent.com de nuevo; las demos viven en /media/")
        if "<video" in text and "media-src 'self'" not in csp_value(text):
            fail(where, "tiene <video> pero la CSP no declara media-src 'self' (default-src "
                        "'none' lo bloquea sin eso)")
    for slug in slugs:
        text = (ROOT / "catalog" / slug / "index.html").read_text(encoding="utf-8")
        if "https://raw.githubusercontent.com" in text:
            fail("catalog/%s/" % slug, "referencia real a raw.githubusercontent.com de nuevo")
        if "<video" in text and "media-src 'self'" not in csp_value(text):
            fail("catalog/%s/" % slug, "tiene <video> pero la CSP no declara media-src 'self'")

    if problems:
        print("verify_seo: %d problema(s)\n" % len(problems))
        for item in problems:
            print("  - " + item)
        return 1
    print(json.dumps({
        "fichas": len(present & set(slugs)),
        "sitemap_urls": len(locs),
        "titles_unicos": len(titles),
        "shim_targets": len(SHIM_TARGETS),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
