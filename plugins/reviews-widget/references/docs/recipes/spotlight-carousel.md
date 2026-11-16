# Recipe: spotlight carousel

Loox's signature look, taken from the Loox Dynamic Carousel: each card pairs a big quote panel with a tall photo, the row scrolls sideways, and the next card peeks in. Tested on a live store at desktop and 390px phone width. Start from this code and change the accent, radius and sizes to fit the request; keep the structure.

Fits requests like: a carousel, a slider, testimonials, quotes, "make it look premium", a picture of a carousel or of quote cards next to photos.

## Code

```html
<loox-reviews-widget>
  <div class="lxr-spot" style="--lxr-accent: rgb(104,117,82); --lxr-radius: 40px;">
    <lxrw-header>
      <div class="lxr-spot__head">
        <lxrw-header-rate-average-icons></lxrw-header-rate-average-icons>
        <lxrw-header-reviews-count></lxrw-header-reviews-count>
      </div>
    </lxrw-header>
    <lxrw-reviews-list>
      <div class="lxr-spot__frame">
        <button type="button" class="lxr-spot__nav lxr-spot__nav--prev" data-dir="-1" aria-label="Previous reviews"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="lxr-spot__track">
          <template slot="review-card">
            <article class="lxr-spot__card">
              <div class="lxr-spot__quote">
                <span class="lxr-spot__mark" aria-hidden="true">&#8220;</span>
                <lxrw-review-rating></lxrw-review-rating>
                <lxrw-review-content></lxrw-review-content>
                <div class="lxr-spot__byline">
                  <lxrw-review-verified-badge></lxrw-review-verified-badge>
                  <lxrw-reviewer-name></lxrw-reviewer-name>
                </div>
              </div>
              <lxrw-review-media></lxrw-review-media>
            </article>
          </template>
        </div>
        <button type="button" class="lxr-spot__nav lxr-spot__nav--next" data-dir="1" aria-label="Next reviews"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      </div>
    </lxrw-reviews-list>
    <lxrw-empty-state></lxrw-empty-state>
  </div>
</loox-reviews-widget>
<style>
  .lxr-spot { --lxr-tint: color-mix(in srgb, var(--lxr-accent) 12%, #fff); }
  .lxr-spot__head { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 16px; }
  .lxr-spot__frame { position: relative; }
  .lxr-spot__track { display: flex; gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none;
    padding: 8px 24px 16px; scroll-padding-inline: 24px; --loox-lxrw-card-gap: 0px; }
  .lxr-spot__track::-webkit-scrollbar { display: none; }
  .lxr-spot__track lxrw-review-card { flex: 0 0 min(760px, 86%); width: auto; margin: 0; scroll-snap-align: start;
    --loox-lxrw-u-card-radius: var(--lxr-radius); --loox-lxrw-u-card-shadow: none; --loox-lxrw-u-review-border: none;
    --loox-lxrw-u-review-background-color: transparent; --loox-lxrw-u-review-background-hover-color: transparent; }
  .lxr-spot__card { display: grid; grid-template-columns: minmax(0, 384px) minmax(0, 1fr); gap: 8px; height: 424px; }
  .lxr-spot__quote { position: relative; display: flex; flex-direction: column; gap: 16px; padding: 56px 40px; border-radius: var(--lxr-radius);
    background: var(--lxr-tint); min-width: 0; }
  .lxr-spot__mark { position: absolute; top: -8px; left: 16px; font: 700 96px/1 Georgia, serif; color: var(--lxr-accent); }
  .lxr-spot__quote lxrw-review-rating::part(stars) { font-size: 24px; }
  .lxr-spot__quote lxrw-review-content { flex: 1; min-height: 0; }
  .lxr-spot__quote lxrw-review-content::part(text) { font-size: 24px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 6; -webkit-box-orient: vertical; overflow: hidden; }
  .lxr-spot__byline { display: flex; align-items: center; gap: 4px; }
  .lxr-spot__byline lxrw-reviewer-name::part(name) { font-size: 18px; }
  .lxr-spot__card > lxrw-review-media { height: 100%; min-height: 0; overflow: hidden; border-radius: var(--lxr-radius); background: color-mix(in srgb, var(--lxr-accent) 25%, #fff); }
  .lxr-spot__card lxrw-review-media::part(media) { height: 100%; aspect-ratio: auto !important; border-radius: 0; }
  .lxr-spot__card lxrw-review-media::part(image) { width: 100%; height: 100%; object-fit: cover; }
  .lxr-spot__nav { position: absolute; top: calc(50% - 20px); z-index: 2; width: 40px; height: 40px; padding: 0; box-sizing: border-box; border: 0; border-radius: 50%;
    display: grid; place-items: center; background: #fff; box-shadow: 0 0 12px rgba(0,0,0,.15); cursor: pointer; color: #222; }
  .lxr-spot__nav--prev { inset-inline-start: 4px; } .lxr-spot__nav--next { inset-inline-end: 4px; }
  .lxr-spot__nav svg:dir(rtl) { transform: scaleX(-1); }
  @container (max-width: 719px) {
    .lxr-spot__nav { display: none; }
    .lxr-spot__track { gap: 8px; padding-inline: 16px; scroll-padding-inline: 16px; }
    .lxr-spot__track lxrw-review-card { flex-basis: 84%; }
    .lxr-spot__card { grid-template-columns: minmax(0, 1fr); grid-template-rows: 280px auto; height: auto; }
    .lxr-spot__card > lxrw-review-media { order: -1; }
    .lxr-spot__quote { padding: 24px 24px 32px; gap: 8px; text-align: center; align-items: center; }
    .lxr-spot__mark { top: auto; bottom: -52px; left: 50%; transform: translateX(-50%); font-size: 64px; }
    .lxr-spot__track { padding-bottom: 32px; }
    .lxr-spot__quote lxrw-review-rating::part(stars) { font-size: 16px; }
    .lxr-spot__quote lxrw-review-content::part(text) { font-size: 20px; -webkit-line-clamp: 3; }
  }
  @media (prefers-reduced-motion: no-preference) {
    .lxr-spot__track { scroll-behavior: smooth; }
    @supports (animation-timeline: view()) {
      @keyframes lxr-spot-focus { 0%, 100% { opacity: .5; transform: scale(.94); } 25%, 75% { opacity: 1; transform: none; } }
      .lxr-spot__track lxrw-review-card { animation: lxr-spot-focus linear both; animation-timeline: view(inline); }
    }
  }
</style>
<script>
  document.querySelectorAll('.lxr-spot__frame:not([data-ready])').forEach(function (f) {
    f.setAttribute('data-ready', '');
    var track = f.querySelector('.lxr-spot__track');
    f.querySelectorAll('.lxr-spot__nav').forEach(function (b) {
      b.addEventListener('click', function () {
        var card = track.querySelector('lxrw-review-card');
        var step = card ? card.getBoundingClientRect().width + 16 : track.clientWidth * 0.8;
        var rtl = getComputedStyle(track).direction === 'rtl' ? -1 : 1;
        track.scrollBy({ left: rtl * Number(b.dataset.dir) * step, behavior: 'smooth' });
      });
    });
  });
</script>
```

## Why each piece is there

- **Quote panel + photo in one card.** Desktop: a 384px quote panel beside the photo, 8px apart, 424px tall. Phone (widget under 720px): the photo on top (280px), the quote panel under it, text centered.
- **The quote is the hero:** store font (no `font-family`), 24px with line height 1.5, max 6 lines; on phones 20px, max 3 lines. Stars 24px (16px on phones). The name sits after the verified mark; no date.
- **One accent color** drives the panel tint (12% of the accent on white), the quote mark and the empty-photo background. Take it from the store's design.
- **Round, flat shapes:** 40px corners on the panel and the photo, no borders, no shadows. Depth comes only from shape and size.
- **The next card peeks in:** cards are 86% of the row (84% on phones), so shoppers see there is more.
- **Arrows only on wide widgets:** 40px white circles with a soft shadow, hidden under 720px, where swipe is the control.
- **Calm motion:** cards outside the center fade to 50% and shrink to 94% while scrolling (scroll-driven, only when the shopper allows motion). One swipe moves one card (`scroll-snap`).
- **The script only scrolls the row** by one card per click and marks each carousel it set up.

## What can change

Accent and tint, corner radius (24 to 40px), card height (360 to 480px on desktop), panel width, quote size (20 to 28px), and whether the header shows. Keep the photo in every card (it is required) and keep the peek on phones.
