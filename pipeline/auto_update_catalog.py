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
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINE_DIR = os.path.join(ROOT, "pipeline")
STATIC_PATH = os.path.join(PIPELINE_DIR, "catalog_static_metadata.json")
HISTORY_PATH = os.path.join(PIPELINE_DIR, "catalog_daily_history.json")
LATEST_PATH = os.path.join(PIPELINE_DIR, "catalog_latest_data.json")
INDEX_PATH = os.path.join(ROOT, "index.html")

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


def main():
    with open(STATIC_PATH, encoding="utf-8") as f:
        static = json.load(f)["plugins"]

    history = load_history()
    today = str(date.today())

    results = {}
    snapshot_for_history = {}

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
        downloads = p.get("downloads")
        pricing = p.get("pricingModel")
        reviews, rating = fetch_reviews(numeric_id)
        stars = github_stars(repo)

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
    new_html = pattern.sub(lambda mm: mm.group(1) + new_json + mm.group(3), html, count=1)

    m2 = pattern.search(new_html)
    reparsed = json.loads(m2.group(2))  # valida el bloque NUEVO antes de escribir a disco
    assert reparsed["totalPlugins"] == len(rows)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("[auto_update] index.html actualizado, JSON re-parseado limpio antes y despues del swap")


if __name__ == "__main__":
    main()
