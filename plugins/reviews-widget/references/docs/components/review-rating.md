# lxrw-review-rating

The review's star rating as five icons, filled to match the rating.

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

None.

## Style

| Token or hook | Changes | Default |
|---|---|---|
| `--loox-lxrw-u-stars-color` | Star fill color | store's stars color |
| `::part(stars)` | The row of icons: gap, size | |

## Admin settings that affect it

The icon shape (star, round star, hearts, custom icon) is the store's "rating icon" setting. Layouts cannot change the shape.

## Can't do

- Show the rating as a number.
- Half stars on a single review.
- Show in the header. The store's average is `lxrw-header-rate-average-icons`.
