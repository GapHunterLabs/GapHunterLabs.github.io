#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actualizacion automatica diaria del catalogo -- corre DENTRO de este
repo (GapHunterLabs.github.io), disparado por
.github/workflows/update-catalog.yml (cron diario). No depende de
ningun archivo local de los 34 repos de plugins -- a diferencia del
pipeline original (../pipeline/28_catalog_report.py +
29_catalog_artifact_data.py, que viven en el repo raiz "Gap Hunter
Labs" y leen plugin.xml/README.md locales de cada repo hermano), este
script es standalone: solo necesita `pipeline/catalog_static_metadata.json`
(los campos que casi nunca cambian -- pitch/why/niche/xmlId, congelados
a mano la ultima vez que alguien corrio el pipeline original) mas 2
APIs publicas en vivo:

1. JetBrains Marketplace (`searchPlugins` + `/plugins/<id>/comments`)
   -- descargas, pricing, reviews/rating. Mismos endpoints que el
   pipeline original.
2. GitHub (`gh repo view <owner>/<repo> --json stargazerCount`) --
   estrellas. `gh` CLI viene preinstalada en runners `ubuntu-latest`,
   sin necesitar autenticacion extra para leer repos publicos.

Que hace:
1. Lee `pipeline/catalog_static_metadata.json` (34 entradas fijas).
2. Para cada plugin: resuelve el id numerico real via `searchPlugins`
   (nunca asumir el id -- confirmado que puede cambiar), trae
   descargas/pricing/reviews/rating en vivo, trae stars via `gh`.
3. Calcula growth-desde-baseline igual que el pipeline original,
   usando el MISMO `out/catalog_history.json` versionado en el repo
   raiz -- pero como este script vive en un repo separado, la
   comparacion de growth usa el ultimo snapshot que este propio repo
   ya tiene guardado (`pipeline/catalog_daily_history.json`, propio de
   ESTE repo, se va acumulando dia a dia desde que el workflow arranco
   -- no es el mismo archivo que el pipeline manual, serian historias
   distintas si se mezclaran).
4. Escribe el JSON compacto listo para inyectar
   (`pipeline/catalog_latest_data.json`) y hace el swap-in-place
   dentro de `index.html` (mismo mecanismo ya usado en cada refresh
   manual: regex sobre `<script id="catalog-data">`, valida JSON antes
   y despues).
5. Imprime un resumen -- el workflow hace `git diff --stat` despues y
   solo commitea si de verdad cambio algo (evita commits vacios todos
   los dias si las metricas no se movieron).

Uso:  python pipeline/auto_update_catalog.py
      (pensado para correr con cwd = raiz de este repo, ver el workflow)
"""
import json
import os
import re
import sys
import subprocess
import urllib.request
import html
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINE_DIR = os.path.join(ROOT, "pipeline")
STATIC_PATH = os.path.join(PIPELINE_DIR, "catalog_static_metadata.json")
HISTORY_PATH = os.path.join(PIPELINE_DIR, "catalog_daily_history.json")
LATEST_PATH = os.path.join(PIPELINE_DIR, "catalog_latest_data.json")
INDEX_PATH = os.path.join(ROOT, "index.html")
SITEMAP_PATH = os.path.join(ROOT, "sitemap.xml")

API = "https://plugins.jetbrains.com/api"
UA = {"User-Agent": "gap-hunter-auto-update/1.0", "Accept": "application/json"}


def get(url):
    return json.load(urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=30))


def resolve_numeric_id(xml_id, name):
    url = "%s/searchPlugins?search=%s" % (API, urllib.request.quote(name))
    try:
        data = get(url)
    except Exception as e:
        print(f"  [warn] searchPlugins fallo para '{name}': {e}", file=sys.stderr)
        return None
    for p in data.get("plugins", []):
        if p.get("xmlId") == xml_id:
            # Defense in depth: `id` becomes the numeric segment of
            # marketplaceUrl below, which index.html's safeUrl() already
            # gates to http(s)-only before ever using it in an href -- but
            # validating the *shape* here too means a malformed/non-numeric
            # `id` (a JetBrains API bug, or a compromised response) never
            # even reaches catalog_latest_data.json in the first place,
            # rather than relying solely on the browser-side gate.
            plugin_id = p.get("id")
            if not isinstance(plugin_id, int):
                print(f"  [warn] id no-numerico para '{name}' ({plugin_id!r}), tratando como no encontrado", file=sys.stderr)
                return None
            return p
    return None


def fetch_reviews(numeric_id):
    try:
        comments = get("%s/plugins/%s/comments" % (API, numeric_id))
    except Exception:
        return 0, None
    ratings = [c.get("rating") for c in comments if c.get("rating")]
    avg = round(sum(ratings) / len(ratings), 2) if ratings else None
    return len(comments), avg


def github_stars(repo):
    try:
        out = subprocess.run(
            ["gh", "repo", "view", "GapHunterLabs/%s" % repo, "--json", "stargazerCount"],
            capture_output=True, text=True, timeout=20,
        )
        if out.returncode != 0:
            print(f"  [warn] gh repo view fallo para {repo}: {out.stderr.strip()}", file=sys.stderr)
            return None
        return json.loads(out.stdout).get("stargazerCount")
    except Exception as e:
        print(f"  [warn] gh repo view excepcion para {repo}: {e}", file=sys.stderr)
        return None


def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"snapshots": []}


def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def earliest_datapoint(history, xml_id):
    for snap in history.get("snapshots", []):
        if xml_id in snap.get("plugins", {}):
            return snap["date"], snap["plugins"][xml_id]["downloads"]
    return None, None


SITE = "https://gaphunterlabs.github.io/"

JSONLD_RE = re.compile(
    r'(<script type="application/ld\+json" id="catalog-jsonld">)(.*?)(</script>)',
    re.S,
)
NOSCRIPT_RE = re.compile(
    r'(<noscript id="catalog-crawler">)(.*?)(</noscript>)',
    re.S,
)
CATALOG_DATA_RE = re.compile(
    r'(<script id="catalog-data" type="application/json">)(.*?)(</script>)',
    re.S,
)


def plain_text(s):
    s = "" if s is None else str(s)
    s = re.sub(r"`+", "", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_catalog_jsonld(rows, generated_at):
    elements = []
    for i, p in enumerate(rows, 1):
        url = p.get("marketplaceUrl") or p.get("githubUrl") or SITE
        item = {
            "@type": "SoftwareApplication",
            "name": p.get("name") or p.get("repo"),
            "url": url,
            "applicationCategory": "DeveloperApplication",
            "operatingSystem": "IntelliJ Platform",
        }
        desc = plain_text(p.get("pitch"))
        if desc:
            item["description"] = desc
        if p.get("githubUrl"):
            item["sameAs"] = p["githubUrl"]
        if p.get("marketplaceUrl"):
            item["downloadUrl"] = p["marketplaceUrl"]
        if p.get("firstPublished"):
            item["datePublished"] = p["firstPublished"]
        if p.get("pricing") == "FREE":
            item["offers"] = {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
            }
        reviews = p.get("reviews") or 0
        rating = p.get("rating")
        if reviews > 0 and rating:
            item["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(rating),
                "ratingCount": str(int(reviews)),
                "bestRating": "5",
                "worstRating": "1",
            }
        elements.append({
            "@type": "ListItem",
            "position": i,
            "item": item,
        })
    payload = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Gap Hunter Labs Plugin Catalog",
        "url": SITE,
        "description": "A catalog of IntelliJ/JetBrains-family IDE plugins, each built from a documented, evidence-based gap in an existing tool.",
        "inLanguage": "en",
        "isPartOf": {"@id": SITE + "#org"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(rows),
            "itemListOrder": "https://schema.org/ItemListUnordered",
            "itemListElement": elements,
        },
    }
    if generated_at:
        payload["dateModified"] = generated_at[:10]
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return raw.replace("</script>", "<\\/script>")


def build_catalog_noscript(rows):
    items = []
    for p in rows:
        name = html.escape(p.get("name") or p.get("repo") or "Plugin")
        pitch = html.escape(plain_text(p.get("pitch")))
        mp = p.get("marketplaceUrl")
        gh = p.get("githubUrl")
        if mp:
            title = '<a href="%s">%s</a>' % (html.escape(mp, quote=True), name)
        else:
            title = name
        parts = [title]
        if pitch:
            parts.append(" — " + pitch)
        if gh:
            parts.append(
                ' <a href="%s">Source</a>' % html.escape(gh, quote=True)
            )
        items.append("<li>" + "".join(parts) + "</li>")
    n = str(len(rows))
    return (
        '\n  <div style="max-width:720px;margin:40px auto;padding:24px;'
        "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;"
        'color:#E9EDF8;background:#090D16;">\n'
        '    <p style="font-size:22px;font-weight:700;margin:0 0 12px;">'
        "Gap Hunter Labs — IntelliJ &amp; JetBrains Plugin Catalog</p>\n"
        '    <p style="color:#9AA6C4;line-height:1.6;margin:0 0 16px;">'
        + n
        + " IntelliJ-family plugins, each built from a documented gap in existing tooling. "
        '<a href="https://plugins.jetbrains.com/vendor/gap-hunter-labs" style="color:#3FA2FF;">JetBrains Marketplace</a>'
        ' · <a href="https://github.com/GapHunterLabs" style="color:#3FA2FF;">GitHub</a></p>\n'
        '    <ol style="color:#E9EDF8;line-height:1.55;padding-left:1.3em;">\n      '
        + "\n      ".join(items)
        + "\n    </ol>\n  </div>\n"
    )


def _replace_inner(page_html, pattern, inner, label):
    if not pattern.search(page_html):
        sys.exit("[auto_update] ERROR: missing %s block in index.html" % label)

    def repl(mm):
        return mm.group(1) + inner + mm.group(3)

    return pattern.sub(repl, page_html, count=1)


def apply_seo_blocks(page_html, rows, generated_at):
    page_html = _replace_inner(
        page_html, JSONLD_RE, build_catalog_jsonld(rows, generated_at), "catalog-jsonld"
    )
    page_html = _replace_inner(
        page_html, NOSCRIPT_RE, build_catalog_noscript(rows), "catalog-crawler"
    )
    mld = JSONLD_RE.search(page_html)
    ld = json.loads(mld.group(2))
    if ld.get("mainEntity", {}).get("numberOfItems") != len(rows):
        sys.exit("[auto_update] ERROR: catalog-jsonld numberOfItems does not match plugin count")
    ns = NOSCRIPT_RE.search(page_html)
    if not ns or "<ol" not in ns.group(2) or "</ol>" not in ns.group(2):
        sys.exit("[auto_update] ERROR: catalog-crawler list did not render")
    return page_html


def refresh_seo_from_index():
    with open(INDEX_PATH, encoding="utf-8") as f:
        page = f.read()
    m = CATALOG_DATA_RE.search(page)
    if not m:
        sys.exit("[auto_update] ERROR: catalog-data not found")
    data = json.loads(m.group(2))
    rows = data["plugins"]
    generated_at = data.get("generatedAt") or datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )
    page = apply_seo_blocks(page, rows, generated_at)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(page)
    print("[auto_update] SEO blocks refreshed from catalog-data (%d plugins)" % len(rows))


def main():
    with open(STATIC_PATH, encoding="utf-8") as f:
        static = json.load(f)["plugins"]

    history = load_history()
    today = str(date.today())

    results = {}
    snapshot_for_history = {}
    # 2026-08-28 (fix del hallazgo critico #25/#24 de la auditoria):
    # contador real de exito/fallo de github_stars() -- antes nada
    # trackeaba esto, asi que un GH_TOKEN faltante/invalido/sin permisos
    # (exactamente lo que paso hasta este fix) hacia fallar el 100% de
    # las llamadas en silencio, sin que el workflow lo notara. Ver el
    # chequeo real despues del loop.
    stars_attempted = 0
    stars_succeeded = 0

    print(f"[auto_update] {len(static)} plugins en metadata estatica")
    for repo, meta in sorted(static.items()):
        xml_id = meta["xmlId"]
        name = meta["name"]
        p = resolve_numeric_id(xml_id, name)

        if p is None:
            print(f"  -> {repo:28} sin indexar todavia / no encontrado")
            entry = dict(meta)
            entry.update({
                "repo": repo,
                "marketplaceUrl": None,
                "downloads": None,
                "pricing": None,
                "reviews": 0,
                "rating": None,
                "growth": None,
                "growthSince": None,
                "growthFrom": None,
            })
            results[repo] = entry
            continue

        numeric_id = p.get("id")
        # -1, floored at 0: JetBrains' own review/approval step
        # registers exactly 1 phantom download per plugin (their team
        # installing it once during manual review), counted in the raw
        # API `downloads` figure from day one -- confirmed real by the
        # user 2026-09-03, consistent with many freshly-approved
        # plugins in this catalog sitting at exactly 1 raw download
        # with zero real users yet. Never applied retroactively to
        # already-recorded history snapshots (catalog_daily_history.json)
        # -- only the live figure going forward.
        raw_downloads = p.get("downloads")
        downloads = max(0, raw_downloads - 1) if raw_downloads is not None else None
        pricing = p.get("pricingModel")
        reviews, rating = fetch_reviews(numeric_id)
        stars = github_stars(repo)
        stars_attempted += 1
        if stars is not None:
            stars_succeeded += 1

        base_date, base_downloads = earliest_datapoint(history, xml_id)
        growth = None
        if base_downloads is not None and base_downloads > 0 and downloads is not None:
            growth = round((downloads - base_downloads) / base_downloads * 100, 1)

        entry = dict(meta)
        entry.update({
            "repo": repo,
            "marketplaceUrl": f"https://plugins.jetbrains.com/plugin/{numeric_id}-{repo}",
            "downloads": downloads,
            "pricing": pricing,
            "reviews": reviews,
            "rating": rating,
            "stars": stars,
            "growth": growth,
            "growthSince": base_date,
            "growthFrom": base_downloads,
        })
        results[repo] = entry
        snapshot_for_history[xml_id] = {"downloads": downloads}

        print(f"  -> {repo:28} {downloads if downloads is not None else 'sin indexar'} dl")

    # Guarda el snapshot de HOY en el historico propio de este repo --
    # si ya existe uno de hoy (2 corridas el mismo dia), lo reemplaza en
    # vez de duplicar.
    history["snapshots"] = [s for s in history["snapshots"] if s["date"] != today]
    history["snapshots"].append({"date": today, "plugins": snapshot_for_history})
    save_history(history)

    rows = list(results.values())
    rows.sort(key=lambda r: (r["downloads"] is None, -(r["downloads"] or 0)))

    total_downloads = sum(r["downloads"] or 0 for r in rows)
    pending = sum(1 for r in rows if r["downloads"] is None)
    total_stars = sum(r["stars"] or 0 for r in rows if r.get("stars"))
    total_reviews = sum(r["reviews"] or 0 for r in rows)
    rated = [r["rating"] for r in rows if r.get("rating")]
    avg_rating_all = round(sum(rated) / len(rated), 2) if rated else None

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    data = {
        "generatedAt": generated_at,
        "totalPlugins": len(rows),
        "totalDownloads": total_downloads,
        "pending": pending,
        "totalStars": total_stars,
        "totalReviews": total_reviews,
        "avgRating": avg_rating_all,
        "plugins": rows,
    }

    with open(LATEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"[auto_update] plugins: {len(rows)} | descargas totales: {total_downloads} "
          f"| pendientes: {pending} | stars: {total_stars}")
    print(f"[auto_update] github_stars(): {stars_succeeded}/{stars_attempted} llamadas exitosas")

    # 2026-08-28 (fix del hallazgo critico #25/#24 de la auditoria):
    # abortar con exit code distinto de 0 si el 100% de las llamadas a
    # github_stars() fallaron -- asi el workflow se marca en ROJO en vez
    # de verde-silencioso cuando GH_TOKEN falta/expira/pierde permisos,
    # que es exactamente el bug real que dejo GitHub Stars/Reviews/Rating
    # en cero durante semanas sin que nadie lo notara (documentado en
    # DOCUMENTATION.md). El umbral es "0 exitosas de al menos 10
    # intentos" (no "menos del 100%") -- un puñado de fallos puntuales
    # por rate-limit/timeout de gh en un plugin especifico es normal y
    # no amerita abortar toda la corrida, solo un fallo TOTAL sistemico
    # (token invalido/faltante) lo amerita.
    if stars_attempted >= 10 and stars_succeeded == 0:
        sys.exit(
            "[auto_update] ERROR: 0/%d llamadas a github_stars() tuvieron exito -- "
            "esto casi siempre significa que GH_TOKEN no esta seteado o no tiene "
            "permisos (ver el paso 'Run auto-update' en update-catalog.yml). "
            "Abortando ANTES del swap de index.html para no publicar stars en "
            "cero silenciosamente." % stars_attempted
        )

    # Swap-in-place dentro de index.html -- mismo mecanismo ya usado en
    # cada refresh manual: regex sobre el bloque <script id="catalog-data">,
    # valida como JSON real antes Y despues de escribir.
    with open(INDEX_PATH, encoding="utf-8") as f:
        html = f.read()

    pattern = re.compile(
        r'(<script id="catalog-data" type="application/json">)(.*?)(</script>)', re.S
    )
    m = pattern.search(html)
    if not m:
        sys.exit("[auto_update] ERROR: no se encontro el bloque <script id=\"catalog-data\"> en index.html")

    json.loads(m.group(2))  # valida el bloque VIEJO antes de tocar nada

    new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # json.dumps() nunca escapa "</script>" -- si cualquier campo de texto
    # (pitch/why en catalog_static_metadata.json, en teoria tambien algo
    # devuelto por la API de JetBrains) llegara a contener ese substring
    # literal, cerraria el <script id="catalog-data"> antes de tiempo y el
    # resto del documento se interpretaria fuera de contexto. "\/" es un
    # escape JSON valido (a diferencia de "\!", que NO lo es y rompe
    # json.loads -- confirmado antes de fijar este approach) que JSON.parse
    # revierte a "/" sin cambiar el valor decodificado, asi que este fix es
    # transparente para el JS que lo lee.
    new_json = new_json.replace("</script>", "<\\/script>")
    new_html = pattern.sub(lambda mm: mm.group(1) + new_json + mm.group(3), html, count=1)

    m2 = pattern.search(new_html)
    reparsed = json.loads(m2.group(2))  # valida el bloque NUEVO antes de escribir a disco
    assert reparsed["totalPlugins"] == len(rows)

    # 2026-08-28 (fix del hallazgo alto #32 de la auditoria): 3 literales
    # estaticos del HTML seguian codificados a mano como "43 plugins" --
    # numero real del catalogo cuando se escribieron por primera vez
    # (2026-08-14), nunca actualizado pese a que el catalogo crecio a 101.
    # El JS SI los sobrescribe en runtime con el numero real
    # (updateHeroSubtitle()/initTopbar(), ver index.html), pero:
    # (a) un crawler sin JS (la mayoria, ver hallazgo #31 relacionado) lee
    #     el valor estatico desactualizado como el numero real del sitio,
    # (b) durante la ventana entre first-paint y que el JS termine de
    #     parsear ~380KB de JSON, un usuario real ve "43" tambien.
    # Mismo swap-in-place que el bloque catalog-data de arriba -- 3
    # reemplazos anclados por el ID real del elemento (nunca un regex
    # generico "43 plugins" suelto, que podria matchear texto no
    # relacionado en el futuro si el copy cambia).
    # 2026-09-02: topbarStatusText dropped from this list -- the hero/
    # topbar rework removed that element entirely (no replacement, the
    # topbar no longer carries a live plugin count). Confirmed absent
    # via grep before removing the swap, not assumed.
    #
    # 2026-09-03: footerStatusText's own tag changed from
    # `<span id="footerStatusText">` to `<div class="footer-status"
    # id="footerStatusText">` (footer/contact-page rework) -- the old
    # pattern anchored on the literal `<span id=...` substring, which
    # no longer exists. Anchored on `id="footerStatusText">` alone
    # instead of the surrounding tag, so a future tag-name/attribute-
    # order change doesn't silently break this again the same way.
    total = len(rows)
    swaps = [
        (re.compile(r'(id="heroSubtitle">Real state of the )\d+(-plugin catalog)'),
         r"\g<1>%d\g<2>" % total),
        (re.compile(r'(id="footerStatusText">)\d+( plugins tracked)'),
         r"\g<1>%d\g<2>" % total),
    ]
    swap_count = 0
    for rx, repl in swaps:
        new_html, n = rx.subn(repl, new_html, count=1)
        swap_count += n
    if swap_count != len(swaps):
        sys.exit(
            "[auto_update] ERROR: se esperaban %d swaps de literales estaticos "
            "(heroSubtitle/footerStatusText), se aplicaron %d -- "
            "el markup de index.html probablemente cambio de forma incompatible "
            "con estos regex. Abortando antes de escribir a disco." % (len(swaps), swap_count)
        )

    new_html = apply_seo_blocks(new_html, rows, generated_at)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"[auto_update] index.html actualizado (catalog-data + {swap_count} literales estaticos + SEO), "
          f"JSON re-parseado limpio antes y despues del swap")

    # sitemap.xml <lastmod>, 2026-08-23 (audit finding): the page's real
    # content changes twice a day via this same script, but the sitemap
    # never carried a <lastmod> for crawlers to prioritize re-fetching
    # against. Swap-in-place on the one <url> entry, same discipline as
    # the catalog-data block above -- generatedAt is already a real UTC
    # timestamp from this same run, just reused here as the date portion.
    if os.path.exists(SITEMAP_PATH):
        with open(SITEMAP_PATH, encoding="utf-8") as f:
            sitemap = f.read()
        lastmod_date = generated_at[:10]  # YYYY-MM-DD from the ISO timestamp
        if "<lastmod>" in sitemap:
            sitemap = re.sub(r"<lastmod>.*?</lastmod>", f"<lastmod>{lastmod_date}</lastmod>", sitemap)
        else:
            sitemap = sitemap.replace(
                "<changefreq>daily</changefreq>",
                f"<lastmod>{lastmod_date}</lastmod>\n    <changefreq>daily</changefreq>",
            )
        with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
            f.write(sitemap)
        print(f"[auto_update] sitemap.xml lastmod actualizado a {lastmod_date}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--seo-from-index":
        refresh_seo_from_index()
    else:
        main()
