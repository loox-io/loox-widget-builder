# How the parts fit

## The tree

```
<loox-reviews-widget>            holds the reviews and the store's settings
  <lxrw-header>                  data part: the store's totals
    header display parts         average stars, review count, write button, sort menu
  <lxrw-reviews-list>            data part: the reviews of the current page
    <div> (any container)        the layout of the cards: grid, row, column
      <template slot="review-card">   the card, written once
        card display parts       photo, stars, text, name, date, badges
```

## Data parts and display parts

- **Data parts** hold data and draw nothing: no box, no spacing. `<loox-reviews-widget>`, `<lxrw-header>` and `<lxrw-reviews-list>` are data parts.
- **Display parts** each show one thing, taken from the data part above them. A header display part shows something only inside `<lxrw-header>`. A card display part shows something only inside the card template. In the wrong place they show nothing, and no error appears.
- **Display parts carry no layout.** Placed bare, they sit in a plain line. Spacing, rows and columns come from the merchant's own wrappers (`div`, `article`, `footer`) and CSS.
- **Presets** are ready-made arrangements from Loox, such as `<lxrw-widget-preset>` (the whole default widget). A preset is the quick option; writing the parts by hand gives full control of the layout.

## What Loox owns

- Which reviews appear, their order, how many per page (1 to 50, 20 by default), and the numbers in the header.
- Sorting, filtering by stars, loading more, opening the review form and the review detail.
- The card box: Loox wraps every card in a box that is one button. It is not part of the merchant's markup.
- Store settings: a setting turned off in Loox admin hides its part in every layout.

## The 4 ways to customize (layout and look only)

| Way | What it changes | Example |
|---|---|---|
| Tokens | Colors, corner radius, shadow | `--loox-lxrw-u-stars-color: #c0392b;` |
| Style hooks (`::part`) | One named piece inside a part | `lxrw-review-rating::part(stars) { gap: 2px; }` |
| Slots | Own content in a marked place, such as an icon | listed on the part's page when it has one |
| Card template | Which parts a card shows, in what order and wrappers | `<template slot="review-card">` |

Tokens work when set on an element inside the widget, such as a wrapper. Set on `<loox-reviews-widget>` itself, or on `body`, the store's own values win.

## What a script can read

Once Loox has drawn the cards, each `lxrw-review-card`, its `lxrw-review-card-provider` wrapper and its
`lxrw-review-rating` carry a `review` object. A script inside the widget's wrapper can read it:

| Field | What it holds |
|---|---|
| `_id` | the review's id |
| `rating` | 1 to 5 |
| `review` | the review text |
| `date` | the review date |
| `nickname` | the reviewer's name |
| `verified` | `true` for a verified buyer |
| `media` | the photos and videos, `[]` when there are none |

The stars also name the rating in their shadow root: `aria-label="Rating icons: 3 / 5 star review"`.

A script reads this data, and can hide or tag a card from it (a class for cards with no photo, a class for
cards with a reply). It cannot change the data: the text, stars, order and the reviews Loox loads stay as Loox
sends them. Read on the drawn page only: the cards are not there before Loox draws them, so look them up
after the widget has rendered, and again after each load more.

### What a script must not do

Scripts run on the store's domain for every shopper, and anyone can write a review. So:

- Review text, names and dates go on the page as text (`textContent`), never as HTML (`innerHTML`).
- No outside scripts or frames, no network calls, no cookies or browser storage, no `eval`.

The installer warns with the line. Fix it, unless the person asked for exactly that: then list it under "Overrides".

Don't build anything that hides or filters reviews by rating (for example "only 5-star reviews"). It isn't
supported: hiding low ratings while the header shows
the overall rating is the kind of review suppression consumer-review rules target. When a request asks for
it, say so in the proposal and offer the widget without the filter.

## Pages

`reviews-limit` on `<loox-reviews-widget>` sets the page size and takes 1 to 50. A value outside that range
is thrown away with no warning (60 does not become 50), and the page falls back to the store's reviews-per-page
setting, 20 by default. An all-reviews widget (`surface="aggregate"`) always falls back to 20. Shoppers see the next page through
`lxrw-load-more`. A script can click the button inside `lxrw-load-more`'s shadow root to load pages
itself (worked 10-21). That button is Loox's internal markup, not a supported API: if Loox changes it, the
script stops loading pages with no error. Each click fetches a page, so load at most 3 pages this way, never
every page on open. Prefer keeping `lxrw-load-more` visible.

## Missing data

A review may have no photo, no date or no text, and a store setting may hide a part. The part then shows nothing and takes no space. A layout that still reads well when a part is empty works for every review.
