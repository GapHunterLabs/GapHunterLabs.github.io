#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh the public plugin catalog from Marketplace and GitHub data.

The generated browser data is written to ``data/catalog-data.json``.
The catalog page's JSON-LD and no-script listing are then regenerated
from that same file, while static counts on the home and catalog pages
are kept in sync for first paint and non-JavaScript visitors.

Usage:
    python pipeline/auto_update_catalog.py
    python pipeline/auto_update_catalog.py --seo-from-data
"""
import json
import os
import re
import sys
import subprocess
import urllib.request
import urllib.parse
import html
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINE_DIR = os.path.join(ROOT, "pipeline")
STATIC_PATH = os.path.join(PIPELINE_DIR, "catalog_static_metadata.json")
HISTORY_PATH = os.path.join(PIPELINE_DIR, "catalog_daily_history.json")
LATEST_PATH = os.path.join(PIPELINE_DIR, "catalog_latest_data.json")
DATA_PATH = os.path.join(ROOT, "data", "catalog-data.json")
INDEX_PATH = os.path.join(ROOT, "index.html")
# 2026-09-10 (clean-URL migration): the catalog page now lives at
# catalog/index.html so GitHub Pages serves it at /catalog/ with no
# ".html" in the address bar. catalog.html itself became a tiny
# client-side redirect stub and is no longer touched by this script.
CATALOG_PATH = os.path.join(ROOT, "catalog", "index.html")
SITEMAP_PATH = os.path.join(ROOT, "sitemap.xml")

API = "https://plugins.jetbrains.com/api"
UA = {"User-Agent": "gap-hunter-auto-update/1.0", "Accept": "application/json"}


def get(url):
    return json.load(urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=30))


def resolve_numeric_id(xml_id, name):
    url = "%s/searchPlugins?search=%s" % (API, urllib.parse.quote(name))
    try:
        data = get(url)
    except Exception as e:
        print(f"  [warn] searchPlugins fallo para '{name}': {e}", file=sys.stderr)
        return None
    for p in data.get("plugins", []):
        if p.get("xmlId") == xml_id:
            # Defense in depth: `id` becomes the numeric segment of
            # marketplaceUrl below, which the catalog's safeUrl() already
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


# Fase 3 del plan de rediseño (Intelligence layer) -- el sparkline de la
# home necesita una serie corta de {date, totalDownloads} en vez de
# mandar el historico completo (pipeline/catalog_daily_history.json,
# que crece sin poda) al navegador. Se computa aca, sobre el `history`
# que YA incluye el snapshot de hoy (agregado mas arriba en main()
# antes de este punto), sin ninguna llamada de red adicional.
def compute_trend7d(history):
    snaps = sorted(history.get("snapshots", []), key=lambda s: s["date"])[-7:]
    return [
        {
            "date": s["date"],
            "totalDownloads": sum(
                (v.get("downloads") or 0) for v in s.get("plugins", {}).values()
            ),
        }
        for s in snaps
    ]


# "Intelligence changes" -- dos señales reales, ambas con granularidad
# de dia (nunca de hora: el cron corre 2x/dia, cualquier timestamp mas
# fino seria fabricado). 1) plugins nuevos via firstPublished (campo
# curado real); 2) mayores subas de descargas entre los ultimos dos
# snapshots disponibles. Sin umbral "magico" de importancia -- se
# ordena por fecha real y se recorta a un maximo razonable.
def compute_recent_changes(history, rows, days=14, max_events=8):
    events = []
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    for r in rows:
        fp = r.get("firstPublished")
        if fp and fp >= cutoff:
            events.append({"date": fp, "type": "new", "name": r["name"], "niche": r.get("niche")})

    snaps = sorted(history.get("snapshots", []), key=lambda s: s["date"])
    if len(snaps) >= 2:
        prev_snap, cur_snap = snaps[-2], snaps[-1]
        name_by_id = {r["xmlId"]: r["name"] for r in rows}
        niche_by_id = {r["xmlId"]: r.get("niche") for r in rows}
        deltas = []
        for xml_id, cur_v in cur_snap.get("plugins", {}).items():
            prev_v = prev_snap.get("plugins", {}).get(xml_id)
            if not prev_v:
                continue
            prev_dl, cur_dl = prev_v.get("downloads"), cur_v.get("downloads")
            if prev_dl is None or cur_dl is None:
                continue
            delta = cur_dl - prev_dl
            if delta > 0:
                deltas.append((delta, xml_id))
        deltas.sort(reverse=True)
        for delta, xml_id in deltas[:5]:
            events.append({
                "date": cur_snap["date"], "type": "growth",
                "name": name_by_id.get(xml_id, xml_id), "niche": niche_by_id.get(xml_id),
                "delta": delta,
            })

    events.sort(key=lambda e: e["date"], reverse=True)
    return events[:max_events]


SITE = "https://gaphunterlabs.github.io/"
CATALOG_URL = SITE + "catalog/"

JSONLD_RE = re.compile(
    r'(<script type="application/ld\+json" id="catalog-jsonld">)(.*?)(</script>)',
    re.S,
)
NOSCRIPT_RE = re.compile(
    r'(<noscript id="catalog-crawler">)(.*?)(</noscript>)',
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
        url = p.get("marketplaceUrl") or p.get("githubUrl") or CATALOG_URL
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
        "url": CATALOG_URL,
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
        sys.exit("[auto_update] ERROR: missing %s block in catalog/index.html" % label)

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


def refresh_seo_from_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    rows = data["plugins"]
    generated_at = data.get("generatedAt") or datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )
    with open(CATALOG_PATH, encoding="utf-8") as f:
        page = f.read()
    page = apply_seo_blocks(page, rows, generated_at)
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        f.write(page)
    print("[auto_update] catalog SEO refreshed from external data (%d plugins)" % len(rows))


def update_static_counts(path, rows):
    with open(path, encoding="utf-8") as f:
        page = f.read()
    total = len(rows)
    swaps = [
        (re.compile(r'(id="footerStatusText">)\d+( plugins tracked)'), r"\g<1>%d\g<2>" % total),
    ]
    # 2026-09-11 (cron incident): a hero-subtitle marker used to live
    # here too ("Real state of the N-plugin catalog"), but commit
    # bcd7753 (2026-09-10, "Rewrite hero subtitle to lead with the
    # mission") replaced that copy with a generic no-JS mission
    # statement that embeds no count at all -- the live count now only
    # ever reaches #heroSubtitle via the JS hydration in index.html
    # (which sets its own textContent from data.totalPlugins at
    # runtime, independent of this script). That silently broke every
    # scheduled run since (regex stopped matching -> sys.exit here) --
    # the marker is intentionally gone from the static HTML now, not a
    # bug to restore; removing the dead swap instead of re-adding a
    # count to copy that was deliberately rewritten to not have one.
    for rx, repl in swaps:
        page, count = rx.subn(repl, page, count=1)
        if count != 1:
            # os.path.basename alone would print "index.html" for both
            # index.html and catalog/index.html -- use the path relative
            # to ROOT so a failure here says which file actually broke.
            sys.exit("[auto_update] ERROR: expected static count marker in %s" % os.path.relpath(path, ROOT))
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)


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
        "trend7d": compute_trend7d(history),
        "recentChanges": compute_recent_changes(history, rows),
        "plugins": rows,
    }

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
            "Abortando antes de publicar datos con stars en "
            "cero silenciosamente." % stars_attempted
        )

    save_history(history)
    with open(LATEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    update_static_counts(INDEX_PATH, rows)
    update_static_counts(CATALOG_PATH, rows)
    refresh_seo_from_data()
    print("[auto_update] external catalog JSON and static page counts updated")

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
        catalog_entry = re.compile(
            r"(<loc>%scatalog/</loc>\s*<lastmod>).*?(</lastmod>)" % re.escape(SITE),
            re.S,
        )
        sitemap, count = catalog_entry.subn(r"\g<1>%s\g<2>" % lastmod_date, sitemap, count=1)
        if count != 1:
            sys.exit("[auto_update] ERROR: catalog/ sitemap entry missing")
        with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
            f.write(sitemap)
        print(f"[auto_update] sitemap.xml lastmod actualizado a {lastmod_date}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args in (["--seo-from-data"], ["--seo-from-index"]):
        refresh_seo_from_data()
    elif not args:
        main()
    else:
        sys.exit(
            "Usage: python pipeline/auto_update_catalog.py [--seo-from-data]"
        )
