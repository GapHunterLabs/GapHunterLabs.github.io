#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_page_og.py -- one distinct 1200x630 social-share image per hand-made
site page (19 pages), in English and Spanish (not the plugin cards, which
build_og_images.py renders one-per-plugin into media/<slug>/og.png).

Redesigned 2026-10-29 in the site's v3 look (see og_kit.py): near-black ground
with the hero grid and glow, a large headline, one short line of purpose and
inline-SVG badges for the platform, language, tooling or discipline that the page
itself names. Four compositions: the home (with a gap/fix evidence card),
services (price table), the performance audit (price card) and a generic hero for
every other page. Deliberately timeless: no live catalog numbers, so the twice-daily
catalog refresh never has to regenerate these.

Output lives at the repo root:
  home -> og-image.png / og-image.es.png
  /services/ -> og-services.png / og-services.es.png
  ... and og-<slug>.png / og-<slug>.es.png for the rest (38 images).

The English page HTML references these directly in <head>; build_i18n.py rewrites
the ES pages' og:image from og-X.png to og-X.es.png automatically. After changing
an image, bump OG_VERSION in site_config.py so social networks fetch it again.

Requires: playwright + `python -m playwright install chromium`.

Usage:
  python pipeline/build_page_og.py                 # all 38
  python pipeline/build_page_og.py --only og-methodology og-image.es
  python pipeline/build_page_og.py --out-dir /tmp/preview --only og-image
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import og_kit as K  # noqa: E402

ROOT = HERE.parent
NL = "\n"

CSS_HERO = """
  .headline { margin-top:0; }
  .lede { max-width:1020px; }
"""

CSS_HOME = """
  .cols { display:grid; grid-template-columns:minmax(0,1fr) 390px; gap:40px; align-items:center; }
  .headline { font-size:56px; }
  .lede { font-size:26px; margin-top:20px; max-width:640px; }
  .evidence { padding:8px 26px; }
  .evidence .row { padding:20px 0; display:grid; gap:10px; }
  .evidence .row + .row { border-top:1px solid #2E2E2E; }
  .evidence .tag { font:700 17px/1 "JetBrains Mono",monospace; letter-spacing:.14em; display:flex; align-items:center; gap:10px; }
  .evidence .tag::before { content:""; width:12px; height:12px; border-radius:50%; background:var(--c); }
  .evidence .gap { --c:#F59E0B; color:#F59E0B; } .evidence .fix { --c:#10B981; color:#10B981; }
  .evidence .ref { font:600 24px/1.2 "JetBrains Mono",monospace; color:#FFFFFF; }
  .evidence .txt { font-size:23px; line-height:1.35; color:#B4B4B4; }
"""

CSS_SERVICES = """
  .headline { font-size:62px; }
  .table { margin-top:26px; padding:2px 28px; }
  .table .tr { display:flex; align-items:baseline; justify-content:space-between; gap:24px; padding:15px 0; font-size:27px; }
  .table .tr + .tr { border-top:1px solid #2E2E2E; }
  .table .nm { color:#EDEDED; font-weight:500; }
  .table .pr { font:600 25px/1 "JetBrains Mono",monospace; color:#FFFFFF; white-space:nowrap; }
  .table .pr small { font:500 19px/1 "JetBrains Mono",monospace; color:#9A9A9A; margin-left:8px; }
"""

CSS_AUDIT = """
  .cols { display:grid; grid-template-columns:minmax(0,1fr) 400px; gap:48px; align-items:center; }
  .headline { font-size:56px; }
  .list { margin-top:22px; display:grid; gap:10px; }
  .list div { display:flex; gap:14px; align-items:baseline; font-size:26px; line-height:1.3; color:#D4D4D4; }
  .list div::before { content:""; flex:none; width:12px; height:12px; border-radius:3px; background:#FF6A1A; transform:translateY(1px); }
  .price { padding:28px 30px; }
  .price .amt { font:700 78px/1 "JetBrains Mono",monospace; letter-spacing:-0.03em; color:#FFFFFF; }
  .price .amt small { font:500 34px/1 "JetBrains Mono",monospace; color:#9A9A9A; margin-right:10px; letter-spacing:0; }
  .price p { margin-top:16px; font-size:23px; line-height:1.4; color:#B4B4B4; }
  .price p.ext { margin-top:18px; padding-top:16px; border-top:1px solid #2E2E2E; font:500 20px/1.4 "JetBrains Mono",monospace; color:#EDEDED; }
"""


def hero_body(h1, lede, badge_keys, lang):
    return ('<h1 class="headline" style="font-size:%dpx">%s</h1>'
            '<p class="lede">%s</p>%s'
            % (K.headline_size(h1), K.text_html(h1), K.esc(lede), K.badges_html(badge_keys, lang)))


def home_body(c, lang):
    return ('<div class="cols"><div>'
            '<h1 class="headline">%s</h1><p class="lede">%s</p>%s</div>'
            '<div class="card evidence">'
            '<div class="row"><span class="tag gap">%s</span><span class="ref">%s</span><span class="txt">%s</span></div>'
            '<div class="row"><span class="tag fix">%s</span><span class="ref">%s</span><span class="txt">%s</span></div>'
            '</div></div>'
            % (K.text_html(c["h1"]), K.esc(c["lede"]), K.badges_html(c["badges"], lang),
               c["gap_label"], K.esc(c["gap_ref"]), K.esc(c["gap_text"]),
               c["fix_label"], K.esc(c["fix_ref"]), K.esc(c["fix_text"])))


def services_body(c, lang):
    rows = "".join('<div class="tr"><span class="nm">%s</span><span class="pr">%s<small>· %s</small></span></div>'
                   % (K.esc(n), K.esc(p), K.esc(w)) for n, p, w in c["rows"])
    return ('<h1 class="headline">%s</h1><div class="card table">%s</div>%s'
            % (K.text_html(c["h1"]), rows, K.badges_html(c["badges"], lang).replace('class="badges"', 'class="badges" style="margin-top:22px"')))


def audit_body(c, lang):
    lis = "".join("<div>%s</div>" % K.esc(b) for b in c["bullets"])
    return ('<div class="cols"><div><h1 class="headline">%s</h1><div class="list">%s</div>%s</div>'
            '<div class="card price"><div class="amt"><small>%s</small>%s</div><p>%s</p><p class="ext">%s</p></div></div>'
            % (K.text_html(c["h1"]), lis, K.badges_html(c["badges"], lang),
               K.esc(c["cur"]), K.esc(c["amount"]), K.esc(c["price_note"]), K.esc(c["ext_note"])))


LAYOUTS = {"hero": (CSS_HERO, None), "home": (CSS_HOME, home_body), "services": (CSS_SERVICES, services_body),
           "audit": (CSS_AUDIT, audit_body)}


def page(stem, layout, en, es):
    return dict(stem=stem, layout=layout, en=en, es=es)


# Each entry has an English and a Spanish block. `label` is the mono eyebrow (what the page is), `h1` the headline
# (\n = line break), `lede` one short line of purpose, `badges` keys from og_kit.REG, `note` the footer line.
PAGES = [
    page("og-image", "home",
         dict(label="Engineering practice of Joel Díaz", h1="Find the gap.\nUnderstand the cause.\nBuild the fix.",
              lede="Performance, security and reliability failures in developer tools and open-source software, traced to their root cause and fixed.",
              badges=["static", "perf", "security", "reliability"], gap_label="GAP", fix_label="FIX",
              gap_ref="lsp4ij#1540", gap_text="A UI-thread violation in Red Hat's LSP4IJ",
              fix_ref="commit f38259550e", fix_text="Fixed by the maintainer after the report",
              note="Fixed-scope engagements from USD 4,500"),
         dict(label="Estudio de ingeniería de Joel Díaz", h1="Encuentra la brecha.\nEntiende la causa.\nConstruye la solución.",
              lede="Fallas de rendimiento, seguridad y fiabilidad en herramientas de desarrollo y código abierto, rastreadas hasta su causa raíz y corregidas.",
              badges=["static", "perf", "security", "reliability"], gap_label="BRECHA", fix_label="SOLUCIÓN",
              gap_ref="lsp4ij#1540", gap_text="Una violación del hilo de UI en LSP4IJ de Red Hat",
              fix_ref="commit f38259550e", fix_text="Corregido por el mantenedor tras el reporte",
              note="Proyectos de alcance fijo desde USD 4.500")),
    page("og-services", "services",
         dict(label="Engineering services", h1="Fixed scope. Published prices.", badges=["jetbrains", "kotlin", "gradle", "actions", "gitlab"],
              rows=[("Plugin performance audit", "USD 10,500", "10 business days"), ("Plugin updates for new IDE versions", "from USD 4,500", "5 business days"),
                    ("Custom plugins and inspections", "from USD 7,500", "10 business days"), ("Dependency and CI/CD security review", "from USD 4,800", "5 business days")],
              note="Written deliverables · 50% on start, 50% on delivery"),
         dict(label="Servicios de ingeniería", h1="Alcance fijo. Precios publicados.", badges=["jetbrains", "kotlin", "gradle", "actions", "gitlab"],
              rows=[("Auditoría de rendimiento de plugins", "USD 10.500", "10 días hábiles"), ("Actualización de plugins para nuevos IDE", "desde USD 4.500", "5 días hábiles"),
                    ("Plugins e inspecciones a medida", "desde USD 7.500", "10 días hábiles"), ("Seguridad de dependencias y CI/CD", "desde USD 4.800", "5 días hábiles")],
              note="Entregables por escrito · 50% al iniciar, 50% al entregar")),
    page("og-audit", "audit",
         dict(label="Plugin performance audit", h1="Your plugin freezes.\nI find the cause and patch it.", badges=["jetbrains", "perf"],
              bullets=["Reproduction on each IDE version you support", "UI-thread measurements, cold and warm", "Patches with before-and-after measurements"],
              cur="USD", amount="10,500", price_note="Fixed price. One plugin, up to 3 IDE versions, 10 business days.",
              ext_note="Extended: USD 15,000 · 15 business days", note="The same method found freeze bugs in the IntelliJ Platform"),
         dict(label="Auditoría de rendimiento de plugins", h1="Tu plugin se congela.\nEncuentro la causa y lo parcheo.", badges=["jetbrains", "perf"],
              bullets=["Reproducción en cada versión del IDE que soportas", "Mediciones del hilo de UI, en frío y en caliente", "Parches con mediciones antes y después"],
              cur="USD", amount="10.500", price_note="Precio fijo. Un plugin, hasta 3 versiones del IDE, 10 días hábiles.",
              ext_note="Extendida: USD 15.000 · 15 días hábiles", note="El mismo método halló congelamientos en IntelliJ Platform")),
    page("og-dependency-security", "hero",
         dict(label="Security review", h1="Dependency and CI/CD\nsecurity review",
              lede="A read-only review of your dependencies and CI/CD workflows: known CVEs, dependency confusion and workflow permissions.",
              badges=["security"], note="Fixed price from USD 4,800"),
         dict(label="Revisión de seguridad", h1="Revisión de seguridad de\ndependencias y CI/CD",
              lede="Una revisión de solo lectura de tus dependencias y flujos de CI/CD: CVE conocidos, confusión de dependencias y permisos de workflows.",
              badges=["security"], note="Precio fijo desde USD 4.800")),
    page("og-custom-plugins", "hero",
         dict(label="Custom plugins", h1="Custom plugins and\ninspections",
              lede="Static-analysis inspections tailored to your codebase, delivered as a plugin your team installs and runs in CI.",
              badges=["static", "actions", "gitlab"], note="Fixed price from USD 7,500"),
         dict(label="Plugins a medida", h1="Plugins e inspecciones\na medida",
              lede="Inspecciones de análisis estático a medida de tu código, entregadas como un plugin que tu equipo instala y corre en CI.",
              badges=["static", "actions", "gitlab"], note="Precio fijo desde USD 7.500")),
    page("og-plugin-updates", "hero",
         dict(label="IDE compatibility", h1="Plugin updates for\nnew IDE versions",
              lede="Your JetBrains plugin built and verified against the IDE versions you support: removed APIs, Kotlin K2 and Plugin Verifier failures.",
              badges=["jetbrains", "kotlin", "gradle"], note="Fixed price from USD 4,500"),
         dict(label="Compatibilidad del IDE", h1="Actualización de plugins\npara nuevos IDE",
              lede="Tu plugin de JetBrains compilado y verificado contra las versiones del IDE que soportas: API removidas, Kotlin K2 y fallos del Plugin Verifier.",
              badges=["jetbrains", "kotlin", "gradle"], note="Precio fijo desde USD 4.500")),
    page("og-catalog", "hero",
         dict(label="Plugin catalog", h1="JetBrains & VS Code plugins\nfor real developer gaps",
              lede="Every Gap Hunter Labs plugin for JetBrains IDEs and VS Code: filter by category and price and see the gap each one fixes.",
              badges=["jetbrains", "vscode", "free", "freemium", "paid"], note="Filter by category, platform and price"),
         dict(label="Catálogo de plugins", h1="Plugins para JetBrains y VS Code\nque resuelven brechas reales",
              lede="Todos los plugins de Gap Hunter Labs para IDE de JetBrains y VS Code: filtra por categoría y precio y mira la brecha que resuelve cada uno.",
              badges=["jetbrains", "vscode", "free", "freemium", "paid"], note="Filtra por categoría, plataforma y precio")),
    page("og-methodology", "hero",
         dict(label="Methodology", h1="How a gap becomes a fix",
              lede="How performance, security and reliability problems are investigated and fixed, and how the catalog data is reported.",
              badges=["perf", "security", "reliability"], note="Investigate · Reproduce · Fix · Report"),
         dict(label="Metodología", h1="De la brecha a la solución",
              lede="Cómo se investigan y corrigen los problemas de rendimiento, seguridad y fiabilidad, y cómo se reportan los datos del catálogo.",
              badges=["perf", "security", "reliability"], note="Investigar · Reproducir · Corregir · Reportar")),
    page("og-evidence", "hero",
         dict(label="Engineering & Evidence", h1="Everything that backs the work",
              lede="Root-cause analysis and fixes in the IntelliJ Platform, security reports fixed by maintainers and plugin case studies, each with a public source.",
              badges=["platform", "github", "security"], note="Tickets · Security reports · Audits · Case studies"),
         dict(label="Ingeniería y evidencia", h1="Todo lo que respalda el trabajo",
              lede="Análisis de causa raíz y correcciones en IntelliJ Platform, reportes de seguridad corregidos por mantenedores y casos de estudio, cada uno con fuente pública.",
              badges=["platform", "github", "security"], note="Tickets · Reportes · Auditorías · Casos")),
    page("og-evidence-case-studies", "hero",
         dict(label="Case studies", h1="Plugins with the strongest evidence",
              lede="A freeze pattern JetBrains named itself, a compliance gap cloud tools cannot clear, and injection sinks behind real CVEs.",
              badges=["static", "perf", "security"], note="Engineering & Evidence"),
         dict(label="Casos de estudio", h1="Plugins con la evidencia\nmás sólida",
              lede="Un congelamiento que nombró JetBrains, una brecha de cumplimiento que la nube no cubre y sinks de inyección con CVE reales.",
              badges=["static", "perf", "security"], note="Ingeniería y evidencia")),
    page("og-evidence-jetbrains-tickets", "hero",
         dict(label="JetBrains Platform tickets", h1="Root-cause reports in the\nIntelliJ Platform",
              lede="Bugs filed in JetBrains' YouTrack after a catalog check found them in IntelliJ's source, plus root-cause analysis on existing tickets.",
              badges=["idea", "platform"], note="Engineering & Evidence"),
         dict(label="Tickets de JetBrains Platform", h1="Reportes de causa raíz en\nIntelliJ Platform",
              lede="Errores reportados en el YouTrack de JetBrains tras hallarlos un control del catálogo en el código de IntelliJ, y análisis de causa raíz en tickets existentes.",
              badges=["idea", "platform"], note="Ingeniería y evidencia")),
    page("og-evidence-security-reports", "hero",
         dict(label="Open-source security reports", h1="Vulnerable dependencies,\nfixed by maintainers",
              lede="Advisories reported to open-source maintainers, each checked against the exact pinned version in OSV and listed once fixed.",
              badges=["github", "security"], note="Engineering & Evidence"),
         dict(label="Reportes de seguridad", h1="Dependencias vulnerables,\ncorregidas por sus mantenedores",
              lede="Avisos reportados a mantenedores de código abierto, cada uno verificado contra la versión exacta fijada en OSV y publicado cuando se corrigió.",
              badges=["github", "security"], note="Ingeniería y evidencia")),
    page("og-evidence-third-party-audits", "hero",
         dict(label="Third-party plugin audits", h1="Findings in other vendors'\nplugins, fixed by them",
              lede="Performance findings in third-party IntelliJ plugins, reported with the root cause and a suggested fix, listed once public.",
              badges=["platform", "perf", "audit"], note="Engineering & Evidence"),
         dict(label="Auditorías de plugins de terceros", h1="Hallazgos en plugins de otros\nproveedores, corregidos por ellos",
              lede="Hallazgos de rendimiento en plugins de terceros para IntelliJ, reportados con la causa raíz y un arreglo sugerido, publicados cuando son públicos.",
              badges=["platform", "perf", "audit"], note="Ingeniería y evidencia")),
    page("og-contact", "hero",
         dict(label="Contact", h1="Get in touch",
              lede="Audits and engineering work, plugin support or partnerships, by email, GitHub, JetBrains Marketplace or LinkedIn.",
              badges=["email", "github", "marketplace", "linkedin"], note="Email · GitHub · JetBrains · LinkedIn"),
         dict(label="Contacto", h1="Ponte en contacto",
              lede="Auditorías y trabajo de ingeniería, soporte de plugins o alianzas, por correo, GitHub, JetBrains Marketplace o LinkedIn.",
              badges=["email", "github", "marketplace", "linkedin"], note="Correo · GitHub · JetBrains · LinkedIn")),
    page("og-security", "hero",
         dict(label="Security", h1="What the plugins do with your\ncode, and what they don't",
              lede="What the plugins do and don't do with your code, how vulnerabilities are reported, and where certification stands.",
              badges=["security", "github"], note="Responsible disclosure · No telemetry"),
         dict(label="Seguridad", h1="Qué hacen los plugins con tu\ncódigo, y qué no",
              lede="Qué hacen y qué no hacen los plugins con tu código, cómo se reportan las vulnerabilidades y en qué punto está la certificación.",
              badges=["security", "github"], note="Divulgación responsable · Sin telemetría")),
    page("og-privacy", "hero",
         dict(label="Privacy", h1="A short privacy policy",
              lede="What this site collects, what it doesn't, and why: a short policy, because the data footprint is short.",
              badges=[("No accounts", "shield", "dark"), ("No ad tracking", "shield", "dark")], note="Gap Hunter Labs"),
         dict(label="Privacidad", h1="Una política de privacidad corta",
              lede="Qué recoge este sitio, qué no y por qué: una política corta, porque la huella de datos real del sitio es corta.",
              badges=[("No accounts", "shield", "dark"), ("No ad tracking", "shield", "dark")], note="Gap Hunter Labs")),
    page("og-terms", "hero",
         dict(label="Terms", h1="Terms of Service",
              lede="What this catalog is, what it isn't, and who is responsible for what.",
              badges=["jetbrains", "vscode"], note="Gap Hunter Labs"),
         dict(label="Términos", h1="Términos de servicio",
              lede="Qué es este catálogo, qué no es y quién responde por qué.",
              badges=["jetbrains", "vscode"], note="Gap Hunter Labs")),
    page("og-eula", "hero",
         dict(label="License (EULA)", h1="End User License Agreement",
              lede="License terms for the paid Gap Hunter Labs plugins on JetBrains Marketplace: license, source code, warranty, liability and support.",
              badges=["marketplace", ("Apache-2.0", "code", "dark")], note="Paid plugins · Apache-2.0 source"),
         dict(label="Licencia (EULA)", h1="Acuerdo de Licencia\nde Usuario Final",
              lede="Términos de licencia de los plugins de pago de Gap Hunter Labs en JetBrains Marketplace: licencia, código fuente, garantía, responsabilidad y soporte.",
              badges=["marketplace", ("Apache-2.0", "code", "dark")], note="Plugins de pago · Código Apache-2.0")),
    page("og-ghl-jail", "hero",
         dict(label="Open-source tool", h1="A one-line Windows sandbox\nfor untrusted CLIs",
              lede="Run a command-line tool so it can only touch one project folder, not your SSH keys, cloud tokens or .env. No admin, no driver.",
              badges=["windows", "python", "security"], note="No admin · No driver · Just Python"),
         dict(label="Herramienta de código abierto", h1="Un sandbox de Windows de una\nlínea para CLIs no confiables",
              lede="Ejecuta una herramienta de línea de comandos para que solo toque una carpeta de proyecto, no tus claves SSH, tokens de la nube ni tu .env. Sin admin, sin controlador.",
              badges=["windows", "python", "security"], note="Sin admin · Sin controlador · Solo Python")),
    page("og-sponsors", "hero",
         dict(label="Sponsors", h1="Sponsor the work",
              lede="Fund the upstream fixes and the free JetBrains and VS Code tools. Five levels from USD 5 a month, and no sponsor can change a finding or a report.",
              badges=[("Sponsorship", "heart", "dark"), "jetbrains", "vscode", "security"], note="Independent by design"),
         dict(label="Patrocinadores", h1="Patrocina el trabajo",
              lede="Financia las correcciones al origen y las herramientas gratuitas para JetBrains y VS Code. Cinco niveles desde USD 5 al mes, y ningún patrocinador puede cambiar un hallazgo o un informe.",
              badges=[("Patrocinio", "heart", "dark"), "jetbrains", "vscode", "security"], note="Independiente por diseño")),
]


def jobs():
    out = []
    for p in PAGES:
        for lang in ("en", "es"):
            c = p[lang]
            css, builder = LAYOUTS[p["layout"]]
            body = builder(c, lang) if builder else hero_body(c["h1"], c["lede"], c["badges"], lang)
            stem = p["stem"] + (".es" if lang == "es" else "")
            out.append((stem, K.page_html(lang, body, css=css, label=c["label"], note=c["note"])))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=str(ROOT), help="where to write the PNGs (default: the repo root)")
    ap.add_argument("--only", nargs="*", help="only these stems (e.g. og-methodology og-image.es)")
    ap.add_argument("--html", action="store_true", help="also write the source HTML next to the PNG (for debugging)")
    args = ap.parse_args()

    all_jobs = jobs()
    stems = {s for s, _ in all_jobs}
    if args.only:
        unknown = set(args.only) - stems
        if unknown:
            sys.exit("[build_page_og] ERROR: unknown stems: %s" % ", ".join(sorted(unknown)))
        all_jobs = [j for j in all_jobs if j[0] in set(args.only)]
    out_dir = Path(args.out_dir)
    if args.html:
        out_dir.mkdir(parents=True, exist_ok=True)
        for stem, html in all_jobs:
            (out_dir / (stem + ".html")).write_text(html, encoding="utf-8")
    written = K.render(all_jobs, lambda stem: out_dir / (stem + ".png"), label="build_page_og")
    for out in written:
        print("  %-42s %6.0f KB" % (out.name, out.stat().st_size / 1024))
    print("\nOK -- %d image(s)." % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
