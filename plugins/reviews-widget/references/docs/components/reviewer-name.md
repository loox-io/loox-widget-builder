# lxrw-reviewer-name

The reviewer's name, shortened for privacy (for example "Dana K.").

Kind: display part. Goes inside: the card template. Optional.

## Example

```html
<template slot="review-card">
  <lxrw-review-media></lxrw-review-media>
  <lxrw-review-rating></lxrw-review-rating>
  <lxrw-review-content></lxrw-review-content>
  <div class="byline">
    <lxrw-reviewer-name></lxrw-reviewer-name>
    <lxrw-review-verified-badge></lxrw-review-verified-badge>
  </div>
</template>
<style>
  .byline { display: flex; align-items: center; gap: 6px; }
</style>
```

## Options

None.

## Style

| Token or hook | Changes | Default |
|---|---|---|
| `--loox-lxrw-u-reviewer-name-color` | Name color | store setting |
| `::part(name)` | The name text: font size, weight | |

## Admin settings that affect it

None. The name shows in its shortened form in every card.

## Can't do

- Show the full name or email.
- Include the verified badge. The badge is its own part, `lxrw-review-verified-badge`, placed next to the name in a row wrapper.
