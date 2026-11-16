# Recipe: collage

A dark panel with a sideways-scrolling, staggered collage: photo tiles with stars and name, and cream quote cards mixed in between them. Tested on a live store at desktop and 390px phone width. Start from this code and change the colors, radius, title and sizes to fit the request; keep the structure.

Fits requests like: a collage, a staggered or masonry wall that scrolls, photo cards mixed with quote cards, a dark section, a picture of tall photo cards in offset columns with a text card among them.

## Code

```html
<loox-reviews-widget>
  <div class="lxr-col" style="--lxr-dark: rgb(47,58,45); --lxr-cream: rgb(240,234,220); --lxr-on-dark: rgb(240,234,220); --lxr-radius: 20px;">
    <h2 class="lxr-col__title">Loved by our customers</h2>
    <lxrw-reviews-list>
      <div class="lxr-col__track">
        <template slot="review-card">
          <article class="lxr-col__tile">
            <lxrw-review-media></lxrw-review-media>
            <div class="lxr-col__over">
              <lxrw-review-rating></lxrw-review-rating>
              <lxrw-review-content></lxrw-review-content>
              <div class="lxr-col__byline">
                <lxrw-review-verified-badge></lxrw-review-verified-badge>
                <lxrw-reviewer-name></lxrw-reviewer-name>
              </div>
            </div>
          </article>
        </template>
      </div>
    </lxrw-reviews-list>
    <lxrw-empty-state></lxrw-empty-state>
  </div>
</loox-reviews-widget>
<style>
  .lxr-col { background: var(--lxr-dark); color: var(--lxr-on-dark); border-radius: 24px; padding: 32px 0 8px; overflow: hidden; }
  .lxr-col__title { margin: 0 16px 24px; text-align: center; color: var(--lxr-on-dark); font-size: 28px; line-height: 1.2; }
  .lxr-col__track { display: grid; grid-auto-flow: column; grid-template-rows: repeat(2, 220px); grid-auto-columns: 168px; gap: 10px;
    overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; padding: 0 16px 48px; scroll-padding-inline: 16px; --loox-lxrw-card-gap: 0px; }
  .lxr-col__track::-webkit-scrollbar { display: none; }
  @container (min-width: 720px) { .lxr-col__track { grid-template-rows: repeat(2, 280px); grid-auto-columns: 210px; gap: 12px; padding-inline: 24px; } }
  .lxr-col__track lxrw-review-card { width: auto; margin: 0; height: 100%; scroll-snap-align: start;
    --loox-lxrw-u-card-radius: var(--lxr-radius); --loox-lxrw-u-card-shadow: none; --loox-lxrw-u-review-border: none;
    --loox-lxrw-u-review-background-color: transparent; --loox-lxrw-u-review-background-hover-color: transparent; }
  /* Stagger: every second column sits 40px lower. Each card sits in its own lxrw-review-card-provider, so counting is done on those. Cards fill columns top then bottom: cards 3 and 4 of every 4 form the lower column. */
  .lxr-col__track lxrw-review-card-provider:nth-of-type(4n+3) lxrw-review-card, .lxr-col__track lxrw-review-card-provider:nth-of-type(4n+4) lxrw-review-card { transform: translateY(40px); }
  .lxr-col__tile { display: grid; grid-template: minmax(0, 1fr) / minmax(0, 1fr); height: 100%; overflow: hidden; border-radius: var(--lxr-radius);
    background: color-mix(in srgb, var(--lxr-cream) 25%, var(--lxr-dark)); }
  .lxr-col__tile > lxrw-review-media, .lxr-col__tile > .lxr-col__over { grid-area: 1 / 1; min-width: 0; }
  .lxr-col__tile > lxrw-review-media { height: 100%; min-height: 0; overflow: hidden; }
  .lxr-col__tile lxrw-review-media::part(media) { height: 100%; aspect-ratio: auto !important; border-radius: 0; }
  .lxr-col__tile lxrw-review-media::part(image) { width: 100%; height: 100%; object-fit: cover; }
  /* Photo tiles: stars and name over a fade, no text. */
  .lxr-col__over { position: relative; z-index: 1; align-self: end; display: flex; flex-direction: column; gap: 4px; padding: 40px 10px 10px;
    background: linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,.5) 48%, rgba(0,0,0,.7)); text-shadow: 0 1px 2px rgba(0,0,0,.5);
    --loox-lxrw-u-reviewer-name-color: #fff; --loox-lxrw-u-review-verified-badge-color: #fff; }
  .lxr-col__over lxrw-review-content { display: none; }
  .lxr-col__byline { display: flex; align-items: center; gap: 4px; }
  .lxr-col__over lxrw-reviewer-name::part(name) { font-size: 13px; font-weight: 600; }
  .lxr-col__over lxrw-review-verified-badge::part(text) { display: none; }
  /* Quote cards: every third card hides its photo and shows the text on cream. */
  .lxr-col__track lxrw-review-card-provider:nth-of-type(3n+2) lxrw-review-media { display: none; }
  .lxr-col__track lxrw-review-card-provider:nth-of-type(3n+2) .lxr-col__tile { background: var(--lxr-cream); }
  .lxr-col__track lxrw-review-card-provider:nth-of-type(3n+2) .lxr-col__over { align-self: stretch; justify-content: center; align-items: center; text-align: center;
    gap: 10px; padding: 16px 14px; background: none; text-shadow: none; color: var(--lxr-dark);
    --loox-lxrw-u-reviewer-name-color: var(--lxr-dark); --loox-lxrw-u-text-color: var(--lxr-dark); --loox-lxrw-u-review-verified-badge-color: rgb(194,120,100); }
  .lxr-col__track lxrw-review-card-provider:nth-of-type(3n+2) lxrw-review-content { display: block; }
  .lxr-col__track lxrw-review-card-provider:nth-of-type(3n+2) lxrw-review-content::part(text) { font-size: 15px; line-height: 1.45;
    display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }
  .lxr-col__track lxrw-review-card-provider:nth-of-type(3n+2) > lxrw-review-card { --loox-lxrw-u-stars-color: var(--lxr-dark); }
  .lxr-col__track lxrw-review-card-provider:nth-of-type(3n+2) lxrw-review-rating::part(stars) { font-size: 18px; }
  .lxr-col__track lxrw-review-card-provider:nth-of-type(3n+2) lxrw-reviewer-name::part(name) { font-size: 14px; font-weight: 400; }
  @media (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference) {
    .lxr-col__tile lxrw-review-media::part(image) { transition: transform 300ms ease-in-out; }
    .lxr-col__track lxrw-review-card:hover lxrw-review-media::part(image) { transform: scale(1.04); }
  }
</style>
```

## Why each piece is there

- **Two rows that fill column by column** (`grid-auto-flow: column; grid-template-rows: repeat(2, 220px)`), scrolling sideways with `scroll-snap`. Column width 168px on phones, so a third column peeks in; 210px from a 720px widget.
- **Each card sits in its own `lxrw-review-card-provider`.** Counting cards ("every second column", "every third card") is done on that wrapper: `lxrw-review-card-provider:nth-of-type(…) lxrw-review-card`. A selector like `lxrw-review-card:nth-of-type(3n)` matches nothing.
- **Stagger:** cards 3 and 4 of every 4 form the lower column and move down 40px.
- **Quote cards:** every third card hides its photo and shows the stars, up to 5 lines of text, the verified mark and the name, centered on cream. The photo part stays in the template (every card keeps photo, stars and text); it is only hidden on those cards.
- **Photo tiles** show stars, the verified mark and the name over a fade on the text box; the text is hidden there and a tap opens the full review.
- **Colors** come from the store: a dark brand color for the panel, a light cream for quote cards and text on the panel.
- **The text box sits above the photo** (`position: relative; z-index: 1`).

## What can change

Panel and cream colors, radius (12 to 24px), row height (180 to 300px), column width, which cards become quote cards (`3n+2`, `4n+2`…), the stagger offset (0 to 60px) and the title.
