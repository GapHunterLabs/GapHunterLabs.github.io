from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BROKEN = "--ease-standard: var(--ease-standard);\n    --ease-emphasized: var(--ease-emphasized);"
FIXED = "--ease-standard: cubic-bezier(.65,0,.35,1);\n    --ease-emphasized: cubic-bezier(.2,.7,.3,1);"

for name in ("index.html", "catalog.html", "methodology.html", "contact.html"):
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    if BROKEN not in text:
        raise SystemExit(f"broken ease tokens missing in {name}")
    text = text.replace(BROKEN, FIXED, 1)
    text = text.replace("opacity 0.4s ease, transform 0.4s ease", "opacity var(--duration-slow) ease, transform var(--duration-slow) ease")
    path.write_text(text, encoding="utf-8")
    print(f"fixed {name}")
