# Next tasks — box/detail/transition consolidation

Follow-up to the catalog-split round now live on `main`. That round
correctly prioritized structure over polish; this round closes the token-
consolidation work the alignment system called for but didn't get to.
Refactor-only — none of this should change how anything *looks* at a
glance, only make the values behind it consistent. Work in small
increments on `site-improvements`, screenshot before/after each
meaningful chunk in `_review/screenshots/` (create it, gitignored),
verify no visual regression before moving to the next item.

## 1. Border-radius consolidation

143 `border-radius` declarations across the 4 pages, only 22 reference
`var(--radius)` — the rest hardcode one of 9 different pixel values
(8px, 4px, 10px, 7px, 6px, 5px, 9px, 1px, plus `50%`/`100px` for circles/
pills, which are legitimately different and stay as-is). Define a real
scale next to the existing `--radius` and migrate every hardcoded value
onto it — don't invent a 10th value along the way:

```
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius: 10px;   /* keep as-is, already used in 22 places */
```

Go component by component (buttons, cards, badges, inputs, panels), pick
the closest existing radius from that scale for each, and audit that
visually similar components end up with the *same* radius, not just
"a value from the scale." A button and an input sitting in the same
control row should probably share one radius, for example.

## 2. Extend `--card-pad`/`--card-pad-sm` to all 4 pages

These tokens exist and are used in `index.html`/`catalog.html` (4 times
each) but **zero times** in `methodology.html`/`contact.html` — those two
pages have their own independent padding values instead. Same class of
problem as the nav inconsistency fixed earlier ("feels like a different
site"). Migrate every card/box/tile on those two pages onto
`--card-pad`/`--card-pad-sm` instead of a page-local value.

## 3. Transition duration + easing scale

12 different duration values in use today (`0.15s` dominates with 42
uses — keep that as the default). Define a small real scale and migrate
onto it:

```
--duration-fast: 120ms;
--duration-base: 150ms;   /* matches the existing dominant value */
--duration-slow: 300ms;
```

Also:
- Fix the loading-screen animation blocks (`slRotate`, `slDraw`, etc.)
  that write durations without the leading zero (`.4s`, `.12s`, `.24s`
  instead of `0.4s`/`0.12s`/`0.24s`) — same value, inconsistent format.
- Consolidate the two real easing curves in use
  (`cubic-bezier(.65,0,.35,1)` and `cubic-bezier(.2,.7,.3,1)`) into named
  custom properties (e.g. `--ease-standard`, `--ease-emphasized`) and fix
  the copies of the first curve that have stray spaces
  (`cubic-bezier(.65, 0, .35, 1)`) so it's written one way everywhere.

## Verification

- Screenshot every page before and after, desktop + mobile — this is a
  refactor, so "looks identical, values are cleaner underneath" is the
  actual success condition, not a visual redesign.
- `new Function(...)` syntax check on all 4 pages afterward.
- Grep for the raw pixel/second values you migrated away from, to
  confirm nothing was missed by accident.
- Don't touch `50%`/`100px` radius values (circles/pills) or the 4
  legitimate hover/active glow `box-shadow` effects — those are
  intentionally different from the base card radius/shadow, not part of
  this cleanup.

## Reminders

- English-only comments/copy, no internal document or process names, no
  invented technology, no personal details beyond what's already public
  — same constraints as always.
- Delete this file once done and merged.
