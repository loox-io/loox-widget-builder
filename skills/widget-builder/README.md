# Loox Widget Builder

Build a Loox reviews widget for your Shopify store with your AI assistant: describe it or paste a
picture, pick one of a few versions, see it with your store's real reviews, and get the code. Version 1.12.1.

## Install

Put the `widget-builder` folder where your assistant keeps its skills. Make the `skills` folder if it isn't
there yet.

| Assistant | Put the folder here |
|---|---|
| Claude Code | `~/.claude/skills/widget-builder/` |
| Codex | `~/.codex/skills/widget-builder/` |
| Cursor | `~/.cursor/skills/widget-builder/` |
| Antigravity | `~/.gemini/antigravity/skills/widget-builder/` |

Start a new session, then ask: "build me a reviews widget" (or type `/widget-builder` where the assistant has
slash commands). Needs Python 3.9 or newer.

## Privacy: what the skill reads, keeps and sends

**Reads.** Your store's public pages and the published reviews of the product you pick, with the reviewers'
names as shoppers see them. If you choose "Install it for me", it works in your Shopify theme editor through
your own login in your own browser. It never sees or asks for your Shopify password.

**Keeps on your computer.** Working files in a temporary folder: the store data it read, the reviews,
screenshots and the widget code. A short build report in a `loox-widget-reports` folder in your home. A
storefront password, if your store has one, sits in a folder only you can open. The skill deletes it when the
build ends, and the next build removes one that was left behind.

**Sends.** Nothing to Loox. The report leaves your computer only if you email it yourself. The skill connects
to your store, to Loox's servers for your reviews and the widget script, to cdnjs for the QR code library, and
to Google Fonts for the review-states page.

**Your AI assistant.** Whatever the assistant reads during a build (store pages, reviews, screenshots) is
handled by your AI provider under your own agreement with them.

## License

Apache License 2.0. See [LICENSE.md](LICENSE.md).

The license covers the files in this repository only. The Loox app, its widget engine and your review data are
a separate service, provided under the Loox Terms of Service.

Questions: support@loox.io
