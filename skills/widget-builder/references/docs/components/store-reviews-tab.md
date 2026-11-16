# lxrw-store-reviews-tab

Two tabs above the reviews: this product's reviews and the store's reviews, each with its count. A click switches the list.

Kind: control. Goes inside: `<loox-reviews-widget>`, above `<lxrw-reviews-list>`, outside the card template. Optional.

## Example

```html
<loox-reviews-widget>
  <div class="lxr-x">
    <lxrw-store-reviews-tab></lxrw-store-reviews-tab>
    <lxrw-reviews-list>…</lxrw-reviews-list>
  </div>
</loox-reviews-widget>
```

## When it shows

Only when the store has store reviews turned on in Loox (block setting "Reviews to display" and the store reviews tab). Otherwise it shows nothing and takes no space, so a layout needs no room set aside for it. Tested: on a store with store reviews off it renders nothing and the list shows the product's reviews.

## Style

| Token or hook | Changes |
|---|---|
| `--loox-lxrw-u-tab-text-color` | Tab text |
| `--loox-lxrw-u-tab-active-bg`, `--loox-lxrw-u-tab-hover-bg` | Active and hover tab background |
| `--loox-lxrw-u-tab-count-bg` | Count bubble |
| `::part(tab)`, `::part(tab-active)`, `::part(count)` | The tabs, the active tab, the count |

## Can't do

- Show both sets in one list with labels (use "Reviews to display: both" for a combined list without tabs).
- Rename the tabs (the labels follow the store's language).
