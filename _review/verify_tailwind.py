"""Comprueba que css/tw.css es exactamente lo que genera el Tailwind CLI hoy.

Reconstruye en un archivo temporal (no toca css/tw.css) y compara. Sale con 1 si difieren:
cambiaste una clase tw-* o css-src/tailwind.css y falta `cd pipeline && npm run build:css`.
Tambien avisa de utilidades tw-* usadas en el HTML que no existen en tw.css.

    python _review/verify_tailwind.py
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "pipeline"
BIN = PIPE / "node_modules" / ".bin" / ("tailwindcss.cmd" if sys.platform == "win32" else "tailwindcss")


def main() -> int:
    if not BIN.exists():
        print("falta tailwindcss: ejecuta `npm install` en pipeline/")
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "tw.css"
        r = subprocess.run([str(BIN), "-c", "tailwind.config.js", "-i", "css-src/tailwind.css", "-o", str(out), "--minify"],
                           cwd=PIPE, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            print(r.stderr[-800:])
            return 2
        fresh = out.read_bytes().replace(b"\r\n", b"\n")
    current = (ROOT / "css" / "tw.css").read_bytes().replace(b"\r\n", b"\n")
    if fresh != current:
        print("css/tw.css esta desactualizado: ejecuta `cd pipeline && npm run build:css`")
        return 1
    # Utilidades tw-* presentes en el HTML de las paginas manuales/home pero ausentes del CSS.
    css = current.decode("utf-8")
    missing = set()
    for page in [ROOT / "index.html", ROOT / "es" / "index.html"]:
        for cls in re.findall(r'class="([^"]*)"', page.read_text(encoding="utf-8")):
            for c in cls.split():
                if c.startswith("tw-") and c.replace(":", "\\:") not in css and ("." + c) not in css:
                    missing.add(c)
    if missing:
        print("clases tw-* sin regla en tw.css:", sorted(missing)[:10])
        return 1
    print("tw.css al dia (%d bytes)" % len(current))
    return 0


if __name__ == "__main__":
    sys.exit(main())
