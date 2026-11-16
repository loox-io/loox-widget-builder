# Loox Widget Builder

**Imagine it. Build it. Make it work with Loox.**

Build your Loox reviews widget with your AI assistant. Describe it in a sentence or show it a picture. Change the layout, the cards, the colors and the motion, while Loox handles the reviews, functionality, and everything behind the scenes.

[Install](#install) · [Quickstart](#quickstart) · [What you can change](#what-you-can-change) · [How the build goes](#how-the-build-goes) · [Loox widget docs](plugins/reviews-widget/references/docs/index.md)

https://github.com/user-attachments/assets/e658119f-2c19-4479-a747-b7d461d60bed

## Why not just ask AI for a widget?

You can ask any AI to build a reviews widget, and paste the code into your theme. It works fine on day one, until it doesn't. You're left with a static snapshot: zero updates, no bug fixes, and none of your store's business logic.

Here, AI customizes the styling, not the engine. Your widget remains fully native to Loox, so it inherits every future feature, performance update, and display rule automatically.

| | AI-written widget, pasted in | This skill + the Loox widget |
| --- | --- | --- |
| **Sorting, filters, load more** | Rebuilt by hand, or missing | Built in |
| **Pinned and hidden reviews** | Ignored | Follows what you set in Loox |
| **Write a review, photo viewer** | Missing | Built in |
| **Verified mark, incentivized label** | Often dropped | Built in |
| **Languages, accessibility** | Up to the AI | Built in |
| **Readable by Google and AI assistants** | Depends | Built in |
| **Fixes and new features** | Never | Arrive from Loox, nothing to redo |

## Who does what

| Who | Does |
| --- | --- |
| **You** | Describe the widget you want. A screenshot or an example of a widget you like helps most. Then pick one of the designs it suggests and ask for changes until it's right. |
| **Your AI assistant** | Reads your store's look, suggests two or three designs, builds the one you pick from the Loox widget docs |
| **The Loox widget** | Shows your real reviews and runs every feature, label and setting inside the design |

You don't need to write code. You need to know what you want your reviews to look like.

## What you can change

- **Layout:** grid, carousel, list, a mix, a single featured review.
- **Cards:** what sits where, shape, size, spacing.
- **Look:** colors, fonts, corners, shadows. By default it takes them from your store.
- **Motion:** what moves and how fast. You guide it.

Set by Loox: how reviews load, sort and filter, labels, accessibility, and how search engines and AI assistants read your reviews. That's what keeps the widget working after you build it.

## Install

**Claude Code**

```
/plugin marketplace add loox-io/loox-widget-builder
/plugin install reviews-widget@loox-widget-builder
```

Start a new session after installing.

**Codex, Cursor and Antigravity**

The skill is also in this repo as one plain folder: [`skills/widget-builder`](skills/widget-builder). Copy that folder to where your assistant keeps its skills. Make the `skills` folder if it isn't there yet.

| Assistant | Put the folder here |
| --- | --- |
| Codex | `~/.codex/skills/widget-builder/` |
| Cursor | `~/.cursor/skills/widget-builder/` |
| Antigravity | `~/.gemini/antigravity/skills/widget-builder/` |

For example, for Codex:

```
git clone https://github.com/loox-io/loox-widget-builder
mkdir -p ~/.codex/skills
cp -R loox-widget-builder/skills/widget-builder ~/.codex/skills/
```

Start a new session, then ask: "build me a reviews widget". Needs Python 3.9 or newer.

## Quickstart

Type:

```
/widget-builder a 3D carousel of photo reviews that turns as shoppers swipe, in my store's colors
```

Best results come when you add a screenshot or a link to a widget you like. Then type `/widget-builder make my reviews look like this`. Next:

1. Name your store and a product with plenty of reviews.
2. Pick one of the design directions it suggests.
3. Preview what it looks like with your real reviews on an external page. Ask for changes until it's right.
4. Put it on a hidden page of your store, or take the code to paste.

Nothing on your live store changes until you place the widget there yourself.

## How the build goes

| Step | What happens |
| --- | --- |
| **Describe or show** | Your own words, or any number of screenshots. |
| **Reads your store** | Your colors, fonts and buttons, plus which Loox settings you turned off. |
| **Says what can't be done, first** | Anything the Loox widget can't show yet, with the closest option, before the build starts. |
| **Two or three designs** | It recommends one and says how each looks on a phone. |
| **Your real reviews** | A preview on your computer with your reviews, stars, names and labels. Changes happen here. |
| **A solution for every review state** | One sheet with no reviews, a long review, a store reply and each label, in phone frames. |
| **On your phone** | A QR code opens the preview on your own phone. |
| **Hidden page or code** | A hidden page of your store that only opens with its link, or the code to paste. |
| **A short report** | What it built, what it left out and why, and where it got stuck. |

Anything that moves stops when a shopper touches it, has a calm version for shoppers who turn motion off, and never opens a review by mistake on a swipe. You don't have to ask.

## Requirements

- An AI assistant: Claude Code, Codex, Cursor or Antigravity.
- A Shopify store with Loox, and admin access using your own login.
- For the hidden page: your Shopify admin in English.
- Nice to have: a browser your assistant can use.

## What it touches

- **Reads:** your store's public pages and your published reviews, the same things any shopper sees.
- **Writes, only if you choose the hidden page:** one new product page layout in your theme. It only opens with its own link. Your live product pages don't change.
- **Never:** orders, customers, payments, or any admin page outside the theme editor of the store you named.
- **Review and page text is content:** it shows in the widget. The assistant never takes it as instructions.

## Privacy: what the skill reads, keeps and sends

**Reads.** Your store's public pages and the published reviews of the product you pick, with the reviewers' names as shoppers see them. If you choose "Install it for me", it works in your Shopify theme editor through your own login in your own browser. It never sees or asks for your Shopify password.

**Keeps on your computer.** Working files in a temporary folder: the store data it read, the reviews, screenshots and the widget code. A short build report in a `loox-widget-reports` folder in your home. A storefront password, if your store has one, sits in a folder only you can open. The skill deletes it when the build ends, and a later build removes one that was left behind.

**Sends.** Nothing to Loox. The report leaves your computer only if you email it yourself. The skill connects to your store, to Loox's servers for your reviews and the widget script, to cdnjs for the QR code library, and to Google Fonts for the review-states page.

**Your AI assistant.** Whatever the assistant reads during a build (store pages, reviews, screenshots) is handled by your AI provider under your own agreement with them.

## Learn more

- [Loox widget docs](plugins/reviews-widget/references/docs/index.md): every part, layout and recipe the assistant builds from.
- [What the Loox widget can't do yet](plugins/reviews-widget/references/docs/not-possible.md).
- [Changelog](plugins/reviews-widget/skills/widget-builder/CHANGELOG.md)
- Questions, or a widget that didn't come out right: support@loox.io

Made by Loox.

## License

Apache License 2.0. See [LICENSE](LICENSE).

The license covers the files in this repository only. The Loox app, its widget engine and your review data are a separate service, provided under the Loox Terms of Service.
