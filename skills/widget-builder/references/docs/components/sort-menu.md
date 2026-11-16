# lxrw-header-sort-menu

The sort button and its dropdown of sort options. Clicking an option re-sorts the reviews.

Kind: display part. Goes inside: `<lxrw-header>`.

## Style

| Token or hook | Changes |
|---|---|
| `--loox-lxrw-u-dropdown-bg` | Dropdown background |
| `::part(menu)` | The whole control |
| `::part(trigger)` | The button. Its icon is the store's sort icon setting |
| `::part(dropdown)` | The open list |
| `::part(option)`, `::part(option-selected)` | One option, and the current one |

## Admin settings that affect it

"Show sorting options" off, or a product with no reviews: the button stays, and its dropdown holds only the Loox mark. With "Hide Loox branding" on too, no sort menu. The starting order is the store's "Default sorting".

## Can't do

- Change the option names or their order. They come from Loox, in the store's language.
