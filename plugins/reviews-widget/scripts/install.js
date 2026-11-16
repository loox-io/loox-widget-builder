// Browser half of the Widget 2.0 installer. install.py prepends `const CFG = {...};` and pipes this to `ego-browser nodejs`.
// Prints "STEP ..." progress lines and one final "RESULT {json}" line.
const fs = await import("node:fs/promises");
const out = (o) => { last = o.status; console.log("RESULT " + JSON.stringify(o)); };
const step = (s) => console.log("STEP " + s);
// A finished or closed space is gone; a new one is still logged in, since every space shares the browser profile.
const task = CFG.space ? await taskSpace(Number(CFG.space)).catch(() => taskSpace("Widget 2.0 install")) : await taskSpace("Widget 2.0 install");
const page = task.page("p1");
const base = { space: task.spaceId };
// Close the task space at every exit: a left-open theme editor keeps running in ego lite and heats the computer.
// needs_login is the one exception: the person logs in there and the rerun resumes it with --space.
let last = null;
const end = async () => {
  await page.cdp("Emulation.clearDeviceMetricsOverride", {}).catch(() => {});
  // finish() has hung elsewhere; cap the wait so a good install never reads as a timeout.
  if (last !== "needs_login") await Promise.race([task.finish({ keep: [] }), new Promise((r) => setTimeout(r, 10000))]).catch(() => {});
  process.exit(0);
};
const snap = async (full) => (await page.snapshot(full ? { scope: "full_page" } : undefined)).split("\n");
const refOf = (l) => l && (l.match(/\[ref=(\d+)[,\]]/) || [])[1];
const refBefore = (lines, i, back = 4) => lines.slice(Math.max(0, i - back), i + 1).reverse().map(refOf).find(Boolean);
// Storefronts with slow third-party scripts can take over 15s to reach "load"; the page is usable once the DOM is ready.
const go = (url) => page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
const find = (lines, re, from = 0) => lines.findIndex((l, k) => k >= from && re.test(l));
// Screen text goes back to Claude only as a short view: it is the store's content, and it can hold anyone's words.
const view = (ls, n = 20, w = 80) => ls.slice(0, n).map((l) => l.trim().slice(0, w));

try {
  // 1. Storefront: get in, learn the shop handle and live theme.
  const host = CFG.store.includes(".") ? CFG.store : `${CFG.store}.myshopify.com`;
  step(`open storefront ${host}`);
  await page.cdp("Emulation.clearDeviceMetricsOverride", {});
  await go(`https://${host}/`);
  if ((await page.url()).includes("/password")) {
    if (!CFG.password) { out({ ...base, status: "needs_password", detail: "Storefront is password protected. Pass --password." }); await end(); }
    step("storefront password");
    await page.fill("input[type=password]", CFG.password);
    await page.press("input[type=password]", "Enter");
    await page.waitForTimeout(4000);
    if ((await page.url()).includes("/password")) { out({ ...base, status: "bad_password" }); await end(); }
  }
  const shop = await page.evaluate(async (want) => {
    const S = window.Shopify || {};
    let product = want;
    if (!product) { try { const r = await fetch("/products.json?limit=1"); product = (await r.json()).products?.[0]?.handle || null; } catch (e) {} }
    else { try { if (!(await fetch(`/products/${product}.js`)).ok) product = null; } catch (e) { product = null; } }
    return { shop: S.shop, themeId: S.theme?.id, themeName: S.theme?.name, product };
  }, CFG.product || null);
  if (!shop.shop || !shop.themeId) { out({ ...base, status: "not_shopify", detail: shop }); await end(); }
  if (!shop.product) { out({ ...base, status: "no_product", detail: CFG.product ? `No product "${CFG.product}" on this store.` : "The store has no products." }); await end(); }
  const handle = shop.shop.replace(".myshopify.com", "");
  Object.assign(base, { shop: shop.shop, theme: shop.themeName, product: shop.product, template: CFG.template });

  // 2. Admin theme editor: needs the person's admin login.
  step("open theme editor");
  const editor = `https://admin.shopify.com/store/${handle}/themes/${shop.themeId}/editor?previewPath=${encodeURIComponent("/products/" + shop.product)}`;
  base.editor = editor;  // every early exit below carries the link to open
  await go(editor);
  await page.waitForTimeout(8000);
  const u = await page.url();
  if (!u.includes(`/store/${handle}/themes`)) { out({ ...base, status: "needs_login", detail: u }); await end(); }

  // 3. Template picker > Products > Create template (based on the default product template).
  step(`create template ${CFG.template}`);
  let lines = await snap();
  let i = find(lines, /(?:text|button|heading|anchor|option|menuitem|tab) "Default product"/);
  if (i < 0) { out({ ...base, status: "editor_changed", detail: "No 'Default product' in the editor top bar. The steps read the Shopify admin in English: set your admin language to English (Settings > Users > your name > Language), or pick a preview product that uses the default product template.", view: view(lines) }); await end(); }
  await page.click("@" + refBefore(lines, i), { label: "Open template picker" });
  await page.waitForTimeout(2500);
  lines = await snap(true);
  let ci = find(lines, /(?:text|button|heading|anchor|option|menuitem|tab) "Create template"/);
  if (ci < 0) {
    const pi = find(lines, /(?:text|button|heading|anchor|option|menuitem|tab) "Products"/);
    await page.click("@" + refBefore(lines, pi), { label: "Products templates" });
    await page.waitForTimeout(2000);
    lines = await snap(true); ci = find(lines, /(?:text|button|heading|anchor|option|menuitem|tab) "Create template"/);
  }
  await page.click("@" + refBefore(lines, ci), { label: "Create template" });
  await page.waitForTimeout(2500);
  lines = await snap();
  const nameBox = lines.map((l) => l.match(/textbox "Name" \[ref=(\d+)/)).filter(Boolean).pop()?.[1];
  await page.fill("@" + nameBox, CFG.template);
  await page.waitForTimeout(800);
  lines = await snap();
  const btns = lines.map((l, k) => ({ l, k })).filter((x) => /(?:text|button|heading|anchor|option|menuitem|tab) "Create template"/.test(x.l));
  await page.click("@" + refBefore(lines, btns[btns.length - 1].k), { label: "Confirm create" });
  await page.waitForTimeout(7000);
  if (!(await page.url()).includes(CFG.template)) {
    lines = await snap();
    out({ ...base, status: "template_not_created", detail: view(lines.filter((l) => /already|exists|error|taken/i.test(l)), 5, 160) }); await end();
  }

  // 4. Add one Custom Liquid section per code part, at the end of the template.
  for (const [n, file] of CFG.files.entries()) {
    step(`add Custom Liquid section ${n + 1}/${CFG.files.length}`);
    const code = await fs.readFile(file, "utf8");
    lines = await snap(true);
    const t = find(lines, /(?:text|button|heading|anchor|option|menuitem|tab) "Template"/), f = find(lines, /(?:text|button|heading|anchor|option|menuitem|tab) "Footer"/, t + 1);
    const adds = lines.slice(t, f > 0 ? f : undefined).map((l) => l.match(/button "Add section" \[ref=(\d+)/)).filter(Boolean);
    await page.click("@" + adds[adds.length - 1][1], { label: "Add section at end" });
    await page.waitForTimeout(2500);
    lines = await snap();
    const sb = lines.map((l) => l.match(/textbox "Search sections" \[ref=(\d+)/)).filter(Boolean).pop()[1];
    await page.fill("@" + sb, "Custom Liquid");
    await page.waitForTimeout(2000);
    lines = await snap();
    const s = find(lines, /textbox "Search sections"/);
    const pick = lines.slice(s).map((l, k) => ({ l, k })).find((x) => /(?:text|button|heading|anchor|option|menuitem|tab) "Custom Liquid"/.test(x.l) && x.k > 2);
    if (!pick) { out({ ...base, status: "editor_changed", detail: "No Custom Liquid section in the picker. The steps read the Shopify admin in English: set your admin language to English.", view: view(lines.slice(s)) }); await end(); }
    await page.click("@" + refBefore(lines, s + pick.k), { label: "Choose Custom Liquid" });
    await page.waitForTimeout(3000);
    lines = await snap();
    // Shopify renamed the code box from "Custom Liquid" to "Liquid code" (10-21); accept both.
    const tbm = lines.map((l) => l.match(/textbox "(?:Custom Liquid|Liquid code)" \[ref=(\d+)[,\]]/)).filter(Boolean).pop();
    if (!tbm) { out({ ...base, status: "editor_changed", detail: "No code box (\"Liquid code\" or \"Custom Liquid\") in the section settings.", view: view(lines) }); await end(); }
    const tb = tbm[1];
    await page.fill("@" + tb, code);
    await page.waitForTimeout(2500);
    lines = await snap();
    const err = lines.filter((l) => /Liquid syntax error|Liquid error|can't be saved|exceeds/i.test(l));
    if (err.length) { out({ ...base, status: "liquid_error", detail: view(err, 5, 200) }); await end(); }
    const back = lines.map((l) => l.match(/button "(Back|Close)[^"]*" \[ref=(\d+)/)).filter(Boolean)[0];
    if (back) { await page.click("@" + back[2]); await page.waitForTimeout(1500); }
  }

  // 5. Save.
  step("save");
  lines = await snap();
  // The Save button has no label of its own in newer snapshots: find its "Save" text and take the button above it.
  const si = lines.findIndex((l) => /^(?:button|text) "Save"(?: \[|$)/.test(l.trim()));
  const save = si >= 0 ? (refOf(lines[si]) || refBefore(lines, si)) : undefined;
  if (save) { await page.click("@" + save, { label: "Save template" }); await page.waitForTimeout(5000); }
  else { await page.keyboard.press("Meta+s"); await page.waitForTimeout(5000); }

  // 6. Verify on the storefront: the widget renders review cards. Then screenshots.
  const link = `https://${host}/products/${shop.product}?view=${CFG.template}`;
  step(`verify ${link}`);
  const check = async () => page.evaluate((name) => {
    const all = (root, sel, acc = []) => { root.querySelectorAll(sel).forEach((e) => acc.push(e)); root.querySelectorAll("*").forEach((e) => e.shadowRoot && all(e.shadowRoot, sel, acc)); return acc; };
    const box = document.querySelector(`[data-lx-install="${name}"]`);
    if (!box) return { found: false };
    // A tag the store's script doesn't define draws nothing and gives no error: a wrong name, or a part not shipped yet.
    const tags = [...box.querySelectorAll("*"), ...[...box.querySelectorAll("template")].flatMap((tp) => [...tp.content.querySelectorAll("*")])]
      .map((e) => e.tagName.toLowerCase()).filter((tg) => tg.startsWith("lxrw-"));
    const unknownParts = [...new Set(tags)].filter((tg) => !customElements.get(tg));
    return { found: true, unknownParts, widgets: all(box, "loox-reviews-widget").length, cards: all(box, "lxrw-review-card-provider").length,
      liquidError: /Liquid error/i.test(box.textContent), height: Math.round(box.getBoundingClientRect().height) };
  }, CFG.template);
  const shots = {};
  for (const [label, w, mobile] of [["desktop", 1280, false], ["phone", 390, true]]) {
    await page.cdp("Emulation.setDeviceMetricsOverride", { width: w, height: 900, deviceScaleFactor: mobile ? 2 : 1, mobile });
    await go(link);
    // Pop-ups (newsletter, cookie) cover the widget; the widget may also wait until it is on screen.
    const clear = () => page.evaluate((name) => {
      document.querySelectorAll('[class*="omnisend"],[id*="omnisend"],[class*="klaviyo-form"],[aria-modal="true"]').forEach((e) => e.remove());
      const box = document.querySelector(`[data-lx-install="${name}"]`);
      if (box) { box.scrollIntoView({ block: "start" }); window.scrollBy(0, -90); }
    }, CFG.template);
    await clear();
    let v = await check();
    for (let k = 0; k < 12 && v.found && !v.cards; k++) { await page.waitForTimeout(1500); await clear(); v = await check(); }
    shots[label + "_check"] = v;
    if (v.found) {
      await page.waitForTimeout(2000);
      await clear();
      await page.waitForTimeout(800);
      const path = `${CFG.out}/${CFG.template}-${label}.png`;
      await page.screenshot({ path });
      shots[label] = path;
    }
  }
  await page.cdp("Emulation.clearDeviceMetricsOverride", {});
  const d = shots.desktop_check || {}, m = shots.phone_check || {};
  const liquidError = d.liquidError || m.liquidError;
  const status = liquidError ? "liquid_error_on_page"
    : d.found && d.cards > 0 && m.cards > 0 ? "installed"
    : d.found && d.cards > 0 ? "phone_failed"
    : d.found ? "installed_no_reviews" : "not_on_page";
  const hints = {
    liquid_error_on_page: "The page shows a Liquid error inside the widget. Look at the screenshot for the message.",
    phone_failed: "Desktop shows the cards but the phone check found none: a pop-up or slow loading on the phone, not missing reviews. Look at the phone screenshot.",
    installed_no_reviews: "The widget is on the page but shows no reviews: check the product has published reviews and Widget 2.0 is on for this store.",
    not_on_page: "Shopify did not keep the section. Open the editor link to see its error.",
  };
  const unknownParts = [...new Set([...(d.unknownParts || []), ...(m.unknownParts || [])])];
  out({ ...base, status, hint: hints[status], unknown_parts: unknownParts, link, editor: editor.replace(/\/editor.*/, `/editor?previewPath=${encodeURIComponent(`/products/${shop.product}?view=${CFG.template}`)}`), checks: shots });
} catch (e) {
  out({ ...base, status: "error", detail: String(e && e.stack || e).slice(0, 800), url: await page.url().catch(() => null) });
}
// The phone pass sets a 390px mobile view on the shared tab; end() clears it before the login hand-off reuses the tab.
await end();
