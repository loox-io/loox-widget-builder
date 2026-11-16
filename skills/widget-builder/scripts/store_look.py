#!/usr/bin/env python3
"""Read a Shopify store's look from its live storefront: colors, fonts and corner radius.

Opens the storefront in ego lite (the person's own browser, so no login is needed for a public store),
gets past a storefront password if one is given, and reads the theme's CSS variables plus the computed
styles of the page, headings and buttons. The widget's tokens are set from this, never guessed.

Usage:
    python3 store_look.py --store mystore.myshopify.com [--password-file <file>] [--space 12]

Prints one JSON line: {"status": "ok"|"needs_password"|"bad_password"|"error", "look": {...}, "space": id}.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from preflight import ego_path, read_password, timed_out_output

JS = r"""
const out = (o) => console.log("RESULT " + JSON.stringify(o));
// Always close the space: nothing reuses it, and a left-open storefront keeps running in ego lite.
const end = async () => { await Promise.race([task.finish({ keep: [] }), new Promise((r) => setTimeout(r, 10000))]).catch(() => {}); process.exit(0); };
const task = CFG.space ? await taskSpace(Number(CFG.space)).catch(() => taskSpace("Widget 2.0 store look")) : await taskSpace("Widget 2.0 store look");
const page = task.page("p1");
const base = { space: task.spaceId };
try {
  const host = CFG.store.includes(".") ? CFG.store : `${CFG.store}.myshopify.com`;
  await page.goto(`https://${host}/`, { waitUntil: "domcontentloaded", timeout: 45000 });
  if ((await page.url()).includes("/password")) {
    if (!CFG.password) { out({ ...base, status: "needs_password" }); await end(); }
    await page.fill("input[type=password]", CFG.password);
    await page.press("input[type=password]", "Enter");
    await page.waitForTimeout(4000);
    if ((await page.url()).includes("/password")) { out({ ...base, status: "bad_password" }); await end(); }
  }
  const look = await page.evaluate(() => {
    const cs = (el) => el ? getComputedStyle(el) : null;
    const pick = (el, props) => { const s = cs(el); return s ? Object.fromEntries(props.map((p) => [p, s.getPropertyValue(p)])) : null; };
    const vars = {};
    for (const sheet of [...document.styleSheets]) {
      let rules; try { rules = sheet.cssRules; } catch { continue; }
      for (const r of [...rules]) {
        if (!r.style || !/^(:root|body|html)\b/.test(r.selectorText || "")) continue;
        for (const name of [...r.style]) {
          if (name.startsWith("--") && /color|font|radius|background|button|accent|text/i.test(name) && Object.keys(vars).length < 60) {
            vars[name] = r.style.getPropertyValue(name).trim().slice(0, 120);
          }
        }
      }
    }
    // querySelector with a list returns the first match in page order, usually a header icon. Try selectors in
    // priority order instead, skipping the header and hidden elements.
    const visible = (e) => !e.closest("header, [role=banner], .header") && e.offsetParent !== null;
    const btn = ["a.button", ".button", ".btn", "button[type=submit]", "button"]
      .map((sel) => [...document.querySelectorAll(sel)].find(visible)).find(Boolean) || null;
    return {
      page: pick(document.body, ["background-color", "color", "font-family", "font-size"]),
      heading: pick(document.querySelector("h1, h2"), ["font-family", "font-weight", "color", "letter-spacing"]),
      button: pick(btn, ["background-color", "color", "border-radius", "font-family"]),
      theme: (window.Shopify && window.Shopify.theme && window.Shopify.theme.name) || null,
      vars,
    };
  });
  out({ ...base, status: "ok", look });
} catch (e) {
  out({ ...base, status: "error", detail: String(e && e.stack || e).slice(0, 600) });
}
await end();
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--store", required=True, help="store handle, myshopify domain or storefront domain")
    ap.add_argument("--password", help="storefront password, if the store has one")
    ap.add_argument("--password-file", type=Path, help="a private file that holds the storefront password (keeps it off the command line)")
    ap.add_argument("--space", help="ego lite task space id to reuse")
    a = ap.parse_args()
    try:
        a.password = read_password(a.password, a.password_file)
    except OSError as e:
        print(json.dumps({"status": "error", "detail": f"password file: {e}"}))
        return 1
    store = a.store.strip().removeprefix("https://").removeprefix("http://").split("/")[0]
    cfg = {"store": store, "password": a.password, "space": a.space}
    ego = ego_path()
    try:
        if not ego:
            raise FileNotFoundError("ego-browser")
        run = subprocess.run([ego, "nodejs"], input=f"const CFG = {json.dumps(cfg)};\n{JS}", capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    except FileNotFoundError:
        print(json.dumps({"status": "error", "detail": "ego lite isn't installed"}))
        return 1
    except subprocess.TimeoutExpired as e:
        text = timed_out_output(e)  # the result may be out already, with only closing the browser stuck
        if "RESULT " not in text:
            print(json.dumps({"status": "error", "detail": "the storefront took over 3 minutes"}))
            return 1
    else:
        text = run.stdout + "\n" + run.stderr
    results = [l[7:] for l in text.splitlines() if l.startswith("RESULT ")]
    if not results:
        print(json.dumps({"status": "error", "detail": text[-600:]}))
        return 1
    print(results[-1])
    return 0 if json.loads(results[-1]).get("status") == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
