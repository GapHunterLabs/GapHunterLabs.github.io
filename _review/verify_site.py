from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8973"
OUT = Path(__file__).parent / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
CATEGORIES = ("api", "devops", "security", "data", "quality", "codegen", "testing", "editor")


def ready(page, url):
    page.goto(BASE + url, wait_until="networkidle")
    page.locator("#siteLoader").wait_for(state="detached")


def row_spreads(page, selector):
    return page.eval_on_selector_all(
        selector,
        """els => {
          const rows = {};
          els.forEach(el => {
            const r = el.getBoundingClientRect();
            const key = Math.round(r.top);
            (rows[key] ||= []).push(r);
          });
          return Object.values(rows).map(rs => ({
            count: rs.length,
            top: Math.max(...rs.map(r => r.top)) - Math.min(...rs.map(r => r.top)),
            bottom: Math.max(...rs.map(r => r.bottom)) - Math.min(...rs.map(r => r.bottom))
          }));
        }""",
    )


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    )

    for label, viewport in (
        ("desktop", {"width": 1440, "height": 1000}),
        ("mobile", {"width": 390, "height": 844}),
    ):
        context = browser.new_context(viewport=viewport, device_scale_factor=1)
        page = context.new_page()
        for name, url in (
            ("home", "/index.html"),
            ("catalog", "/catalog.html"),
            ("methodology", "/methodology.html"),
        ):
            ready(page, url)
            page.screenshot(path=str(OUT / f"{name}-{label}.png"), full_page=True)

        page.add_init_script(
            """{
              const nativeFetch = window.fetch;
              window.fetch = function(resource, init) {
                if (String(resource).includes('data/catalog-data.json')) {
                  return new Promise(function() {});
                }
                return nativeFetch.call(this, resource, init);
              };
            }"""
        )
        page.goto(BASE + "/index.html", wait_until="domcontentloaded")
        page.locator("#siteLoader").wait_for(state="visible")
        page.screenshot(path=str(OUT / f"loader-{label}.png"))
        context.close()

    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    page = context.new_page()
    ready(page, "/index.html")
    alignment = {
        "hero_stats": row_spreads(page, "#stats .tele-row"),
        "category_tiles": row_spreads(page, ".category-links .cat-cell"),
        "identity_steps": row_spreads(page, ".identity-process .identity-step"),
        "method_facts": row_spreads(page, "#methodFacts .method-fact"),
    }

    for category in CATEGORIES:
        ready(page, f"/catalog.html?category={category}")
        assert page.locator("#categoryFilter").input_value() == category
        assert page.locator(".plugin-card").count() > 0

    ready(page, "/catalog.html")
    alignment["plugin_cards"] = row_spreads(page, ".plugin-card")
    page.locator("#searchInput").fill("Mermaid")
    page.wait_for_timeout(250)
    assert page.locator(".plugin-card").count() == 1
    page.locator("#searchInput").fill("")
    page.locator("#pricingFilter").select_option("FREE")
    assert page.locator(".plugin-card").count() > 0
    page.locator("#pricingFilter").select_option("")
    page.locator("[data-page-dir='1']").first.click()
    assert "Page 2 of" in page.locator(".catalog-pager-status").first.inner_text()
    page.locator(".plugin-card").first.click()
    assert page.locator(".dossier-sheet").count() == 1
    page.locator("#dossierBack").click()
    page.locator("#modeToggle [data-mode='table']").click()
    page.locator("thead th[data-key='name']").click()
    row = page.locator("tr.row").first
    repo = row.get_attribute("data-repo")
    plugin_name = row.locator(".plugin-name").inner_text().strip()
    row.click()
    assert page.locator(".tbl-dossier").count() == 1
    assert page.evaluate("location.hash") == "#" + repo
    assert page.title() == plugin_name + " — Gap Hunter Labs"
    page.locator(".dossier-close").click()
    assert page.evaluate("location.hash") == ""
    assert page.title() == "Plugin Catalog for IntelliJ & JetBrains IDEs | Gap Hunter Labs"

    for group, rows in alignment.items():
        for row in rows:
            assert row["top"] <= 2 and row["bottom"] <= 2, (group, row)
    context.close()

    failure_context = browser.new_context(viewport={"width": 1440, "height": 1000})
    failure_page = failure_context.new_page()
    failure_page.route("**/data/catalog-data.json", lambda route: route.abort())
    failure_page.goto(BASE + "/catalog.html", wait_until="domcontentloaded")
    failure_page.locator("#catalogRetry").wait_for(state="visible")
    assert "Catalog data could not be loaded" in failure_page.locator("#fieldMain").inner_text()
    failure_page.goto(BASE + "/index.html", wait_until="domcontentloaded")
    failure_page.locator("#homeCatalogRetry").wait_for(state="visible")
    assert "Catalog data could not be loaded" in failure_page.locator("main").inner_text()
    failure_context.close()

    print({
        "alignment": alignment,
        "categories": list(CATEGORIES),
        "functional": "passed",
        "table_url_state": "passed",
        "failure_states": "passed",
    })
    browser.close()
