# Next tasks — home page reorganization + catalog split + methodology page

Continuing on `site-improvements`. Recap of what's already live on `main`:
self-hosted fonts, the Hunting Field radial diagram replaced by a category
grid (`.cat-board`), full-catalog JSON-LD + `<noscript>` crawler fallback
(145 plugins), `contact.html` (real channels only, no fake form), the
binary-lock loading overlay removed, hero reworked (single-line title,
zero-value stats moved out of the hero).

This is the biggest round yet — it touches most of `index.html`. Work in
small increments, checkpoint with a screenshot before piling on more, push
to `site-improvements` (never `main` directly). You own the actual visual
execution here — composition, exact spacing choices within the token
system, animation timing, final wording — as long as facts stay accurate
and the hard constraints below are respected. This isn't a pixel-spec to
transcribe literally.

## Hard constraints — read before writing any copy

- **Never** name any internal process, pipeline stage, or document by name
  anywhere in code comments or visible copy — no "Workstream 1/2/3/4", no
  internal script names, no internal doc names (`CONSTITUTION.md`,
  `ARCHITECTURE.md`, etc.).
- **Never** publish a case study, finding, or story about a third party's
  repo, org, or exposed secret — anonymized or not. The only real-world
  "finding" content allowed on this site is the Background ReadAction
  Freeze Companion plugin and its own real pitch/why text already in the
  catalog data. Nothing else in that category, ever, without being told
  explicitly.
- **Before linking to any external article/post about that plugin**,
  verify it's actually live (check the real URL responds, isn't a draft)
  — don't assume something is published just because it's referenced
  somewhere. If you can't verify it's live, link only to the plugin's own
  GitHub repo (`https://github.com/GapHunterLabs/background-readaction-freeze-companion`),
  nothing else.
- **Never** invent technology that doesn't exist — no AI/ML/"neural
  model"/fake server names in any copy, especially the loading screen.
  This is a static site with plain JS; describe only what's real.
- **Never** publish any personal identifying detail beyond what's already
  on the live site today (the LinkedIn URL and `gaphunterlabs@gmail.com`,
  already in the footer/contact page). No legal name, no location, no
  phone number, no employment history — if a bio section is built, it
  stays at the level of "built and maintained by one person, self-taught,
  no formal software background" — nothing more specific than that.
- English-only code comments and copy.

## Phase A — Identity section (replaces the `id="methodology"` block)

The current section right before the footer (4 "log entries": Methodology
/ The Gap-Fix / Reviews-Rating-Stars / What's Never Stored) does double
duty as both a strong closing statement and a trust disclosure. Split it:
the trust content moves to its own page (Phase B), and this spot becomes a
real identity section. Everything below reuses text and data that's
already real on this site — nothing invented.

1. **Headline** — reuse the tagline already in `.brand-blurb` ("We hunt
   gaps others miss"), given more visual weight here. Subhead reuses the
   real footer sentence ("We hunt real, evidence-based gaps in developer
   tooling and ship focused IntelliJ-family plugins to fix them. Every
   product in this catalog exists because of a documented complaint, not
   a guess.").
2. **How we work** — a larger, more narrative version of the existing
   `.process-strip` (Observe → Detect → Validate → Build, with its real
   descriptions: "Identify friction" / "Find real gaps" / "Evidence &
   impact" / "Ship the missing tool"). Reuse the same 4 step colors
   (`--text`, `--good`, `--purple`, `--amber`) already used for these 4
   steps elsewhere. The compact version in the Field-mode sidebar stays as
   is — this is a second, fuller presentation of the same real steps, not
   new content.
3. **One real case** — Background ReadAction Freeze Companion. Use its
   real pitch/why already in `catalog_static_metadata.json` ("Not the
   usual 'a paid competitor's users are complaining' story this catalog
   is built around — this one is motivated directly by JetBrains' own
   Platform Blog."). Frame it honestly as the first case like this, not a
   series. See the hard constraints above for the link.
4. **A short "built by one person" line** — see the hard constraints
   above for exactly how far this goes. If you want a verifiable date to
   anchor it, the first real plugin in this catalog was first committed
   July 23, 2026 — that's more defensible than the site's own publish
   date (August 14), which is just when the landing page went up.
5. **Why install these** — 3-4 real value props: evidence-based (not
   guessed), one focused purpose per plugin (not bloated suites),
   transparent methodology (link to the new methodology page), free or
   freemium for most of the catalog. A modest closing link to
   `contact.html` ("Have a gap only your team can see? Tell us") — don't
   imply any consulting/services offering, none exists.
6. **Zero-value stats fix**: in `renderStats()`, `#methodFacts` currently
   always renders 3 tiles (Reviews total / Avg rating / GitHub stars)
   even when all three are `0`/`null`/`0`. Change it to only render a
   tile when its value is actually informative (`totalReviews > 0`,
   `avgRating != null`, `totalStars > 0`) — if none qualify, render
   nothing. Self-corrects as the catalog earns real reviews/stars.

## Phase B — `methodology.html` (new page)

Same skeleton as `contact.html` (own topbar/footer, same tokens,
`@font-face`, scoped CSP). Content: the 4 log-entries currently on the
home page, migrated as-is (same text; the "terminal log" styling can be
simplified if you want, the factual content doesn't change).

**Add a decision diagram** above the migrated content — a hand-drawn SVG
(same angular, no-circles style as the logo) visualizing the real
decision process in its public-safe, conceptual form (no internal script
or file names, ever):

```
Documented, recurring complaint found
   (Marketplace reviews, ratings, bug reports)
              |
              v
   Is it a real, repeated pattern? --No--> Not built
              | Yes
              v
   Does a focused fix already exist
   on the Marketplace?             --Yes--> Not built (redundant)
              | No
              v
   Buildable as one narrow,
   single-purpose plugin?          --No--> Documented as a known
              | Yes                        limit, not built
              v
   Built, tested, published --
   evidence stays attached to the listing
```

Use existing tokens only (`--good` for "Built", `--text-faint` for
discard branches, `--border` for connector lines). Label it something
plain and honest like "How a plugin gets greenlit" — never anything that
implies a more sophisticated or secret process than this.

## Phase C — Unify navigation across all 4 pages

`contact.html` has its own topbar nav ("Catalog | Methodology | Contact",
plain text) that's visually different from the home page's ("01 Overview
/ 02 Table / 03 Methodology", numbered badges) — this is why it feels
like a separate site. Fix: same nav group, same style, on all 4 pages
(`index.html`, the new `catalog.html` from Phase D, `methodology.html`,
`contact.html`) — logo always links home, nav is **Catalog | Methodology
| Contact**, no numbered badges, current page marked `aria-current="page"`
with active styling (same pattern `contact.html` already uses for
itself). Same unification for the footer nav.

## Phase D — Split the catalog into its own page, `catalog.html`

The full interactive catalog (search, Field/Table toggle, category/pricing
filters, the Hunting Field sidebar, the plugin grid/table, pagination,
dossier) currently loads immediately below the hero on the home page. Move
it to a new page, reached from the home page through Hunting Field category
tiles (a real link, not just scrolling to a grid on the same page).

**Architecture** (already mapped, reuse this — don't rediscover it):
- Global state (`mode, sortKey, sortDir, filterText, filterPricing,
  filterCategory, selectedRepo, PAGE_SIZE, catalogPage`) and the catalog
  rendering functions (`matches`, `sortedFiltered`, pagination helpers,
  `populateCategorySelect`/`wireCategorySelect`, `categoryCounts`,
  `updateCategoryBoard`/`wireCategoryBoard`, `pluginCardHtml`,
  `renderGrid`, `dossierBodyHtml`, `tableDossierBodyHtml`,
  `wireDossierInteractions`, `renderDossier`, `renderField`,
  `renderTable`, `updateModeNavLabels`, scroll helpers,
  `updateDocumentTitle`, `syncHashToState`, `renderAll`, `switchMode`,
  the column-sort handler, search/pricing listeners) all move to
  `catalog.html`.
- `renderStats()`, the hero-subtitle/visitor-count helpers, the featured
  slider (`initHeroSlider`), and `initTopbar` stay on the home page
  (simplified — no Field/Table toggle in nav anymore, see Phase C).
- Shared helpers used by both pages (`plugins`, `CATEGORIES`/`CAT_BY_KEY`,
  `esc`/`safeUrl`/`mdInline`, `pricingLabel`, `growthMarkup`, `GIF_URL`,
  `byRepo`) go into one shared file both pages load — don't copy-paste
  them into two places, that's exactly how the earlier
  `topbarStatusText`/`footerStatusText` bugs happened.
- **Extract the embedded `<script id="catalog-data">` JSON blob to an
  external `data/catalog-data.json`**, loaded via `fetch()` on both
  pages. This also means `auto_update_catalog.py` can switch from its
  fragile regex swap-in-place to a plain `json.dump()` — ask before
  changing the pipeline script if you're not confident about this part,
  it's the part with the most room for a subtle break.
- Move the full JSON-LD `CollectionPage`/`ItemList` and the `<noscript>`
  crawler fallback to `catalog.html` (that's where the real full listing
  lives now). The home page keeps a lighter `Organization`/`WebSite`
  JSON-LD instead.
- **New: category deep-linking.** `catalog.html?category=security` (etc.)
  should pre-apply that filter on load — read it via `URLSearchParams`
  before the first render. Nothing like this exists today (only
  `selectedRepo` is hash-linked); build it fresh.
- On the home page, the Hunting Field becomes a **navigation preview**:
  the same 8 category tiles (same HTML/CSS/icons/colors, nothing new
  invented), each a real `<a>` to `catalog.html?category=<key>` — no
  in-memory filtering JS needed here, just links. Add an "Explore the
  full catalog →" link to `catalog.html` with no filter.
- Update `sitemap.xml` (add `catalog.html`, high priority, daily
  changefreq) and the GitHub Actions sanity-check step to validate the
  new file locations.

**This is a real migration, not a redesign of the catalog UI itself** —
search, filters, sort, pagination, dossier, and the Field/Table toggle
must work exactly the same as they do today once moved. Verify this by
actually testing each one, not by assuming the move went cleanly.

Suggested order: (1) extract shared helpers + `catalog-data.json` first,
confirm the home page still works unchanged loading from the external
file; (2) build `catalog.html` with everything migrated + the new
category deep-linking, verify full functional parity; (3) replace the
catalog area on the home page with the Hunting Field preview; (4) update
the pipeline; (5) screenshots of both pages, desktop + mobile, before
calling this done.

## Phase E — Loading screen redesign

Replace `lab-loading.jpg` (a generic stock-photo-style server room image —
it contradicts this site's own "everything is hand-coded SVG/CSS, nothing
rasterized" approach, and adds 136KB to a screen whose job is to cover
load time, not add to it). Build it in pure CSS/SVG:

- Background: the same dot-grid + `--accent` radial glow already used
  site-wide, no image.
- Center: the real brand mark (the same 3-shape geometric SVG used in
  topbar/footer), animated once with a stroke-draw effect
  (`stroke-dasharray`/`stroke-dashoffset`).
- A circular HUD ring around the mark with tick marks and decorative
  binary digits (pure SVG `<circle>`/`<text>`, slow rotation, stopped
  under `prefers-reduced-motion`) — same "HUD" visual language the site
  already uses elsewhere (`.corner-frame`).
- Wordmark + tagline as today ("GAP HUNTER LABS / PLUGIN INTELLIGENCE").
- Status text must be real and verifiable — e.g. "Fetching catalog
  data…" while the real `fetch()` from Phase D is in flight, then "145
  plugins loaded" with the real parsed count. See the hard constraints
  above — no invented technology in this text, ever.
- Duration tied to real readiness (`DOMContentLoaded` + data parsed), not
  a fixed timer — check what currently drives `.is-done` on
  `.site-loader` (a `slDrift 9s ease-out` animation suggests a fixed 9s
  today) and change it to hide as soon as content is actually ready, with
  a small minimum floor (300-500ms) just to avoid flicker on fast
  connections.
- Respects `prefers-reduced-motion` (stroke-draw, ring rotation, any
  drift/pulse all become static).
- Delete `lab-loading.jpg` from the repo once nothing references it.

## Alignment and grid system — applies to everything above, not one section

Every card/box/tile touched or created in this round should share one
real system, not a new one-off per component:

1. One container width everywhere: `max-width: var(--page-max)` +
   `padding: 0 var(--page-pad)` on every top-level section on every page
   — never an invented width per section.
2. One vertical rhythm between sections: `--section-gap` (already 20px)
   used consistently, including on the new pages.
3. One padding scale for card/tile/box elements. Today each invents its
   own (`.log-entry` uses `14px 16px 14px 42px`, `.method-fact` uses
   `6px 10px`, `.process-step` uses `8px 10px`, etc.). Define one token
   (e.g. `--card-pad: 16px`, plus `--card-pad-sm: 10px` for small tiles
   like stats/badges) and migrate everything in this round onto one of
   those two — don't add a third value.
4. Real horizontal alignment between siblings in a row — not just equal
   container height, but icon/title/value starting at the same Y
   coordinate across every item in a group. Applies to: the 8 Hunting
   Field preview tiles, the 2 hero stat tiles, the `#methodFacts` tiles,
   the 4 steps of the narrative process strip, and the plugin cards in
   `catalog.html`. Use `align-items: stretch` on the container plus the
   same internal structure/order/gap in every item of a group.
5. Reuse existing radius/shadow tokens (`--radius`, `--shadow`, plus
   whatever gets added for `--card-pad`) — the methodology decision
   diagram and the loading-screen HUD ring lean on this same scale too,
   not one-off values.
6. Reuse existing breakpoints — don't invent a new `@media` for one
   component on the new pages.

**Verify alignment with a real check, not a look**: for each sibling
group in point 4, write a quick one-off script using
`getBoundingClientRect()` on each sibling, comparing `top`/`bottom` with
a 1-2px tolerance, and report the actual result.

## Verification checklist

- `new Function(...)` syntax check on the main script of all 4 pages.
- `python pipeline/auto_update_catalog.py --seo-from-index` (or its
  equivalent once adapted to `data/catalog-data.json`) stays idempotent,
  and the plugin count in `catalog-data.json`/`catalog-jsonld`/`noscript`
  (the last two now living in `catalog.html`) matches reality.
- Full functional parity check on `catalog.html`: search, category/
  pricing filters, column sort, pagination, opening a dossier in both
  Field and Table, and the Field/Table toggle itself — all identical to
  today's behavior.
- `catalog.html?category=<key>` actually pre-filters on first load for
  all 8 categories, not just after a manual click.
- Grep for `#methodology`, `#fieldView`, `#tableView`, `#tbody`, and any
  other moved ID across all 4 files afterward — zero dangling references.
- Grep for `CONSTITUTION\.md|SDK_GOTCHAS\.md|AUTOMATION_PLAYBOOK\.md|
  ARCHITECTURE\.md|INTELLIJ_PLATFORM_KNOWLEDGE\.md` across every touched/
  new file before any commit.
- Manual read-through of every new piece of copy (identity section, case
  study, decision diagram, loading screen, bio line) against the hard
  constraints at the top of this file.
- Nav: all 4 pages show the same link group with the same style, correct
  `aria-current="page"` on each.
- Screenshots (desktop + mobile) of: full home page, full `catalog.html`,
  `methodology.html`, and the loading screen, in `_review/screenshots/`
  (gitignored) before calling a phase done.
- Alignment: run the `getBoundingClientRect()` check described above on
  every sibling group listed there, report the real result.

## Reminders

- Keep WCAG AA contrast, ARIA landmarks, and reduced-motion support
  intact throughout — a visual fix that breaks accessibility isn't a fix.
- Don't break the auto-update cron.
- Delete this file once everything above is done and merged.
