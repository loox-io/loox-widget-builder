# lxrw-review-verified-badge

The verified-purchase mark: a small check and, when the store shows it, the word "Verified". Loox shows it on every card next to the name, and every card example in these docs includes it.

Kind: display part. Goes inside: the card template, right after `lxrw-reviewer-name` in a row. Optional. Loox shows it next to the name on every card, and every example here includes it.

## Example

```html
<div class="byline">
  <lxrw-reviewer-name></lxrw-reviewer-name>
  <lxrw-review-verified-badge></lxrw-review-verified-badge>
</div>
<style>
  .byline { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
</style>
```

The Loox Dynamic Carousel places the check before the name instead. Either order works.

## When it shows

Only on verified reviews, and only when the store has not turned verification off in Loox admin. On other reviews it shows nothing and takes no space, so a layout needs no room set aside for it. Some stores show an "Unverified" note instead, through the same `text` hook.

## Style

| Token or hook | Changes |
|---|---|
| `--loox-lxrw-u-review-verified-badge-color` | The check mark color only |
| `::part(badge)` | The check mark box |
| `::part(text)` | The "Verified" word (color, size) |
| default slot | Replaces the check glyph, for example with an inline SVG |

On a dark background or a photo, set both: `--loox-lxrw-u-review-verified-badge-color: #fff;` and `lxrw-review-verified-badge::part(text) { color: #fff; }`.

On the default widget the hooks are `lxrw-review-card-grid-preset::part(verified-badge)` and `::part(verified-text)` (`lxrw-review-card-list-preset` on a List or Mosaic store).

## Can't do

- Show the mark on a review that is not verified.
- Make it clickable.
