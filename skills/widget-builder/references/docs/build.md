# Building a widget

## 1. Collect the four choices

Layout, which reviews, photos, and where (table in index.md).

## 2. Map the choices

| Choice | Where it goes |
|---|---|
| Layout | the container and CSS around the card template |
| Which reviews | attribute `reviews-to-display`: `product_reviews_only`, `store_reviews_only`, `product_store_reviews` |
| Photos | attribute `only-photos="true"` |
| Where | attribute `surface`: `product`, `aggregate` (all-reviews page), `cart` |


## 3. Compose

Start from the tree in concepts.md:

```html
<loox-reviews-widget>
  <div class="lxr-grid" style="--loox-lxrw-u-stars-color: #d4a017;">
    <lxrw-header>
      <div class="lxr-grid__summary">
        <lxrw-header-rate-average-icons></lxrw-header-rate-average-icons>
        <lxrw-header-reviews-count></lxrw-header-reviews-count>
        <lxrw-header-write-button></lxrw-header-write-button>
      </div>
    </lxrw-header>
    <lxrw-reviews-list>
      <div class="lxr-grid__cards">
        <template slot="review-card">
          <article class="lxr-grid__card">
            <lxrw-review-media></lxrw-review-media>
            <div class="lxr-grid__body">
              <lxrw-review-rating></lxrw-review-rating>
              <lxrw-review-content></lxrw-review-content>
              <div class="lxr-grid__byline">
                <lxrw-reviewer-name></lxrw-reviewer-name>
                <lxrw-review-verified-badge></lxrw-review-verified-badge>
              </div>
            </div>
          </article>
        </template>
      </div>
    </lxrw-reviews-list>
    <lxrw-empty-state></lxrw-empty-state>
    <lxrw-load-more></lxrw-load-more>
  </div>
</loox-reviews-widget>
<style>
  .lxr-grid__summary { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
  .lxr-grid__cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; --loox-lxrw-card-gap: 0px; }
  @container (min-width: 600px) { .lxr-grid__cards { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; } }
  @container (min-width: 920px) { .lxr-grid__cards { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
  .lxr-grid__cards lxrw-review-card { width: auto; margin: 0; height: 100%; }
  .lxr-grid__card lxrw-review-media::part(media) { aspect-ratio: 1 !important; }
  .lxr-grid__byline { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
  .lxr-grid__card { display: flex; flex-direction: column; height: 100%; }
  .lxr-grid__body { display: flex; flex-direction: column; gap: 8px; padding: 12px; }
  .lxr-grid__card lxrw-review-content::part(text) { display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
</style>
```

The cards sit in the container that holds the template (`.lxr-grid__cards` here). **When a request matches a recipe, start from the recipe's code** (recipes/spotlight-carousel.md for carousels, quotes or a premium look; recipes/photo-tiles.md for photo grids or text on photos). Look and motion: design-rules.md. Phones: phone.md.

- **Columns follow the widget's width.** The widget is a size container: use `@container`, not `@media`, for layout steps. A phone grid has 2 columns.
- **The verified mark goes next to every name.**

- **One wrapper for the tokens.** A single `div` directly inside `<loox-reviews-widget>` holds the header, the list and the extra parts, and carries every token. Tokens set inside the list do not reach the header.
- **Class names.** Every class starts with one widget prefix such as `lxr-grid__`. Theme stylesheets already use names like `.card`, `.track` and `.nav`, so plain names change other parts of the store, and the theme changes the widget.
- **Load more and empty state.** `<lxrw-load-more>` shows the next page of reviews; without it, shoppers see only the first page, which holds 20 reviews by default (`reviews-limit` takes 1 to 50; a value outside that range is ignored). `<lxrw-empty-state>` shows the message for a product with no reviews; without it, such a product shows an empty section.
- **Theme colors.** Theme color variables hold three numbers (`rgb(var(--color-foreground))`) or a full color: check which.
- **Cards apart from the page.** The card background differs from the page background (a tint, a border or a shadow), or the cards disappear into the page.

## 4. Check

Before saving, the composition passes these checks:
- One `<loox-reviews-widget>`, with every other part inside it.
- Header display parts inside `<lxrw-header>`. Card display parts inside the card template.
- Every card has `lxrw-review-media`, `lxrw-review-rating` and `lxrw-review-content`, and the name has `lxrw-review-verified-badge` next to it.
- At 390px wide: a grid shows 2 reviews per row, a carousel shows the next card peeking, nothing scrolls sideways (phone.md).
- No links, buttons or inputs inside the card template.
- Tokens set on a wrapper inside the widget.
- Only parts listed in these pages.
- Class names carry the widget prefix. Scripts look up elements inside the widget's own wrapper, not the whole page.

## 5. Save

The Custom Liquid version in outputs/liquid-section.md, added through Customize > product page > Add section > Custom Liquid.
