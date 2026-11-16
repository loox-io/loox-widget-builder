# Changing the look

## Where tokens go

Tokens are CSS variables that start with `--loox-lxrw-u-`. They work when set on an element inside `<loox-reviews-widget>`, such as a wrapper `div`. On the widget element itself, on `body` or on `:root`, the store's own values win. Three variables without `u-` work from any wrapper: `--loox-lxrw-card-gap` (space Loox puts around each card box, default 14px; set `0px` when your own container sets the gap), `--loox-lxrw-card-width` and `--loox-lxrw-media-opacity`.

```html
<lxrw-reviews-list>
  <div class="cards" style="--loox-lxrw-u-stars-color: #d4a017;">
    ...
  </div>
</lxrw-reviews-list>
```

A token applies to every part inside the element where it is set.

## Restyling the default widget

A store that uses Loox's default layout has `<lxrw-widget-preset>` inside the widget. To change its look without rebuilding the layout, the tokens go on the preset element itself:

```html
<loox-reviews-widget>
  <lxrw-widget-preset style="--loox-lxrw-u-stars-color: #d4a017; --loox-lxrw-u-card-radius: 16px;"></lxrw-widget-preset>
</loox-reviews-widget>
```

This is a complete answer for a style-only request about colors and corners: the preset keeps the default header, cards and order.

Tokens reach every part inside the default widget. `::part()` rules reach it through the two inner presets, not through `lxrw-widget-preset` itself:

- Header: the store's header layout setting picks one of three. Standard is `lxrw-header-minimal-preset` (five stars, breakdown in a dropdown). Compact is `lxrw-header-compact-preset` (one star beside the average number, breakdown always open, stacked). Expanded is `lxrw-header-expanded-preset` (Compact's pieces in one row). All three: `::part(average | count | row | bar | distribution-count | write-button | menu | trigger | dropdown | option | option-selected)`. Minimal also has `stars | summary | toggle | chevron | panel | distribution-average`. Write header rules for all three. `count` is the summary count; the count on each star row is `distribution-count`.
- Cards: `lxrw-review-card-grid-preset::part(media | image | media-badge | name | verified-badge | verified-text | date | stars | text | read-more | reply | reply-title | reply-text | product | product-image | product-name | item-type)`. List and Mosaic stores use `lxrw-review-card-list-preset`, same parts: write card rules for both.

Example, gold write button on the default widget: `lxrw-header-minimal-preset::part(write-button) { background: #d4a017; }`. A style-only request keeps the preset and adds rules like these.

## Visible changes

A style request gets a value the shopper can see change: if the store's stars are already gold, "gold stars" gets a deeper or brighter gold. The answer states in one line what changed and from what.

## Common requests

| Request | Change |
|---|---|
| Gold stars | `--loox-lxrw-u-stars-color: #d4a017;` |
| Rounder cards | `--loox-lxrw-u-card-radius: 16px;` |
| No card shadow | `--loox-lxrw-u-card-shadow: none;` |
| Card background | `--loox-lxrw-u-review-background-color: #faf7f2;` |
| Card border | `--loox-lxrw-u-review-border: 1px solid #e5e5e5;` |
| Text color | `--loox-lxrw-u-text-color: #222;` |
| Square photos | own card: `lxrw-review-media { display: block; aspect-ratio: 1; min-height: 0; overflow: hidden; }` plus `lxrw-review-media::part(media) { height: 100%; aspect-ratio: auto !important; }` (components/review-media.md: the frame rule alone clips names in a flex card); default widget: `lxrw-review-card-grid-preset::part(media) { aspect-ratio: 1 !important; }` |
| Rounder photos | `--loox-lxrw-u-media-radius: 12px;` |
| Shorter text | `lxrw-review-content::part(text) { -webkit-line-clamp: 4; display: -webkit-box; -webkit-box-orient: vertical; overflow: hidden; }` (default widget: `lxrw-review-card-grid-preset::part(text)`) |
| Bigger stars | `lxrw-review-rating::part(stars) { font-size: 20px; }` (default widget: `lxrw-review-card-grid-preset::part(stars)`) |

## All tokens

| Token | Changes | Read by |
|---|---|---|
| `--loox-lxrw-u-stars-color` | Star color | review stars, header average, distribution |
| `--loox-lxrw-u-text-color` | Review text color | card, review text |
| `--loox-lxrw-u-reviewer-name-color` | Name color | reviewer name |
| `--loox-lxrw-u-date-color` | Date color | review date |
| `--loox-lxrw-u-header-text-color` | Header text | header parts, empty state |
| `--loox-lxrw-u-review-background-color` | Card background | card |
| `--loox-lxrw-u-review-background-hover-color` | Card background on hover | card |
| `--loox-lxrw-u-review-border` | Card border | card |
| `--loox-lxrw-u-card-radius` | Card corners | card, badges, tabs |
| `--loox-lxrw-u-card-shadow` | Card shadow | card |
| `--loox-lxrw-u-media-radius` | Photo corners | photo |
| `--loox-lxrw-u-badge-bg`, `--loox-lxrw-u-badge-text-color` | "+N" photo badge | photo |
| `--loox-lxrw-u-review-verified-badge-color` | Verified mark | verified badge |
| `--loox-lxrw-u-button-bg`, `--loox-lxrw-u-button-text-color`, `--loox-lxrw-u-button-radius` | Buttons | write button, sort menu, load more |
| `--loox-lxrw-u-reply-background-color`, `--loox-lxrw-u-reply-text-color` | Store reply | reply |
| `--loox-lxrw-u-meta-text-color`, `--loox-lxrw-u-product-name-color` | Small grey text, product name | card |
| `--loox-lxrw-u-dropdown-bg`, `--loox-lxrw-u-dropdown-text-color`, `--loox-lxrw-u-dropdown-selected-color` | Sort menu | header |
| `--loox-lxrw-u-progress-bar-color`, `--loox-lxrw-u-progress-track-color` | Star distribution bars | header |
| `--loox-lxrw-u-tab-text-color`, `--loox-lxrw-u-tab-active-bg`, `--loox-lxrw-u-tab-hover-bg`, `--loox-lxrw-u-tab-count-bg` | Product / store review tabs | tabs |
| `--loox-lxrw-u-empty-state-text-color` | No-reviews message | empty state |

Defaults come from the store's settings in Loox admin.

## Style hooks (`::part`)

Each part page lists its hooks. They accept normal CSS: color, font, size, spacing, border. Example: `lxrw-review-date::part(date) { font-size: 12px; }`.

## Matching the store

The widget takes the merchant's store look, laid out the Loox way.

**From the store:** colors, fonts and corner shapes, so stars, text, card background and radius match the store. Theme CSS variables can be used directly, for example `--loox-lxrw-u-text-color: rgb(var(--color-foreground));`, so the widget follows later theme changes. Fonts are set on the merchant's own wrappers inside the card (for example `font-family: var(--font-body-family)`).

**Loox layout rules (clean, with space):**
- Equal card heights (a choice; Loox's default grid is a masonry of uneven cards): the card box fills its cell (`.cards lxrw-review-card { width: auto; margin: 0; height: 100%; }`), and the card wrapper is a flex column with `height: 100%`.
- Aligned footers: the middle block takes the free space (`flex: 1`), the footer gets `margin-top: auto`.
- One photo shape, set as in components/review-media.md, photo first in the card.
- One spacing scale: 4, 8, 12, 16, 24, 32 px. One gap between cards, one inner padding, padding on the text block and not on the card (so the photo reaches the edges).
- One corner radius, through `--loox-lxrw-u-card-radius`.
- No fixed heights on cards, text or photos.
- Even text: clamp long text to about 5 lines.
- Phones: 2 columns from a 320px-wide widget (`repeat(2, minmax(0, 1fr))`), more columns through `@container (min-width: 600px)` and `(min-width: 920px)`. `minmax(240px, 1fr)`-style formulas give one column on every phone (phone.md).

**Check:** cards in a row have the same height, footers line up, and the layout still reads well for a card with no photo, a one-line review and a very long review.

## Can't change

- The rating icon shape (store setting).
- Anything a store setting hides.
