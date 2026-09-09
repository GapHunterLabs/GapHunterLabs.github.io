# Homepage visual refresh — task brief for Cursor

## Scope

Restyle the existing homepage (and the matching sections of
`catalog.html`) toward the dark/high-contrast concept shown in the
reference screenshot the user provided. **This is a visual reskin of
the current site, not a rewrite.** Keep the existing plain HTML/CSS/JS
structure, the existing files (`index.html`, `catalog.html`,
`methodology.html`, `contact.html`, `js/catalog-shared.js`), and the
existing data pipeline (`data/catalog-data.json`, loaded via
`window.GapCatalog.ready`). An earlier attempt to rebuild this site on
a new framework from scratch was reverted because the result was worse
than the original — don't repeat that shape of change. If a piece of
the concept genuinely requires new markup or a new small module, that's
fine; introducing a build step or a frontend framework is not in scope.

## Read this before touching any number, label, or filename in the screenshot

The reference screenshot is a **concept mockup, not a real screenshot**
of working software — likely produced by an image-generation tool. Two
tells, confirmed against the live data:

1. **The little embedded "code editor" panel has garbled/nonsense
   text** — the dropdown menu labels, the file-tree folder names, are
   not real words (image generators cannot render arbitrary text
   correctly). If the final design keeps an editor-panel illustration
   at all, use *real* labels (e.g. actual menu names, a real folder
   structure) — never copy the mockup's placeholder strings literally.
2. **The numbers in the mockup don't match each other or reality**:
   - Header says "145-plugin catalog" — **145 is correct** (matches
     live data as of this writing).
   - "Explore by category" tile counts in the mockup: API 12, DevOps
     48, Security 36, Data 4, Code Quality 22, Codegen 19, Testing 14,
     Editor 7. Those sum to **162**, which already contradicts the
     145 total in the same screenshot. The real live counts (computed
     from the same category system already implemented in
     `js/catalog-shared.js` / `CATEGORIES` / `NICHE_TO_CATEGORY`) are:
     **API 12, DevOps 48, Security 36, Data 4, Code Quality 31,
     Codegen 3, Testing 3, Editor 8** — sums to 145. Four of the eight
     match the mockup exactly; four (Quality, Codegen, Testing, Editor)
     don't. Do not hardcode any of these numbers — the homepage
     already renders them live via `renderCategories()`; keep that.
   - "4,523 downloads ↑281.7%": real current total is ~4,244 (grows
     daily via the existing data pipeline — pull it live, never
     hardcode). The "↑281.7%" growth badge has no real source: only a
     subset of plugins carry historical growth data at all, and their
     aggregate works out to roughly +134%, not +282%. **Don't ship an
     aggregate growth percentage unless you compute it live from real
     per-plugin `growth`/`growthFrom` fields** (and only for the
     subset that has them) — otherwise drop that badge rather than
     invent a number.

Treat the screenshot as direction for layout, spacing, color, and
motion only. Every number and label that ends up on the live page must
come from the real data file or existing copy, never transcribed from
the image.

## Concrete tasks

1. **Hero + stat cards**: restyle to match the concept's contrast and
   card treatment. Keep both stat cards driven by the real live
   totals (plugin count, downloads). Skip the growth-percentage badge
   unless it can be computed live and honestly (see above).
2. **"Explore by category" tiles**: pure visual reskin. The counts are
   already live via `renderCategories()` / `CATEGORIES` — don't touch
   that logic, just restyle the cards.
3. **Top bar**:
   - Add a plugin search input (the concept shows `Search plugins...
     ⌘K`). Wire it against the plugin data already loaded on the page
     (`catalog.html` already has search/filter logic against the same
     data — reuse it rather than writing a second implementation) and
     link results to `catalog.html`.
   - **Keep the existing JetBrains Marketplace icon link** — it's not
     in the mockup, but it's real and currently the primary
     distribution channel; the mockup is incomplete here, not a
     spec to follow literally.
   - The mockup's small circular "profile/account" icon in the top
     right doesn't correspond to anything real — this site has no
     login/accounts. Drop it (or repurpose that slot for something
     real, like the JetBrains icon, if the top bar is getting crowded).
   - A working theme toggle (the mockup's sun icon) is a real feature,
     not a decoration — it needs a complete second (light) color
     palette, not just an icon swap. Treat it as optional/stretch for
     this pass; call it out explicitly if it's dropped rather than
     silently shipping a non-functional icon.
4. **VS Code Marketplace icon**: a second icon/link is being added
   next to the JetBrains one (top bar, footer, and per-plugin catalog
   cards where applicable), pointing at the VS Code Marketplace
   publisher/extension pages. The data field that flags which catalog
   entries have a VS Code listing is being added separately to the
   data file — build the icon rendering to read that field once it
   lands (ask before hardcoding any extension list into HTML).

## Housekeeping

Delete this file once its tasks are merged — don't leave a working
task list committed in the repo after the work is done.
