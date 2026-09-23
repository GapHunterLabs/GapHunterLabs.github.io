#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_demo_media.py -- convierte un GIF/PNG de demo a media/<slug>/ y
imprime la entrada DEMO_MEDIA lista para pegar en js/catalog-shared.js.

Formaliza el pipeline ad hoc de la migracion de Fase 3 (2026-09-23, ver
DOCUMENTATION.md "Demo media") para que agregar/actualizar la demo de un
plugin sea un comando, no una receta a mano.

Requiere ffmpeg en PATH. Para un GIF: genera demo.mp4 (H.264) +
demo.webm (VP9) + poster.webp (primer frame). Para un PNG/JPG: genera
solo poster.webp (screenshot estatico, sin video -- mismo caso que
react-native-companion).

fps=12 en el filtro de ffmpeg no es cosmetico: varias demos reales solo
tienen 2-4 frames de verdad con delays largos (una diapositiva "escena A
-> escena B -> escena C", no animacion fluida) -- sin ese resample
explicito, ffmpeg colapsa esos delays largos y el video dura una
fraccion de lo que dura el GIF real. Verificar SIEMPRE que la duracion
de salida calce con la de entrada (este script lo hace solo y avisa si
no calzan).

Uso:
    python pipeline/convert_demo_media.py mermaid-companion path/to/demo.gif
    python pipeline/convert_demo_media.py react-native-companion path/to/screenshot.png
    python pipeline/convert_demo_media.py mermaid-companion https://raw.githubusercontent.com/.../demo.gif
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA_DIR = ROOT / "media"
WIDTH = 960
FPS = 12
UA = {"User-Agent": "gap-hunter-media-fetch/1.0"}


def die(msg: str) -> "NoReturn":  # noqa: F821
    sys.exit("[convert_demo_media] ERROR: " + msg)


def fetch_if_url(source: str, tmp_dir: Path) -> Path:
    if not source.startswith(("http://", "https://")):
        path = Path(source)
        if not path.exists():
            die("no existe: %s" % source)
        return path
    ext = source.rsplit(".", 1)[-1].lower()
    dest = tmp_dir / ("source.%s" % ext)
    req = urllib.request.Request(source, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        dest.write_bytes(resp.read())
    return dest


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        die("comando fallo: %s\n%s" % (" ".join(cmd), result.stderr[-2000:]))


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def convert_gif(slug: str, src: Path, out_dir: Path) -> dict:
    scale = "scale=%d:-2:flags=lanczos" % WIDTH
    out_dir.mkdir(parents=True, exist_ok=True)

    run(["ffmpeg", "-y", "-i", str(src),
         "-vf", "%s,fps=%d" % (scale, FPS),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "28", "-preset", "slow",
         "-movflags", "+faststart", "-an", str(out_dir / "demo.mp4")])
    run(["ffmpeg", "-y", "-i", str(src),
         "-vf", "%s,fps=%d" % (scale, FPS),
         "-c:v", "libvpx-vp9", "-pix_fmt", "yuv420p", "-crf", "34", "-b:v", "0", "-an",
         str(out_dir / "demo.webm")])
    run(["ffmpeg", "-y", "-i", str(src), "-vf", scale, "-frames:v", "1", "-update", "1",
         str(out_dir / "poster.webp")])

    src_dur = probe_duration(src)
    out_dur = probe_duration(out_dir / "demo.mp4")
    if abs(src_dur - out_dur) > 1.0:
        die("duracion no calza: fuente %.1fs vs salida %.1fs -- revisar antes de usar esto "
            "(el resample fps=%d deberia preservar la duracion real)" % (src_dur, out_dur, FPS))
    print("  duracion OK: %.1fs (fuente) -> %.1fs (salida)" % (src_dur, out_dur))

    return {
        "poster": "/media/%s/poster.webp" % slug,
        "mp4": "/media/%s/demo.mp4" % slug,
        "webm": "/media/%s/demo.webm" % slug,
    }


def convert_static(slug: str, src: Path, out_dir: Path) -> dict:
    from PIL import Image
    out_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(src).convert("RGB")
    if img.width > WIDTH:
        ratio = WIDTH / img.width
        img = img.resize((WIDTH, int(img.height * ratio)), Image.LANCZOS)
    img.save(out_dir / "poster.webp", "WEBP", quality=82, method=6)
    return {"poster": "/media/%s/poster.webp" % slug}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", help="mismo slug que catalog/<slug>/ (el campo repo)")
    ap.add_argument("source", help="ruta local o URL a un .gif/.png/.jpg")
    args = ap.parse_args()

    out_dir = MEDIA_DIR / args.slug
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        src = fetch_if_url(args.source, Path(tmp))
        ext = src.suffix.lower()
        if ext == ".gif":
            entry = convert_gif(args.slug, src, out_dir)
        elif ext in (".png", ".jpg", ".jpeg"):
            entry = convert_static(args.slug, src, out_dir)
        else:
            die("extension no soportada: %s (esperaba .gif/.png/.jpg)" % ext)

    print("\nOK -- pegar esta linea en DEMO_MEDIA (js/catalog-shared.js), orden alfabetico:")
    js_entry = "{ " + ", ".join("%s: %s" % (k, json.dumps(v)) for k, v in entry.items()) + " }"
    print("    '%s': %s," % (args.slug, js_entry))
    print("\nDespues: pipeline/build_catalog_grid.py, build_home.py y "
          "build_plugin_pages.py --sitemap --inject para que se refleje en el sitio.")


if __name__ == "__main__":
    main()
