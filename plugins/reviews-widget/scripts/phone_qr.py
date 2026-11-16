"""Make a page with a QR code for the hidden preview page, so the person can open it on their own phone.

Claude's phone check runs at phone width in a desktop browser. It can't see bugs that only show on a real
phone (iPhone Safari, touch, swipes). This page lets the person scan the link with their phone camera.

No Python packages needed: the page draws the QR code in the browser (qrcode-generator from cdnjs).

Usage:
    python3 phone_qr.py --url "https://mystore.com/products/my-product?view=ai-grid-11031030" --out /tmp/loox-widget-build/grid

Prints one JSON line: {"status": "ready", "page": <path to phone-check.html>, "open": <command that opens it>, "url": <link>}.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

LIB = "https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"
# The library's fingerprint (cdnjs, 2026-11-10). The browser refuses the file if it ever changes.
LIB_SRI = "sha512-ZDSPMa/JM1D+7kdg2x3BsruQ6T/JpJo3jWDWkCZsP+5yVyp1KfESqLI+7RqB5k24F7p2cV7i2YHh/890y6P6Sw=="


def page(url: str, has_password: bool = False) -> str:
    """The password itself is never written on the page: the person knows it."""
    pw = '<p class="pw">The store asks for its storefront password first.</p>' if has_password else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Check it on your phone</title>
<script src="{LIB}" integrity="{LIB_SRI}" crossorigin="anonymous"></script>
<style>
body{{margin:0;font-family:system-ui,sans-serif;background:#f6f6f4;color:#1f1f1f;display:grid;place-items:center;min-height:100vh}}
main{{background:#fff;border-radius:16px;padding:32px;max-width:440px;text-align:center;box-shadow:0 2px 16px rgba(0,0,0,.08)}}
h1{{font-size:22px;margin:0 0 8px}} p{{margin:8px 0;line-height:1.45}}
#qr{{margin:20px auto;width:260px;height:260px}} #qr img,#qr svg{{width:100%;height:100%}}
ol{{text-align:left;padding-left:20px;line-height:1.6}} a{{word-break:break-all;color:#1f1f1f}}
.pw{{background:#fff6dc;border-radius:8px;padding:8px}}
</style></head><body><main>
<h1>Check the widget on your phone</h1>
<p>Point your phone's camera at the code and open the link.</p>
<div id="qr" aria-label="QR code for the preview link"></div>
{pw}
<ol><li>Scroll to the reviews.</li><li>Swipe and tap a few cards.</li><li>Tell Claude "looks good", or send a screenshot of what's off.</li></ol>
<p>Or open this link on your phone:<br><a href="{html.escape(url)}">{html.escape(url)}</a></p>
<p style="color:#666;font-size:13px">Shoppers can't see this page. It opens only with this link.</p>
</main>
<script>
try {{ const q = qrcode(0, "M"); q.addData({json.dumps(url)}); q.make();
  document.getElementById("qr").innerHTML = q.createSvgTag({{ cellSize: 6, margin: 2, scalable: true }}); }}
catch (e) {{ document.getElementById("qr").textContent = "The QR code couldn't load. Use the link below."; }}
</script></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True, help="the hidden preview link (preview_url or link from the install)")
    ap.add_argument("--out", required=True, type=Path, help="folder for phone-check.html")
    ap.add_argument("--has-password", action="store_true", help="the store has a storefront password (the page says so; it never shows it)")
    ap.add_argument("--password", help=argparse.SUPPRESS)  # accepted for old commands, never shown
    a = ap.parse_args()
    u = urlparse(a.url)
    if u.scheme != "https" or not u.netloc:
        print(json.dumps({"status": "bad_url", "detail": "pass the full https link of the hidden page"}))
        return 1
    try:
        a.out.mkdir(parents=True, exist_ok=True)
        f = a.out / "phone-check.html"
        f.write_text(page(a.url, a.has_password or bool(a.password)), encoding="utf-8")
    except OSError as e:
        print(json.dumps({"status": "error", "detail": str(e)}))
        return 1
    print(json.dumps({"status": "ready", "page": str(f), "open": f'open "{f}"', "url": a.url}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
