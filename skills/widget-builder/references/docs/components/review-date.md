# lxrw-review-date

The date the review was written, in the shopper's browser format.

Kind: display part. Goes inside: the card template. Optional.

## Example

```html
<template slot="review-card">
  <lxrw-review-media></lxrw-review-media>
  <div class="body">
    <lxrw-review-rating></lxrw-review-rating>
    <lxrw-review-content></lxrw-review-content>
    <lxrw-review-date></lxrw-review-date>
  </div>
</template>
```

## Options

None.

## Style

| Token or hook | Changes | Default |
|---|---|---|
| `--loox-lxrw-u-date-color` | Date color | soft grey |
| `::part(date)` | The date text: font size, spacing | |

## Admin settings that affect it

"Show review date" in Loox admin (on by default). When off, the date shows in no card, and a layout cannot bring it back.

## Empty state

Hidden by the setting, or a review without a usable date: shows nothing, takes no space.

## Can't do

- Relative dates such as "3 days ago".
- Follow the store's language. The format follows the shopper's browser.
