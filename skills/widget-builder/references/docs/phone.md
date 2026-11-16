# Phone rules

Most shoppers see the widget on a phone. These rules come from Loox's own widgets. A widget that breaks one of them fails on phones.

1. **Measure the widget, not the screen.** The widget is a size container. Use `@container (min-width: …)` or `@container (max-width: …)` on its width, not `@media` on the screen width. Loox steps: 320, 420, 480, 600, 720, 920px.
2. **Two reviews per row on phones.** Loox grids show 2 columns from a 320px-wide widget: `grid-template-columns: repeat(2, minmax(0, 1fr))`, gap 8px. Formulas like `repeat(auto-fill, minmax(240px, 1fr))` give one full-width card per row on every phone.
3. **Cap photo height.** Tiles get a fixed shape (`aspect-ratio: 1`, `4/5` or `3/4`), so a photo in a half-width column is about 160 to 220px tall.
4. **Carousels show the next card.** Cards are 80 to 86% of the row on phones. Arrows are hidden under 720px; swipe is the control.
5. **Smaller, shorter text.** Featured quotes go from 24px to 20px and from 6 lines to 3. Tile text: 1 to 2 lines, 13 to 14px. Names 14px, bold.
6. **Touch targets are at least 44px.** Loox buttons are 48px tall.
7. **Hover only with a mouse.** Every hover effect sits inside `@media (hover: hover) and (pointer: fine)`. Touch screens get no hover state; a tap opens the review.
8. **Text on photos keeps its fade.** The dark fade sits behind the text box (recipes/photo-tiles.md), so it grows with the text instead of covering a fixed part of the photo.
9. **Center on phones.** Quote panels and headers center their text under 720px; desktop aligns to the start.
10. **Check at 390px.** Before answering, the widget is checked at 390px wide: at least 2 reviews visible per screen in a grid, the next card visible in a carousel, no sideways page scroll.
