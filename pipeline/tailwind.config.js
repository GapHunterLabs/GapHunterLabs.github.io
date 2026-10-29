/* Tailwind CLI config for the static site. Compiled by `npm run build:css` into ../css/tw.css.
 * - prefix "tw-": the site already has ~300 hand-written classes; utilities never collide.
 * - preflight off: the existing base.css owns resets.
 * - colors are the CSS tokens of css/theme.css, so light/dark/System keep working without `dark:` variants.
 */
module.exports = {
  prefix: 'tw-',
  content: [
    '../**/*.html', '../js/*.js', './*.py',
    '!../node_modules/**', '!./node_modules/**', '!../_review/**',
    // generated copies: their classes come from the .py generators scanned above
    '!../catalog/**', '!../es/**',
  ],
  corePlugins: { preflight: false },
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)', surface: 'var(--surface)', 'surface-2': 'var(--surface-2)', 'surface-3': 'var(--surface-3)',
        line: 'var(--border)', 'line-strong': 'var(--border-strong)',
        ink: 'var(--text)', dim: 'var(--text-dim)', faint: 'var(--text-faint)',
        signal: 'var(--signal)', valid: 'var(--valid)', inspect: 'var(--inspect)', bad: 'var(--bad)',
      },
      fontFamily: { sans: 'var(--sans)', mono: 'var(--mono)' },
      borderRadius: { DEFAULT: 'var(--radius)', md: 'var(--radius-md)', lg: 'var(--radius-lg)' },
    },
  },
};
