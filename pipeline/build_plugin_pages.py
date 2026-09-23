#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_plugin_pages.py -- una URL real por plugin.

Convierte cada entrada de data/catalog-data.json en

    /catalog/<repo>/index.html

donde <repo> es EXACTAMENTE el mismo slug que hoy viaja en el hash del
catalogo (/catalog/#mermaid-companion), asi que cada enlace ya compartido
sigue apuntando al mismo plugin despues de la migracion.

Principio de diseno: este script NO reimplementa el dossier ni el shell.
Los lee del propio catalogo:

  * el shell (topbar, sidebar, wrappers, footer, <head>) sale de
    catalog/index.html por marcadores estables;
  * el CSS sale de los <style> inline de esa misma pagina y se escribe UNA
    vez a css/plugin.css, cacheable por las 146 fichas;
  * los mapas de datos (NICHE_TO_CATEGORY, GAP_OVERRIDES, GIF_URL,
    CATEGORIES, ICONS) se parsean de js/catalog-shared.js.

Si alguno de esos marcadores desaparece, el script aborta con un mensaje
concreto en vez de generar paginas silenciosamente rotas. Una sola fuente
de verdad; nada duplicado a mano.

Sin dependencias externas: solo biblioteca estandar.

Uso:
    python pipeline/build_plugin_pages.py --inspect
    python pipeline/build_plugin_pages.py --dry-run --limit 3
    python pipeline/build_plugin_pages.py            # genera todo
    python pipeline/build_plugin_pages.py --sitemap --inject
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SITE = "https://gaphunterlabs.github.io"
ORG_ID = SITE + "/#org"
CATALOG_URL = SITE + "/catalog/"

DATA_FILE = ROOT / "data" / "catalog-data.json"
VSX_DATA_FILE = ROOT / "data" / "vscode-catalog-data.json"
SHARED_JS = ROOT / "js" / "catalog-shared.js"
CATALOG_PAGE = ROOT / "catalog" / "index.html"
INDEX_PAGE = ROOT / "index.html"
CATALOG_STUB = ROOT / "catalog.html"
CSS_OUT = ROOT / "css" / "plugin.css"
SITEMAP = ROOT / "sitemap.xml"
LASTMOD_STORE = ROOT / "_review" / "plugin_lastmod.json"

OG_IMAGE = SITE + "/og-image.png"
OG_IMAGE_ALT = "Gap Hunter Labs - Plugin Intelligence Catalog Report"
TITLE_SOFT_MAX = 70
DESC_MAX = 155
SIMILAR_MAX = 4
GROWTH_PERCENT_MIN_BASELINE = 10

# Paginas que llevan el shim hash -> ruta.
SLUG_INJECTION_TARGETS = ("catalog/index.html", "index.html", "catalog.html")
SLUG_MARK_OPEN = "/*SLUGS*/"
SLUG_MARK_CLOSE = "/*ENDSLUGS*/"

# Campos que cuentan como contenido sustancial para el <lastmod>. Las
# metricas en vivo (downloads/growth/stars/reviews/rating) quedan fuera a
# proposito: cambian dos veces al dia y convertirian el lastmod en ruido.
MATERIAL_FIELDS = (
    "name", "pitch", "why", "niche", "pricing",
    "marketplaceUrl", "githubUrl", "firstPublished",
)


def die(msg: str) -> "NoReturn":  # noqa: F821
    sys.exit("[build_plugin_pages] ERROR: " + msg)


# =============================================================================
# 1. Parser tolerante de literales JS (objetos/arrays de catalog-shared.js)
# =============================================================================

class JsLiteralParser:
    """Lee un literal JS de objeto/array. Solo soporta lo que realmente hay
    en catalog-shared.js: strings, numeros, booleanos, null, objetos y
    arrays, con comentarios // y /* */ y claves sin comillas."""

    def __init__(self, src: str, pos: int):
        self.s = src
        self.i = pos

    def parse(self):
        self._ws()
        return self._value()

    def _ws(self):
        s, n = self.s, len(self.s)
        while self.i < n:
            c = s[self.i]
            if c in " \t\r\n":
                self.i += 1
            elif s.startswith("//", self.i):
                j = s.find("\n", self.i)
                self.i = n if j < 0 else j + 1
            elif s.startswith("/*", self.i):
                j = s.find("*/", self.i + 2)
                if j < 0:
                    die("comentario /* sin cerrar en el literal JS")
                self.i = j + 2
            else:
                return

    def _value(self):
        c = self.s[self.i]
        if c == "{":
            return self._object()
        if c == "[":
            return self._array()
        if c in "\"'":
            return self._string()
        if self.s.startswith("true", self.i):
            self.i += 4
            return True
        if self.s.startswith("false", self.i):
            self.i += 5
            return False
        if self.s.startswith("null", self.i):
            self.i += 4
            return None
        m = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?").match(self.s, self.i)
        if not m:
            die("valor JS no reconocido en la posicion %d: %r" % (self.i, self.s[self.i:self.i + 40]))
        self.i = m.end()
        text = m.group(0)
        return float(text) if ("." in text or "e" in text or "E" in text) else int(text)

    def _object(self):
        out = {}
        self.i += 1  # '{'
        self._ws()
        if self.s[self.i] == "}":
            self.i += 1
            return out
        while True:
            self._ws()
            key = self._string() if self.s[self.i] in "\"'" else self._ident()
            self._ws()
            if self.s[self.i] != ":":
                die("se esperaba ':' tras la clave %r" % key)
            self.i += 1
            self._ws()
            out[key] = self._value()
            self._ws()
            c = self.s[self.i]
            if c == ",":
                self.i += 1
                self._ws()
                if self.s[self.i] == "}":  # coma final
                    self.i += 1
                    return out
                continue
            if c == "}":
                self.i += 1
                return out
            die("se esperaba ',' o '}' tras el valor de %r" % key)

    def _array(self):
        out = []
        self.i += 1  # '['
        self._ws()
        if self.s[self.i] == "]":
            self.i += 1
            return out
        while True:
            self._ws()
            out.append(self._value())
            self._ws()
            c = self.s[self.i]
            if c == ",":
                self.i += 1
                self._ws()
                if self.s[self.i] == "]":
                    self.i += 1
                    return out
                continue
            if c == "]":
                self.i += 1
                return out
            die("se esperaba ',' o ']' dentro del array JS")

    def _ident(self):
        m = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*").match(self.s, self.i)
        if not m:
            die("clave JS invalida en la posicion %d" % self.i)
        self.i = m.end()
        return m.group(0)

    _ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "0": "\0"}

    def _string(self):
        quote = self.s[self.i]
        self.i += 1
        buf = []
        while True:
            c = self.s[self.i]
            if c == "\\":
                nxt = self.s[self.i + 1]
                if nxt == "u":
                    buf.append(chr(int(self.s[self.i + 2:self.i + 6], 16)))
                    self.i += 6
                elif nxt == "x":
                    buf.append(chr(int(self.s[self.i + 2:self.i + 4], 16)))
                    self.i += 4
                else:
                    buf.append(self._ESCAPES.get(nxt, nxt))
                    self.i += 2
                continue
            if c == quote:
                self.i += 1
                return "".join(buf)
            if c == "\n":
                die("salto de linea dentro de un string JS")
            buf.append(c)
            self.i += 1


def js_literal(src: str, name: str, label: str):
    m = re.search(r"\bvar\s+" + re.escape(name) + r"\s*=\s*", src)
    if not m:
        die("no se encontro `var %s =` en %s -- el renderer cambio, revisar antes de generar" % (name, label))
    return JsLiteralParser(src, m.end()).parse()


# =============================================================================
# 2. Helpers de render (puerto 1:1 de los de js/catalog-shared.js)
# =============================================================================

def esc(value) -> str:
    """Mismo escape que esc() en catalog-shared.js: & < > "."""
    if value is None:
        return ""
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def safe_url(value) -> str:
    """Mismo gate que safeUrl(): solo http(s) sobrevive."""
    if value is None:
        return "#"
    text = str(value).strip()
    return text if re.match(r"^https?://", text, re.I) else "#"


def md_inline(text) -> str:
    """Puerto de mdInline(): **negrita** y pares de backticks."""
    out = esc(text).replace("\n", " ")
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    parts = out.split("`")
    if len(parts) < 3:
        return out
    rebuilt = parts[0]
    i = 1
    while i + 1 < len(parts):
        rebuilt += "<code>" + parts[i] + "</code>" + parts[i + 1]
        i += 2
    if i < len(parts):
        rebuilt += "`" + parts[i]
    return rebuilt


def plain_text(value) -> str:
    """Igual que plain_text() de auto_update_catalog.py: markdown fuera."""
    text = "" if value is None else str(value)
    text = re.sub(r"`+", "", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def thousands(n) -> str:
    return "{:,}".format(int(n))


def truncate(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit - 1].rstrip()
    space = cut.rfind(" ")
    if space > limit * 0.6:
        cut = cut[:space]
    return cut.rstrip(" ,.;:-") + "…"


# =============================================================================
# 3. Fuentes: datos + mapas + shell
# =============================================================================

class Sources:
    def __init__(self):
        self.data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        self.plugins = self.data["plugins"]
        self.shared_js = SHARED_JS.read_text(encoding="utf-8")
        self.catalog_html = CATALOG_PAGE.read_text(encoding="utf-8")

        label = "js/catalog-shared.js"
        self.niche_to_category = js_literal(self.shared_js, "NICHE_TO_CATEGORY", label)
        self.gap_overrides = js_literal(self.shared_js, "GAP_OVERRIDES", label)
        self.gif_url = js_literal(self.shared_js, "GIF_URL", label)
        self.categories = js_literal(self.shared_js, "CATEGORIES", label)
        self.icons = js_literal(self.shared_js, "ICONS", label)
        self.cat_icon_inner = js_literal(self.shared_js, "CAT_ICON_INNER", label)

        # ICON_CALENDAR vive inline en catalog/index.html (ningun otro
        # consumidor lo usa); se extrae de ahi para no duplicarlo.
        m = re.search(r"var\s+ICON_CALENDAR\s*=\s*'((?:[^'\\]|\\.)*)'", self.catalog_html)
        if not m:
            die("no se encontro ICON_CALENDAR en catalog/index.html")
        self.icon_calendar = m.group(1).replace("\\'", "'")

        # Cross-reference real a VS Code, por el mismo slug de repo.
        self.vsx_by_repo = {}
        if VSX_DATA_FILE.exists():
            vsx = json.loads(VSX_DATA_FILE.read_text(encoding="utf-8"))
            for e in vsx.get("extensions", []):
                if e.get("name"):
                    self.vsx_by_repo[e["name"]] = e

        self.css = self._build_css()
        self.cat_color = self._resolve_category_colors()
        for p in self.plugins:
            p["categoryKey"] = self.niche_to_category.get(p.get("niche"), "other")
        self.cat_by_key = {c["key"]: c for c in self.categories}

    # ---- CSS -------------------------------------------------------------
    def _build_css(self) -> str:
        # Los <style> que viven dentro de un <noscript> son condicionales
        # por definicion (el del catalogo oculta el loader cuando no hay
        # JS): sacarlos de ahi los volveria incondicionales, asi que se
        # excluyen antes de extraer nada.
        without_noscript = re.sub(r"<noscript>.*?</noscript>", "", self.catalog_html, flags=re.S)
        blocks = re.findall(r"<style>(.*?)</style>", without_noscript, re.S)
        if not blocks:
            die("catalog/index.html no tiene bloques <style> -- shell cambiado")
        css = "\n".join(blocks)
        # El dossier estatico usa <h1> donde el overlay usaba <h2>: una
        # pagina, un H1. Se amplia el selector en vez de duplicar la regla.
        css, n = re.subn(r"\.dossier-title-row h2\b", ".dossier-title-row :is(h1, h2)", css)
        if n != 1:
            die("se esperaba 1 regla `.dossier-title-row h2`, se encontraron %d" % n)
        return css + PLUGIN_PAGE_CSS

    def _resolve_category_colors(self) -> dict:
        """CATEGORIES guarda el nombre del token (--accent); en el navegador
        lo resuelve getComputedStyle. Aca se resuelve leyendo el :root."""
        root = re.search(r":root\s*\{(.*?)\}", self.css, re.S)
        if not root:
            die("no se encontro un bloque :root en el CSS del catalogo")
        tokens = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", root.group(1)))
        colors = {}
        for cat in self.categories:
            token = cat["colorToken"]
            if token not in tokens:
                die("el token de color %s (categoria %s) no existe en :root" % (token, cat["key"]))
            colors[cat["key"]] = tokens[token].strip()
        return colors


PLUGIN_PAGE_CSS = """

/* ------------------------------------------------------------------
   Generado por pipeline/build_plugin_pages.py -- NO editar a mano.
   Ajustes minimos para la ficha estatica: en el catalogo el dossier es
   un panel dentro de una pagina, aca es la pagina entera, y las tarjetas
   "similar" pasan de <div> con JS a <a> reales.
   ------------------------------------------------------------------ */
.plugin-page .dossier-sheet { margin: 0; }
.plugin-page .dossier-card { animation: none; }
.crumbs {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  font-family: var(--mono); font-size: 12px; color: var(--text-faint);
  margin: 0 0 var(--space-4);
}
.crumbs a { color: var(--text-dim); text-decoration: none; }
.crumbs a:hover { color: var(--accent); }
.crumbs [aria-current="page"] { color: var(--text); }
.crumb-sep { opacity: .55; }
a.similar-card, a.tbl-similar-card { text-decoration: none; color: inherit; }
.dossier-back { text-decoration: none; }
.plugin-asof {
  font-family: var(--mono); font-size: 11.5px; color: var(--text-faint);
  margin: var(--space-4) 0 0;
}
"""


# =============================================================================
# 4. Render de una ficha
# =============================================================================

class PluginRenderer:
    def __init__(self, src: Sources):
        self.src = src

    # ---- piezas portadas del dossier ------------------------------------
    def pricing_label(self, pricing, is_pending):
        if is_pending:
            return ("pending", "Pending")
        return {"FREE": ("free", "Free"),
                "FREEMIUM": ("freemium", "Freemium"),
                "PAID": ("paid", "Paid")}.get(pricing, ("free", pricing or "—"))

    def gap_text(self, p):
        return self.src.gap_overrides.get(p["repo"]) or p.get("why") or "—"

    def platform_of(self, p):
        m = re.match(r"^(IntelliJ[^.]*?plugin)\s*[.(]", p.get("pitch") or "")
        return m.group(1) if m else "IntelliJ-family"

    def marketplace_id(self, p):
        if not p.get("marketplaceUrl"):
            return None
        m = re.search(r"/plugin/(\d+)-", p["marketplaceUrl"])
        return m.group(1) if m else None

    def growth_fact_line(self, p):
        if p.get("growth") is None or p.get("growthFrom") is None or p.get("downloads") is None:
            return "New listing"
        arrow = "▲ +" if p["growth"] > 0 else ("▼ " if p["growth"] < 0 else "")
        return "%s%.1f%% since %s (%s→%s)" % (
            arrow, p["growth"], p.get("growthSince"), p["growthFrom"], p["downloads"])

    def growth_markup(self, p):
        g = p.get("growth")
        title = ("Since %s: %s → %s" % (p.get("growthSince"), p.get("growthFrom"), p.get("downloads"))
                 if p.get("growthSince") else "No earlier snapshot")
        attr = ' title="%s"' % esc(title)
        if g is None:
            return '<span class="growth flat"%s>—</span>' % attr
        if p.get("growthFrom") is not None and p["growthFrom"] < GROWTH_PERCENT_MIN_BASELINE and p.get("downloads") is not None:
            delta = p["downloads"] - p["growthFrom"]
            if delta > 0:
                return '<span class="growth up"%s>▲ +%d</span>' % (attr, delta)
            if delta < 0:
                return '<span class="growth down"%s>▼ %d</span>' % (attr, delta)
            return '<span class="growth flat"%s>±0</span>' % attr
        if g > 0:
            return '<span class="growth up"%s>▲ %.1f%%</span>' % (attr, g)
        if g < 0:
            return '<span class="growth down"%s>▼ %.1f%%</span>' % (attr, abs(g))
        return '<span class="growth flat"%s>0%%</span>' % attr

    def cat_icon_html(self, key):
        inner = self.src.cat_icon_inner.get(key) or self.src.cat_icon_inner["other"]
        return '<svg viewBox="-8 -8 16 16" aria-hidden="true">%s</svg>' % inner

    def similar_card_html(self, s):
        cat = self.src.cat_by_key.get(s["categoryKey"], self.src.cat_by_key["other"])
        color = self.src.cat_color[cat["key"]]
        dl = "Pending" if s.get("downloads") is None else thousands(s["downloads"]) + " downloads"
        return (
            '<a class="similar-card" href="/catalog/%s/" aria-label="%s details">'
            '<span class="card-cat" style="--cat:%s" title="%s" aria-hidden="true">%s</span>'
            '<div class="sc-name">%s</div><div class="sc-niche">%s</div>'
            '<div class="sc-dl">%s</div></a>'
        ) % (esc(s["repo"]), esc(s["name"]), color, esc(cat["label"]),
             self.cat_icon_html(s["categoryKey"]), esc(s["name"]), esc(s.get("niche")), dl)

    # ---- cuerpo de la ficha ---------------------------------------------
    def body_html(self, p):
        src, icons = self.src, self.src.icons
        is_pending = p.get("downloads") is None
        pr_cls, pr_text = self.pricing_label(p.get("pricing"), is_pending)
        cat = src.cat_by_key.get(p["categoryKey"], src.cat_by_key["other"])
        color = src.cat_color[cat["key"]]
        gif = src.gif_url.get(p["repo"])
        mp_id = self.marketplace_id(p)

        similar = sorted(
            (o for o in src.plugins
             if o["repo"] != p["repo"] and o["categoryKey"] == p["categoryKey"]),
            key=lambda o: o.get("downloads") or 0, reverse=True)[:SIMILAR_MAX]

        h = []
        h.append('<nav class="crumbs" aria-label="Breadcrumb">'
                 '<a href="/">Home</a><span class="crumb-sep">›</span>'
                 '<a href="/catalog/">Catalog</a><span class="crumb-sep">›</span>'
                 '<span aria-current="page">%s</span></nav>' % esc(p["name"]))
        h.append('<div class="dossier-sheet"><div class="dossier-card">')
        h.append('<a class="dossier-back" href="/catalog/">← All plugins</a>')
        h.append('<div class="dossier-top">')
        h.append('<div class="dossier-intro"><div class="dossier-title-row"><h1>%s</h1>'
                 '<span class="chip %s">%s</span>'
                 '<span class="chip" style="background:color-mix(in srgb, %s 20%%, transparent); color:%s">%s</span></div>'
                 '<div class="dossier-niche">%s</div>'
                 '<div class="dossier-pitch">%s</div>'
                 % (esc(p["name"]), pr_cls, esc(pr_text), color, color, esc(cat["label"]),
                    esc(p.get("niche")), md_inline(p.get("pitch") or "—")))
        h.append('<div class="dossier-stats">')
        h.append('<div class="stat"><span class="stat-icon">%s</span><div><div class="num">%s</div>'
                 '<div class="label">Downloads%s</div></div></div>'
                 % (icons["downloads"],
                    "—" if is_pending else thousands(p["downloads"]),
                    "" if is_pending else " " + self.growth_markup(p)))
        h.append('<div class="stat"><span class="stat-icon">%s</span><div><div class="num">%s</div>'
                 '<div class="label">GitHub stars</div></div></div>'
                 % (icons["github"], p.get("stars") if p.get("stars") is not None else "—"))
        h.append('<div class="stat"><span class="stat-icon">%s</span><div><div class="num">%s</div>'
                 '<div class="label">Published</div></div></div>'
                 % (src.icon_calendar, esc(p.get("firstPublished") or "—")))
        h.append('</div></div>')

        h.append('<div class="dossier-side"><div class="dossier-links">')
        if p.get("marketplaceUrl"):
            h.append('<a class="btn primary" href="%s" target="_blank" rel="noopener">'
                     '<span class="btn-icon">%s</span>Install on JetBrains ↗</a>'
                     % (esc(safe_url(p["marketplaceUrl"])), icons["jetbrains"]))
        h.append('<a class="btn" href="%s" target="_blank" rel="noopener">'
                 '<span class="btn-icon">%s</span>View on GitHub ↗</a>'
                 % (esc(safe_url(p.get("githubUrl"))), icons["github"]))
        vsx = src.vsx_by_repo.get(p["repo"])
        if vsx:
            h.append('<a class="btn" href="%s" target="_blank" rel="noopener">'
                     '<span class="btn-icon">%s</span>Download for VS Code ↗</a>'
                     % (esc(safe_url(vsx.get("marketplaceUrl"))), icons["vscode"]))
        h.append('</div>')
        if gif:
            h.append('<img class="dossier-gif" src="%s" alt="%s in action" loading="lazy" decoding="async">'
                     % (esc(gif), esc(p["name"])))
        h.append('</div></div></div>')

        h.append('<div class="dossier-body">')
        h.append('<div class="info-block"><div class="ib-head"><span class="ib-icon gap">!</span>'
                 '<span class="ib-title">The Gap</span></div><div class="ib-body">%s</div></div>'
                 % md_inline(self.gap_text(p)))
        h.append('<div class="info-block"><div class="ib-head"><span class="ib-icon fix">✓</span>'
                 '<span class="ib-title">The Fix</span></div><div class="ib-body">%s</div></div>'
                 % md_inline(p.get("pitch") or "—"))
        h.append('</div>')

        h.append('<div class="info-block facts-block"><div class="ib-head">'
                 '<span class="ib-icon facts">⚙</span><span class="ib-title">Facts</span></div>'
                 '<ul class="facts-list">'
                 '<li><span class="fk">Category</span><span class="fv">%s</span></li>'
                 '<li><span class="fk">Pricing</span><span class="fv">%s</span></li>'
                 '<li><span class="fk">Platform</span><span class="fv">%s</span></li>'
                 '<li><span class="fk">First published</span><span class="fv">%s</span></li>'
                 '<li><span class="fk">Marketplace ID</span><span class="fv">%s</span></li>'
                 '<li><span class="fk">Repository</span><span class="fv"><code>%s</code>'
                 '<button type="button" class="copy-btn" data-copy="%s" aria-label="Copy repository name">%s</button>'
                 '</span></li>'
                 '<li><span class="fk">Growth</span><span class="fv">%s</span></li>'
                 '</ul></div>'
                 % (esc(cat["label"]), esc(pr_text), esc(self.platform_of(p)),
                    esc(p.get("firstPublished") or "—"),
                    ("#" + esc(mp_id)) if mp_id else ("Pending" if is_pending else "—"),
                    esc(p["repo"]), esc(p["repo"]), icons["copy"],
                    esc(self.growth_fact_line(p))))

        if similar:
            h.append('<div class="similar-section"><div class="similar-title">'
                     'Similar plugins you might like</div><div class="similar-grid">')
            h.extend(self.similar_card_html(s) for s in similar)
            h.append('</div></div>')

        h.append('</div>')
        h.append('<p class="plugin-asof">Download and star counts as of %s, refreshed twice daily '
                 'from the JetBrains Marketplace and GitHub APIs.</p>'
                 % esc((self.src.data.get("generatedAt") or "")[:10]))
        return "".join(h)

    # ---- metadatos -------------------------------------------------------
    def title(self, p):
        # Presupuesto de caracteres, no una plantilla fija: el nombre del
        # plugin ya varia entre 12 y 39 caracteres (p.ej. "Background
        # ReadAction Freeze Companion"), asi que "nombre + niche + cola"
        # puede pasarse de TITLE_SOFT_MAX antes de sumar la marca. Se
        # recorta el niche primero (lo menos importante para SEO), nunca
        # el nombre del plugin.
        name = p["name"]
        niche = plain_text(p.get("niche")) or "JetBrains"
        tail = " for IntelliJ"
        sep = " — "
        fixed_len = len(name) + len(sep) + len(tail)
        if fixed_len > TITLE_SOFT_MAX:
            # Ni siquiera nombre+cola entra: se cae la cola tambien.
            return truncate(name, TITLE_SOFT_MAX)
        budget = TITLE_SOFT_MAX - fixed_len
        niche_fit = niche if len(niche) <= budget else (truncate(niche, budget) if budget >= 4 else None)
        base = (name + sep + niche_fit + tail) if niche_fit else (name + tail)
        with_brand = base + " | Gap Hunter Labs"
        return with_brand if len(esc(with_brand)) <= TITLE_SOFT_MAX else base

    def description(self, p):
        text = plain_text(p.get("pitch")) or plain_text(self.gap_text(p))
        # truncate() acota la longitud del texto plano, pero esc() (que
        # va a envolver este valor en un atributo HTML) puede inflarlo --
        # cada `"` o `&` que sobreviva al corte suma varios caracteres al
        # escapar. Encoger hasta que la version ESCAPADA (la que
        # verify_seo.py y un crawler realmente miden) entre en el limite.
        limit = DESC_MAX
        result = truncate(text, limit)
        while len(esc(result)) > DESC_MAX and limit > 40:
            limit -= 10
            result = truncate(text, limit)
        return result

    def jsonld(self, p, url):
        app = {
            "@type": "SoftwareApplication",
            "@id": url + "#app",
            "name": p["name"],
            "url": url,
            "description": plain_text(p.get("pitch")),
            "applicationCategory": "DeveloperApplication",
            "operatingSystem": "IntelliJ Platform",
            "publisher": {"@id": ORG_ID},
        }
        same_as = [u for u in (p.get("marketplaceUrl"), p.get("githubUrl")) if u]
        vsx = self.src.vsx_by_repo.get(p["repo"])
        if vsx and vsx.get("marketplaceUrl"):
            same_as.append(vsx["marketplaceUrl"])
        if same_as:
            app["sameAs"] = same_as
        if p.get("marketplaceUrl"):
            app["downloadUrl"] = p["marketplaceUrl"]
        if p.get("firstPublished"):
            app["datePublished"] = p["firstPublished"]
        if p.get("pricing") == "FREE":
            app["offers"] = {"@type": "Offer", "price": "0", "priceCurrency": "USD"}
        # Sin aggregateRating a proposito: las valoraciones son de otro
        # sitio (Marketplace) y Google no admite ratings agregados de
        # terceros -- marcarlos es una violacion de sus guidelines, no un
        # rich result gratis.
        crumbs = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Catalog", "item": CATALOG_URL},
                {"@type": "ListItem", "position": 3, "name": p["name"]},
            ],
        }
        payload = {"@context": "https://schema.org", "@graph": [app, crumbs]}
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        return raw.replace("</script>", "<\\/script>")


# =============================================================================
# 5. Shell: se recorta del propio catalog/index.html
# =============================================================================

LOADER_RE = re.compile(r'<div id="siteLoader".*?<!-- Crawler fallback', re.S)
NOSCRIPT_RE = re.compile(r'<noscript id="catalog-crawler">.*?</noscript>\s*', re.S)
CATALOG_JSONLD_RE = re.compile(
    r'<script type="application/ld\+json" id="catalog-jsonld">.*?</script>\s*', re.S)
MAIN_RE = re.compile(r'(<main class="wrap">).*?(</main>)', re.S)
TAIL_SCRIPTS_RE = re.compile(
    r'<script src="/js/catalog-shared\.js"></script>.*?(?=<script data-goatcounter)', re.S)
STYLE_RE = re.compile(r"<style>.*?</style>\s*", re.S)


class Shell:
    """Plantilla derivada de catalog/index.html. Cada recorte tiene su
    assert: si el shell cambia de forma, el build falla y lo dice."""

    def __init__(self, src: Sources):
        html = src.catalog_html

        def cut(pattern, replacement, label, expected=1):
            new, n = pattern.subn(replacement, html, count=expected)
            if n != expected:
                die("marcador del shell no encontrado: %s "
                    "(catalog/index.html cambio; revisar build_plugin_pages.py)" % label)
            return new

        # El shim hash -> ruta solo tiene sentido en el catalogo y en la
        # home: una ficha ya ES el destino, y su lista de 146 slugs pesa
        # mas que todo el resto del <head>.
        html = cut(re.compile(r"<script>(?:(?!</script>).)*?/\*SLUGS\*/.*?</script>\s*", re.S),
                   "", "shim de slugs")
        html = cut(LOADER_RE, "<!-- Crawler fallback", "loader")
        html = cut(NOSCRIPT_RE, "", "noscript crawler")
        html = cut(CATALOG_JSONLD_RE, "@@JSONLD@@\n", "catalog-jsonld")
        html = cut(TAIL_SCRIPTS_RE, '<script src="/js/plugin-page.js" defer></script>\n', "scripts del catalogo")
        html = cut(MAIN_RE, r"\1@@BODY@@\2", "<main class=\"wrap\">")

        # Todo el CSS inline pasa a /css/plugin.css: una descarga cacheada
        # por las 146 fichas en vez de ~107 KB repetidos en cada una. El
        # <noscript> que envolvia la regla del loader se va con el loader.
        n_styles = len(STYLE_RE.findall(html))
        if n_styles < 1:
            die("no quedan bloques <style> que reemplazar")
        html = cut(re.compile(r"<noscript>\s*<style>.*?</style>\s*</noscript>\s*", re.S),
                   "", "noscript del loader")
        html = STYLE_RE.sub("", html)
        html = html.replace('<link rel="stylesheet" href="/css/shell.css">',
                            '<link rel="stylesheet" href="/css/plugin.css">\n'
                            '<link rel="stylesheet" href="/css/shell.css">', 1)
        if "/css/plugin.css" not in html:
            die("no se encontro el <link> a /css/shell.css para anclar plugin.css")

        html = html.replace('<html lang="en" class="boot">', '<html lang="en">', 1)
        if 'class="boot"' in html:
            die("la clase boot sigue presente tras quitar el loader")

        # Los comentarios del <head> de catalog/index.html son documentacion
        # de esa pagina (por que la CSP dice lo que dice, etc.): valiosos en
        # el fuente, 8 KB repetidos 146 veces aca. Se quitan solo de las
        # copias generadas; el original no se toca.
        html = re.sub(r"<!--(?!\[if).*?-->\s*", "", html, flags=re.S)
        for marker in ('<meta charset="UTF-8">', '@@BODY@@', '@@JSONLD@@',
                       'id="topbarBurger"', 'class="site-footer"'):
            if marker not in html:
                die("se perdio %r al quitar los comentarios del shell" % marker)

        # El sidebar marca Catalog como pagina actual; en una ficha sigue
        # siendo la seccion activa, asi que se deja tal cual.
        html = self._swap_head(html)
        self.template = html

    @staticmethod
    def _swap_head(html: str) -> str:
        subs = [
            (r'<meta name="description" content="[^"]*">', '<meta name="description" content="@@DESC@@">', "description"),
            (r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="@@URL@@">', "canonical"),
            (r"<title>.*?</title>", "<title>@@TITLE@@</title>", "title"),
            (r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="@@URL@@">', "og:url"),
            (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="@@OGTITLE@@">', "og:title"),
            (r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="@@DESC@@">', "og:description"),
            (r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="article">', "og:type"),
            (r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="@@OGTITLE@@">', "twitter:title"),
            (r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="@@DESC@@">', "twitter:description"),
        ]
        for pattern, replacement, label in subs:
            html, n = re.subn(pattern, replacement, html, count=1, flags=re.S)
            if n != 1:
                die("no se pudo reemplazar %s en el <head> del shell" % label)
        return html

    def render(self, *, title, og_title, desc, url, jsonld, body):
        out = self.template
        out = out.replace("@@TITLE@@", esc(title))
        out = out.replace("@@OGTITLE@@", esc(og_title))
        out = out.replace("@@DESC@@", esc(desc))
        out = out.replace("@@URL@@", esc(url))
        out = out.replace("@@JSONLD@@",
                          '<script type="application/ld+json">%s</script>' % jsonld)
        out = out.replace("@@BODY@@", body)
        left = [m for m in re.findall(r"@@[A-Z]+@@", out)]
        if left:
            die("quedaron marcadores sin resolver en la plantilla: %s" % sorted(set(left)))
        return out


# =============================================================================
# 6. Sitemap
# =============================================================================

def rebuild_sitemap(slugs_with_lastmod, static_entries):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in static_entries:
        lines += ["  <url>", "    <loc>%s</loc>" % loc,
                  "    <lastmod>%s</lastmod>" % lastmod, "  </url>"]
    for slug, lastmod in slugs_with_lastmod:
        lines += ["  <url>", "    <loc>%s/catalog/%s/</loc>" % (SITE, slug),
                  "    <lastmod>%s</lastmod>" % lastmod, "  </url>"]
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def read_static_entries():
    """Conserva las 6 URLs estaticas actuales con su lastmod real.
    changefreq/priority se descartan: Google no los usa desde hace anos."""
    text = SITEMAP.read_text(encoding="utf-8")
    entries = re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", text)
    static = [(loc, lastmod) for loc, lastmod in entries if "/catalog/" not in loc or loc.endswith("/catalog/")]
    if not any(loc == CATALOG_URL for loc, _ in static):
        die("sitemap.xml no tiene la entrada de /catalog/ -- auto_update_catalog.py depende de ella")
    return static


# =============================================================================
# 7. Shim hash -> ruta
# =============================================================================

def inject_slugs(slugs, apply=True):
    payload = json.dumps(sorted(slugs), ensure_ascii=False, separators=(",", ","))
    touched, missing = [], []
    for rel in SLUG_INJECTION_TARGETS:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        if SLUG_MARK_OPEN not in text:
            missing.append(rel)
            continue
        new = re.sub(
            re.escape(SLUG_MARK_OPEN) + r"\[.*?\]" + re.escape(SLUG_MARK_CLOSE),
            lambda _m: SLUG_MARK_OPEN + payload + SLUG_MARK_CLOSE,
            text, count=1, flags=re.S)
        if new == text:
            continue
        if apply:
            path.write_text(new, encoding="utf-8")
        touched.append(rel)
    return touched, missing


# =============================================================================
# 8. Main
# =============================================================================

def cmd_inspect(src: Sources):
    from collections import Counter
    keys = Counter()
    for p in src.plugins:
        keys.update(p.keys())
    print("plugins: %d  (generatedAt %s)" % (len(src.plugins), src.data.get("generatedAt")))
    print("\ncampos del JSON:")
    for k, c in keys.most_common():
        sample = next((p[k] for p in src.plugins if p.get(k) not in (None, "")), None)
        print("  %-16s %3d/%d  ej: %s" % (k, c, len(src.plugins), repr(sample)[:70]))
    print("\nmapas parseados de js/catalog-shared.js:")
    print("  NICHE_TO_CATEGORY %d  GAP_OVERRIDES %d  GIF_URL %d  CATEGORIES %d  ICONS %d"
          % (len(src.niche_to_category), len(src.gap_overrides), len(src.gif_url),
             len(src.categories), len(src.icons)))
    print("  colores resueltos: %s" % src.cat_color)
    print("  VS Code cross-refs: %d" % len(src.vsx_by_repo))
    unmapped = sorted({p["niche"] for p in src.plugins if p["categoryKey"] == "other"})
    if unmapped:
        print("\n  niches que caen en 'other' (%d): %s" % (len(unmapped), unmapped))
    bad = [p["repo"] for p in src.plugins
           if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", p.get("repo") or "")]
    if bad:
        print("\n  !! repos que no sirven como ruta: %s" % bad)
    dup = [r for r, c in Counter(p["repo"] for p in src.plugins).items() if c > 1]
    if dup:
        print("  !! repos duplicados: %s" % dup)


def main():
    ap = argparse.ArgumentParser(description="Genera /catalog/<slug>/index.html por plugin")
    ap.add_argument("--inspect", action="store_true", help="imprime el esquema real y sale")
    ap.add_argument("--dry-run", action="store_true", help="no escribe nada")
    ap.add_argument("--limit", type=int, default=0, help="genera solo las primeras N fichas")
    ap.add_argument("--sitemap", action="store_true", help="reescribe sitemap.xml")
    ap.add_argument("--inject", action="store_true", help="inyecta los slugs en el shim")
    args = ap.parse_args()

    src = Sources()
    if args.inspect:
        cmd_inspect(src)
        return

    seen = {}
    for p in src.plugins:
        slug = p.get("repo")
        if not slug or not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
            die("repo invalido como ruta: %r (plugin %r)" % (slug, p.get("name")))
        if slug in seen:
            die("repo duplicado: %r" % slug)
        seen[slug] = p

    renderer = PluginRenderer(src)
    shell = Shell(src)

    store = json.loads(LASTMOD_STORE.read_text(encoding="utf-8")) if LASTMOD_STORE.exists() else {}
    today = date.today().isoformat()
    rows = src.plugins if not args.limit else src.plugins[:args.limit]

    written, unchanged, lastmods = 0, 0, []
    for p in rows:
        slug = p["repo"]
        url = "%s/catalog/%s/" % (SITE, slug)
        page = shell.render(
            title=renderer.title(p),
            # En una tarjeta social el nombre del plugin ya es el gancho;
            # el sufijo de categoria que ayuda en SERP solo estorba ahi.
            og_title="%s — Gap Hunter Labs" % p["name"],
            desc=renderer.description(p),
            url=url,
            jsonld=renderer.jsonld(p, url),
            body=renderer.body_html(p),
        )
        # Marca la pagina para que el CSS de la ficha pueda diferenciarse
        # del panel del catalogo sin duplicar reglas.
        page = page.replace('<div class="app-main">', '<div class="app-main plugin-page">', 1)

        fingerprint = json.dumps({k: p.get(k) for k in MATERIAL_FIELDS},
                                 ensure_ascii=False, sort_keys=True)
        prev = store.get(slug, {})
        lastmod = prev.get("lastmod", today) if prev.get("fingerprint") == fingerprint else today
        lastmods.append((slug, lastmod))
        store[slug] = {"fingerprint": fingerprint, "lastmod": lastmod}

        out = ROOT / "catalog" / slug / "index.html"
        if args.dry_run:
            written += 1
            continue
        if out.exists() and out.read_text(encoding="utf-8") == page:
            unchanged += 1
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        written += 1

    if args.dry_run:
        print("[dry-run] %d fichas renderizadas, nada escrito" % written)
        return

    CSS_OUT.write_text(src.css, encoding="utf-8")
    LASTMOD_STORE.parent.mkdir(parents=True, exist_ok=True)
    LASTMOD_STORE.write_text(json.dumps(store, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    print("[build] %d fichas escritas, %d sin cambios -> catalog/<slug>/index.html" % (written, unchanged))
    print("[build] css/plugin.css %d KB" % (len(src.css) // 1024))

    if args.sitemap:
        if args.limit:
            die("--sitemap con --limit generaria un sitemap incompleto")
        SITEMAP.write_text(rebuild_sitemap(lastmods, read_static_entries()), encoding="utf-8")
        print("[build] sitemap.xml: %d estaticas + %d fichas" % (len(read_static_entries()), len(lastmods)))

    if args.inject:
        touched, missing = inject_slugs([s for s, _ in lastmods])
        print("[build] shim actualizado en: %s" % (touched or "nada que actualizar"))
        if missing:
            print("[build] AVISO: falta el bloque %s en %s" % (SLUG_MARK_OPEN, missing))


if __name__ == "__main__":
    main()
