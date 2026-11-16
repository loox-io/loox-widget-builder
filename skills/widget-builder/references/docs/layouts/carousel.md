# Carousel layout

A row of review cards that scrolls sideways, with previous and next buttons. For the Loox signature look (quote panel beside a tall photo), start from recipes/spotlight-carousel.md instead; this page is the plain version.

Uses: `lxrw-reviews-list` with a scrolling container. Cards hold the three required parts: photo, stars, text.

## Example

```html
<loox-reviews-widget>
  <lxrw-header>
    <div class="lxr-car__summary">
      <lxrw-header-rate-average-icons></lxrw-header-rate-average-icons>
      <lxrw-header-reviews-count></lxrw-header-reviews-count>
    </div>
  </lxrw-header>
  <lxrw-reviews-list>
    <div class="lxr-car">
      <button type="button" class="lxr-car__nav" data-dir="-1" aria-label="Previous reviews">&#8249;</button>
      <div class="lxr-car__track">
        <template slot="review-card">
          <article class="lxr-car__card">
            <lxrw-review-media></lxrw-review-media>
            <div class="lxr-car__body">
              <lxrw-review-rating></lxrw-review-rating>
              <lxrw-review-content></lxrw-review-content>
              <div class="lxr-car__byline">
                <lxrw-reviewer-name></lxrw-reviewer-name>
                <lxrw-review-verified-badge></lxrw-review-verified-badge>
              </div>
            </div>
          </article>
        </template>
      </div>
      <button type="button" class="lxr-car__nav" data-dir="1" aria-label="Next reviews">&#8250;</button>
    </div>
  </lxrw-reviews-list>
</loox-reviews-widget>
<style>
  .lxr-car__summary { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
  .lxr-car { display: flex; align-items: center; gap: 8px; }
  .lxr-car__track { flex: 1; min-width: 0; display: flex; gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
  .lxr-car__track lxrw-review-card { flex: 0 0 260px; width: 260px; margin: 0; scroll-snap-align: start; }
  @container (max-width: 719px) { .lxr-car__nav { display: none; } .lxr-car__track lxrw-review-card { flex-basis: 80%; width: auto; } }
  .lxr-car__card { display: flex; flex-direction: column; height: 100%; }
  .lxr-car__card lxrw-review-media::part(media) { aspect-ratio: 1 !important; }
  .lxr-car__card .lxr-car__body { display: flex; flex-direction: column; gap: 8px; padding: 12px; flex: 1; }
  .lxr-car__card lxrw-review-content::part(text) { display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
  .lxr-car__byline { margin-top: auto; display: flex; align-items: center; gap: 4px; }
  .lxr-car__nav { flex: none; width: 36px; height: 36px; border: 1px solid #d0d0d0; border-radius: 50%; background: #fff; font-size: 20px; cursor: pointer; }
</style>
<script>
  document.querySelectorAll('.lxr-car:not([data-ready])').forEach(function (c) {
    c.setAttribute('data-ready', '');
    var track = c.querySelector('.lxr-car__track');
    c.querySelectorAll('.lxr-car__nav').forEach(function (b) {
      b.addEventListener('click', function () {
        var rtl = getComputedStyle(track).direction === 'rtl' ? -1 : 1;
        track.scrollBy({ left: rtl * Number(b.dataset.dir) * track.clientWidth * 0.8, behavior: 'smooth' });
      });
    });
  });
</script>
```

## How it works

- The scrolling container (`.lxr-car__track`) holds the card template, so Loox puts the cards there.
- The buttons sit outside the template, inside `lxrw-reviews-list`. Inside a card they would be a button inside a button.
- Card width is set on `lxrw-review-card` (the Loox box), not on `.lxr-car__card`.
- Square photos keep the cards the same height. Set the shape as in components/review-media.md: the frame rule alone clips the names in a flex card.
- The script only scrolls the row, and marks each carousel it set up (`data-ready`) so two carousels on one page do not bind twice. A script can read each card's review data (concepts.md, "What a script can read") but cannot change it.

## What can vary

- Card width (`flex: 0 0 260px`), gap, button look and position.
- Which optional parts each card shows (name, date).
- Stars color and card look through tokens (style.md).

## Can't do

- Auto-play that loads more reviews. The row holds the reviews of the current page (up to the block's review limit).
- Showing the same review twice. A loop that looks endless still works: move the card that leaves one edge to the other end, or glide back to the start (known-limits.md, "Loox draws each review once").
