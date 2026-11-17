# Changelog

## v1.12.2

- "Install it for me" is stricter about where it adds the widget. It only adds the section inside the hidden page's own area. If it can't tell where that area ends, it stops, adds nothing, and gives you the code and the paste steps.

## v1.12.1

- The skill now calls itself Loox Widget Builder everywhere.
- README: install steps you can run from a terminal, for every assistant, on Mac and Windows.

## v1.12.0

- The widget code is now only the widget. It no longer loads a Loox script or reads Loox's store details: the Loox app embed on your store does that.
- The Loox app embed must be on: Online Store > Customize > App embeds > Loox. The skill checks this at the start and tells you if it is off.
- A widget built with an earlier version still works. Run it through the skill again to get the shorter code.

## v1.11.0

First public release.
