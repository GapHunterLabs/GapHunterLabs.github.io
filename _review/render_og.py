"""Render the social share images (1200x630): home, services and the audit page.

Each *-source.html is a standalone, noindex HTML page that loads the same
fonts/ and brand mark as the live site; Chromium (via Playwright) screenshots
it at exactly 1200x630. Deliberately timeless: no live catalog numbers baked
in, so the twice-daily refresh workflow never has to regenerate these.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "og-image-source.html", ROOT / "og-image.png"),          # home
    (ROOT / "og-services-source.html", ROOT / "og-services.png"),    # /services/
    (ROOT / "og-audit-source.html", ROOT / "og-audit.png"),          # /plugin-performance-audit/
]


def render_playwright() -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for src, out in PAIRS:
                page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
                page.goto(src.resolve().as_uri(), wait_until="networkidle")
                page.evaluate("() => document.fonts.ready")
                page.wait_for_timeout(400)
                page.screenshot(path=str(out), type="png", omit_background=False)
                page.close()
        finally:
            browser.close()


if __name__ == "__main__":
    try:
        render_playwright()
    except Exception as exc:
        print(f"playwright failed: {exc}", file=sys.stderr)
        sys.exit(1)
    for _, out in PAIRS:
        print(f"wrote {out} ({out.stat().st_size} bytes)")
