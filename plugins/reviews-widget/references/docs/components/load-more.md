# lxrw-load-more

A "Show more reviews" button that adds the next page of reviews to the list.

Kind: display part. Goes inside: `<loox-reviews-widget>`, after `<lxrw-reviews-list>`.

## Style

| Token or hook | Changes |
|---|---|
| `--loox-lxrw-u-button-bg`, `--loox-lxrw-u-button-text-color`, `--loox-lxrw-u-button-radius` | The button |
| `::part(button)` | The button: size, border, font |

Style `::part(button)`, not the element: the element's box is full width. The button turns grey on hover unless `::part(button):hover` sets a look.

## Empty state

Draws nothing when there's no next page.
