# Output: Liquid section file

A custom Widget 2.0 layout on product pages, in one of two places:

| Where | How the merchant adds it | Which code |
|---|---|---|
| A section file | Online Store > Themes > Edit code > Sections > Add a new section, paste the full file, Save. Then Customize > product page > Add section > "Loox reviews (custom)" | "Full file" below, with `{% schema %}` and settings in the sidebar |
| A Custom Liquid box | Customize > product page > Add section > Custom Liquid, paste the code, Save. No code editor needed | "Custom Liquid version" below: no `{% schema %}`, no `section.*`, fixed values |

A `{% schema %}` block or `section.settings` inside a Custom Liquid box gives "This code has errors". Each version only works in its own place.

## What the section does

1. Reads three values Loox writes into the shop's metafield `loox.global_html_head`: the server root (`__LXR:`), the version hash (`__LXV:`) and the store id (`__LXC:`).
2. Tells the widget where the Loox server is (`window.LOOX.root`), then loads the widget script. Without the first line the widget can load before the Loox script sets that address, and then it shows no reviews.
3. Writes `<loox-reviews-widget>` with the product's id, rating, count and reviews, then the composition.

## Full file

```liquid
{%- assign loox_meta = shop.metafields.loox.global_html_head -%}
{%- assign loox_hash = loox_meta | split: '__LXV:' | last | split: ';' | first | strip -%}
{%- assign loox_root = loox_meta | split: '__LXR:' | last | split: ';' | first | strip -%}
{%- assign loox_client_id = loox_meta | split: '__LXC:' | last | split: ';' | first | strip -%}
{%- assign loox_feed = product.metafields.loox.review_feed.value -%}

{%- if loox_client_id != blank and loox_root != blank and product -%}
  <script>window.LOOX = window.LOOX || {}; window.LOOX.root = window.LOOX.root || "{{ loox_root }}";</script>
  <script src="{{ loox_root }}/widget/{{ loox_client_id }}/reviews-widget/reviews-widget.js?h={{ loox_hash }}" defer></script>

  <div class="loox-custom-{{ section.id }} page-width">
    {%- if section.settings.heading != blank -%}<h2>{{ section.settings.heading }}</h2>{%- endif -%}
    <loox-reviews-widget
      client-id="{{ loox_client_id }}"
      widget-id="plugin-AGENT-RANDOM"
      surface="product"
      product-id="{{ product.id }}"
      {% if product.metafields.loox.avg_rating != blank %}average-rating="{{ product.metafields.loox.avg_rating }}"{% endif %}
      {% if product.metafields.loox.num_reviews != blank %}review-count="{{ product.metafields.loox.num_reviews }}"{% endif %}
      reviews-limit="{{ section.settings.reviews_limit }}"
      only-photos="{% if section.settings.only_photos %}true{% else %}false{% endif %}"
    >
      <script type="application/json" slot="reviews">
        {%- if loox_feed != blank -%}{{ loox_feed | json | replace: '</', '<\/' }}{%- endif -%}
      </script>

      <!-- COMPOSITION: header, reviews list and card template go here (build.md, layouts/) -->

    </loox-reviews-widget>
  </div>

  <style>
    /* Composition CSS, scoped to this section */
    .loox-custom-{{ section.id }} { margin-block: 32px; }
  </style>
{%- endif -%}

{% schema %}
{
  "name": "Loox reviews (custom)",
  "enabled_on": { "templates": ["product"] },
  "settings": [
    { "type": "text", "id": "heading", "label": "Heading", "default": "Customer reviews" },
    { "type": "range", "id": "reviews_limit", "label": "Reviews per page", "min": 1, "max": 50, "step": 1, "default": 20 },
    { "type": "checkbox", "id": "only_photos", "label": "Only reviews with photos", "default": false }
  ],
  "presets": [{ "name": "Loox reviews (custom)" }]
}
{% endschema %}
```

`reviews-limit` takes 1 to 50. A value outside that range is ignored with no warning and the store's reviews-per-page setting applies (20 by default); `lxrw-load-more` shows the next page.

## Custom Liquid version

Tested in Custom Liquid boxes on a live store. Values that were section settings are written in.

```liquid
{%- assign loox_meta = shop.metafields.loox.global_html_head -%}
{%- assign loox_hash = loox_meta | split: '__LXV:' | last | split: ';' | first | strip -%}
{%- assign loox_root = loox_meta | split: '__LXR:' | last | split: ';' | first | strip -%}
{%- assign loox_client_id = loox_meta | split: '__LXC:' | last | split: ';' | first | strip -%}
<script>window.LOOX = window.LOOX || {}; window.LOOX.root = window.LOOX.root || "{{ loox_root }}";</script>
<script src="{{ loox_root }}/widget/{{ loox_client_id }}/reviews-widget/reviews-widget.js?h={{ loox_hash }}" defer></script>
<div class="lxr-box page-width">
  <loox-reviews-widget client-id="{{ loox_client_id }}" widget-id="plugin-AGENT-RANDOM" surface="product" product-id="{{ product.id }}"
    {% if product.metafields.loox.avg_rating != blank %}average-rating="{{ product.metafields.loox.avg_rating }}"{% endif %}
    {% if product.metafields.loox.num_reviews != blank %}review-count="{{ product.metafields.loox.num_reviews }}"{% endif %}
    reviews-limit="20" only-photos="false">
    <script type="application/json" slot="reviews"></script>
    <!-- COMPOSITION goes here -->
  </loox-reviews-widget>
</div>
<style>/* Composition CSS, selectors start with .lxr-box or the widget prefix */</style>
```

With the reviews slot left empty, the widget loads the reviews itself after the page loads. `reviews-to-display="product_store_reviews"` (or `store_reviews_only`) on `<loox-reviews-widget>` sets which reviews show.

## Rules for the section

- Each widget has its own `widget-id` (`plugin-<agent>-<random>`, lowercase): Loox will fetch each widget's reviews by it.
- CSS selectors start with `.loox-custom-{{ section.id }}`, so two sections on one page do not clash.
- Tokens are set on a wrapper inside `<loox-reviews-widget>`, as in style.md.
- A carousel's script stays scoped to this section: `document.querySelectorAll('.loox-custom-{{ section.id }} .carousel')`.
- The section shows nothing when Loox's values are missing (Loox not installed) or the page has no product.
- With an empty `loox_feed`, the widget loads the reviews itself after the page loads.

## Requirements on the store

- Loox installed, with the reviews metafield sync on (it fills `loox.review_feed`, `loox.avg_rating`, `loox.num_reviews`).
- Widget 2.0 available on the Loox server for the store.

## Can't do

- Show reviews of a different product than the page's product. (The Loox block's "product handle" option does that.)
- Turn off a store setting from the section.
