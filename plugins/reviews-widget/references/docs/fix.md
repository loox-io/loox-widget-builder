# Fix: the widget shows nothing or looks wrong

Check the first matching symptom, then the cause, before changing the layout.

| What the merchant sees | Likely cause | Check and change |
|---|---|---|
| Only the wrapper or title: empty stars, no count, no cards | The widget has no data or no script. The code was pasted without the Liquid wiring, or the Loox app embed is off (`window.LOOX.root` missing), so the widget draws nothing | Liquid output: the two `<script>` lines and the `<loox-reviews-widget client-id=… product-id=…>` attributes are present (outputs/liquid-section.md). The browser console shows whether `reviews-widget.js` failed to load |
| One part shows nothing at all, with no error (bars, a button, a date) | Check in this order. 1: the part's name is wrong, or the store's script doesn't have that part yet. 2: a store setting hides it. 3: the product has no data for it | 1: in the browser console, `customElements.get('<tag>')` returns undefined for an unknown name (the installer reports these as `unknown_parts`). 2: Loox app > Reviews Widget > Settings > Preferences > Display settings. 3: the product's published reviews |
| "This code has errors" in a Custom Liquid box | The section file's `{% schema %}` block or `section.settings` was pasted into a Custom Liquid box | Use the Custom Liquid version in outputs/liquid-section.md (no schema, fixed values) |
| Cards appear but no reviews text or stars | A display part sits outside its data part (outside the card template or outside `lxrw-header`) | Move it inside, as in concepts.md |
| Stars, name or text missing on a photo | The photo paints over the text box | Text box: `position: relative; z-index: 1` (recipes/photo-tiles.md) |
| Text cut off at the bottom of a photo tile | A tall photo stretches the tile | Tile: `grid-template: minmax(0, 1fr) / minmax(0, 1fr)`; photo part: `min-height: 0` |
| One huge review per screen on phones | Grid formula gives 1 column on phones | phone.md rule 2: 2 columns from a 320px widget |
| "Every third card" styling does nothing | Each card sits in an `lxrw-review-card-provider` | Count on the provider: `lxrw-review-card-provider:nth-of-type(3n) lxrw-review-card` |
| A style rule has no effect on the default widget | `::part()` aimed at the wrong element | Default widget: `lxrw-header-minimal-preset::part(…)` (or the compact or expanded preset) and `lxrw-review-card-grid-preset::part(…)` (style.md) |
| Store reviews tabs do not show | The store has store reviews off in Loox | The tabs show only when store reviews are on (components/store-reviews-tab.md) |
| Fonts look different than planned | A font named in the CSS is not loaded by the theme | Use the theme's font variables, for example `var(--font-body-family)` |
