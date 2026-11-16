# Review card

One review: written once as a template, copied by Loox for every review, and wrapped in a clickable box.

Kind: template + Loox box. Goes inside: a container inside `<lxrw-reviews-list>`.

## Example

```html
<lxrw-reviews-list>
  <div class="cards">
    <template slot="review-card">
      <article class="card">
        <lxrw-review-media></lxrw-review-media>
        <div class="body">
          <lxrw-review-rating></lxrw-review-rating>
          <lxrw-review-content></lxrw-review-content>
          <div class="byline">
            <lxrw-reviewer-name></lxrw-reviewer-name>
            <lxrw-review-verified-badge></lxrw-review-verified-badge>
          </div>
        </div>
      </article>
    </template>
  </div>
</lxrw-reviews-list>
```

## What every card shows

| Part | Required | Shows |
|---|---|---|
| `lxrw-review-media` | yes | First photo, or a video's poster. Empty without a photo. |
| `lxrw-review-rating` | yes | The review's stars |
| `lxrw-review-content` | yes | The review text |
| `lxrw-reviewer-name` | no | Short name, for example "Dana K." |
| `lxrw-review-date` | no | When it was written |
| `lxrw-review-verified-badge` | next to the name (Loox default) | Verified purchase mark (components/review-verified-badge.md) |
| `lxrw-review-incentivized-badge` | yes, next to the name | "Rewarded" label on a review that got a discount or a manual reward (components/review-labels.md) |
| `lxrw-review-rewarded-badge` | yes, next to the name | "Incentivized" label on a review from Loox Reviewers (components/review-labels.md) |
| `lxrw-review-reply` | no | The store's reply (components/review-reply.md) |

A card without the three required parts fails the Loox check. The two incentive labels are a disclosure: a widget that leaves them out shows a review someone was paid for with no label. Put them in one wrapper with the verified mark, so labels that draw nothing don't add gaps.

## How the template works

- `<template slot="review-card">` sits inside a container of the merchant's choice (a `div` with grid, flex or a scrolling row). Loox puts one card per review into that container.
- Each card is wrapped in a Loox box, `lxrw-review-card`. The box is the item inside the container, so container CSS sizes the box: `.cards lxrw-review-card { width: 280px; margin: 0; }`. A child selector (`.cards > lxrw-review-card`) does not match. Loox adds space around each box (`--loox-lxrw-card-gap`, 14px); set it to `0px` on the container when the container sets its own gap.
- Each box sits inside its own `lxrw-review-card-provider`. To style "every third card", count on the provider: `.cards lxrw-review-card-provider:nth-of-type(3n) lxrw-review-card { … }`. `lxrw-review-card:nth-of-type()` matches nothing.
- After each render the list fires `lxrw-cards-changed` (bubbles; `detail.added` holds the new card boxes). A script that tags cards listens to it.
- The box is one button that opens the review. Links, buttons and inputs inside the template are not possible.
- One template per list.

## Options

None.

## Style (the box)

| Token | Changes | Default |
|---|---|---|
| `--loox-lxrw-u-review-background-color` | Card background | store setting |
| `--loox-lxrw-u-review-background-hover-color` | Background on hover | store setting |
| `--loox-lxrw-u-review-border` | Card border | store setting |
| `--loox-lxrw-u-card-radius` | Corner radius | store setting |
| `--loox-lxrw-u-card-shadow` | Shadow | store setting |
| `--loox-lxrw-u-text-color` | Text color inside the card | store setting |

Everything inside the box (padding, rows, gaps) comes from the merchant's wrappers inside the template.

## Admin settings that affect it

Store colors fill the token defaults. Settings that hide a part (for example the date) hide it in every card.

## Can't do

- Remove the box or change what a click does.
- A second clickable thing inside the card.
- Show a different card for one specific review.
