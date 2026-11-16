# lxrw-review-content

The text the customer wrote.

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

| Attribute | Values | Default |
|---|---|---|
| `full-text` | present or absent | absent: long text is cut |

Without `full-text`, text over 500 characters is cut with "...", or over 150 characters when the store replied. The full text shows in the review detail.

## Style

| Token or hook | Changes | Default |
|---|---|---|
| `--loox-lxrw-u-text-color` | Text color | store setting |
| `::part(text)` | The text block: font size, line height, line clamp | |

Shorter cards: `lxrw-review-content::part(text) { display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }`

## Admin settings that affect it

None.

## Empty state

A review with no text shows nothing here and takes no space.

## Can't do

- A "read more" link in the card. The card's click opens the full review.
- Change the 500 and 150 character limits.
