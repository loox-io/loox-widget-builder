"""Install a Loox Reviews Widget 2.0 widget on a hidden product page of a Shopify store.

Takes widget code (HTML/CSS/JS or Liquid), makes a new product template based on the default one,
adds the code as a Custom Liquid section, saves, then opens the page and checks that review cards render.
Shoppers never see the page: it only opens with ?view=<template>.

Runs the browser through ego-browser, so it uses the person's own Shopify admin login. With --prepare-only it
skips the browser and writes the paste-ready code (product details added) for an install by hand. The code never
loads a Loox script: the store's Loox app embed does that.

Usage:
    python3 install.py --store mystore.myshopify.com --code widget.html --name grid-tiles --password-file <file with the storefront password>
    python3 install.py --store mystore.com --code widget.liquid --name carousel --product my-product --space 12
    python3 install.py --store mystore.com --code widget.liquid --name carousel --prepare-only

Prints one JSON line. status is one of: installed, installed_no_reviews, no_app_embed, not_on_page, needs_password,
bad_password, needs_login, not_shopify, no_product, template_not_created, editor_changed, liquid_error,
too_big, error, prepared (--prepare-only).
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from preflight import ego_path, read_password, timed_out_output

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "references" / "docs"
TMP = Path(tempfile.gettempdir())
LIMIT = 12_000  # Shopify's Custom Liquid box failed at ~13,100 chars and saved ~12,050 (tested 10-27)
# Builds before 1.12.0 started with Loox's own wiring: four assigns read from a Loox shop metafield, a line that
# set window.LOOX.root, and a tag that loaded reviews-widget.js. The store's Loox app embed does all of that (it
# sets LOOX.root and LOOX.clientId, and loads the widget script once it sees a widget on the page), so the lines
# only repeated it. They are taken out of any code that still has them.
OLD_WIRING = [
    r"[ \t]*\{%-?\s*assign\s+loox_(?:meta|hash|root|client_id)\s*=[^%]*%\}[ \t]*\n?",
    r"[ \t]*<script>\s*window\.LOOX\s*=\s*window\.LOOX\s*\|\|\s*\{\};\s*window\.LOOX\.root\s*=[^<]*</script>[ \t]*\n?",
    r"""[ \t]*<script\b[^>]*\bsrc\s*=\s*["']?\{\{-?\s*loox_root\s*-?\}\}/widget/[^>]*>\s*</script>[ \t]*\n?""",
    r"""\s+client-id\s*=\s*(?:"\{\{-?\s*loox_client_id\s*-?\}\}"|'\{\{-?\s*loox_client_id\s*-?\}\}')""",
]
OLD_GUARD = r"\{%(-?)\s*if\s+loox_client_id\s*!=\s*blank\s+and\s+loox_root\s*!=\s*blank\s+and\s+product\s*(-?)%\}"


def strip_old_wiring(code: str) -> tuple[str, bool]:
    """Take the pre-1.12.0 Loox wiring out of widget code. Returns the code and whether anything was removed."""
    before = code
    for pattern in OLD_WIRING:
        code = re.sub(pattern, "", code)
    code = re.sub(OLD_GUARD, r"{%\1 if product \2%}", code)
    return code, code != before


# What the widget needs to know which product to load. A Loox theme block sets these for the merchant; a Custom
# Liquid box does not, so bare roots get them here. The store itself comes from the Loox app embed, never from the code.
ROOT_ATTRS = {
    "surface": '"product"',
    "product-id": '"{{ product.id }}"',
    "reviews-limit": '"20"',
}
ROOT_EXTRAS = ('{% if product.metafields.loox.avg_rating != blank %} average-rating="{{ product.metafields.loox.avg_rating }}"{% endif %}'
               '{% if product.metafields.loox.num_reviews != blank %} review-count="{{ product.metafields.loox.num_reviews }}"{% endif %}')

# Every widget the skill builds carries its own widget-id, set once by the agent: plugin-<agent name>-<random>.
# Loox is to fetch each widget's reviews by it, so two widgets on one page don't get the same cached answer.
# The scripts only check it; they never make one up or change it.
WIDGET_ID = re.compile(r"""\swidget-id=(["'])(plugin-[a-z0-9]+(?:-[a-z0-9]+)*-[a-z0-9]{6,})\1""")
# The example in SKILL.md step 5. Copied as is, every widget would share it.
SAMPLE_WIDGET_ID = "plugin-claude-3f9a1c7e"

log = logging.getLogger("widget-install")


def known_parts() -> set[str]:
    """Every lxrw- name the Widget 2.0 docs mention. A tag outside this set draws nothing and gives no error."""
    return {n for f in DOCS.rglob("*.md") for n in re.findall(r"lxrw-[a-z0-9-]+", f.read_text(encoding="utf-8"))}


def unknown_tags(code: str, known: set[str] | None = None) -> list[str]:
    """lxrw- tags in the code that the store's widget script doesn't define (`known`), or, without it, no docs page names."""
    known = known or known_parts()
    return sorted({t for t in re.findall(r"<(lxrw-[a-z0-9-]+)", code) if t not in known})


def preview_url(store: str, product: str | None, template: str) -> str | None:
    """The hidden page's link, with the same host rule as install.js: a bare handle means <handle>.myshopify.com."""
    if not product:
        return None
    host = store if "." in store else f"{store}.myshopify.com"
    return f"https://{host}/products/{product}?view={template}"


def has_attr(tag: str, name: str) -> bool:
    """True when the tag sets the attribute, whatever whitespace (space, tab, newline) comes before it."""
    return re.search(rf"\s{re.escape(name)}=", tag) is not None


def fix_root(m: re.Match) -> str:
    tag = m.group(0)
    add = "".join(f" {k}={v}" for k, v in ROOT_ATTRS.items() if not has_attr(tag, k))
    if not has_attr(tag, "average-rating"):
        add += ROOT_EXTRAS
    return tag[:-1] + add + ">" if add else tag


PAIRS = {"if": "endif", "unless": "endunless", "for": "endfor", "case": "endcase", "capture": "endcapture",
         "comment": "endcomment", "raw": "endraw", "form": "endform", "paginate": "endpaginate", "javascript": "endjavascript",
         "style": "endstyle"}


def liquid_problems(code: str) -> list[str]:
    """Catch unclosed or stray Liquid block tags before the store does (Shopify silently drops the section)."""
    stack, problems = [], []
    # Tags inside {% comment %} and {% raw %} are text, not Liquid.
    code = re.sub(r"{%-?\s*(comment|raw)\s*-?%}.*?{%-?\s*end\1\s*-?%}", "", code, flags=re.S)
    for m in re.finditer(r"{%-?\s*(\w+)", code):
        tag = m.group(1)
        if tag in PAIRS:
            stack.append(tag)
        elif tag in PAIRS.values():
            if stack and PAIRS[stack[-1]] == tag:
                stack.pop()
            else:
                problems.append(f"stray {{% {tag} %}}")
    problems += [f"{{% {t} %}} is never closed" for t in stack]
    # A lone }} is normal in CSS and JS (nested braces), so only a {{ left after removing every complete {{ ... }} counts.
    if "{{" in re.sub(r"{{.*?}}", "", code, flags=re.S):
        problems.append("a {{ is never closed with }}")
    return problems


# Code that is risky on a live store: the widget's scripts run on the merchant's own domain, for every shopper.
# (what to look for, what it is, what to do instead). A warning, never a stop: the person decides.
UNSAFE = [
    (r"<iframe\b", "adds a frame from another page", "leave it out"),
    (r"\.(?:innerHTML|outerHTML)\s*\+?=|insertAdjacentHTML|document\.write(?:ln)?\s*\(|createContextualFragment|\bsrcdoc\b",
     "writes HTML from a script", "put review text, names and dates on the page as text (textContent)"),
    (r"\beval\s*\(|new\s+Function\s*\(|set(?:Timeout|Interval)\s*\(\s*['\"`]|javascript:", "runs text as code",
     "call a function instead"),
    (r"\bfetch\s*\(|XMLHttpRequest|sendBeacon|\bWebSocket\b|\bEventSource\b", "sends or loads data over the network",
     "the widget's own parts load the reviews; a script has no need to"),
    (r"document\.cookie|\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b", "reads or writes the shopper's cookies or browser storage",
     "leave it out"),
]


def unsafe_code(code: str) -> list[str]:
    """WARNING notes for code that is risky on a live store, each with its line. See concepts.md, "What a script must not do"."""
    notes = []
    # A script tag is read whole, since its src can sit on a later line. No script address passes: widget code
    # loads no script at all, and the widget's own script comes from the store's Loox app embed.
    for m in re.finditer(r"<script\b[^>]*>", code, re.I):
        src = re.search(r"""\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", m.group(0), re.I)
        if not src:
            continue
        address = next(g for g in src.groups() if g is not None).strip()
        n = code.count("\n", 0, m.start()) + 1
        if re.match(r"\{\{-?\s*loox_root\s*-?\}\}/widget/", address):
            notes.append(f"WARNING: line {n} loads the Loox widget script. The Loox app embed already loads the widget script: remove this line")
        else:
            notes.append(f"WARNING: line {n} loads a script from outside Loox: `{address[:70]}`. Safer: write the script inside the "
                         "widget, or leave it out. Keep it only if the person asked for it, and list it under Overrides")
    for n, line in enumerate(code.splitlines(), 1):
        for pattern, what, instead in UNSAFE:
            if re.search(pattern, line, re.I):
                notes.append(f"WARNING: line {n} {what}: `{line.strip()[:70]}`. Safer: {instead}. Keep it only if the person asked for it, and list it under Overrides")
    return notes


def liquid_string(s: str) -> str:
    """A Liquid string literal: single quotes, double quotes when the text has an apostrophe."""
    if "'" not in s:
        return f"'{s}'"
    if '"' not in s:
        return f'"{s}"'
    return "'" + s.replace("'", "") + "'"


def prepare(code: str, template: str) -> tuple[str, list[str]]:
    """Make sandbox output safe for a Custom Liquid box. Returns the code and notes on what changed."""
    notes = []
    blocks = re.findall(r"^```(\w*)[ \t]*\n(.*?)^```", code, re.S | re.M)
    body = next((b for lang, b in blocks if lang in ("liquid", "html", "") and "<" in b), None)
    if body is not None:
        code, _ = body, notes.append("took the code block out of the reply")
    schema = re.search(r"{%-?\s*schema\s*-?%}(.*?){%-?\s*endschema\s*-?%}", code, re.S)
    if schema:
        try:
            settings = json.loads(schema.group(1)).get("settings", [])
        except json.JSONDecodeError:
            settings = []
        code = code[: schema.start()] + code[schema.end():]
        notes.append("removed the {% schema %} block (Custom Liquid rejects it)")
        filled = []
        for st in settings:
            if "id" in st and "default" in st:
                val = st["default"]
                lit = ("true" if val else "false") if isinstance(val, bool) else (str(val) if isinstance(val, (int, float)) else liquid_string(str(val)))
                code, n = re.subn(rf"\b(section|block)\.settings\.{re.escape(st['id'])}\b", lit, code)
                if n:
                    filled.append(st["id"])
        if filled:
            notes.append("filled section settings with their defaults: " + ", ".join(filled))
    code = re.sub(r"{{-?\s*section\.id\s*-?}}", template, code)
    code, stripped = strip_old_wiring(code)
    if stripped:
        notes.append("removed the Loox loader lines from an older build: the store's Loox app embed loads the widget script")
    if re.search(r"\b(section|block)\.settings\.", code):
        notes.append("WARNING: code reads section/block settings with no default, which are empty in Custom Liquid")
    roots = re.findall(r"<loox-reviews-widget\b[^>]*>", code)
    ids = [m.group(2) if (m := WIDGET_ID.search(r)) else None for r in roots]
    if any(i is None and not has_attr(r, "widget-id") for r, i in zip(roots, ids)):
        notes.append('WARNING: a <loox-reviews-widget> has no widget-id="plugin-<agent name>-<random>". '
                     "Add one, made once for this widget and kept through every round (SKILL.md step 5)")
    if any(i is None and has_attr(r, "widget-id") for r, i in zip(roots, ids)):
        notes.append('WARNING: a <loox-reviews-widget> has a widget-id of the wrong shape: it should be '
                     '"plugin-<agent name>-<random>", lowercase, with a random part of 6 or more letters and digits')
    found = [i for i in ids if i]
    if SAMPLE_WIDGET_ID in found:
        notes.append(f"WARNING: a <loox-reviews-widget> uses the example widget-id {SAMPLE_WIDGET_ID} from the skill. "
                     "Make a new random part for this widget")
    if len(set(found)) < len(found):
        notes.append("WARNING: two <loox-reviews-widget> roots share a widget-id: each widget needs its own")
    if not roots:
        notes.append("WARNING: no <loox-reviews-widget> root in the code")
    elif any(not has_attr(r, k) for r in roots for k in ROOT_ATTRS):
        code = re.sub(r"<loox-reviews-widget\b[^>]*>", fix_root, code)
        notes.append("added product details to the widget root")
    return f'<div data-lx-install="{template}">\n{code.strip()}\n</div>\n', notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--store", required=True, help="store handle, myshopify domain or storefront domain")
    ap.add_argument("--code", required=True, type=Path, help="file with the widget code")
    ap.add_argument("--name", required=True, help="short name; the template becomes ai-<name>-<MMDDHHMM>")
    ap.add_argument("--product", help="product handle (default: the store's first product)")
    ap.add_argument("--password", help="storefront password, if the store has one")
    ap.add_argument("--password-file", type=Path, help="a private file that holds the storefront password (keeps it off the command line)")
    ap.add_argument("--space", help="ego-browser task space id to reuse (after a login hand-off)")
    ap.add_argument("--prepare-only", action="store_true", help="write the paste-ready code and stop; no browser")
    ap.add_argument("--out", type=Path, default=TMP / "loox-widget-install", help="where the code and screenshots go")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    try:
        a.password = read_password(a.password, a.password_file)
    except OSError as e:
        print(json.dumps({"status": "error", "detail": f"password file: {e}"}))
        return 1

    prod = re.search(r"/products/([^/?#]+)", a.store)
    if prod and not a.product:
        a.product = prod.group(1)
    store = re.sub(r"^https?://|/.*$", "", a.store.strip())
    slug = re.sub(r"[^a-z0-9]+", "-", a.name.lower()).strip("-")[:13].strip("-") or "widget"  # Shopify cuts template names at 25 chars
    template = f"ai-{slug}-{datetime.now():%m%d%H%M}"
    raw = a.code.read_text(encoding="utf-8")
    code, notes = prepare(raw, template)
    notes += unsafe_code(raw)
    bad = liquid_problems(code)
    if bad:
        print(json.dumps({"status": "liquid_error", "detail": bad, "notes": notes}))
        return 1
    if len(code) > LIMIT:
        print(json.dumps({"status": "too_big", "chars": len(code), "limit": LIMIT, "notes": notes}))
        return 1
    a.out.mkdir(parents=True, exist_ok=True)
    part = a.out / f"{template}.liquid"
    part.write_text(code, encoding="utf-8")
    if a.prepare_only:
        print(json.dumps({"status": "prepared", "template": template, "file": str(part),
                          "preview_url": preview_url(store, a.product, template), "unknown_parts": unknown_tags(code),
                          "notes": notes}))
        return 0
    cfg = {"store": store, "template": template, "files": [str(part)], "product": a.product,
           "password": a.password, "space": a.space, "out": str(a.out)}
    script = f"const CFG = {json.dumps(cfg)};\n" + (HERE / "install.js").read_text(encoding="utf-8")
    log.info("installing %s on %s (%d chars)", template, store, len(code))
    try:
        ego = ego_path()
        if not ego:
            raise FileNotFoundError("ego-browser")
        run = subprocess.run([ego, "nodejs"], input=script, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=420)
    except FileNotFoundError:
        print(json.dumps({"status": "error", "detail": "ego-browser is not installed"}))
        return 1
    except subprocess.TimeoutExpired as e:
        text = timed_out_output(e)  # the result may be out already, with only closing the browser stuck
        if "RESULT " not in text:
            print(json.dumps({"status": "error", "detail": "browser run took over 7 minutes"}))
            return 1
    else:
        text = run.stdout + "\n" + run.stderr  # ego-browser prints console output on stderr
    for line in text.splitlines():
        if line.startswith("STEP "):
            log.info("  %s", line[5:])
    results = [l[7:] for l in text.splitlines() if l.startswith("RESULT ")]
    if not results:
        print(json.dumps({"status": "error", "detail": text[-600:]}))
        return 1
    res = json.loads(results[-1])
    res["notes"] = notes
    res["file"] = str(part)
    print(json.dumps(res))
    return 0 if res.get("status") == "installed" else 2


if __name__ == "__main__":
    sys.exit(main())
