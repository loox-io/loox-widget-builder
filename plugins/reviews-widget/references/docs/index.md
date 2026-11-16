# Loox Reviews Widget 2.0

Loox Reviews Widget 2.0 shows a store's product reviews on its Shopify storefront. It is built from small HTML elements (tags that start with `lxrw-`) placed inside one `<loox-reviews-widget>` element. The layout and look are open to change. The reviews, their order and the widget's behavior belong to Loox.

These pages produce a **Liquid section**: widget code added in the theme editor.

## How the parts fit

- `<loox-reviews-widget>` holds the reviews and passes them down. Every other part sits inside it.
- Data parts hold data and show nothing: `lxrw-header` (store totals) and `lxrw-reviews-list` (the reviews).
- Display parts show one thing each, and only work inside their data part. A display part placed anywhere else shows nothing, with no error.
- The review card is a template, written once and copied by Loox for every review.
- Full explanation: concepts.md

## Rules

- **Every review card shows three things:** the photo (`lxrw-review-media`), the star rating (`lxrw-review-rating`) and the review text (`lxrw-review-content`). The photo part stays empty on reviews without a photo. A card without all three fails the Loox check.
- The whole card is one button that opens the review. Links and buttons inside a card are not possible.
- Colors and sizes change through `--loox-lxrw-u-*` tokens, set on an element inside the widget. A style-only change to the default widget puts the tokens on `<lxrw-widget-preset>` (style.md).
- The widget matches the store's look: colors, fonts and corners (style.md).
- **Start from a recipe when one fits.** Match a request or a picture by its layout:
  - Even grid of photo cards, text on the photos: recipes/photo-tiles.md
  - Big quote beside a photo, one card at a time, a premium carousel: recipes/spotlight-carousel.md
  - Staggered or offset columns, quote cards mixed with photos, a dark section: recipes/collage.md
  - One review per row, text then the photo on the right: recipes/list.md
  The recipe is built in the store's colors, then changed to match the request.
- **Phones first:** a grid shows 2 reviews per row on a phone, a carousel shows the next card peeking (phone.md).
- **The verified mark goes next to every name** (`lxrw-review-verified-badge`).
- Store settings in Loox admin win. A setting that hides something (for example the date) hides it in every layout.

## Before building, the merchant's choices

Where: from the request (default: product page).

| Choice | Options | Default |
|---|---|---|
| Layout | grid, carousel, list | grid |
| Which reviews | this product's reviews, store reviews, both | this product's reviews |
| Photos | all reviews, only reviews with photos | all reviews |
| Where | product page, all-reviews page, cart | product page |

## Pages

| Page | What it covers |
|---|---|
| concepts.md | How data parts and display parts fit, what Loox owns, the 4 ways to customize |
| build.md | From the merchant's choices to a saved widget, for both results |
| style.md | Colors, sizes and shapes: which token or style hook changes what |
| recipes/spotlight-carousel.md | Tested code: Loox's signature carousel, a quote panel beside a tall photo |
| recipes/photo-tiles.md | Tested code: photo tiles with stars, name and text over the photo |
| recipes/list.md | Tested code: one review per row, photo on the right |
| recipes/collage.md | Tested code: staggered scrolling collage with quote cards mixed in |
| phone.md | The phone rules every widget follows |
| design-rules.md | The Loox look and motion: real Loox values for grids and featured widgets, and 5 tested animations |
| styles/editorial.md, minimal.md, photo-first.md, bold.md | Four named looks. When the merchant names one, its page sets layout, text, photo, cards and motion |
| fix.md | Widget shows nothing or looks wrong: symptom, cause, change |
| components/header.md | `lxrw-header`: the store's totals at the top of the widget |
| components/header-write-button.md | `lxrw-header-write-button`: the "Write a review" button, and how to restyle it (for example as an animated icon) |
| components/review-card.md | The card template and the card box around it |
| components/review-media.md | `lxrw-review-media`: the review's first photo or video poster |
| components/review-rating.md | `lxrw-review-rating`: the review's stars |
| components/review-content.md | `lxrw-review-content`: the review text |
| components/review-date.md | `lxrw-review-date`: when the review was written |
| components/reviewer-name.md | `lxrw-reviewer-name`: the reviewer's short name |
| components/review-verified-badge.md | `lxrw-review-verified-badge`: the verified mark next to the name |
| components/sort-menu.md | `lxrw-header-sort-menu`: the sort button and its options |
| components/load-more.md | `lxrw-load-more`: the "Show more reviews" button |
| components/empty-state.md | `lxrw-empty-state`: "Be the first to write a review" |
| components/review-reply.md | `lxrw-review-reply`: the store's reply on a card |
| components/review-labels.md | The "Rewarded" and "Incentivized" labels |
| components/store-reviews-tab.md | `lxrw-store-reviews-tab`: product and store review tabs |
| layouts/carousel.md | A sideways-scrolling row of cards with previous and next buttons |
| outputs/liquid-section.md | Where the code goes: a section file or a Custom Liquid box, with the code for each |
| not-possible.md | What cannot be built, the closest option, and what is coming soon |
