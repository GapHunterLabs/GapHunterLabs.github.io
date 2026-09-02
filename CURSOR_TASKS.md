# Next tasks

Continuing the site improvement work on this branch (`site-improvements`).
Recap of what's already done and merged to `main`, live: self-hosted
fonts (IBM Plex Sans + JetBrains Mono), the Hunting Field radial diagram
replaced by a category grid (`.cat-board`, fully wired), a crawler-visible
static fallback (`<noscript>` block listing every plugin), and a full
101-plugin JSON-LD (previously a stale 8-plugin sample).

Work in small increments, checkpoint before piling on more, push to
`site-improvements` (never `main` directly).

## 1. Visual QA pass — screenshots first, then fix

Before changing anything else, take real screenshots of the live
rendered page so problems are documented, not guessed at:

- Use whatever screenshot capability you have (a headless browser via
  Playwright is fine if needed — `npx playwright screenshot` or a small
  throwaway script; it doesn't need to become a permanent dependency).
- Cover every major region individually, plus a couple of full-page
  shots: topbar/nav, header, the featured-plugin slider, main body
  sections (the category grid, methodology, brand blurb), the bottom
  of the page, footer, plugin cards, the Table view, the Field view,
  and every button style on the site.
- Capture at least two viewport widths: desktop (~1280px) and mobile
  (~375px) — proportions often differ between the two.
- Save everything to `_review/screenshots/` in this repo (create it,
  add it to `.gitignore` — these are working artifacts, not something
  to commit or ship).

Then, before touching code, write a short concrete list of what's
actually wrong: inconsistent spacing/padding between sections,
misaligned elements, things disproportionately large or small relative
to their neighbors, broken alignment on mobile, buttons that don't
match each other in size/padding/radius, cards with uneven heights or
spacing, anything that reads as unfinished or accidental rather than
designed. Be specific (section + what's wrong), not general.

Fix what you found, same small-increment process, with a fresh
before/after screenshot for each meaningful chunk.

## 2. Rename "Hunting Field"

The section heading still says "Hunting Field" (and the hint text
still says "Explore by technology gap") even though the radial diagram
is gone and it's a category grid now. Pick a name that matches what it
actually is — something like "Categories" or "Browse by category" —
and update the heading, hint text, and any other visible copy that
still assumes the old diagram (aria-labels, titles, etc.). Check for
other leftover references to the old concept while you're in there.

## 3. Reduce homepage plugin overload

Right now the full catalog (101 plugins) is visible on load. Add a
curated/featured view as the default landing state — a small set
(8-12 plugins; your call on selection logic: highest growth, most
recent, or one per category) with a clear, obvious action to see the
full catalog. The full Table/Field views stay exactly as they are,
just one click away instead of the default.

## 4. Related-plugin cross-links

In each plugin's dossier panel, add links to 2-4 related plugins (same
category, or shared niche keywords) and a link to that category's
filtered view. This is the main internal-linking mechanism for this
site — right now there's almost none, since everything lives behind
one URL.

## 5. Design token cleanup (do this last)

Refactor-only, should not change how anything looks. The CSS has ~30
different font-size values, ~24 spacing values, 9 border-radius
values, and 19 box-shadow declarations, most of them one-off
variations of the same handful of ideas. Consolidate into real CSS
custom-property scales (type scale, spacing scale, radius scale,
shadow scale) and use them consistently. Do this after the visual
items above, not before — easier to review as its own isolated change.

## Reminders

- Keep WCAG AA contrast, ARIA landmarks, and reduced-motion support
  intact through all of this — a visual fix that breaks accessibility
  isn't a fix.
- Don't break the auto-update cron (`pipeline/auto_update_catalog.py`
  + `.github/workflows/update-catalog.yml`).
- English-only new code/copy.
- Don't reference any internal document or process name in code
  comments or copy.
- Delete this file (`CURSOR_TASKS.md`) once everything above is done
  and merged — it's a working checklist, not permanent repo content.
