# Style: Photo-first

Shopper photos lead, like a social feed. Strong on phones, where swiping feels natural.

| Part | Photo-first |
|---|---|
| Layout | Sideways-swiping row; cards 4:5 tall, about 80% width on phones so the next photo peeks, 3 to 4 per view on desktop (layouts/carousel.md, lx-snap) |
| Photo | Fills the whole card (`lxrw-review-media::part(media) { aspect-ratio: 4/5 !important; }`), text sits on top of it |
| Text on photo | A fade behind the text box (design-rules.md, rule 6) under white stars, name, verified mark and 1 to 2 lines of text. Complete code: recipes/photo-tiles.md |
| Reviews without photo | Accent-tinted card with larger text instead of the photo; the card keeps the same size |
| Cards | Radius 16 to 24px, no border, no shadow |
| Motion | lx-snap with faded edges; lx-rise on first view |
