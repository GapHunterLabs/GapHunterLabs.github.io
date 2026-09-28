#!/usr/bin/env python3
"""refresh_why_from_readmes.py -- completa el campo "why" (la brecha que
resuelve cada plugin) desde la seccion "## Why it exists" del README local
de cada plugin.

Motivo (2026-09-27): el "why" se habia tomado solo del primer parrafo, asi
que en 23 plugins quedaba cortado en un "...complaints:" sin la lista de
citas que sigue. Solo reemplaza los "why" que terminan en ":" (cortados);
los demas no se tocan. Es un script local de mantenimiento: necesita los
repos de los plugins como carpetas hermanas de este repo, que CI no tiene.

Actualiza pipeline/catalog_static_metadata.json (fuente) y
data/catalog-data.json (para no esperar a la proxima corrida del CI).

Uso: python pipeline/refresh_why_from_readmes.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
STATIC = ROOT / "pipeline" / "catalog_static_metadata.json"
DATA = ROOT / "data" / "catalog-data.json"


def why_section(readme: str) -> str | None:
    m = re.search(r"^##\s+Why it exists\s*$(.*?)(?=^##\s|\Z)", readme, re.S | re.M)
    if not m:
        return None
    blocks, cur, kind = [], [], None
    for raw in m.group(1).splitlines():
        line = raw.rstrip()
        if not line.strip():
            if cur:
                blocks.append((kind, " ".join(cur)))
                cur, kind = [], None
            continue
        if re.match(r"^\s*[-*]\s+", line):
            if cur:
                blocks.append((kind, " ".join(cur)))
            cur, kind = [re.sub(r"^\s*[-*]\s+", "", line).strip()], "li"
        else:
            if kind is None:
                kind = "p"
            cur.append(line.strip())
    if cur:
        blocks.append((kind, " ".join(cur)))
    out = []
    for kind, text in blocks:
        out.append(("- " if kind == "li" else "") + text)
    # parrafos separados por linea en blanco; items de lista, por salto simple
    text = ""
    for i, block in enumerate(out):
        if i:
            text += "\n" if (block.startswith("- ") and out[i - 1].startswith("- ")) else "\n\n"
        text += block
    return text.strip() or None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    static = json.loads(STATIC.read_text(encoding="utf-8"))
    fixed = {}
    for repo, meta in static["plugins"].items():
        why = (meta.get("why") or "").rstrip()
        if not why.endswith(":"):
            continue
        readme = WORKSPACE / repo / "README.md"
        if not readme.exists():
            print("  sin README local:", repo)
            continue
        full = why_section(readme.read_text(encoding="utf-8"))
        if not full or len(full) <= len(why):
            print("  seccion no encontrada o no mas larga:", repo)
            continue
        fixed[repo] = full
    print("[refresh_why] %d 'why' cortados completados" % len(fixed))
    if args.dry_run or not fixed:
        return 0
    for repo, full in fixed.items():
        static["plugins"][repo]["why"] = full
    STATIC.write_text(json.dumps(static, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    items = data["plugins"]
    n = 0
    for item in items:
        repo = (item.get("githubUrl") or "").rstrip("/").rsplit("/", 1)[-1]
        if repo in fixed:
            item["why"] = fixed[repo]
            n += 1
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("[refresh_why] catalog-data.json: %d actualizados" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
