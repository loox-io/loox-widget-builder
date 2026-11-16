# Design rules: the Loox look

Taken from Loox's own widgets (Dynamic Carousel, Video Slider, review form), and tested on a live store. The store's colors and fonts still apply. The class names below are short for reading; in a real widget they carry the widget's own prefix (build.md, "Class names"). `.lx`, `.cards`, `.track`, `.quote` and `.stars` are the merchant's own wrappers; `.quote` wraps `lxrw-review-content` and `.stars` wraps `lxrw-review-rating`.

## The Loox look

Two families, both from Loox's own code. A request names or shows one; otherwise a grid uses the grid values and a carousel uses the featured values. Complete tested code: recipes/spotlight-carousel.md and recipes/photo-tiles.md. Phone rules: phone.md.

| | Grid (Loox default widget) | Featured (Dynamic Carousel, photo tiles) |
|---|---|---|
| Corners | 8px cards (`--loox-lxrw-u-card-radius`, store setting) | 16px tiles, 40px featured panels and photos |
| Gaps | 14px | 8px between photos, 16px between panels |
| Text | 14px, line height 20px; names 14px bold; date 11px grey | Quote 24px, line height 1.5, 6 lines (phone: 20px, 3 lines); tile text 13 to 14px, 1 to 2 lines |
| Shadow | `0 0 3px rgba(0,0,0,.2)` | none |
| Photos | Masonry, each photo keeps its shape | Fixed shape, cover crop, edge to edge |
| Columns | 2 from a 320px widget, more as it grows | Carousel: 86% card with the next one peeking |

1. **One accent color.** The store's brand color drives the panel tint (8 to 12% on white), the quote mark, the active dot and the background of reviews without a photo. Stars keep their own color (`--loox-lxrw-u-stars-color`, Loox default orange #FF8D00).
2. **The store's font.** Review text inherits the store font when no `font-family` is set on it.
3. **A 4px spacing grid:** 4, 8, 12, 16, 24, 32. Featured text panels: 56px by 40px padding (24px on phones).
4. **An oversized quote mark** in the accent color, about 54 by 38px, overlapping the panel's top-left corner.
5. **The verified mark next to every name** (components/review-verified-badge.md).
6. **Text on photos: the fade sits on the text box,** not the photo: `linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.5) 48%, rgba(0,0,0,.7) 100%)`, 48px top padding, white text with `text-shadow: 0 1px 2px rgba(0,0,0,.5)`. The text box needs `position: relative; z-index: 1`, or the photo paints over it.
7. **Flat depth.** Featured pieces have no border and no shadow. Depth comes from corners, the fade and size.
8. **Navigation:** 32 to 40px white circles, `box-shadow: 0 0 12px rgba(0,0,0,.15)`, half outside the row edge, hidden under a 720px widget.
9. **Pill pagination** (optional): 5 to 8px dots, 8px apart; the active one a 24 by 8px accent pill.
10. **Alignment:** start-aligned on desktop, centered on phones.

## Right-to-left stores

Hebrew and Arabic stores get the widget right-to-left: it sets its own `dir` from the store language. Don't set `dir` on it, because yours wins. Write your CSS with logical properties (`margin-inline-start`, `inset-inline-end`, `text-align: start`), never `left` or `right`, so it flips with the widget. A script that scrolls a row multiplies its step by -1 when `getComputedStyle(row).direction === 'rtl'`. Loox's own header keeps the stars on the left. Multilingual stores keep the old widget.

## Motion

Loox motion is quiet: 200ms for hover and fades, 500ms for slides (one swipe moves one card), `cubic-bezier(.16,1,.3,1)` for entrances, `cubic-bezier(.22,1,.36,1)` for star pops, 300ms `cubic-bezier(.4,0,.2,1)` for sheets sliding up, 200ms for dropdowns. Text fades to 40% while a carousel moves. Every hover effect sits inside `@media (hover: hover) and (pointer: fine)`. Loox's own carousel doesn't autoplay, but a custom widget may move on its own when the person asks for it. Whatever moves gets the four shopper basics in known-limits.md (stops on touch, calm version, drag never opens a review, no gaps with few reviews). Each snippet runs only when the shopper allows motion.

**lx-rise: card entrance with stagger**
```css
@media (prefers-reduced-motion: no-preference) {
  @keyframes lx-rise { from { opacity: 0; transform: translateY(12px) scale(.98); } }
  .cards lxrw-review-card { animation: lx-rise 500ms cubic-bezier(.16,1,.3,1) both; }
  /* Each card sits in its own lxrw-review-card-provider, so count the providers, not the cards. */
  .cards lxrw-review-card-provider:nth-of-type(2) > lxrw-review-card { animation-delay: 60ms; }
  .cards lxrw-review-card-provider:nth-of-type(3) > lxrw-review-card { animation-delay: 120ms; }
  .cards lxrw-review-card-provider:nth-of-type(4) > lxrw-review-card { animation-delay: 180ms; }
  .cards lxrw-review-card-provider:nth-of-type(n+5) > lxrw-review-card { animation-delay: 240ms; }
}
```

**lx-lift: hover lift and photo zoom**
```css
.cards lxrw-review-media::part(media) { overflow: hidden; }
@media (prefers-reduced-motion: no-preference) and (hover: hover) and (pointer: fine) {
  .cards lxrw-review-card { transition: transform 200ms ease-in-out; }
  .cards lxrw-review-media::part(image) { transition: transform 300ms ease-in-out; }
  .cards lxrw-review-card:hover { transform: translateY(-4px); }
  .cards lxrw-review-card:hover lxrw-review-media::part(image) { transform: scale(1.04); }
}
```

**lx-star-pop: star pop and shine on hover**
```css
.stars { position: relative; display: inline-block; overflow: hidden; }
@media (prefers-reduced-motion: no-preference) {
  @keyframes lx-star-pop { 40% { transform: scale(.7); } 60% { transform: scale(1.2); } 80% { transform: scale(.9); } }
  @keyframes lx-shine { to { transform: translateX(100%); } }
  .stars::after { content: ""; position: absolute; inset: 0; transform: translateX(-100%);
    background: linear-gradient(100deg, transparent 30%, rgba(255,255,255,.7) 50%, transparent 70%); }
}
@media (prefers-reduced-motion: no-preference) and (hover: hover) and (pointer: fine) {
  .cards lxrw-review-card:hover .stars { animation: lx-star-pop 600ms cubic-bezier(.22,1,.36,1); }
  .cards lxrw-review-card:hover .stars::after { animation: lx-shine 900ms ease-out; }
}
```

**lx-snap: carousel snap with faded edges and a focused center**
```css
.track { display: flex; gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none;
  padding-inline: 24px; scroll-padding-inline: 24px;
  mask-image: linear-gradient(90deg, transparent, #000 24px, #000 calc(100% - 24px), transparent); }
.track lxrw-review-card { flex: 0 0 min(86%, 340px); margin: 0; scroll-snap-align: start; }
@media (prefers-reduced-motion: no-preference) {
  .track { scroll-behavior: smooth; }
  @supports (animation-timeline: view()) {
    @keyframes lx-focus { 0%, 100% { opacity: .45; transform: scale(.94); } 30%, 70% { opacity: 1; transform: none; } }
    .track lxrw-review-card { animation: lx-focus linear both; animation-timeline: view(inline); }
  }
}
```

**lx-quote: quote-mark accent**
```css
.quote { position: relative; padding-top: 32px; }
.quote::before { content: "\201C"; position: absolute; top: -16px; left: -8px;
  font: 700 80px/1 Georgia, serif; color: var(--accent); }
@media (prefers-reduced-motion: no-preference) {
  @keyframes lx-quote-in { from { opacity: 0; transform: translateY(8px) scale(.8); } }
  .quote::before { animation: lx-quote-in 500ms cubic-bezier(.16,1,.3,1) 200ms both; }
}
```

## What makes it look premium

- One accent color, one radius, one photo shape across the widget.
- Large review text with space around it.
- Photos edge to edge, no inner border.
- A tinted surface and light or no shadows.
- The next card peeking in on mobile.
- Motion the person asked for. With no request: hover, entrance and scroll only.
- A card with no photo, a one-line review and a very long review all look intended.
