"""Capture desktop + mobile screenshots of the four pages."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_review" / "screenshots"
PAGES = ("index.html", "catalog.html", "methodology.html", "contact.html")
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}


def capture(label: str, base: str) -> None:
    from playwright.sync_api import sync_playwright

    dest = OUT / label
    dest.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for page_name in PAGES:
            for vp_name, vp in VIEWPORTS.items():
                page = browser.new_page(viewport=vp, device_scale_factor=1)
                page.goto(f"{base.rstrip('/')}/{page_name}", wait_until="networkidle", timeout=60000)
                page.evaluate("() => document.fonts.ready")
                loader = page.locator("#siteLoader")
                if loader.count():
                    page.wait_for_function(
                        "() => { const el = document.getElementById('siteLoader'); return !el || el.getAttribute('aria-busy') === 'false' || getComputedStyle(el).opacity === '0' || el.hidden; }",
                        timeout=15000,
                    )
                    page.wait_for_timeout(400)
                stem = page_name.replace(".html", "")
                path = dest / f"{stem}-{vp_name}.png"
                page.screenshot(path=str(path), full_page=True, type="png")
                print(f"wrote {path.relative_to(ROOT)}")
                page.close()
        browser.close()


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "before"
    base = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8973"
    try:
        capture(label, base)
    except Exception as exc:
        print(f"capture failed: {exc}", file=sys.stderr)
        sys.exit(1)
