# lxrw-review-incentivized-badge, lxrw-review-rewarded-badge

The two incentive labels. Required on every card, next to the name: they tell shoppers a review was rewarded.

- `lxrw-review-incentivized-badge` shows **"Rewarded"** with a coupon icon, on a review that got a discount or a manual reward.
- `lxrw-review-rewarded-badge` shows **"Incentivized"** with a gift icon, on a review from Loox Reviewers.

Kind: display parts. Goes inside: the card template, next to the name.

The names and the labels don't match: that's Loox's naming. Both show a tooltip on hover or tap.

## Style

| Token or hook | Changes |
|---|---|
| `--loox-lxrw-u-review-incentivized-badge-bg`, `--loox-lxrw-u-review-incentivized-badge-text-color` | Both labels |
| `::part(badge)`, `::part(label)`, `::part(tooltip)` | The pill, its text, the tooltip |

## Admin settings that affect it

Each has its own store setting. Off or missing: that label draws nothing.
