# Recipe: photo tiles

Shopper photos as tiles, with the stars, name, verified mark and one line of text laid over the bottom of the photo. Tested on a live store at desktop and 390px phone width. Start from this code and change the accent, radius, title and column counts to fit the request; keep the structure.

Fits requests like: a photo grid, a gallery, an Instagram or UGC wall, tiles with text on the photo, a picture of a grid of photo cards.

## Code

```html
<loox-reviews-widget>
  <div class="lxr-tiles" style="--lxr-accent: rgb(104,117,82); --lxr-radius: 16px;">
    <lxrw-header>
      <div class="lxr-tiles__head">
        <h2 class="lxr-tiles__title">Straight from our customers</h2>
        <div class="lxr-tiles__summary">
          <lxrw-header-rate-average-icons></lxrw-header-rate-average-icons>
          <lxrw-header-reviews-count></lxrw-header-reviews-count>
        </div>
      </div>
    </lxrw-header>
    <lxrw-reviews-list>
      <div class="lxr-tiles__grid">
        <template slot="review-card">
          <article class="lxr-tiles__tile">
            <lxrw-review-media></lxrw-review-media>
            <div class="lxr-tiles__over">
              <lxrw-review-rating></lxrw-review-rating>
              <div class="lxr-tiles__byline">
                <lxrw-reviewer-name></lxrw-reviewer-name>
                <lxrw-review-verified-badge></lxrw-review-verified-badge>
              </div>
              <lxrw-review-content></lxrw-review-content>
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
  .lxr-tiles { font-family: inherit; }
  .lxr-tiles__head { text-align: center; margin-bottom: 24px; }
  .lxr-tiles__title { margin: 0 0 8px; }
  .lxr-tiles__summary { display: inline-flex; align-items: center; gap: 8px; }
  .lxr-tiles__grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; --loox-lxrw-card-gap: 0px; }
  @container (min-width: 600px) { .lxr-tiles__grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; } }
  @container (min-width: 920px) { .lxr-tiles__grid { grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; } }
  .lxr-tiles__grid lxrw-review-card { width: auto; margin: 0; height: 100%; --loox-lxrw-u-card-radius: var(--lxr-radius); --loox-lxrw-u-card-shadow: none; --loox-lxrw-u-review-border: none; }
  .lxr-tiles__tile { display: grid; grid-template: minmax(0, 1fr) / minmax(0, 1fr); aspect-ratio: 4 / 5; overflow: hidden; border-radius: var(--lxr-radius); background: var(--lxr-accent); }
  .lxr-tiles__tile > lxrw-review-media, .lxr-tiles__tile > .lxr-tiles__over { grid-area: 1 / 1; min-width: 0; }
  .lxr-tiles__tile > lxrw-review-media { height: 100%; min-height: 0; overflow: hidden; }
  .lxr-tiles__tile lxrw-review-media::part(media) { height: 100%; aspect-ratio: auto !important; border-radius: 0; }
  .lxr-tiles__tile lxrw-review-media::part(image) { width: 100%; height: 100%; object-fit: cover; }
  .lxr-tiles__over { position: relative; z-index: 1; align-self: end; display: flex; flex-direction: column; gap: 4px; padding: 48px 12px 12px; color: #fff;
    background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.5) 48%, rgba(0,0,0,.7) 100%);
    text-shadow: 0 1px 2px rgba(0,0,0,.5);
    --loox-lxrw-u-reviewer-name-color: #fff; --loox-lxrw-u-text-color: #fff; --loox-lxrw-u-review-verified-badge-color: #fff; }
  .lxr-tiles__byline { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
  .lxr-tiles__over lxrw-reviewer-name::part(name) { font-weight: 600; font-size: 14px; }
  .lxr-tiles__over lxrw-review-verified-badge::part(text) { color: #fff; }
  .lxr-tiles__over lxrw-review-content::part(text) { font-size: 13px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; opacity: .9; }
  @container (max-width: 599px) { .lxr-tiles__over lxrw-review-content::part(text) { -webkit-line-clamp: 2; } }
  @media (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference) {
    .lxr-tiles__tile lxrw-review-media::part(image) { transition: transform 300ms ease-in-out; }
    .lxr-tiles__over lxrw-review-content::part(text) { transition: opacity 200ms ease; }
    .lxr-tiles__grid lxrw-review-card:hover lxrw-review-media::part(image) { transform: scale(1.04); }
    .lxr-tiles__grid lxrw-review-card:hover lxrw-review-content::part(text) { -webkit-line-clamp: 6; }
  }
</style>
```

## Why each piece is there

- **One grid cell, two layers.** The tile is a one-cell grid (`grid-template: minmax(0, 1fr) / minmax(0, 1fr)`). The photo and the text box both sit in that cell (`grid-area: 1 / 1`). Without `minmax(0, 1fr)` a tall photo stretches the tile and the text is cut off at the bottom.
- **Text box above the photo.** `position: relative; z-index: 1` on the text box. The photo part is positioned, so without this the photo paints over the text and the stars and name disappear.
- **The dark fade belongs to the text box,** not the photo: `rgba(0,0,0,0) 0%, .5 at 48%, .7 at 100%` with 48px of top padding, plus a soft text shadow. The fade grows with the text, so white names stay readable on bright photos.
- **White text through tokens:** `--loox-lxrw-u-reviewer-name-color`, `--loox-lxrw-u-text-color` and `--loox-lxrw-u-review-verified-badge-color` set to white on the text box, plus `::part(text)` of the verified badge.
- **Reviews without a photo** show the accent background with the same white text, so they look intended.
- **Phone first:** 2 columns at any width, 3 from a 600px widget, 4 from 920px. Columns follow the widget's own width (`@container`), not the screen. 8px gaps on phones.
- **The card box is reset:** `--loox-lxrw-card-gap: 0px` on the grid, and no shadow, border or background on the card, so the tile is the only shape.
- **Hover only with a mouse:** the photo zooms 4% and the text opens to 6 lines, inside `(hover: hover) and (pointer: fine)` and the reduced-motion check. Widgets under 600px wide show 2 lines of text, so phone shoppers read more than a snippet; a tap opens the full review.

## What can change

Accent color (`--lxr-accent`, from the store's design), corner radius (`--lxr-radius`, 8 to 40px), tile shape (`aspect-ratio`: 1, 4/5 or 3/4), columns per width, lines of text (1 to 3 on phones), and the title.
