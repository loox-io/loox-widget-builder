# Not possible

Requests that composing parts cannot meet. The answer to the merchant says so and offers the closest option.

## Not possible

| Request | Why | Closest option |
|---|---|---|
| "Helpful" or like buttons on reviews | No part for votes. A button inside a card is not possible (the card is one button). | none |
| Links or buttons inside a card ("read more", "buy") | The whole card is one button that opens the review. | The card click opens the full review. |
| Country flags or reviewer location | No part shows it. | none |
| Filter by country, product option or keyword | Filtering belongs to Loox. Only filter by stars exists. | `lxrw-header-distribution-list` filters by stars. |
| New sort orders | Sorting belongs to Loox: featured, newest, highest, lowest. | `lxrw-header-sort-menu` |
| Play video in the card | The card shows the video's poster. | Video plays in the review detail. The poster already shows a play icon. |
| A video-only marker or style | No part tells whether a review is a video. | The poster's own play icon. |
| Rating as a number on each review | No part shows it. | `lxrw-review-rating` stars |
| Relative dates ("3 days ago") | The date part shows a fixed date. | `lxrw-review-date` |
| Showing something a store setting hides | Store settings win. | Change the setting in Loox admin. |
| Changing reviews with a script (text, stars, order, which ones Loox loads) | Loox owns the data. A script can read it, not change it (concepts.md, "What a script can read"). | Hide or tag cards from what the script reads. |
| More than 50 reviews on one page | `reviews-limit` takes 1 to 50. A value outside that range is thrown away with no warning, and the page falls back to the store's reviews-per-page setting (20 by default). | `lxrw-load-more` for the next page. |
| Review highlights (the AI-picked phrase in bold) | The widget doesn't draw highlights. They're planned for after launch, with no date. | The review's opening words in one clamped line. |
| A new kind of part | Only the listed parts exist. | Combine existing parts. |

## Coming soon

| Feature | Status |
|---|---|
| Custom review questions on the card | not available yet |
| Translation note in the text | not available yet |
