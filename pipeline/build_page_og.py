#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_page_og.py -- one distinct 1200x630 social-share image per hand-made
site page, in English and Spanish (not the plugin cards, which
build_og_images.py already renders one-per-plugin into media/<slug>/og.png).

Supersedes _review/render_og.py: it covers home, /services/ and
/plugin-performance-audit/ with the exact same three layouts as before, and
adds every other static page (catalog, methodology, the engineering-evidence
pages, contact, security, privacy, terms, eula, ghl-jail) plus a native
Spanish image for all sixteen -- so no two pages share a preview any more.

Each image is a standalone, noindex HTML page that loads the same fonts/ and
brand mark as the live site; Chromium (via Playwright) screenshots it at
exactly 1200x630. Deliberately timeless: no live catalog numbers baked in, so
the twice-daily catalog refresh never has to regenerate these.

Output lives at the repo root next to the three originals:
  home -> og-image.png / og-image.es.png
  /services/ -> og-services.png / og-services.es.png
  ... and og-<slug>.png / og-<slug>.es.png for the rest.

The English page HTML references these directly in <head>; build_i18n.py
rewrites the ES pages' og:image from og-X.png to og-X.es.png automatically.

Requires: playwright + `python -m playwright install chromium`.

Usage:
  python pipeline/build_page_og.py                 # all 32
  python pipeline/build_page_og.py --only og-methodology og-image.es
  python pipeline/build_page_og.py --out-dir /tmp/preview --only og-image
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONTS = (ROOT / "fonts").resolve()

LOGO = (
    '<svg viewBox="172 81 675 782" aria-hidden="true">'
    '<path d="M 511,81 L 847,283 L 725,351 L 508,223 L 296,348 L 296,588 L 463,691 L 342,765 L 173,665 L 172,281 Z" fill="#0151FC"/>'
    '<path d="M 846,412 L 844,668 L 518,863 L 393,795 L 724,589 L 721,540 L 567,538 L 568,412 Z" fill="#01B3FD"/>'
    '<polygon points="569,413 695,413 695,539 569,539" fill="#02F172"/></svg>'
)

# Shared base: identical to the three original og-*-source.html files so the
# existing home/services/audit images come out byte-for-byte equivalent.
BASE_CSS = """
  @font-face { font-family:"IBM Plex Sans"; src:url("@@FONTS@@/IBMPlexSans-Latin.woff2") format("woff2"); font-weight:100 700; font-display:block; }
  @font-face { font-family:"IBM Plex Serif"; src:url("@@FONTS@@/IBMPlexSerif-SemiBold-Latin.woff2") format("woff2"); font-weight:600; font-display:block; }
  @font-face { font-family:"JetBrains Mono"; src:url("@@FONTS@@/JetBrainsMono-Latin.woff2") format("woff2"); font-weight:100 800; font-display:block; }
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:1200px; height:630px; overflow:hidden; background:#F6F8FA; color:#1F2328; font-family:"IBM Plex Sans",sans-serif; }
  .page { position:absolute; inset:28px; background:#FFFFFF; border:1px solid #D0D7DE; border-radius:2px; padding:40px 48px 30px; display:flex; flex-direction:column; }
  .top { display:flex; align-items:center; justify-content:space-between; padding-bottom:18px; border-bottom:1px solid #1F2328; }
  .brand { display:flex; align-items:center; gap:12px; font-size:22px; font-weight:600; letter-spacing:-0.01em; }
  .brand svg { width:30px; height:35px; display:block; }
  .label { font:600 16px/1 "JetBrains Mono",monospace; letter-spacing:0.1em; text-transform:uppercase; color:#57606A; }
  h1 { font-family:"IBM Plex Serif",serif; font-weight:600; letter-spacing:-0.015em; color:#1F2328; }
  .mono { font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums; }
  .foot { margin-top:auto; display:flex; justify-content:space-between; align-items:baseline; gap:20px; padding-top:16px; border-top:1px solid #D0D7DE; font:500 18px/1 "JetBrains Mono",monospace; color:#57606A; }
  .foot b { font-weight:600; color:#1F2328; }
  .tag { display:inline-block; width:52px; padding:5px 0 4px; text-align:center; font:700 12px/1 "JetBrains Mono",monospace; letter-spacing:0.1em; border-left:3px solid; }
  .tag.gap { color:#9A4A08; background:#FBF0DF; border-color:#F59E0B; }
  .tag.fix { color:#047857; background:#E3F3EC; border-color:#10B981; }
"""

# ---- layout-specific CSS ----------------------------------------------------
CSS_HOME = """
  .record { margin-top:24px; display:grid; grid-template-columns:60px 260px minmax(0,1fr); gap:12px 18px; align-items:center; font-size:24px; line-height:1.3; }
  .record .ref { font:500 19px/1.3 "JetBrains Mono",monospace; color:#57606A; }
  h1 { margin-top:30px; font-size:60px; line-height:1.08; }
  .lede { margin-top:20px; max-width:960px; font-size:26px; line-height:1.45; color:#57606A; }
"""
CSS_SERVICES = """
  h1 { margin-top:30px; font-size:52px; line-height:1.1; }
  table { margin-top:26px; width:100%; border-collapse:collapse; }
  td { padding:17px 0; border-bottom:1px solid #D0D7DE; font-size:26px; vertical-align:baseline; }
  tr:first-child td { border-top:1px solid #1F2328; }
  td.p { text-align:right; font:500 22px/1 "JetBrains Mono",monospace; font-variant-numeric:tabular-nums; white-space:nowrap; }
  td.p small { font-size:18px; color:#57606A; }
"""
CSS_AUDIT = """
  .cols { margin-top:32px; display:grid; grid-template-columns:minmax(0,1fr) 380px; gap:40px; }
  h1 { font-size:54px; line-height:1.1; }
  ul { margin-top:20px; list-style:none; border-top:1px solid #D0D7DE; }
  li { padding:11px 0; border-bottom:1px solid #D0D7DE; font-size:24px; color:#1F2328; }
  .price { border-top:1px solid #1F2328; padding-top:16px; }
  .price .amt { font:600 54px/1 "JetBrains Mono",monospace; letter-spacing:-0.02em; font-variant-numeric:tabular-nums; }
  .price .amt small { font-size:30px; font-weight:500; color:#57606A; margin-right:8px; }
  .price p { margin-top:14px; font-size:22px; line-height:1.45; color:#57606A; }
  .price p.ext { margin-top:16px; padding-top:14px; border-top:1px solid #D0D7DE; font:500 19px/1.4 "JetBrains Mono",monospace; color:#1F2328; }
"""
# Generic page: a serif headline, a grey lede, and an accent rule that carries
# the page's category colour -- enough to make every static page read as its
# own card without baking in any number that would go stale.
CSS_HERO = """
  .hero { flex:1 1 auto; display:flex; flex-direction:column; justify-content:center; align-items:flex-start; }
  .accent { width:80px; height:6px; border-radius:3px; background:#0151FC; }
  h1 { margin-top:28px; font-size:54px; line-height:1.14; max-width:1000px; }
  h1.sm { font-size:48px; }
  .lede { margin-top:24px; max-width:980px; font-size:27px; line-height:1.5; color:#57606A; }
"""

PAGE_TPL = """<!doctype html>
<html lang="@@LANG@@">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<title>Gap Hunter Labs social share preview</title>
<style>@@CSS@@</style>
</head>
<body>
<div class="page">
  <div class="top">
    <div class="brand">@@LOGO@@ Gap Hunter Labs</div>
    <div class="label">@@LABEL@@</div>
  </div>
  @@BODY@@
  <div class="foot">@@FOOT@@</div>
</div>
</body>
</html>
"""


def foot(spans):
    return "".join("<span>%s</span>" % s for s in spans)


def hero_body(headline, lede, accent="#0151FC", small=False):
    cls = "sm" if small else ""
    return ('<div class="hero"><div class="accent" style="background:%s"></div>'
            '<h1 class="%s">%s</h1><p class="lede">%s</p></div>' % (accent, cls, headline, lede))


# ---- the three original rich layouts (text parametrised for EN/ES) ----------
def home_body(h1, lede, gap_ref, gap_text, fix_ref, fix_text, gap_label="GAP", fix_label="FIX"):
    return (
        '<h1>%s</h1>\n'
        '  <p class="lede">%s</p>\n'
        '  <div class="record">\n'
        '    <span class="tag gap">%s</span><span class="ref">%s</span><span>%s</span>\n'
        '    <span class="tag fix">%s</span><span class="ref">%s</span><span>%s</span>\n'
        '  </div>' % (h1, lede, gap_label, gap_ref, gap_text, fix_label, fix_ref, fix_text)
    )


def services_body(h1, rows):
    trs = "".join(
        '<tr><td>%s</td><td class="p">%s <small>&middot; %s</small></td></tr>' % (name, price, when)
        for name, price, when in rows)
    return '<h1>%s</h1>\n  <table>%s</table>' % (h1, trs)


def audit_body(h1, bullets, amount_small, amount, price_note, ext_note):
    lis = "".join("<li>%s</li>" % b for b in bullets)
    return (
        '<div class="cols">\n'
        '    <div><h1>%s</h1><ul>%s</ul></div>\n'
        '    <div class="price"><div class="amt"><small>%s</small>%s</div>'
        '<p>%s</p><p class="ext">%s</p></div>\n'
        '  </div>' % (h1, lis, amount_small, amount, price_note, ext_note)
    )


# ---- page table -------------------------------------------------------------
# Each entry: (out_stem, lang, css, body_html, label, [foot spans]).
# out_stem -> <out_stem>.png.  ES mirrors carry the ".es" in the stem.
SITE = "gaphunterlabs.com"


def pages():
    P = []

    # ---------- HOME ----------
    P.append(("og-image", "en", CSS_HOME, home_body(
        "Find the gap.<br>Understand the cause.<br>Build the fix.",
        "Performance bottlenecks, security vulnerabilities and structural failures in developer tools and open-source software, traced to their root cause and fixed.",
        "lsp4ij#1540", "A UI-thread violation in Red Hat&rsquo;s LSP4IJ",
        "commit f38259550e", "Fixed by the maintainer after the report"),
        "Engineering practice of Joel D&iacute;az",
        ["Performance &middot; Security &middot; Reliability", "<b>Fixed-scope engagements from USD 4,500</b>", SITE]))
    P.append(("og-image.es", "es", CSS_HOME, home_body(
        "Encuentra la brecha.<br>Entiende la causa.<br>Construye la soluci&oacute;n.",
        "Cuellos de botella de rendimiento, vulnerabilidades de seguridad y fallas estructurales en herramientas de desarrollo y software de c&oacute;digo abierto, rastreados hasta su causa ra&iacute;z y corregidos.",
        "lsp4ij#1540", "Una violaci&oacute;n del hilo de UI en LSP4IJ de Red Hat",
        "commit f38259550e", "Corregido por el mantenedor tras el reporte"),
        "Estudio de ingenier&iacute;a de Joel D&iacute;az",
        ["Rendimiento &middot; Seguridad &middot; Fiabilidad", "<b>Proyectos de alcance fijo desde USD 4.500</b>", SITE]))

    # ---------- SERVICES ----------
    P.append(("og-services", "en", CSS_SERVICES, services_body(
        "Fixed scope. Published prices.", [
            ("Plugin performance audit", "USD 10,500", "10 business days"),
            ("Plugin updates for new IDE versions", "from USD 4,500", "5 business days"),
            ("Custom plugins and inspections", "from USD 7,500", "10 business days"),
            ("Dependency and CI/CD security review", "from USD 4,800", "5 business days"),
        ]),
        "Engineering services",
        ["Written deliverables &middot; 50% on start, 50% on delivery", SITE]))
    P.append(("og-services.es", "es", CSS_SERVICES, services_body(
        "Alcance fijo. Precios publicados.", [
            ("Auditor&iacute;a de rendimiento de plugins", "USD 10.500", "10 d&iacute;as h&aacute;biles"),
            ("Actualizaci&oacute;n de plugins para nuevas versiones del IDE", "desde USD 4.500", "5 d&iacute;as h&aacute;biles"),
            ("Plugins e inspecciones a medida", "desde USD 7.500", "10 d&iacute;as h&aacute;biles"),
            ("Revisi&oacute;n de seguridad de dependencias y CI/CD", "desde USD 4.800", "5 d&iacute;as h&aacute;biles"),
        ]),
        "Servicios de ingenier&iacute;a",
        ["Entregables por escrito &middot; 50% al iniciar, 50% al entregar", SITE]))

    # ---------- PLUGIN PERFORMANCE AUDIT ----------
    P.append(("og-audit", "en", CSS_AUDIT, audit_body(
        "Your plugin freezes.<br>I find the cause and patch it.",
        ["Reproduction on each IDE version you support",
         "UI-thread measurements, cold and warm",
         "Patches with before-and-after measurements"],
        "USD", "10,500",
        "Fixed price. One plugin, up to 3 IDE versions, delivered in 10 business days.",
        "Extended: USD 15,000 &middot; 15 business days"),
        "Plugin performance audit",
        ["The same method found freeze bugs in the IntelliJ Platform", SITE]))
    P.append(("og-audit.es", "es", CSS_AUDIT, audit_body(
        "Tu plugin se congela.<br>Encuentro la causa y lo parcheo.",
        ["Reproducci&oacute;n en cada versi&oacute;n del IDE que soportas",
         "Mediciones del hilo de UI, en fr&iacute;o y en caliente",
         "Parches con mediciones antes y despu&eacute;s"],
        "USD", "10.500",
        "Precio fijo. Un plugin, hasta 3 versiones del IDE, entregado en 10 d&iacute;as h&aacute;biles.",
        "Extendida: USD 15.000 &middot; 15 d&iacute;as h&aacute;biles"),
        "Auditor&iacute;a de rendimiento de plugins",
        ["El mismo m&eacute;todo hall&oacute; congelamientos en IntelliJ Platform", SITE]))

    # ---------- CATALOG ----------
    P.append(("og-catalog", "en", CSS_HERO, hero_body(
        "JetBrains &amp; VS Code plugins<br>for real developer gaps",
        "Browse every Gap Hunter Labs plugin for JetBrains IDEs and VS Code: filter by category and price, and see the gap each one fixes.",
        "#0151FC"),
        "Plugin catalog",
        ["Filter by category, platform and price", SITE]))
    P.append(("og-catalog.es", "es", CSS_HERO, hero_body(
        "Plugins para JetBrains y VS Code<br>que resuelven brechas reales",
        "Explora todos los plugins de Gap Hunter Labs para IDE de JetBrains y VS Code: filtra por categor&iacute;a y precio, y mira la brecha que resuelve cada uno.",
        "#0151FC"),
        "Cat&aacute;logo de plugins",
        ["Filtra por categor&iacute;a, plataforma y precio", SITE]))

    # ---------- METHODOLOGY ----------
    P.append(("og-methodology", "en", CSS_HERO, hero_body(
        "How a gap becomes a fix",
        "How performance, security and reliability problems are investigated and fixed, how plugin ideas are evaluated, and how catalog data is reported.",
        "#B98CFF"),
        "Methodology",
        ["Investigate &middot; Reproduce &middot; Fix &middot; Report", SITE]))
    P.append(("og-methodology.es", "es", CSS_HERO, hero_body(
        "De la brecha a la soluci&oacute;n",
        "C&oacute;mo se investigan y corrigen los problemas de rendimiento, seguridad y fiabilidad, c&oacute;mo se eval&uacute;an las ideas de plugins y c&oacute;mo se reportan los datos del cat&aacute;logo.",
        "#B98CFF"),
        "Metodolog&iacute;a",
        ["Investigar &middot; Reproducir &middot; Corregir &middot; Reportar", SITE]))

    # ---------- ENGINEERING & EVIDENCE (overview) ----------
    P.append(("og-evidence", "en", CSS_HERO, hero_body(
        "Everything that backs the work",
        "Root-cause analysis and fixes in the IntelliJ Platform, security reports fixed by open-source maintainers, and plugin case studies &mdash; each with a public source.",
        "#34D5C7"),
        "Engineering &amp; Evidence",
        ["Tickets &middot; Security reports &middot; Audits &middot; Case studies", SITE]))
    P.append(("og-evidence.es", "es", CSS_HERO, hero_body(
        "Todo lo que respalda el trabajo",
        "An&aacute;lisis de causa ra&iacute;z y correcciones en IntelliJ Platform, reportes de seguridad corregidos por mantenedores de c&oacute;digo abierto y casos de estudio de plugins &mdash; cada uno con una fuente p&uacute;blica.",
        "#34D5C7"),
        "Ingenier&iacute;a y evidencia",
        ["Tickets &middot; Reportes &middot; Auditor&iacute;as &middot; Casos", SITE]))

    # ---------- CASE STUDIES ----------
    P.append(("og-evidence-case-studies", "en", CSS_HERO, hero_body(
        "Plugins with the strongest evidence",
        "A freeze pattern JetBrains named itself, a compliance gap cloud tools cannot clear, and injection sinks behind real CVEs.",
        "#FFB020"),
        "Case studies",
        ["Engineering &amp; Evidence", SITE]))
    P.append(("og-evidence-case-studies.es", "es", CSS_HERO, hero_body(
        "Plugins con la evidencia m&aacute;s s&oacute;lida",
        "Un congelamiento que nombr&oacute; JetBrains, una brecha de cumplimiento que la nube no cubre y sinks de inyecci&oacute;n con CVE reales.",
        "#FFB020"),
        "Casos de estudio",
        ["Ingenier&iacute;a y evidencia", SITE]))

    # ---------- JETBRAINS PLATFORM TICKETS ----------
    P.append(("og-evidence-jetbrains-tickets", "en", CSS_HERO, hero_body(
        "Root-cause reports in the<br>IntelliJ Platform",
        "Bugs filed in JetBrains&rsquo; YouTrack after a catalog check found them in IntelliJ&rsquo;s source, plus root-cause analysis on existing Platform tickets.",
        "#0151FC"),
        "JetBrains Platform tickets",
        ["Engineering &amp; Evidence", SITE]))
    P.append(("og-evidence-jetbrains-tickets.es", "es", CSS_HERO, hero_body(
        "Reportes de causa ra&iacute;z en<br>IntelliJ Platform",
        "Errores reportados en el YouTrack de JetBrains tras hallarlos un control del cat&aacute;logo en el c&oacute;digo de IntelliJ, m&aacute;s an&aacute;lisis de causa ra&iacute;z en tickets existentes.",
        "#0151FC"),
        "Tickets de JetBrains Platform",
        ["Ingenier&iacute;a y evidencia", SITE]))

    # ---------- OPEN-SOURCE SECURITY REPORTS ----------
    P.append(("og-evidence-security-reports", "en", CSS_HERO, hero_body(
        "Vulnerable dependencies,<br>fixed by maintainers",
        "Vulnerable dependencies reported to open-source maintainers, each advisory checked against the exact pinned version in OSV, listed once they fixed them.",
        "#10B981"),
        "Open-source security reports",
        ["Engineering &amp; Evidence", SITE]))
    P.append(("og-evidence-security-reports.es", "es", CSS_HERO, hero_body(
        "Dependencias vulnerables,<br>corregidas por sus mantenedores",
        "Dependencias vulnerables reportadas a mantenedores de c&oacute;digo abierto, cada aviso verificado contra la versi&oacute;n exacta fijada en OSV, publicadas cuando las corrigieron.",
        "#10B981"),
        "Reportes de seguridad",
        ["Ingenier&iacute;a y evidencia", SITE]))

    # ---------- THIRD-PARTY PLUGIN AUDITS ----------
    P.append(("og-evidence-third-party-audits", "en", CSS_HERO, hero_body(
        "Findings in other vendors&rsquo;<br>plugins, fixed by them",
        "Performance findings in third-party IntelliJ Platform plugins, reported to their maintainers with the root cause and a suggested fix, listed once the fix is public.",
        "#B98CFF"),
        "Third-party plugin audits",
        ["Engineering &amp; Evidence", SITE]))
    P.append(("og-evidence-third-party-audits.es", "es", CSS_HERO, hero_body(
        "Hallazgos en plugins de otros<br>proveedores, corregidos por ellos",
        "Hallazgos de rendimiento en plugins de terceros para IntelliJ Platform, reportados a sus mantenedores con la causa ra&iacute;z y un arreglo sugerido, publicados cuando la correcci&oacute;n es p&uacute;blica.",
        "#B98CFF"),
        "Auditor&iacute;as de plugins de terceros",
        ["Ingenier&iacute;a y evidencia", SITE]))

    # ---------- CONTACT ----------
    P.append(("og-contact", "en", CSS_HERO, hero_body(
        "Get in touch",
        "Contact Gap Hunter Labs about audits and engineering work, plugin support or partnerships &mdash; by email, GitHub, JetBrains Marketplace or LinkedIn.",
        "#34D5C7"),
        "Contact",
        ["Email &middot; GitHub &middot; JetBrains &middot; LinkedIn", SITE]))
    P.append(("og-contact.es", "es", CSS_HERO, hero_body(
        "Ponte en contacto",
        "Contacta a Gap Hunter Labs por auditor&iacute;as y trabajo de ingenier&iacute;a, soporte de plugins o alianzas &mdash; por correo, GitHub, JetBrains Marketplace o LinkedIn.",
        "#34D5C7"),
        "Contacto",
        ["Correo &middot; GitHub &middot; JetBrains &middot; LinkedIn", SITE]))

    # ---------- SECURITY ----------
    P.append(("og-security", "en", CSS_HERO, hero_body(
        "What the plugins do with your<br>code &mdash; and what they don&rsquo;t",
        "What Gap Hunter Labs plugins do and don&rsquo;t do with your code, how vulnerabilities are reported, and why there&rsquo;s no formal SOC 2 / ISO certification yet.",
        "#10B981"),
        "Security",
        ["Responsible disclosure &middot; No telemetry", SITE]))
    P.append(("og-security.es", "es", CSS_HERO, hero_body(
        "Qu&eacute; hacen los plugins con tu<br>c&oacute;digo &mdash; y qu&eacute; no",
        "Qu&eacute; hacen y qu&eacute; no hacen los plugins de Gap Hunter Labs con tu c&oacute;digo, c&oacute;mo se reportan vulnerabilidades y por qu&eacute; todav&iacute;a no hay certificaci&oacute;n formal SOC 2 / ISO.",
        "#10B981"),
        "Seguridad",
        ["Divulgaci&oacute;n responsable &middot; Sin telemetr&iacute;a", SITE]))

    # ---------- PRIVACY ----------
    P.append(("og-privacy", "en", CSS_HERO, hero_body(
        "A short privacy policy",
        "What this site collects, what it doesn&rsquo;t, and why &mdash; a short privacy policy, because the site&rsquo;s actual data footprint is short.",
        "#8DACE0"),
        "Privacy",
        ["No accounts &middot; No ad tracking", SITE]))
    P.append(("og-privacy.es", "es", CSS_HERO, hero_body(
        "Una pol&iacute;tica de privacidad corta",
        "Qu&eacute; recoge este sitio, qu&eacute; no y por qu&eacute; &mdash; una pol&iacute;tica de privacidad corta, porque la huella de datos real del sitio es corta.",
        "#8DACE0"),
        "Privacidad",
        ["Sin cuentas &middot; Sin rastreo publicitario", SITE]))

    # ---------- TERMS ----------
    P.append(("og-terms", "en", CSS_HERO, hero_body(
        "Terms of Service",
        "What this catalog is, what it isn&rsquo;t, and who&rsquo;s responsible for what.",
        "#57606A", small=True),
        "Terms",
        ["Gap Hunter Labs", SITE]))
    P.append(("og-terms.es", "es", CSS_HERO, hero_body(
        "T&eacute;rminos de servicio",
        "Qu&eacute; es este cat&aacute;logo, qu&eacute; no es y qui&eacute;n responde por qu&eacute;.",
        "#57606A", small=True),
        "T&eacute;rminos",
        ["Gap Hunter Labs", SITE]))

    # ---------- EULA ----------
    P.append(("og-eula", "en", CSS_HERO, hero_body(
        "End User License Agreement",
        "License terms for the Gap Hunter Labs paid plugins on JetBrains Marketplace: the license, the Apache-2.0 source code, warranty, liability and support.",
        "#FFB020", small=True),
        "License (EULA)",
        ["Paid plugins &middot; Apache-2.0 source", SITE]))
    P.append(("og-eula.es", "es", CSS_HERO, hero_body(
        "Acuerdo de Licencia de Usuario Final",
        "T&eacute;rminos de licencia de los plugins de pago de Gap Hunter Labs en JetBrains Marketplace: la licencia, el c&oacute;digo fuente Apache-2.0, la garant&iacute;a, la responsabilidad y el soporte.",
        "#FFB020", small=True),
        "Licencia (EULA)",
        ["Plugins de pago &middot; C&oacute;digo Apache-2.0", SITE]))

    # ---------- GHL-JAIL ----------
    P.append(("og-ghl-jail", "en", CSS_HERO, hero_body(
        "A one-line Windows sandbox<br>for untrusted CLIs",
        "Run a command-line tool so it can only touch one project folder &mdash; not your SSH keys, cloud tokens or .env. No admin, no driver: just Python and Windows.",
        "#02F172"),
        "Open-source tool",
        ["No admin &middot; No driver &middot; Just Python", SITE]))
    P.append(("og-ghl-jail.es", "es", CSS_HERO, hero_body(
        "Un sandbox de Windows de una<br>l&iacute;nea para CLIs no confiables",
        "Ejecuta una herramienta de l&iacute;nea de comandos para que solo toque una carpeta de proyecto &mdash; no tus claves SSH, tokens de la nube ni tu .env. Sin administrador, sin controlador: solo Python y Windows.",
        "#02F172"),
        "Herramienta de c&oacute;digo abierto",
        ["Sin admin &middot; Sin controlador &middot; Solo Python", SITE]))

    return P


def build_html(lang, css, body, label, foot_spans):
    html = PAGE_TPL
    subs = {
        "@@LANG@@": lang,
        "@@CSS@@": (BASE_CSS + css).replace("@@FONTS@@", FONTS.as_uri()),
        "@@LOGO@@": LOGO,
        "@@LABEL@@": label,
        "@@BODY@@": body,
        "@@FOOT@@": foot(foot_spans),
    }
    for k, v in subs.items():
        html = html.replace(k, v)
    return html


def render_batch(jobs, out_dir):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("[build_page_og] ERROR: falta playwright -- pip install playwright && python -m playwright install chromium")
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
            for stem, html in jobs:
                out = out_dir / (stem + ".png")
                with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
                    f.write(html)
                    tmp = Path(f.name)
                try:
                    page.goto(tmp.resolve().as_uri(), wait_until="load")
                    page.evaluate("() => document.fonts.ready")
                    page.wait_for_timeout(300)
                    page.screenshot(path=str(out), type="png")
                finally:
                    tmp.unlink(missing_ok=True)
                if not out.exists() or out.stat().st_size < 5000:
                    sys.exit("[build_page_og] ERROR: PNG ausente o sospechosamente chico: %s" % out)
                written.append(out)
        finally:
            browser.close()
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=str(ROOT), help="donde escribir los PNG (default: raiz del repo)")
    ap.add_argument("--only", nargs="*", help="solo estos stems (p.ej. og-methodology og-image.es)")
    args = ap.parse_args()

    rows = pages()
    stems = {r[0] for r in rows}
    if args.only:
        wanted = set(args.only)
        unknown = wanted - stems
        if unknown:
            sys.exit("[build_page_og] ERROR: stems desconocidos: %s" % ", ".join(sorted(unknown)))
        rows = [r for r in rows if r[0] in wanted]

    jobs = [(stem, build_html(lang, css, body, label, fs)) for stem, lang, css, body, label, fs in rows]
    written = render_batch(jobs, Path(args.out_dir))
    for out in written:
        print("  %-42s %6.0f KB" % (out.name, out.stat().st_size / 1024))
    print("\nOK -- %d imagen(es) OG." % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
