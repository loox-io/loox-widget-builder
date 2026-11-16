# lxrw-header-write-button

The "Write a review" button. A click opens the Loox review form.

Kind: display part with one action. Goes inside: `<lxrw-header>`. Optional.

## Example

```html
<lxrw-header>
  <div class="summary">
    <lxrw-header-rate-average-icons></lxrw-header-rate-average-icons>
    <lxrw-header-reviews-count></lxrw-header-reviews-count>
    <lxrw-header-write-button></lxrw-header-write-button>
  </div>
</lxrw-header>
```

## Options

None. The label text comes from Loox and follows the store's language.

## Style

| Token or hook | Changes | Default |
|---|---|---|
| `--loox-lxrw-u-button-bg` | Button background | store setting |
| `--loox-lxrw-u-button-text-color` | Button text | store setting |
| `--loox-lxrw-u-button-radius` | Button corners | 4px |
| `::part(button)` | The button itself: size, border, font, padding | |
| `::part(button)::before`, `::part(button)::after` | Extra decoration drawn inside the button, such as an icon | |

## In the default widget

Inside `<lxrw-widget-preset>`, the default header re-exposes the button as `write-button`: `lxrw-header-minimal-preset::part(write-button) { … }` (or the compact or expanded preset) restyles it and keeps the whole default widget. The icon example below works the same way with `lxrw-header-minimal-preset::part(write-button)` in place of `lxrw-header-write-button::part(button)`.

To change the header's layout too, the header is written by hand and the default reviews stay as a preset:

```html
<loox-reviews-widget>
  <lxrw-header>
    <div class="summary">
      <lxrw-header-rate-average-icons></lxrw-header-rate-average-icons>
      <lxrw-header-reviews-count></lxrw-header-reviews-count>
      <lxrw-header-write-button></lxrw-header-write-button>
    </div>
  </lxrw-header>
  <lxrw-reviews-layout-preset></lxrw-reviews-layout-preset>
  <lxrw-load-more></lxrw-load-more>
</loox-reviews-widget>
```

`<lxrw-reviews-layout-preset>` is the default reviews area (cards and layout). It has no load more: `<lxrw-load-more>` after it shows the next page, or shoppers see only the first page.

## A custom look: icon instead of text

The button has no slot, so its content cannot be replaced with other HTML. A new look comes from CSS on the button part. The label text stays in the button for screen readers and is hidden visually with `font-size: 0`; an icon is drawn with `::before`. Example, an animated star:

```css
lxrw-header-write-button::part(button) {
  font-size: 0; width: 44px; height: 44px; padding: 0;
  border: 0; border-radius: 50%; background: transparent;
}
lxrw-header-write-button::part(button)::before {
  content: "\2605"; font-size: 30px; line-height: 44px;
  color: var(--loox-lxrw-u-stars-color, #EBBF20);
  display: inline-block; animation: star-pulse 2.4s ease-in-out infinite;
}
@keyframes star-pulse {
  0%, 100% { transform: scale(1) rotate(0); }
  50% { transform: scale(1.18) rotate(12deg); }
}
@media (prefers-reduced-motion: reduce) {
  lxrw-header-write-button::part(button)::before { animation: none; }
}
```

The click still opens the review form, and the button keeps its keyboard focus and its "Write a review" name for screen readers.

## Admin settings that affect it

"Show write a review button" in Loox admin. When off, the button shows in no layout.

## Can't do

- Put other HTML (an image, an SVG element, a second button) inside it.
- Change what the click does.
- Show it inside a review card. The card is one button.
