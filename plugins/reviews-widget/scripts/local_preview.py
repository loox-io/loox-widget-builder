"""Preview a Loox Reviews Widget 2.0 widget on a local page, with the store's real reviews written in.

Design rounds happen here, not on the store: no install, no theme editor, no new template per round.
The real widget script runs on the local page. Loox refuses review requests from a local page, so the
script reads the product's reviews once (from the command line, where Loox answers) and writes them into
the page in the widget's own snapshot format. The header average and count come from the same read.

With --states it also writes a state sheet: the same widget in every review state (no reviews, one, a few,
many, no photo, photos and video, long text, stars only, low ratings, store reply, labels, photos only), each in
a browser frame and an iPhone frame, in the store's colors (--look) with Claude's note per state (--notes).

No browser needed. Reads the store three times at most (product page, widget script for the sort setting,
reviews), then reuses store-data.json.

Usage:
    python3 local_preview.py --store mystore.com --product my-product --code widget.liquid --out /tmp/loox-widget-build/grid/local
    python3 local_preview.py --store mystore.com --product my-product --code widget.liquid --out <dir> --states
    python3 local_preview.py ... --password-file <file>     # only if the store has a storefront password
    python3 local_preview.py ... --refresh                            # read the store again

With --settings-only it reads the store and lists the parts its Loox settings hide (hidden_by_settings), with no page.

Prints one JSON line. status is one of: ready, needs_password, bad_password, no_loox, no_product,
fetch_failed, liquid_error, too_big, error. On ready: page (and states with --states), serve (the command that serves the folder),
url, file_url (the same page opened as a file, for when a local server can't start), reviews, with_photos, notes.
"""
from __future__ import annotations

import argparse
import html
import http.cookiejar
import json
import logging
import math
from decimal import ROUND_HALF_UP, Decimal
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from preflight import read_password
from install import LIMIT, liquid_problems, prepare, unknown_tags, unsafe_code

log = logging.getLogger("widget-local-preview")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SAMPLE_PHOTO = ("data:image/svg+xml;utf8," + urllib.parse.quote(
    '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="750"><rect width="100%" height="100%" fill="#c9c4b8"/>'
    '<text x="50%" y="50%" font-family="sans-serif" font-size="36" fill="#555" text-anchor="middle">sample photo</text></svg>'))


class StoreError(Exception):
    def __init__(self, status: str, detail: str = ""):
        super().__init__(detail or status)
        self.status, self.detail = status, detail


def free_port() -> int | None:
    """A port nothing listens on now, so an old preview server can't answer instead.

    None when this computer won't let a program listen at all (some assistants run commands in a closed box).
    The page still works then: it is opened as a file.
    """
    try:
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]
    except OSError:
        return None


def full_links(value):
    """Every link that starts with `//` gets `https:` in front, all the way down. Loox sends photo links without
    the `https:`, which a served page fills in and a page opened as a file can't: there the photos stay blank."""
    if isinstance(value, str):
        return "https:" + value if value.startswith("//") else value
    if isinstance(value, list):
        return [full_links(v) for v in value]
    if isinstance(value, dict):
        return {k: full_links(v) for k, v in value.items()}
    return value


def host_of(store: str) -> str:
    h = re.sub(r"^https?://|/.*$", "", store.strip())
    return h if "." in h else f"{h}.myshopify.com"


# The only hosts a store's Loox address may point at. The address comes from the store's own page, so it is
# checked before anything is read from it.
LOOX_HOSTS = ("loox.io", "loox.app")


def is_loox_host(host: str | None) -> bool:
    host = (host or "").lower().rstrip(".")
    return any(host == h or host.endswith("." + h) for h in LOOX_HOSTS)


def loox_root(value: str) -> str:
    """The Loox address a store page carries, accepted only on a Loox host and always read over https. No file: or other hosts."""
    try:
        u = urllib.parse.urlparse(value.strip())
        port = u.port
    except ValueError as e:
        raise StoreError("fetch_failed", f"the store's Loox address is not a web address: {value[:80]!r}") from e
    # An http address on a Loox host is read over https instead. Every other scheme and host is refused.
    if u.scheme not in ("https", "http") or not is_loox_host(u.hostname) or u.username or u.password or u.query or u.fragment:
        raise StoreError("fetch_failed", f"the store's Loox address is not a Loox https address, so nothing was read from it: {value[:80]!r}")
    return f"https://{u.hostname.lower()}" + (f":{port}" if port else "") + u.path.rstrip("/")


class HttpsOnlyRedirects(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only to another https address."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlparse(newurl).scheme != "https":
            raise urllib.error.URLError(f"refused a redirect to a non-https address: {newurl[:80]}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def opener_for(host: str, password: str | None) -> urllib.request.OpenerDirector:
    """A URL opener with a cookie jar. With a password it unlocks the storefront first.

    Built by hand, not with build_opener: that one also opens file:, ftp: and data: addresses.
    """
    op = urllib.request.OpenerDirector()
    for h in (urllib.request.HTTPSHandler(), urllib.request.HTTPDefaultErrorHandler(), urllib.request.HTTPErrorProcessor(),
              HttpsOnlyRedirects(), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.UnknownHandler()):
        op.add_handler(h)
    op.addheaders = [("User-Agent", UA)]
    if password:
        data = urllib.parse.urlencode({"form_type": "storefront_password", "utf8": "✓", "password": password}).encode()
        try:
            op.open(f"https://{host}/password", data=data, timeout=30).read()
        except urllib.error.URLError as e:
            raise StoreError("fetch_failed", f"storefront password page: {e}") from e
    return op


def get(op: urllib.request.OpenerDirector, url: str, loox: bool = False) -> tuple[str, str]:
    """Returns (final url, body). With `loox`, the answer must still come from a Loox host after any redirect."""
    try:
        with op.open(url, timeout=30) as r:
            final = r.geturl()
            if loox and not is_loox_host(urllib.parse.urlparse(final).hostname):
                raise StoreError("fetch_failed", f"Loox's address redirected to another host, so nothing was read: {final[:80]}")
            return final, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raise StoreError("fetch_failed", f"{url} answered {e.code}") from e
    except urllib.error.URLError as e:
        raise StoreError("fetch_failed", f"{url}: {e.reason}") from e


# The widget keeps the written-in reviews only when the snapshot's sort matches the store's sort setting
# (parseReviewFeed). Otherwise it asks Loox's server, which refuses a local page, and the page comes up empty.
SORTS = {"featured": "featured", "newest": "newest", "highestRatings": "highest_ratings",
         "lowestRatings": "lowest_ratings", "smartVisualSorting": None}  # None: no ?sort=, the store's own order


def sort_from_bundle(js: str) -> str | None:
    """The store's sort setting, as baked into its reviews-widget.js config (display.sortOrder)."""
    m = re.search(r'"sortOrder":"([A-Za-z_]+)"', js)
    return m.group(1) if m and m.group(1) in SORTS else None


def parts_from_bundle(js: str) -> list[str]:
    """Every part the store's widget script defines. The docs list misses some shipped parts (lxrw-rating-average-text)."""
    return sorted(set(re.findall(r'customElements\.define\("((?:lxrw|loox)-[a-z0-9-]+)"', js)))


def settings_from_bundle(js: str) -> dict:
    """The store's Loox display settings, as baked into its reviews-widget.js (`__LX_REVIEWS_WIDGET_CONFIG.display`)."""
    k = "__LX_REVIEWS_WIDGET_CONFIG="
    i = js.find(k)
    if i < 0:
        return {}
    try:
        return json.JSONDecoder().raw_decode(js[i + len(k):])[0].get("display") or {}
    except json.JSONDecodeError:
        return {}


class Unless:
    """A setting that shows its part only at one value (or, with `truthy`, any truthy value): missing hides it too."""
    def __init__(self, shown: str | None = None, truthy: bool = False):
        self.shown, self.truthy = shown, truthy

    def hides(self, value) -> bool:
        return not value if self.truthy else value != self.shown


# Store settings that switch a part off for every widget on the store (read from the widget's
# behavior, 2026-11-03). (setting, value that hides, parts, what the shopper loses)
HIDING = [
    ("write_button_visibility", "hidden", ["lxrw-header-write-button", "lxrw-empty-state"],
     "the write-a-review button, and the \"be the first\" link on a product with no reviews"),
    # No part listed: the sort button still draws, with only the Loox mark in its dropdown.
    ("widget_sorting_menu", Unless("on"), [],
     "the sort options: keep the sort button, its dropdown holds only the Loox mark"),
    ("rating_distribution", Unless("on"), ["lxrw-header-distribution-list"], "the star breakdown"),
    ("disableFilterReviewRating", True, ["lxrw-header-distribution-list"], "filtering by stars: the breakdown rows don't filter"),
    ("verifiedMode", "never", ["lxrw-review-verified-badge"], "the verified mark"),
    ("reviewDateDisplay", "hidden", ["lxrw-review-date"], "the review date"),
    # The widget reads these as yes or no, so a missing setting hides the label too.
    ("badgeForIncentive", Unless(truthy=True), ["lxrw-review-incentivized-badge"], "the \"Rewarded\" label"),
    ("badgeForIncentiveReviewers", Unless(truthy=True), ["lxrw-review-rewarded-badge"], "the \"Incentivized\" label"),
    ("itemTypeDisplay", Unless("shown"), ["lxrw-review-item-type"], "the purchased item on each review"),
    # "Hide Loox branding". With the sort options off too, the sort menu draws nothing (added below).
    ("brandingDisplay", "hidden", [], "the Loox mark in the sort menu"),
]


def hidden_by_settings(display: dict) -> list[dict]:
    """Parts the store's own Loox settings switch off. A widget can't turn them back on: only the setting can."""
    out = []
    for key, value, parts, loses in HIDING:
        if isinstance(value, Unless):
            # The widget compares with the one shown value.
            if display and value.hides(display.get(key)):
                out.append({"setting": key, "value": display.get(key), "parts": parts, "hides": loses})
        elif key in display and display[key] == value:
            out.append({"setting": key, "value": value, "parts": parts, "hides": loses})
    if display.get("brandingDisplay") == "hidden" and display.get("widget_sorting_menu") != "on":
        out.append({"setting": "brandingDisplay + widget_sorting_menu", "value": "hidden + off",
                    "parts": ["lxrw-header-sort-menu"], "hides": "the whole sort menu"})
    return out


def read_store(host: str, product: str, password: str | None, limit: int) -> dict:
    """Read Loox's store details, the store's sort setting and the product's reviews. Three requests."""
    op = opener_for(host, password)
    final, page = get(op, f"https://{host}/products/{product}")
    if "/password" in urllib.parse.urlparse(final).path:
        raise StoreError("bad_password" if password else "needs_password")
    def lx(key: str) -> str | None:
        m = re.search(rf"__{key}:\s*([^;\"'<]+)", page)
        return m.group(1).strip() if m else None
    cid, root, ver = lx("LXC"), loox_root(lx("LXR") or "https://loox.io"), lx("LXV")
    if not cid:
        m = re.search(r"loox\.io/widget/([A-Za-z0-9_-]+)/", page)
        cid = m.group(1) if m else None
    if not cid:
        raise StoreError("no_loox", "no Loox details on the product page: is Loox installed and on?")
    m = re.search(r'"product":\{"id":(\d+)', page) or re.search(r'product-id="(\d+)"', page)
    if not m:
        raise StoreError("no_product", f"no product id on /products/{product}: check the handle")
    pid = m.group(1)
    t = re.search(r'<meta property="og:title" content="([^"]*)"', page) or re.search(r"<title>\s*([^<]*?)\s*</title>", page)
    notes = []
    _, js = get(op, f"{root}/widget/{cid}/reviews-widget/reviews-widget.js?h={urllib.parse.quote(ver or '')}", loox=True)
    sort = sort_from_bundle(js)
    if not sort:
        sort = "featured"
        notes.append("WARNING: couldn't read the store's sort setting from the widget script; assumed featured. If the local page shows no reviews, that's why")
    param = f"&sort={SORTS[sort]}" if SORTS[sort] else ""
    # limit 20 can serve a stale cached page after an import, so read another size.
    _, body = get(op, f"{root}/widget/{cid}/{pid}/reviews-data?page=1&limit={limit}{param}", loox=True)
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise StoreError("fetch_failed", f"reviews answer is not JSON: {body[:120]}") from e
    return {"host": host, "product": product, "product_id": pid, "title": html.unescape(t.group(1)) if t else product,
            "client_id": cid, "root": root, "version": ver, "read_at": datetime.now(timezone.utc).isoformat(),
            "sort": sort, "limit": limit, "notes": notes, "display": settings_from_bundle(js), "data": data,
            "icons": icons_from_page(page), "parts": parts_from_bundle(js),
            # True when the product page carries Loox's core script. A widget built here loads nothing itself, so
            # with this off it shows nothing on the store.
            "app_embed": bool(CORE_SCRIPT.search(page))}


def icons_from_page(page_html: str) -> str:
    """The store's rating icon sheet. Every Loox star draws from it; the product page carries it, a local page doesn't."""
    m = re.search(r'<svg\b[^>]*\bid="loox-rating-icon-svg-store".*?</svg>', page_html, re.S)
    return m.group(0) if m else ""


def to_api(e: dict) -> dict:
    """A snapshot review back in the live answer's shape (the reverse of to_entry), so a local answer can carry samples."""
    r = {"_id": e["id"], "rating": e["rating"], "review": e.get("review", ""), "nickname": e.get("author", ""),
         "date": int(datetime.fromisoformat(e["date"].replace("Z", "+00:00")).timestamp() * 1000)}
    for src, dst in (("verified", "verified"), ("incentivized", "incentivized"), ("incentiveType", "incentiveType"),
                     ("language", "detectedLanguage"), ("country", "country"), ("reply", "reply"), ("highlight", "highlight"),
                     ("product", "product")):
        if e.get(src):
            r[dst] = e[src]
    if e.get("repliedAt"):
        r["replied_at"] = int(datetime.fromisoformat(e["repliedAt"].replace("Z", "+00:00")).timestamp() * 1000)
    if e.get("media"):
        r["media"] = [{"type": "video" if m["t"] == "video" else "photo", "image": m["src"],
                       **{b: m[a] for a, b in (("w", "imageWidth"), ("h", "imageHeight"), ("alt", "altText")) if m.get(a)}}
                      for m in e["media"]]
    return r


def answer_for(reviews: list[dict]) -> dict:
    """A live reviews answer for these reviews: the breakdown and average counted from them."""
    n = len(reviews)
    return {"status": "visible", "reviews": reviews,
            "bottomline": {"average": round(sum(r["rating"] for r in reviews) / n, 1) if n else 0, "count": n},
            "distribution": [{"stars": s, "reviews": sum(1 for r in reviews if r["rating"] == s)} for s in (5, 4, 3, 2, 1)],
            "pagination": {"hasMore": False, "total": n}, "activeTab": "product",
            "tabs": {"productTotal": n, "storeTotal": 0, "showTabs": False}}


# Loox refuses the widget's reviews request from a local page, so the page answers it from what local_preview read:
# the same filter by stars and the same paging, through the reviews in the answer.
LIVE_JS = """<script>(function(){var A=%s,f=window.fetch;window.fetch=function(u,o){var s=String(u&&u.url||u);
if(s.indexOf('/reviews-data')<0)return f.apply(this,arguments);var q=new URL(s,location.href).searchParams,
rt=q.get('rating'),pg=+q.get('page')||1,lm=+q.get('limit')||20,all=A.reviews.filter(function(r){return!rt||String(r.rating)===rt}),
d=Object.assign({},A,{reviews:all.slice((pg-1)*lm,pg*lm),pagination:{hasMore:pg*lm<all.length,total:all.length,nextPage:pg+1}});
return Promise.resolve(new Response(JSON.stringify(d),{status:200,headers:{'Content-Type':'application/json'}}));};})();</script>"""


def live_head(answer: dict) -> str:
    return LIVE_JS % json.dumps(answer, ensure_ascii=False).replace("</", "<\\/")


# The core script the Loox app embed (or an older Loox install) puts on every storefront page: /widget/<id>/loox.<time>.js.
CORE_SCRIPT = re.compile(r"widget\\?/[A-Za-z0-9_-]+\\?/loox\.\d+\.js")


def loader_head(store: dict) -> str:
    """What the store's Loox app embed does on a real page: say which store this is and load the widget script.

    A local page has no app embed, so the page shell carries it. The widget code never does.
    """
    root = loox_root(store["root"])  # checked again here: store-data.json is a file on disk, and this becomes a script address
    cid, ver = str(store["client_id"]), urllib.parse.quote(str(store.get("version") or ""))
    if not re.fullmatch(r"[A-Za-z0-9_-]+", cid):
        raise StoreError("fetch_failed", f"the store's Loox id is not an id: {cid[:40]!r}")
    return (f"<script>window.LOOX = window.LOOX || {{}}; window.LOOX.root = {json.dumps(root)}; window.LOOX.clientId = {json.dumps(cid)};</script>"
            f'<script src="{html.escape(root, quote=True)}/widget/{cid}/reviews-widget/reviews-widget.js?h={ver}" defer></script>')


def iso(ms: int | None) -> str | None:
    return datetime.fromtimestamp(ms / 1000, timezone.utc).isoformat().replace("+00:00", "Z") if ms else None


def to_entry(r: dict) -> dict:
    """One review from the reviews API, in the snapshot format the widget reads."""
    e = {"id": r["_id"], "rating": r["rating"], "review": r.get("review") or "", "author": r.get("nickname") or "",
         "date": iso(r.get("date")) or datetime.now(timezone.utc).isoformat()}
    if r.get("verified"):
        e["verified"] = True
    if r.get("incentivized"):
        e["incentivized"] = True
    for src, dst in (("detectedLanguage", "language"), ("country", "country"), ("reply", "reply"), ("highlight", "highlight")):
        if r.get(src):
            e[dst] = r[src]
    if r.get("replied_at"):
        e["repliedAt"] = iso(r["replied_at"])
    media = []
    for m in r.get("media") or []:
        src = m.get("image") or m.get("src")
        if src:
            item = {"t": "video" if m.get("type") == "video" else "photo", "src": src}
            for a, b in (("imageWidth", "w"), ("imageHeight", "h"), ("altText", "alt")):
                if m.get(a):
                    item[b] = m[a]
            media.append(item)
    if media:
        e["media"] = media
    if isinstance(r.get("product"), dict) and r["product"].get("id"):
        e["product"] = {k: v for k, v in r["product"].items() if k in ("id", "url", "handle", "name", "imageUrl")}
    return e


def snapshot(entries: list[dict], sort: str = "featured") -> str:
    snap = {"version": 1, "updatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "sort": sort,
            "reviews": entries}
    return json.dumps(snap, ensure_ascii=False).replace("</", "<\\/")


_TAG = re.compile(r"{%-?\s*(if|elsif|else|endif|unless|endunless|assign)\b(.*?)-?%}", re.S)
_CMP = re.compile(r"^(.+?)\s*(==|!=|>=|<=|>|<|\bcontains\b)\s*(.+)$")
_EMPTY = object()  # Liquid's `blank` / `empty`


def _value(tok: str, values: dict, unknown: list[str]):
    """One operand: a literal, or a value the local page knows. A value it doesn't know is nil, as on Liquid."""
    tok = tok.strip()
    if tok in ("blank", "empty"):
        return _EMPTY
    if tok in ("nil", "null"):
        return None
    if tok in ("true", "false"):
        return tok == "true"
    if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in "'\"":
        return tok[1:-1]
    if re.fullmatch(r"-?\d+(\.\d+)?", tok):
        return float(tok) if "." in tok else int(tok)
    if tok not in values and tok.endswith(".value") and tok[:-6] in values:
        tok = tok[:-6]  # a metafield's .value is the metafield itself here
    if tok in values:
        v = values[tok]
        return (float(v) if "." in v else int(v)) if isinstance(v, str) and re.fullmatch(r"-?\d+(\.\d+)?", v) else v
    if tok not in unknown:
        unknown.append(tok)
    return None


def _is_empty(v) -> bool:
    return v is None or v is False or (isinstance(v, str) and not v.strip()) or (isinstance(v, (list, dict)) and not v)


def _compare(a, op: str, b) -> bool:
    if a is _EMPTY or b is _EMPTY:
        same = _is_empty(b if a is _EMPTY else a)
        return same if op == "==" else (not same if op == "!=" else False)
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    if op == "contains":
        return isinstance(a, str) and isinstance(b, str) and b in a
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or isinstance(a, bool) or isinstance(b, bool):
        return False  # Liquid compares nil or text to a number as false
    return {">": a > b, "<": a < b, ">=": a >= b, "<=": a <= b}[op]


def _condition(text: str, values: dict, unknown: list[str]) -> bool:
    """`a == b or c and d`, read right to left as Liquid does: a == b or (c and d)."""
    # Split on and/or only outside quotes: `title == "a and b"` is one comparison.
    parts = re.split(r"""\s+(and|or)\s+(?=(?:[^"']*["'][^"']*["'])*[^"']*$)""", text.strip())
    def one(c: str) -> bool:
        m = _CMP.match(c)
        if m:
            return _compare(_value(m.group(1), values, unknown), m.group(2).strip(), _value(m.group(3), values, unknown))
        v = _value(c, values, unknown)
        return v is not None and v is not False and v is not _EMPTY
    result = one(parts[-1])
    for i in range(len(parts) - 3, -1, -2):
        result = (one(parts[i]) or result) if parts[i + 1] == "or" else (one(parts[i]) and result)
    return result


_KEEP = re.compile(r"{%-?\s*(for|comment|raw)\b.*?{%-?\s*end\1\s*-?%}", re.S)


def run_liquid(code: str, values: dict) -> tuple[str, list[str], list[str]]:
    """Run `assign`, `if` / `elsif` / `else` / `unless` and `{{ value | filters }}` for the values a local page knows.

    One pass in code order, as Liquid does: an `assign` inside a branch that isn't taken never runs, and `{{ x }}`
    shows x as it is at that point. Returns the code, the names it didn't know (counted as empty) and problems (an
    unclosed `if`). A `for`, `comment` or `raw` block is left as it is, so the leftover warning names it.
    """
    unknown: list[str] = []
    problems: list[str] = []
    kept: list[str] = []
    def keep(m: re.Match) -> str:
        kept.append(m.group(0))
        return f"\x00{len(kept) - 1}\x00"
    code = _KEEP.sub(keep, code)
    values = dict(values)
    tokens = _TAG.split(code)  # text, tag, args, text, tag, args, ...
    pos = 0
    def block(closers: tuple[str, ...], live: bool) -> tuple[str, str]:
        nonlocal pos
        out = []
        while pos < len(tokens):
            if pos % 3 == 0:
                if live:
                    out.append(_filters(tokens[pos], values, unknown))
                pos += 1
                continue
            tag, args = tokens[pos], tokens[pos + 1]
            if tag in closers:
                return "".join(out), tag
            pos += 2
            if tag == "assign":
                if live:
                    m = re.match(r"\s*([\w.]+)\s*=\s*(.*?)\s*$", args, re.S)
                    ok, v = _expr(m.group(2), values, unknown) if m else (False, None)
                    if ok:
                        values[m.group(1)] = v
                    else:
                        out.append("{% assign" + args + "%}")  # a filter it can't run: leave it for the warning
                continue
            if tag in ("if", "unless"):
                end = "endif" if tag == "if" else "endunless"
                taken, chosen = False, ""
                cond = live and (_condition(args, values, unknown) != (tag == "unless"))
                while True:
                    body, stop = block(("elsif", "else", end), cond)
                    if cond:
                        chosen, taken = body, True
                    if stop != end and pos >= len(tokens):
                        problems.append(f"an unclosed {{% {tag}{args}%}}")
                        break
                    if stop == end:
                        pos += 2
                        break
                    stop_args = tokens[pos + 1]
                    pos += 2
                    # Liquid tries the branches in order and stops at the first true one.
                    cond = live and not taken and (stop == "else" or _condition(stop_args, values, unknown))
                out.append(chosen)
            elif live:
                out.append("{% " + tag + args + "%}")  # a stray closer: leave it for the warning
        return "".join(out), ""
    body, _ = block((), True)
    return re.sub(r"\x00(\d+)\x00", lambda m: kept[int(m.group(1))], body), unknown, problems


_NUM = {"times": lambda a, b: a * b, "divided_by": lambda a, b: a / b if isinstance(a, float) or isinstance(b, float) else a // b,
        "plus": lambda a, b: a + b, "minus": lambda a, b: a - b}


def _expr(expr: str, values: dict, unknown: list[str]) -> tuple[bool, object]:
    """`value | filter: arg | ...` -> (ran, result). A filter it can't run gives (False, None)."""
    parts = [s.strip() for s in expr.split("|")]
    v = _value(parts[0], values, unknown)
    for f in parts[1:]:
        name, _, arg = f.partition(":")
        name, a = name.strip(), _value(arg, values, unknown) if arg else None
        if name == "default":
            v = a if _is_empty(v) else v
        elif name in _NUM and isinstance(v, (int, float)) and isinstance(a, (int, float)):
            if name == "divided_by" and a == 0:
                return False, None  # Liquid prints "divided by 0"; leave it for the leftover warning
            v = _NUM[name](v, a)
        elif name == "round" and isinstance(v, (int, float)):
            # Liquid rounds half up (4.25 -> 4.3), not Python's half to even.
            places = int(a or 0)
            d = Decimal(str(v)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
            v = float(d) if places else int(d)
        elif name in ("floor", "ceil") and isinstance(v, (int, float)):
            v = math.floor(v) if name == "floor" else math.ceil(v)
        else:
            return False, None
    return True, v


def _text(v) -> str:
    return "" if v is None else ("true" if v is True else "false" if v is False else str(v))


def _filters(code: str, values: dict, unknown: list[str]) -> str:
    """`{{ value | times: 1.0 | round: 1 }}` and friends. Anything else stays for the leftover warning."""
    def out(m: re.Match) -> str:
        expr = m.group(1).strip()
        if "|" not in expr:
            if expr in values:
                return html.escape(_text(values[expr]), quote=True)  # plain output keeps its text ("0123")
            v = _value(expr, {}, [])
            return html.escape(_text(v), quote=True) if v is not None and not re.fullmatch(r"[\w.]+", expr) or isinstance(v, (int, float)) else m.group(0)
        ok, v = _expr(expr, values, unknown)
        return html.escape(_text(v), quote=True) if ok else m.group(0)
    return re.sub(r"{{-?\s*(.*?)\s*-?}}", out, code, flags=re.S)


def render(code: str, store: dict, entries: list[dict], average: float, count: int, only_photos: bool | None = None) -> tuple[str, list[str]]:
    """Turn the widget code into plain HTML for a local page: Liquid filled in, reviews written into the root."""
    notes: list[str] = []
    code, prep_notes = prepare(code, "local-preview")
    notes += [n for n in prep_notes if n.startswith("WARNING")]
    code = re.sub(r"{%-?\s*assign loox_(meta|hash|root|client_id)\b.*?-?%}\n?", "", code)
    values = {"loox_root": store["root"], "loox_client_id": store["client_id"], "loox_hash": store["version"] or "",
              "product.id": store["product_id"], "product.handle": store["product"], "product.title": store["title"],
              "product.metafields.loox.avg_rating": f"{average:g}", "product.metafields.loox.num_reviews": str(count),
              "shop.name": store["host"], "product": store["product"]}
    code, unknown, problems = run_liquid(code, values)
    notes += [f"WARNING: {x}: the local page shows everything after it" for x in problems]
    if unknown:
        notes.append("Liquid values the local page doesn't know, counted as empty here (the store fills them): " + ", ".join(unknown[:5]))
    left = sorted(set(re.findall(r"{{.*?}}|{%.*?%}", code, flags=re.S)))
    if left:
        notes.append("WARNING: Liquid the local page can't run, left out here (the store runs it): " + ", ".join(x[:60] for x in left[:5]))
        code = re.sub(r"{{.*?}}|{%.*?%}", "", code, flags=re.S)
    if only_photos is not None:
        val = "true" if only_photos else "false"
        def set_photos(m: re.Match) -> str:
            tag = m.group(0)
            if re.search(r'\sonly-photos="[^"]*"', tag):
                return re.sub(r'only-photos="[^"]*"', f'only-photos="{val}"', tag)
            return tag.replace("<loox-reviews-widget", f'<loox-reviews-widget only-photos="{val}"', 1)
        code = re.sub(r"<loox-reviews-widget\b[^>]*>", set_photos, code)
    snap = f'<script type="application/json" slot="reviews">{snapshot(entries, store.get("sort", "featured"))}</script>'
    if re.search(r'<script type="application/json" slot="reviews">\s*</script>', code):
        code = re.sub(r'<script type="application/json" slot="reviews">\s*</script>', lambda _: snap, code, count=1)
    else:
        code = re.sub(r"(<loox-reviews-widget\b[^>]*>)", lambda m: m.group(1) + "\n" + snap, code, count=1)
    return code, notes


def page(body: str, title: str, rtl: bool = False, extra_head: str = "", icons: str = "") -> str:
    return (f'<!doctype html><html lang="{"he" if rtl else "en"}" dir="{"rtl" if rtl else "ltr"}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>{extra_head}'
            '<style>body{margin:0;padding:24px 16px;background:#fff;font-family:system-ui,sans-serif}'
            '.lx-local{max-width:1200px;margin:0 auto}</style></head>'
            f'<body>{icons}<div class="lx-local">{body}</div></body></html>')


def sample(base: dict, n: int, **over) -> dict:
    e = {k: v for k, v in base.items() if k not in ("media", "reply", "repliedAt", "incentivized", "highlight", "product")}
    e.update({"id": f"sample-{n}", "author": f"Sample {n}.", "review": f"Sample review {n}."})
    e.update(over)
    for flag in ("verified", "incentivized"):
        if e.get(flag) is not True:
            e.pop(flag, None)  # the snapshot omits a flag that isn't set, never writes false
    return e


def states(real: list[dict]) -> list[tuple[str, str, list[dict], dict]]:
    """(key, label, reviews, options) for every review state. Real reviews where the store has them."""
    base = real[0] if real else {"rating": 5, "review": "Sample review text.", "date": datetime.now(timezone.utc).isoformat()}
    photo = next((r for r in real if r.get("media")), None)
    no_photo = [{k: v for k, v in r.items() if k != "media"} for r in real] or [sample(base, 1)]
    many = list(real)
    while len(many) < 24:
        many.append(sample(base, len(many) + 1, review=f"Sample review {len(many) + 1}, added so the sheet has more than one page."))
    long_text = ("Sample long review. " + "The fit is right, the material feels good, and it arrived two days early. ") * 12
    pics = [{"t": "photo", "src": SAMPLE_PHOTO}] * 4
    out = [
        ("none", "No reviews. Loox's \"be the first\" message needs the live store, so it shows on the hidden page, not here", [], {"count": 0, "average": 0}),
        ("one", "One review" + ("" if real else " (sample)"), (real or [sample(base, 1)])[:1], {}),
        ("few", "Three reviews", (real + [sample(base, i) for i in range(1, 4)])[:3], {}),
        ("many", "Many reviews, more than one page", many, {"count": max(len(many), 60)}),
        ("no-photo", "No photos", no_photo[:6], {}),
        ("photos", "Several photos and a video (sample photos)" if not photo else "With photos (real) plus a sample video",
         ([photo] if photo else []) + [sample(base, 1, media=pics), sample(base, 2, media=[{"t": "video", "src": SAMPLE_PHOTO}])], {}),
        ("long", "Very long text and stars only (samples)", [sample(base, 1, review=long_text), sample(base, 2, review="")] + real[:2], {}),
        ("low", "Low ratings (samples)", [sample(base, 1, rating=1, review="Sample 1-star review: it broke after a week."),
                                          sample(base, 2, rating=2, review="Sample 2-star review: smaller than I expected.")] + real[:2], {}),
        ("reply", "Store reply (sample reply)", [sample(base, 1, reply="Sample store reply: thank you, we're glad it arrived on time!",
                                                        repliedAt=base["date"])] + real[:2], {}),
        ("labels", "Verified and not verified (samples)",
         [sample(base, 1, verified=True), sample(base, 2, verified=False), sample(base, 3, verified=True)], {}),
        ("photos-only", "Photos only switched on", [r for r in many if r.get("media")] or [sample(base, 1, media=pics)], {"only_photos": True}),
    ]
    return out


STATE_NAMES = {"none": "No reviews", "one": "One review", "few": "Three reviews", "many": "Many pages", "no-photo": "No photos",
               "photos": "Photos and video", "long": "Long text, stars only", "low": "Low ratings", "reply": "Store reply",
               "labels": "Labels", "photos-only": "Photos only"}
PILLS = {"ok": "Looks right", "fixed": "Fixed", "designed": "Designed", "check": "Check yourself", "unchecked": "Not checked"}


def _rgb(v, fallback: str) -> str:
    m = re.search(r"(\d+)[ ,]+(\d+)[ ,]+(\d+)", v or "")
    return f"rgb({m.group(1)} {m.group(2)} {m.group(3)})" if m else fallback


def theme_from_look(look: dict | None) -> dict:
    """The sheet's colors and fonts from store_look.py's `look`, so the page looks like the store, not like a test tool."""
    look = (look or {}).get("look", look or {})
    v = look.get("vars", {})
    body = look.get("page", {}).get("font-family") or "system-ui, sans-serif"
    head = look.get("heading", {}).get("font-family") or body
    return {"ink": _rgb(v.get("--color-foreground") or look.get("page", {}).get("color"), "rgb(20 20 20)"),
            "paper": _rgb(v.get("--color-background") or look.get("page", {}).get("background-color"), "rgb(255 255 255)"),
            "accent": _rgb(v.get("--color-primary-hover") or v.get("--color-primary"), "rgb(40 90 200)"),
            "soft": _rgb(v.get("--color-primary-button-background"), "rgb(236 236 236)"),
            "line": _rgb(v.get("--color-border"), "rgb(230 230 230)"),
            "body": body, "head": head, "radius": look.get("button", {}).get("border-radius") or "12px"}


SHEET_CSS = """
:root{--muted:color-mix(in srgb,var(--ink) 55%,var(--paper));--tint:color-mix(in srgb,var(--soft) 35%,var(--paper))}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--tint);color:var(--ink);font:15px/1.5 var(--body)}
.hero{padding:40px 32px 28px;background:var(--paper);border-bottom:1px solid var(--line)}
.hero small{display:block;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:12px;margin-bottom:6px}
.hero h1{margin:0;font:400 40px/1.1 var(--head)}.hero p{margin:8px 0 0;color:var(--muted)}
.wrap{display:grid;grid-template-columns:240px minmax(0,1fr);gap:32px;max-width:1500px;margin:0 auto;padding:32px}main{min-width:0}
nav{position:sticky;top:24px;align-self:start;display:flex;flex-direction:column;gap:2px}
nav a{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:9px 12px;border-radius:10px;color:var(--ink);text-decoration:none;font-size:14px}
nav a:hover,nav a.on{background:var(--paper)}nav .pill{font-size:10px;padding:2px 7px}
.pill{font-style:normal;font-size:12px;font-weight:600;padding:3px 10px;border-radius:999px;white-space:nowrap}
.pill.ok,.pill.unchecked{background:var(--paper);color:var(--muted);border:1px solid var(--line)}
.pill.fixed,.pill.designed{background:var(--accent);color:var(--paper)}.pill.check{background:rgb(255 214 102);color:rgb(80 60 0)}
.state{background:var(--paper);border-radius:20px;padding:24px;margin:0 0 28px;scroll-margin-top:24px}
.state header{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.state h2{margin:0;font:400 26px/1.2 var(--head)}
.state .src{margin-left:auto;color:var(--muted);font-size:12px}.note{margin:8px 0 0;color:var(--muted);max-width:70ch}
.frames{display:flex;gap:28px;align-items:flex-start;margin-top:20px}figure{margin:0}
.browser{flex:1;min-width:0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--paper);box-shadow:0 8px 30px rgb(0 0 0 / .06)}
.bar{display:flex;align-items:center;gap:6px;padding:10px 14px;background:color-mix(in srgb,var(--line) 45%,var(--paper));border-bottom:1px solid var(--line)}
.bar b{width:11px;height:11px;border-radius:50%;background:var(--line)}
.bar span{margin-left:12px;font-size:12px;color:var(--muted);background:var(--paper);padding:3px 12px;border-radius:999px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.browser .screen{overflow:hidden}.browser iframe{width:1280px;border:0;transform-origin:0 0;display:block}
.phone{flex:none;width:300px;height:620px;border-radius:46px;background:#111;padding:11px;position:relative;box-shadow:0 12px 40px rgb(0 0 0 / .18)}
.phone .island{position:absolute;top:20px;left:50%;width:84px;height:24px;margin-left:-42px;border-radius:14px;background:#111;z-index:2}
.phone .screen{height:100%;border-radius:36px;overflow:hidden;background:var(--paper);display:flex;flex-direction:column}
.status{flex:none;height:44px;display:flex;justify-content:space-between;align-items:center;padding:6px 26px 0;font:600 12px var(--body)}
.status span{font-size:8px;letter-spacing:1px}.phone iframe{width:390px;height:777px;border:0;transform:scale(.7128);transform-origin:0 0;display:block}
@media (max-width:900px){.wrap{grid-template-columns:1fr;padding:16px}nav{display:none}.frames{flex-direction:column;align-items:center}.browser{width:100%}}
"""
SHEET_JS = """<script>
const S=[...document.querySelectorAll('.state')],N=[...document.querySelectorAll('nav a')];
function fit(){document.querySelectorAll('.browser').forEach(b=>{const f=b.querySelector('iframe'),s=b.clientWidth/1280;f.style.transform='scale('+s+')';
 try{const h=f.contentDocument.documentElement.scrollHeight;f.style.height=h+'px';b.querySelector('.screen').style.height=Math.min(h*s,720)+'px'}catch(e){}})}
setInterval(fit,800);addEventListener('resize',fit);
const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){const k=S.indexOf(x.target);N.forEach((a,j)=>a.classList.toggle('on',j===k))}}),{rootMargin:'-40% 0px -55% 0px'});
S.forEach(s=>io.observe(s));
// Checks wait on this, not on a selector: every state is in its own iframe.
window.__statesReady=Promise.all([...document.querySelectorAll('iframe')].map(f=>new Promise(r=>{f.addEventListener('load',r,{once:true});setTimeout(r,8000)})));
</script>"""


def sheet(code: str, store: dict, real: list[dict], average: float, count: int, look: dict | None = None,
          notes: dict | None = None) -> tuple[str, list[str]]:
    """Every review state on one designed page: a side list with a status per state, browser and iPhone frames.

    `notes` is Claude's check, per state key: {"status": ok|fixed|designed|check, "note": "..."}. A state without
    one reads "Not checked", so an unchecked page never looks approved.
    """
    out_notes: list[str] = []
    th, notes = theme_from_look(look), notes or {}
    url = html.escape(f"{store['host']}/products/{store['product']}")
    nav, parts, counts = [], [], {}
    for key, label, revs, opt in states(real):
        avg = opt.get("average", round(sum(r["rating"] for r in revs) / len(revs), 1) if revs else 0)
        body, n = render(code, store, revs, avg, opt.get("count", len(revs)), opt.get("only_photos"))
        out_notes += n
        doc = html.escape(page(body, label, extra_head=live_head(answer_for([to_api(r) for r in revs])) + loader_head(store),
                               icons=store.get("icons", "")), quote=True)
        info = notes.get(key) or {}
        status = info.get("status") if info.get("status") in PILLS else "unchecked"
        counts[status] = counts.get(status, 0) + 1
        name = html.escape(STATE_NAMES.get(key, label))
        src = "Sample reviews" if any(str(r.get("id", "")).startswith("sample-") for r in revs) else "Real reviews"
        note = f'<p class="note">{html.escape(info["note"])}</p>' if info.get("note") else ""
        pill = f'<i class="pill {status}">{PILLS[status]}</i>'
        nav.append(f'<a href="#{key}"><span>{name}</span>{pill}</a>')
        parts.append(f'<section class="state" id="{key}"><header><h2>{name}</h2>{pill}<span class="src">{src}</span></header>{note}'
                     f'<div class="frames"><figure class="browser"><div class="bar"><b></b><b></b><b></b><span>{url}</span></div>'
                     f'<div class="screen"><iframe srcdoc="{doc}" title="{name}, desktop"></iframe></div></figure>'
                     f'<figure class="phone"><div class="island"></div><div class="screen"><div class="status"><b>9:41</b><span>●●● ▮</span></div>'
                     f'<iframe srcdoc="{doc}" title="{name}, phone"></iframe></div></figure></div></section>')
    fonts = sorted({f.strip().strip('"\'') for f in f"{th['body']},{th['head']}".split(",")} - {"", "serif", "sans-serif", "system-ui"})
    # One request per family: Google rejects a whole request when one name isn't in its library (a custom font).
    link = "".join(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={html.escape(f.replace(" ", "+"))}:wght@400;600&display=swap">'
                   for f in fonts)
    root = (f":root{{--ink:{th['ink']};--paper:{th['paper']};--accent:{th['accent']};--soft:{th['soft']};--line:{th['line']};"
            f"--radius:{th['radius']};--body:{th['body']};--head:{th['head']}}}")
    total = sum(counts.values())
    summary = f"{total} states · {counts.get('fixed', 0) + counts.get('designed', 0)} fixed or designed · {counts.get('check', 0)} to check yourself"
    if counts.get("unchecked"):
        summary += f" · {counts['unchecked']} not checked"
    title = html.escape(store["title"].split("\n")[0].strip())
    hero = (f'<div class="hero"><small>{html.escape(store["host"])} · review states</small><h1>{title}</h1>'
            f'<p>{summary}. Real reviews where the product has them, samples where it doesn\'t.</p></div>')
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Review states: {title}</title>{link}<style>{root}{SHEET_CSS}</style></head><body>{hero}'
            f'<div class="wrap"><nav>{"".join(nav)}</nav><main>{"".join(parts)}</main></div>{SHEET_JS}</body></html>'), sorted(set(out_notes))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--store", required=True, help="store handle, myshopify domain, storefront domain or a product link")
    ap.add_argument("--product", help="product handle (or pass a product link as --store)")
    ap.add_argument("--code", type=Path, help="the widget code from step 5 (not needed with --settings-only)")
    ap.add_argument("--settings-only", action="store_true",
                    help="only read the store and list the parts its Loox settings hide; no page")
    ap.add_argument("--out", required=True, type=Path, help="folder for index.html, states.html and store-data.json")
    ap.add_argument("--password", help="storefront password, if the store has one")
    ap.add_argument("--password-file", type=Path, help="a private file that holds the storefront password (keeps it off the command line)")
    ap.add_argument("--states", action="store_true", help="also write states.html, the widget in every review state")
    ap.add_argument("--look", type=Path, help="store_look.py's JSON, so the states page uses the store's colors and fonts")
    ap.add_argument("--notes", type=Path, help='JSON per state key: {"none": {"status": "designed", "note": "..."}}')
    ap.add_argument("--refresh", action="store_true", help="read the store again instead of reusing store-data.json")
    ap.add_argument("--limit", type=int, default=50, help="how many reviews to read (1 to 50)")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    try:
        a.password = read_password(a.password, a.password_file)
    except OSError as e:
        print(json.dumps({"status": "error", "detail": f"password file: {e}"}))
        return 1
    prod = re.search(r"/products/([^/?#]+)", a.store)
    product = a.product or (prod.group(1) if prod else None)
    if not product:
        print(json.dumps({"status": "no_product", "detail": "pass --product <handle>"}))
        return 1
    host = host_of(a.store)
    a.out.mkdir(parents=True, exist_ok=True)
    cache = a.out / "store-data.json"
    if not a.settings_only and not a.code:
        print(json.dumps({"status": "error", "detail": "pass --code <widget file>, or --settings-only"}))
        return 1
    try:
        if a.settings_only:
            limit = max(1, min(a.limit, 50))
            store = read_store(host, product, a.password, limit)
            cache.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
            print(json.dumps({"status": "ready", "hidden_by_settings": hidden_by_settings(store.get("display") or {}),
                              "reviews": len(store["data"].get("reviews", [])), "sort": store["sort"],
                              "app_embed": store["app_embed"]}))
            return 0
        code = a.code.read_text(encoding="utf-8")
        bad = liquid_problems(code)
        if bad:
            print(json.dumps({"status": "liquid_error", "detail": bad}))
            return 1
        # Same check as the install, so a design round can't pass and then fail at the end.
        size = len(prepare(code, "ai-local-preview-00000000")[0])
        if size > LIMIT:
            print(json.dumps({"status": "too_big", "chars": size, "limit": LIMIT}))
            return 1
        limit = max(1, min(a.limit, 50))
        store = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() and not a.refresh else None
        if not store or (store.get("host"), store.get("product"), store.get("limit")) != (host, product, limit) or "display" not in store or "icons" not in store or "parts" not in store or "app_embed" not in store:
            store = read_store(host, product, a.password, limit)
            cache.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
        data = full_links(store["data"])  # here, not at the read, so a store-data.json from an older run works too
        real = [to_entry(r) for r in data.get("reviews", [])]
        bl = data.get("bottomline") or {}
        average, count = float(bl.get("average") or 0), int(bl.get("count") or len(real))
        body, notes = render(code, store, real, average, count)
        notes += store.get("notes", [])
        notes += unsafe_code(code)
        (a.out / "index.html").write_text(page(body, f"Local preview: {store['title']}", extra_head=live_head({**answer_for(data.get("reviews", [])), **data}) + loader_head(store),
                                               icons=store.get("icons", "")), encoding="utf-8")
        if not store.get("icons"):
            notes.append("WARNING: no rating icons on the product page, so stars draw blank here. Check them on the hidden page")
        port = free_port()
        file_url = (a.out / "index.html").resolve().as_uri()
        # The page works both served and opened as a file. With no port to listen on, `url` is the file itself.
        result = {"status": "ready", "page": str(a.out / "index.html"),
                  "serve": f'python3 -m http.server {port} --bind 127.0.0.1 --directory "{a.out}"' if port else None,
                  "url": f"http://127.0.0.1:{port}/index.html" if port else file_url, "file_url": file_url, "reviews": len(real),
                  "with_photos": sum(1 for r in real if r.get("media")), "total_on_store": count, "sort": store["sort"],
                  "unknown_parts": unknown_tags(code, set(store.get("parts") or [])), "hidden_by_settings": hidden_by_settings(store.get("display") or {}),
                  "app_embed": store["app_embed"]}
        if a.states:
            look = json.loads(a.look.read_text(encoding="utf-8")) if a.look and a.look.exists() else None
            state_notes = json.loads(a.notes.read_text(encoding="utf-8")) if a.notes and a.notes.exists() else None
            html_sheet, n = sheet(code, store, real, average, count, look, state_notes)
            (a.out / "states.html").write_text(html_sheet, encoding="utf-8")
            states_file = (a.out / "states.html").resolve().as_uri()
            result.update({"states": str(a.out / "states.html"), "states_file_url": states_file,
                           "states_url": f"http://127.0.0.1:{port}/states.html" if port else states_file})
            notes += n
        if not real:
            notes.append("the product has no published reviews: pick a product with reviews and photos")
        result["notes"] = sorted(set(notes))
        print(json.dumps(result))
        return 0
    except StoreError as e:
        print(json.dumps({"status": e.status, "detail": e.detail}))
        return 1
    except Exception as e:  # noqa: BLE001 - one JSON line for Claude, whatever broke
        log.exception("local preview failed")
        print(json.dumps({"status": "error", "detail": f"{type(e).__name__}: {e}"}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
