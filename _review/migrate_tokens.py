"""Migrate radius, duration, easing, and card-pad tokens in the four pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / name for name in ("index.html", "catalog.html", "methodology.html", "contact.html")]

RADIUS_SCALE = """    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
"""
MOTION_SCALE = """    --duration-fast: 120ms;
    --duration-base: 150ms;
    --duration-slow: 300ms;
    --ease-standard: cubic-bezier(.65,0,.35,1);
    --ease-emphasized: cubic-bezier(.2,.7,.3,1);
"""
CARD_PAD = """    --card-pad: 16px;
    --card-pad-sm: 10px;
"""

# Closest scale value. 1px ticks, 0, 50%, and 100px pills stay literal.
RADIUS_MAP = {
    "4px": "var(--radius-sm)",
    "5px": "var(--radius-sm)",
    "6px": "var(--radius-md)",
    "7px": "var(--radius-md)",
    "8px": "var(--radius-md)",
    "9px": "var(--radius)",
    "10px": "var(--radius)",
}


def split_styles(html: str) -> list[tuple[str, bool]]:
    parts: list[tuple[str, bool]] = []
    last = 0
    for match in re.finditer(r"<style\b[^>]*>.*?</style>", html, flags=re.I | re.S):
        if match.start() > last:
            parts.append((html[last:match.start()], False))
        parts.append((match.group(0), True))
        last = match.end()
    if last < len(html):
        parts.append((html[last:], False))
    return parts


def inject_tokens(css: str, name: str) -> str:
    if "--radius-sm:" not in css:
        if "--radius: 10px;" in css:
            css = css.replace("--radius: 10px;\n", "--radius: 10px;\n" + RADIUS_SCALE, 1)
        elif "--section-gap: 20px;" in css:
            css = css.replace(
                "--section-gap: 20px;\n",
                "--section-gap: 20px;\n    --radius: 10px;\n" + RADIUS_SCALE,
                1,
            )
    if "--duration-base:" not in css:
        if "--section-gap: 20px;" in css:
            css = css.replace("--section-gap: 20px;\n", "--section-gap: 20px;\n" + MOTION_SCALE, 1)
        elif "--page-pad-sm: 16px;" in css:
            css = css.replace("--page-pad-sm: 16px;\n", "--page-pad-sm: 16px;\n" + MOTION_SCALE, 1)
    if name in {"methodology.html", "contact.html"} and "--card-pad:" not in css:
        css = css.replace("--section-gap: 20px;\n", "--section-gap: 20px;\n" + CARD_PAD, 1)
    return css


def migrate_radius(css: str) -> str:
    def repl(match: re.Match[str]) -> str:
        value = match.group(1)
        return f"border-radius: {RADIUS_MAP.get(value, value)}"

    return re.sub(r"border-radius:\s*([0-9.]+px)", repl, css)


def migrate_motion(css: str) -> str:
    css = css.replace("cubic-bezier(.65, 0, .35, 1)", "var(--ease-standard)")
    css = css.replace("cubic-bezier(.65,0,.35,1)", "var(--ease-standard)")
    css = css.replace("cubic-bezier(.2,.7,.3,1)", "var(--ease-emphasized)")

    # Longest / most specific durations first so 0.15s is not eaten as 0.1s.
    duration_subs = (
        (r"(?<![\d.])0\.35s", "var(--duration-slow)"),
        (r"(?<![\d.])0\.25s", "var(--duration-slow)"),
        (r"(?<![\d.])0\.18s", "var(--duration-base)"),
        (r"(?<![\d.])0\.15s", "var(--duration-base)"),
        (r"(?<![\d.])0\.12s", "var(--duration-fast)"),
        (r"(?<![\d.])0\.3s", "var(--duration-slow)"),
        (r"(?<![\d.])0\.2s", "var(--duration-base)"),
        (r"(?<![\d.])0\.1s", "var(--duration-fast)"),
        (r"(?<![\d.])\.4s", "var(--duration-slow)"),
        (r"(?<![\d.])\.12s", "var(--duration-fast)"),
        (r"(?<![\d.])\.24s", "0.24s"),
        (r"(?<![\d.])\.9s", "0.9s"),
    )
    for pattern, repl in duration_subs:
        css = re.sub(pattern, repl, css)
    return css


def migrate_card_pad(css: str, name: str) -> str:
    if name not in {"methodology.html", "contact.html"}:
        return css
    css = css.replace(
        ".channel-list li {\n    margin: 0;\n    padding: 14px 16px;",
        ".channel-list li {\n    margin: 0;\n    padding: var(--card-pad);",
    )
    css = css.replace("padding: 16px;\n    min-width: 0;", "padding: var(--card-pad);\n    min-width: 0;")
    css = css.replace(".disclosure {\n    padding: 16px;", ".disclosure {\n    padding: var(--card-pad);")
    css = css.replace(".decision-figure { padding: 16px; }", ".decision-figure { padding: var(--card-pad); }")
    return css


def process(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    rebuilt: list[str] = []
    for chunk, is_style in split_styles(html):
        if is_style:
            chunk = inject_tokens(chunk, path.name)
            chunk = migrate_radius(chunk)
            chunk = migrate_motion(chunk)
            chunk = migrate_card_pad(chunk, path.name)
        rebuilt.append(chunk)
    path.write_text("".join(rebuilt), encoding="utf-8")
    print(f"updated {path.name}")


if __name__ == "__main__":
    for page in PAGES:
        process(page)
