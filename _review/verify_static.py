import json
import re
import subprocess
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).parents[1]

# 2026-09-10 (clean-URL migration): real content now lives at
# <page>/index.html so GitHub Pages serves it at /<page>/ with no
# ".html" in the address bar. The old top-level *.html files (still
# named PAGES' display names below for readability) are now tiny
# client-side redirect stubs, checked separately further down --
# they're no longer the same file as the content page.
PAGES = (
    ("index.html", "index.html"),
    ("catalog.html", "catalog/index.html"),
    ("methodology.html", "methodology/index.html"),
    ("contact.html", "contact/index.html"),
    ("security.html", "security/index.html"),
    ("laboratorio.html", "laboratorio/index.html"),
    ("privacy.html", "privacy/index.html"),
    ("terms.html", "terms/index.html"),
)
PROHIBITED = re.compile(
    r"CONSTITUTION\.md|SDK_GOTCHAS\.md|AUTOMATION_PLAYBOOK\.md|"
    r"ARCHITECTURE\.md|INTELLIJ_PLATFORM_KNOWLEDGE\.md"
)
# Regression guard for the clean-URL migration itself: these are the
# exact relative asset references that were real bugs the first time
# (they broke the moment the page moved into a subdirectory) -- a
# future edit re-introducing a relative form of any of these would
# silently 404 for every visitor on a migrated page.
RELATIVE_ASSET_REGRESSION = re.compile(
    r'(?:href|src)="(?:css/shell\.css|js/catalog-shared\.js|js/vscode-catalog\.js)"'
    r'|url\("fonts/'
)

for display_name, rel_path in PAGES:
    text = (ROOT / rel_path).read_text(encoding="utf-8")
    scripts = re.findall(r"<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>", text, re.S | re.I)
    # application/ld+json and speculationrules are data, not code (a bare
    # object literal isn't valid top-level JS), so they're allowed inline.
    # Everything else must be an external /js/*.js file: since 2026-09-24
    # the CSP's script-src has NO 'unsafe-inline', so an inline executable
    # script would simply not run in the browser (silently -- the page still
    # renders, the feature just dies). This is the regression guard for that.
    NON_EXECUTABLE_TYPES = ("application/ld+json", "speculationrules")
    inline_exec = [body for attrs, body in scripts if not any(t in attrs for t in NON_EXECUTABLE_TYPES)]
    assert not inline_exec, (display_name, "script inline ejecutable: la CSP ya no tiene 'unsafe-inline'; moverlo a /js/")
    csp = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)"', text).group(1)
    script_src = re.search(r"script-src ([^;]*)", csp).group(1)
    assert "'unsafe-inline'" not in script_src, (display_name, "script-src volvio a permitir 'unsafe-inline'")
    for src in re.findall(r'<script[^>]*\bsrc="(/[^"]*)"', text):
        assert (ROOT / src.lstrip("/")).is_file(), (display_name, "script inexistente", src)
    print(f"{display_name}: no inline scripts, CSP script-src = {script_src}")
    assert not PROHIBITED.search(text), display_name
    assert not RELATIVE_ASSET_REGRESSION.search(text), (display_name, "relative asset path regression")
    for tag in ("html", "head", "body"):
        opens = len(re.findall(rf"<{tag}[ >]", text, re.I))
        closes = len(re.findall(rf"</{tag}>", text, re.I))
        assert opens == closes == 1, (display_name, tag, opens, closes)

# Los scripts que antes vivian inline ahora son archivos: se sigue verificando
# que TODOS parseen (new Function no ejecuta nada, solo compila).
for js_file in sorted((ROOT / "js").glob("*.js")):
    subprocess.run(
        ["node", "-e",
         f"new Function(require('fs').readFileSync({json.dumps(str(js_file))},'utf8'));"
         f"console.log('js/{js_file.name}: syntax OK')"],
        check=True,
    )

# Todo `shared.X` que un script pide a catalog-shared.js (GapCatalog.ready)
# tiene que ser un export real: el rail de /security/ leia shared.GIF_URL,
# renombrado a DEMO_MEDIA en la Fase 3, y el TypeError resultante lo
# tragaba un .catch -- el rail quedo oculto durante dias sin que nada fallara.
shared_src = (ROOT / "js" / "catalog-shared.js").read_text(encoding="utf-8")
api_start = shared_src.index("var api = {")
api_block = shared_src[api_start:shared_src.index("};", api_start)]
exports = set(re.findall(r"^\s+([A-Za-z_]+):", api_block, re.M))
assert {"DEMO_MEDIA", "plugins", "esc"} <= exports, ("no pude leer el objeto api de catalog-shared.js", sorted(exports))
for js_file in sorted((ROOT / "js").glob("*.js")):
    if js_file.name == "catalog-shared.js":
        continue
    # (?<![-/\w]) y (?!js\b): no confundir "catalog-shared.js" (un nombre de
    # archivo en un comentario) con un acceso a la propiedad shared.<export>.
    used = set(re.findall(r"(?<![-/\w])shared\.(?!js\b)([A-Za-z_]+)", js_file.read_text(encoding="utf-8")))
    missing_exports = sorted(u for u in used if u not in exports)
    assert not missing_exports, (js_file.name, "pide a catalog-shared.js exports que no existen", missing_exports)

# The two shared JS modules must fetch their JSON data with an absolute
# path -- a relative fetch('data/...') resolves against the *page's*
# URL, so it 404s the instant the calling page moves into a
# subdirectory (catalog/, etc.) while working fine from the root. This
# was a real bug caught during the migration; guard against it coming
# back.
for js_name, expected in (
    ("catalog-shared.js", "fetch('/data/catalog-data.json'"),
    ("vscode-catalog.js", "fetch('/data/vscode-catalog-data.json'"),
):
    js_text = (ROOT / "js" / js_name).read_text(encoding="utf-8")
    assert expected in js_text, (js_name, "expected absolute fetch path")

data = json.loads((ROOT / "data/catalog-data.json").read_text(encoding="utf-8"))
catalog = (ROOT / "catalog" / "index.html").read_text(encoding="utf-8")
jsonld = json.loads(
    re.search(
        r'<script type="application/ld\+json" id="catalog-jsonld">(.*?)</script>',
        catalog,
        re.S,
    ).group(1)
)
# Fase 2 (2026-09-22): ya no hay noscript de respaldo -- pipeline/
# build_catalog_grid.py pre-renderiza la grilla y la tabla reales, asi
# que ESE es ahora el contenido que ve un crawler/usuario sin JS. La
# paridad se verifica contra las tarjetas y filas reales, no contra una
# lista aparte.
counts = (
    data["totalPlugins"],
    len(data["plugins"]),
    jsonld["mainEntity"]["numberOfItems"],
    len(re.findall(r'class="plugin-card"', catalog)),
    len(re.findall(r'<tr class="row"', catalog)),
)
assert len(set(counts)) == 1, counts

sitemap_text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
ElementTree.parse(ROOT / "sitemap.xml")
for slug in ("catalog", "methodology", "contact", "security", "laboratorio", "privacy", "terms"):
    assert f"https://gaphunterlabs.github.io/{slug}/</loc>" in sitemap_text, (
        "sitemap.xml missing clean-URL entry for", slug
    )
    assert f"{slug}.html" not in sitemap_text, ("sitemap.xml still has an old .html URL for", slug)

# Migración en curso a un shell con sidebar persistente (ver
# css/shell.css): las páginas ya migradas reemplazan #topbarNav
# (Catalog/Methodology/Contact) por #appSidebar (Home/Catalog/
# Methodology/Contact). Este chequeo entiende ambas generaciones -- lo
# detecta por qué id existe en la página, no por una lista fija, para
# no crashear a mitad de la migración.
# "Insights" (link + #insights anchor en index.html) sacado del sidebar
# 2026-09-10 a pedido explícito -- esa sección ya se había borrado del
# index antes (ver "borra esto del index" en el historial), el link
# quedaba apuntando a un anchor huérfano.
# "Laboratorie" (laboratorio.html) agregado al sidebar el mismo día --
# página nueva con los case studies curados a mano del catálogo. Nombre
# del nav renombrado de "Lab" a "Laboratorie" horas después, a pedido
# explícito del usuario.
# security.html no tiene entrada propia en el sidebar de 5 ítems (se
# llega vía el footer nav / el botón "Security Report" de contact) --
# por eso su active esperado es None, no falta un ítem.
for display_name, rel_path, active in (
    ("index.html", "index.html", "Home"),
    ("catalog.html", "catalog/index.html", "Catalog"),
    ("methodology.html", "methodology/index.html", "Methodology"),
    ("laboratorio.html", "laboratorio/index.html", "Laboratorie"),
    ("security.html", "security/index.html", "Security"),
    ("contact.html", "contact/index.html", "Contact"),
    ("privacy/index.html", "privacy/index.html", "Privacy"),
    ("terms/index.html", "terms/index.html", "Terms"),
):
    text = (ROOT / rel_path).read_text(encoding="utf-8")
    sidebar_match = re.search(r'<aside class="app-sidebar" id="appSidebar">(.*?)</aside>', text, re.S)
    if sidebar_match:
        nav = re.search(r'<nav class="sidebar-nav"[^>]*>(.*?)</nav>', sidebar_match.group(1), re.S).group(1)
        # Enlaces primarios (class="sidebar-link") vs subenlaces del grupo
        # "Legal" (class="sidebar-sublink", dentro de <details>): Security,
        # Privacy y Terms dejaron de ser huerfanos del sidebar (2026-09-24).
        links = re.findall(r'<a class="sidebar-link".*?</a>', nav, re.S)
        labels = [re.sub("<.*?>", "", item).strip() for item in links]
        assert labels == ["Home", "Catalog", "Methodology", "Laboratorie", "Contact"], (display_name, labels)
        sub = [re.sub("<.*?>", "", item).strip() for item in re.findall(r'<a class="sidebar-sublink".*?</a>', nav, re.S)]
        assert sub == ["Security", "Privacy", "Terms"], (display_name, "subenlaces de Legal", sub)
        group = re.search(r'<details class="sidebar-group[^"]*"([^>]*)>', nav)
        assert group and "Legal" in nav, (display_name, "falta el grupo Legal")
        has_current_sub = re.search(r'<a class="sidebar-sublink"[^>]*aria-current="page"', nav) is not None
        assert (" open" in group.group(1)) == has_current_sub, (display_name, "el grupo Legal debe llegar abierto solo en Security/Privacy/Terms")
    else:
        nav = re.search(r'<div class="topbar-nav" id="topbarNav">(.*?)</div>', text, re.S).group(1)
        assert [re.sub("<.*?>", "", item) for item in re.findall(r"<a .*?</a>", nav)] == [
            "Catalog",
            "Methodology",
            "Contact",
        ]
    current = re.findall(r'<a[^>]*aria-current="page"[^>]*>(.*?)</a>', nav, re.S)
    current = [re.sub("<.*?>", "", c).strip() for c in current]
    assert current == ([] if active is None else [active]), (display_name, current)

# Redirect stubs: the 5 old top-level *.html URLs (already indexed by
# search engines) must keep working as redirects to their new clean
# URL rather than disappearing outright -- explicit user decision
# during the clean-URL migration. Verify each stub actually points at
# its matching new location and preserves query/hash (deep links like
# catalog.html#some-repo-slug or security.html#sec-report must keep
# resolving after the redirect).
REDIRECT_STUBS = (
    ("catalog.html", "/catalog/"),
    ("methodology.html", "/methodology/"),
    ("contact.html", "/contact/"),
    ("security.html", "/security/"),
    ("laboratorio.html", "/laboratorio/"),
)
for stub_name, target in REDIRECT_STUBS:
    stub_text = (ROOT / stub_name).read_text(encoding="utf-8")
    for tag in ("html", "head", "body"):
        opens = len(re.findall(rf"<{tag}[ >]", stub_text, re.I))
        closes = len(re.findall(rf"</{tag}>", stub_text, re.I))
        assert opens == closes == 1, (stub_name, tag, opens, closes)
    assert f'content="0; url={target}"' in stub_text, (stub_name, "missing meta refresh")
    assert f'href="https://gaphunterlabs.github.io{target}"' in stub_text, (stub_name, "missing canonical")
    # Fase 0/4 del SuperPlan de SEO (2026-09-23): noindex removido a
    # proposito -- un meta refresh de 0s ya se procesa como redireccion
    # permanente, y noindex junto a canonical en el mismo documento son
    # senales contradictorias.
    assert 'noindex' not in stub_text, (stub_name, "el noindex volvio; el refresh de 0s ya basta como redireccion")
    assert f"location.replace('{target}' + location.search + location.hash)" in stub_text, (
        stub_name, "missing/incorrect JS redirect with query+hash preservation"
    )

print({
    "script_pages": len(PAGES),
    "catalog_counts": counts,
    "navigation": "passed",
    "redirect_stubs": len(REDIRECT_STUBS),
})
