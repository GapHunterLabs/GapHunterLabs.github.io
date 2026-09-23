"""Render og-image-source.html to og-image.png at 1200x630."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "og-image-source.html"
OUT = ROOT / "og-image.png"
URL = SRC.resolve().as_uri()


def render_playwright() -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        page.goto(URL, wait_until="networkidle")
        page.evaluate("() => document.fonts.ready")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT), type="png", omit_background=False)
        browser.close()


if __name__ == "__main__":
    try:
        render_playwright()
    except Exception as exc:
        print(f"playwright failed: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
