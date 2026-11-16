# Widget 2.0: known limits and build checklist

Facts the docs don't say yet, learned from the first builds. Read this next to `index.md` before proposing anything. When a request needs something on this list,
say so in the proposal, before building.

## Data the widget can't reach

- **Review Stories and AI summary data** (key metric, "85% praised...", testimonials): no part shows it. Never write a
  number, a percentage or a quote from a picture into the code. A stat tile with made-up text goes on a real store and
  reads as a claim about the merchant's product.
- **Category scores, review search**: no part exists.
- **The average as a number** ("4.6"): `lxrw-rating-average-text` with `rating` and `count` set; style it with `::part(value)`.
- **Smart filters and topic chips**: no part shows them yet. A store with smart filters on may not have Widget 2.0.
- **Product variant, video autoplay**: not covered by the docs. If the request asks for one, check the
  component pages. If no page covers it, it goes in the "left out" list. Never drop it in silence.

## Behaviour Loox owns

- **A card tap always opens the Loox review popup.** Nothing inside a card can be clicked: no "Show more" link to your
  own page, no buy button. A "Show more" label is decoration only, so leave it out.
- **A page holds 1 to 50 reviews** (`reviews-limit`). A value outside that range, like 64, is thrown away in silence and
  the store's reviews-per-page setting applies (20 by default). A product with 64 reviews shows one page until load more runs. A filter that hides cards (no photo, for example) can leave a first page nearly empty: say so, and
  keep `lxrw-load-more` visible, or load at most 3 pages from a script (concepts.md, "Pages"). Never filter by
  rating: that's undecided (concepts.md).
- **Loox draws each review once.** The same card can't show twice, so a loop can't repeat the same cards side by
  side. A loop that looks endless still works: a script moves the card that leaves one edge to the other end
  (wrap-around), or the row glides back to the start. Both were built and kept. Say which one you'll build.

## Motion

Motion is the person's call. There's no ready-made list of motions: the person says what moves, how it feels and how
fast, and you ask when you're unsure. Autoplay, drifting rows and loops are all allowed when they ask for them.

- A moving row needs **one shared clock for the whole row**, not one animation per card, or the cards drift apart.
- Choose start positions on purpose (staggered rows start at different offsets).

### Shopper basics: always, without asking

Anything that moves on its own, or that the shopper can drag, gets all four. Don't ask about them and don't skip them.

1. **Stops when touched or hovered.** Motion pauses on `pointerenter` and `pointerdown`, and starts again after
   `pointerleave`, or a few seconds after the finger lifts. Also pause while the widget is off screen.
2. **A calm version for shoppers who turn motion off.** Inside `@media (prefers-reduced-motion: reduce)` (or
   `matchMedia` in a script) nothing moves on its own: the row stays still and scrolls by hand, fades replace slides.
3. **A swipe or drag never opens a review.** A card tap opens the Loox popup, so a drag that ends on a card opens it
   too. Catch the click on the container in the capture phase and cancel it if the pointer moved more than about
   6px since `pointerdown`. A plain tap, or Enter on a card from the keyboard, still opens the review (worked on real builds):
   ```js
   let x0 = 0, y0 = 0, moved = false;
   box.addEventListener('pointerdown', e => { x0 = e.clientX; y0 = e.clientY; moved = false; });
   box.addEventListener('pointermove', e => { if (Math.hypot(e.clientX - x0, e.clientY - y0) > 6) moved = true; });
   box.addEventListener('click', e => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
   ```
4. **No gaps with few reviews.** Count the cards after they draw: `lxrw-cards-changed` fires on `lxrw-reviews-list` and bubbles up, so listen on
   the widget or a wrapper around the list, not inside it. If they don't
   fill the row twice over, don't run the loop: show them still, centered. Never stretch 3 cards into a loop with
   empty space between them.

### Hover
- **Hover effects stay inside the card's box.** Loox clips the card, so a lift (`translateY`), a shadow that grows or
  a scale that passes the edge gets cut off. The docs' `lx-lift` hover clips in cards that fill their box: use a photo
  zoom inside the frame or a color change instead.
- CSS only where possible.

## Parts with traps

- **Sort button**: it can be icon-only. Give it a fixed size, about 44px.
- **Local page fonts**: it has no theme fonts. Give each font variable a fallback font.
- **Reviewer name size**: the name sets its own 14px size and 20px line height, so `font-size` on a wrapper doesn't
  reach it. Use `lxrw-reviewer-name::part(name)` with `font-size` and `line-height`. A hover scale on the name also
  needs `display: inline-block`. Hover selectors start from the card: `lxrw-review-card:hover lxrw-reviewer-name::part(name)`.
- **No reviews**: design it in the store's look: a soft box in the card color, one line in the heading font
  ("No reviews yet"), and Loox's `lxrw-empty-state` inside it for the "be the first" link. Show it from the review
  count in Liquid, never from CSS like `:has(lxrw-review-card)`: the card template counts as a card, so it never shows.
- **No photo**: CSS alone (`:empty`, `:has()`) can't hide an empty photo frame, but a script can, and it worked on
  every build that tried it. A script can tell: the card's `review.media` is `[]` and the media
  part's shadow root has no `img` (concepts.md, "What a script can read"). Tag such cards with a class and style
  them as quote cards (worked 10-21).

- **Bento and mixed tile sizes**: Loox wraps each card in `lxrw-review-card-provider`, which has `display: contents`,
  so it takes no part in the grid. Count with the wrapper, size with the card:
  `lxrw-review-card-provider:nth-of-type(7n+1) > lxrw-review-card { grid-column: span 2; grid-row: span 2; }`.
  A span set on the wrapper itself does nothing (found in testing, 10-21).

## Checklist before showing a widget

Every item is checked on the screenshots, not assumed.

1. Store colors and fonts, unless the person chose the picture's colors.
2. No empty photo circles or frames.
3. The same spacing between all items.
4. Motion moves the way the person asked, with a staggered start if rows move, and has the four shopper basics.
5. No extra controls nobody asked for (Load more, arrows, dots).
6. Hover stays inside the card.
7. Phone (390px): 2 per row in a grid, the next card peeking in a carousel, no text cut off or overflowing.
8. Every card shows photo, stars and text, and the verified mark and the incentivized and rewarded labels sit next to the name.
9. Nothing made up: no numbers, quotes or names that don't come from the widget's own data.
10. One `widget-id` per widget, unchanged since the first round.
11. Every text reads clearly against what is behind it, in every state: names, stars, text, labels, buttons. Text on a photo needs a dark fade behind it.
12. Clean code before handover: no unused CSS rules, comments, repeated tokens or `!important` you don't need. Shorter code installs more reliably.

## Widget bugs we know about

- **The header's average stars can be invisible** (`lxrw-header-rate-average-icons`). The header copies the star
  shapes from the page when it first draws. In a Custom Liquid widget the page doesn't have them yet at that moment,
  and the header never looks again, so the stars take up space but show nothing. The card stars draw later and work.
  Until it's fixed, say so in the hand-over instead of hiding the header.
- **A small widget leaves a big gap.** While it has reviews, the widget keeps about 335px of height (315px on
  phones) so the page doesn't jump while it loads. For a small button or badge, hold the root's height yourself:
  `loox-reviews-widget:has(.your-wrapper) { height: 44px; pointer-events: none; }` and `pointer-events: auto` on
  your wrapper (found 10-21).
- **A fixed-width popup runs off a narrow column.** Use `width: min(520px, 100%)` on the panel, inside a wrapper as
  wide as the column.
