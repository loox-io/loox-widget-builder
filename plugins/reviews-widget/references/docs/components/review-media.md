# lxrw-review-media

The review's first photo. For a video review, the video's poster image. A "+N" badge counts the extra photos.

Kind: display part. Goes inside: the card template. Required in every card.

## Example

```html
<template slot="review-card">
  <lxrw-review-media></lxrw-review-media>
  <lxrw-review-rating></lxrw-review-rating>
  <lxrw-review-content></lxrw-review-content>
</template>
```

## Options

`layout`: `single` (default, first photo) or `tiles` (all photos as tiles, no "+N").

## Style

| Token or hook | Changes | Default |
|---|---|---|
| `--loox-lxrw-u-media-radius` | Photo corner radius | store setting |
| `--loox-lxrw-u-badge-bg` | "+N" badge background | store setting |
| `--loox-lxrw-u-badge-text-color` | "+N" badge text | store setting |
| `::part(image)` | The image itself | |
| `::part(media)` | The photo's frame. Set the photo shape here, with `!important` | |
| `::part(badge)` | The "+N" badge | |
| `::part(tile)` | One tile (`layout="tiles"`): set its size | |

Same-shape photos across cards: set the shape on the photo's own box, not only on the frame. `lxrw-review-media { display: block; aspect-ratio: 1; min-height: 0; overflow: hidden; }` with `lxrw-review-media::part(media) { height: 100%; aspect-ratio: auto !important; }` and `lxrw-review-media::part(image) { width: 100%; height: 100%; object-fit: cover; }`. The `!important` is needed because Loox sets each photo's own ratio inline. Don't use `aspect-ratio: 1 !important` on `::part(media)` alone inside a flex card: the card ends up shorter than its content and clips the name (found 10-25). Photo first in the card sits flush with the card's rounded top corners.

Video reviews: the poster image already carries a play icon, so no extra play icon is added. No part tells whether a review is a video.

Text on top of the photo: put the photo and a text box in one grid cell and give the text box `position: relative; z-index: 1`, or the photo paints over it. Complete code: recipes/photo-tiles.md.

## Admin settings that affect it

None.

## Empty state

A review without a photo or video shows nothing here and takes no space. CSS alone cannot detect this (`:empty` and `:has()` have no effect on it), but a script can: on such a card the media part's shadow root has no `img` or `video`, and the card's `review.media` is `[]` (concepts.md, "What a script can read"). Tag those cards with a class and style them on their own, for example as quote cards, or hide the empty frame. This worked on every build that tried it. Without a script, two layouts work either way:
- Photo above the text: a review without a photo simply starts with the stars.
- Photo beside the text in a flex row, photo `flex: 0 0 40%`, text `flex: 1 1 0; min-width: 0`. A review without a photo keeps an empty column on that side.

## Can't do

- Play video in the card. The video plays in the review detail.
- Its own click. The card's click opens the review.
