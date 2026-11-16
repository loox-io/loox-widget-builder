# Recipe: list

One review per row, photo on the right, also on phones. Tested on desktop and phone. Add the header, load more, store colors and the no-photo fix (known-limits.md), or empty photo columns stay.

```html
<loox-reviews-widget>
  <div class="lxr-list">
    <lxrw-reviews-list>
      <div class="lxr-list__rows">
        <template slot="review-card">
          <article class="lxr-list__row">
            <div class="lxr-list__body">
              <lxrw-review-rating></lxrw-review-rating>
              <div class="lxr-list__by"><lxrw-reviewer-name></lxrw-reviewer-name><lxrw-review-verified-badge></lxrw-review-verified-badge></div>
              <lxrw-review-content></lxrw-review-content>
            </div>
            <lxrw-review-media></lxrw-review-media>
          </article>
        </template>
      </div>
    </lxrw-reviews-list>
  </div>
</loox-reviews-widget>
<style>
  .lxr-list__rows { display: flex; flex-direction: column; gap: 12px; --loox-lxrw-card-gap: 0px; }
  .lxr-list__rows lxrw-review-card { width: auto; margin: 0; }
  .lxr-list__row { display: flex; align-items: flex-start; gap: 16px; padding: 16px; }
  .lxr-list__body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 8px; }
  .lxr-list__by { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
  .lxr-list__row > lxrw-review-media { flex: 0 0 30%; aspect-ratio: 4/5; max-height: 215px; overflow: hidden; border-radius: 8px; }
  .lxr-list__row lxrw-review-media::part(media) { height: 100%; aspect-ratio: auto !important; }
  .lxr-list__row lxrw-review-media::part(image) { width: 100%; height: 100%; object-fit: cover; }
  @container (min-width: 620px) { .lxr-list__row { padding: 24px; } .lxr-list__row > lxrw-review-media { flex-basis: 15%; } }
</style>
```
