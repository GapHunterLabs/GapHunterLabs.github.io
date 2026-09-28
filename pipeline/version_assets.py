#!/usr/bin/env python3
"""version_assets.py -- agrega ?v=<hash> a cada referencia /css/*.css,
/js/*.js y /media/* de todas las paginas HTML del sitio.

GitHub Pages sirve todo con Cache-Control: max-age=600, asi que durante
~10 minutos tras un despliegue un navegador puede mezclar HTML nuevo con
CSS/JS viejo. Con el hash del CONTENIDO (primeros 8 hex del sha256) la
URL cambia solo cuando el archivo cambia. Correr al final, despues de
todos los generadores (build_catalog_grid, build_home, build_plugin_pages).

Uso: python pipeline/version_assets.py [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "_review", "pipeline", "media", "fonts", "data", ".github"}
# 2026-09-27: tambien /media/ (poster, videos, imagenes) -- al reemplazar el
# demo de Mermaid con el mismo nombre de archivo, el navegador seguia
# mostrando la copia vieja en cache; con el hash la URL cambia sola.
ASSET_RE = re.compile(
    r'((?:href|src|poster)="/((?:css|js)/[\w.-]+\.(?:css|js)|media/[\w./-]+\.(?:webp|png|jpe?g|gif|mp4|webm|svg)))'
    r'(?:\?v=[0-9a-f]+)?"')


def html_files():
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in SKIP_DIRS:
            continue
        if rel.name == "og-image-source.html":
            continue
        yield path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="solo reporta, no escribe; sale con 1 si hay desfasados")
    args = ap.parse_args()
    cache: dict[str, str] = {}

    def digest(rel: str) -> str | None:
        if rel not in cache:
            f = ROOT / rel
            cache[rel] = hashlib.sha256(f.read_bytes()).hexdigest()[:8] if f.is_file() else None
        return cache[rel]

    changed, missing = 0, set()
    for page in html_files():
        text = page.read_text(encoding="utf-8")

        def repl(m):
            h = digest(m.group(2))
            if h is None:
                missing.add(m.group(2))
                return m.group(0)
            return '%s?v=%s"' % (m.group(1), h)

        new = ASSET_RE.sub(repl, text)
        if new != text:
            changed += 1
            if not args.check:
                page.write_text(new, encoding="utf-8")
    if missing:
        print("[version_assets] ERROR: referencias a archivos inexistentes: %s" % ", ".join(sorted(missing)))
        return 1
    print("[version_assets] %d paginas %s" % (changed, "desfasadas" if args.check else "actualizadas"))
    return 1 if (args.check and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
