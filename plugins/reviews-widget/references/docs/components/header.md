# lxrw-header

The top of the widget: the store's average rating, review count, write button and sort menu.

Kind: data part (holds the store's totals, draws nothing). Goes inside: `<loox-reviews-widget>`, before `<lxrw-reviews-list>`.

## Example

```html
<lxrw-header>
  <div class="summary">
    <lxrw-header-rate-average-icons></lxrw-header-rate-average-icons>
    <lxrw-header-reviews-count></lxrw-header-reviews-count>
  </div>
</lxrw-header>
```

## Display parts that go inside it

| Part | Shows | Tokens | Style hooks |
|---|---|---|---|
| `lxrw-header-rate-average-icons` | The store's average as five stars, rounded to half stars. No number. | `--loox-lxrw-u-stars-color` (star color), `--loox-lxrw-u-header-text-color` | `stars` |
| `lxrw-header-reviews-count` | The count as text, for example "128 Reviews". Empty with zero reviews. | `--loox-lxrw-u-header-text-color` | `count` |
| `lxrw-header-write-button` | The button that opens the review form | `--loox-lxrw-u-button-bg`, `--loox-lxrw-u-button-text-color`, `--loox-lxrw-u-button-radius` | `button` (page: header-write-button.md) |
| `lxrw-header-sort-menu` | The sort menu | see its page | components/sort-menu.md |
| `lxrw-header-distribution-list` | One row per star level (5 to 1): stars, a bar, a count. Rows only, no panel around them. A row click filters the reviews by that rating. Shows only when the store's "Show rating distribution" setting is on and the store has reviews | `--loox-lxrw-u-progress-bar-color`, `--loox-lxrw-u-progress-track-color`, `--loox-lxrw-u-stars-color` | `row`, `bar`, `count` |

Header display parts may sit at any depth inside `<lxrw-header>`, inside the merchant's own wrappers.

## Options

None.

## Style

No tokens or style hooks of its own. Layout comes from wrappers inside it.

## Admin settings that affect it

The write button and sort menu follow their store settings. The average stars and count show whenever the store has reviews.

## Loox's ready-made headers

`<lxrw-header><lxrw-header-compact-preset></lxrw-header-compact-preset></lxrw-header>`, or `-minimal-` or `-expanded-`. What each looks like: style.md.

## Can't do

- Work outside `<loox-reviews-widget>`.
