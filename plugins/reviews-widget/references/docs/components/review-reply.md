# lxrw-review-reply

The store's reply to a review: "Store name replied:" and the reply, cut at 150 characters.

Kind: display part. Goes inside: the card template. Optional.

## Style

| Token or hook | Changes |
|---|---|
| `--loox-lxrw-u-reply-background-color`, `--loox-lxrw-u-reply-text-color` | The reply box |
| `::part(reply)`, `::part(reply-title)`, `::part(reply-text)` | The box, the title line, the text |

## Empty state

A review without a reply: draws nothing, takes no space.
