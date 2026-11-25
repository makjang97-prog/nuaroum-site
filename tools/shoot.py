#!/usr/bin/env python3
"""Capture and check the NOUAROUM site at a given base URL.

Usage: python3 tools/shoot.py http://localhost:8000 out_dir [--live]
"""
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

BASE = sys.argv[1].rstrip("/")
OUT = pathlib.Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

report = {"base": BASE, "console": [], "failed": [], "broken_images": [], "overflow": {}, "checks": {}}

SECTIONS = [
    ("#top", "top"),
    ("#story", "story"),
    ("#collection", "collection"),
    ("#catalog", "catalog"),
    ("#bespoke", "bespoke"),
    ("#showroom", "showroom"),
    ("#reservation", "reservation"),
]


def collect(page):
    page.on("console", lambda m: report["console"].append({"type": m.type, "text": m.text[:300]}) if m.type in ("error", "warning") else None)
    page.on("requestfailed", lambda r: report["failed"].append({"url": r.url[:200], "reason": r.failure}))
    page.on("response", lambda r: report["failed"].append({"url": r.url[:200], "status": r.status}) if r.status >= 400 else None)


def broken(page):
    return page.evaluate(
        """() => Array.from(document.images)
            .filter(i => i.complete && i.naturalWidth === 0)
            .map(i => i.currentSrc || i.src)"""
    )


def overflow(page):
    return page.evaluate(
        """() => ({scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth})"""
    )


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---------------- desktop 1440
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page = ctx.new_page()
    collect(page)
    page.goto(BASE + "/", wait_until="networkidle")
    page.wait_for_timeout(1200)

    report["checks"]["title"] = page.title()
    report["checks"]["h1"] = page.inner_text("h1").replace("\n", " / ")
    report["overflow"]["desktop"] = overflow(page)
    report["broken_images"] += broken(page)

    page.screenshot(path=str(OUT / "pc-top.png"))

    for anchor, name in SECTIONS[1:]:
        page.evaluate(
            """(sel) => { const el = document.querySelector(sel);
                 window.scrollTo({top: el.getBoundingClientRect().top + window.scrollY - 74, behavior: 'instant'}); }""",
            anchor,
        )
        page.wait_for_timeout(700)
        if name in ("story", "collection", "catalog", "bespoke", "showroom", "reservation"):
            page.screenshot(path=str(OUT / f"pc-{name}.png"))

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(900)
    page.screenshot(path=str(OUT / "pc-footer.png"))

    # full page
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / "pc-full.png"), full_page=True)

    # product modal
    page.click("#products .card")
    page.wait_for_timeout(700)
    page.screenshot(path=str(OUT / "pc-modal.png"))
    report["checks"]["modal_title"] = page.inner_text("#modalBody .modal__title")
    report["checks"]["modal_code"] = page.inner_text("#modalBody .modal__code")
    page.keyboard.press("Escape")
    page.wait_for_timeout(400)
    report["checks"]["modal_closed"] = page.evaluate("!document.querySelector('#modal').classList.contains('is-open')")

    # filter to wedding band
    page.click('#filters .chip[data-filter="wedding-band"]')
    page.wait_for_timeout(500)
    report["checks"]["wedding_band_cards"] = page.locator("#products .card").count()
    page.evaluate(
        """() => { const el = document.querySelector('#catalog');
             window.scrollTo({top: el.getBoundingClientRect().top + window.scrollY - 74, behavior: 'instant'}); }"""
    )
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / "pc-catalog-wb.png"))

    # header link behaviour: showroom anchor
    page.click('.hdr__nav--right a[href="#showroom"]')
    page.wait_for_timeout(900)
    report["checks"]["after_showroom_click_hash"] = page.evaluate("location.hash")

    ctx.close()

    # ---------------- mobile 390
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = ctx.new_page()
    collect(page)
    page.goto(BASE + "/", wait_until="networkidle")
    page.wait_for_timeout(1200)

    report["overflow"]["mobile390"] = overflow(page)
    report["broken_images"] += broken(page)
    page.screenshot(path=str(OUT / "mobile-top.png"))

    page.click("#burger")
    page.wait_for_timeout(700)
    page.screenshot(path=str(OUT / "mobile-menu.png"))
    report["checks"]["drawer_open"] = page.evaluate("document.querySelector('#drawer').classList.contains('is-open')")
    page.click(".drawer__nav a[href='#collection']")
    page.wait_for_timeout(1000)
    page.screenshot(path=str(OUT / "mobile-collection.png"))
    report["checks"]["drawer_closed_after_link"] = page.evaluate("!document.querySelector('#drawer').classList.contains('is-open')")

    for anchor, name in [("#catalog", "catalog"), ("#bespoke", "bespoke"), ("#showroom", "showroom"), ("#reservation", "reservation")]:
        page.evaluate(
            """(sel) => { const el = document.querySelector(sel);
                 window.scrollTo({top: el.getBoundingClientRect().top + window.scrollY - 64, behavior: 'instant'}); }""",
            anchor,
        )
        page.wait_for_timeout(600)
        page.screenshot(path=str(OUT / f"mobile-{name}.png"))

    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT / "mobile-full.png"), full_page=True)

    page.click("#products .card")
    page.wait_for_timeout(800)
    page.screenshot(path=str(OUT / "mobile-modal.png"))
    page.click("#modalClose")
    page.wait_for_timeout(400)

    # ---------------- small phone 360
    ctx3 = browser.new_context(viewport={"width": 360, "height": 640}, device_scale_factor=2, is_mobile=True, has_touch=True)
    p3 = ctx3.new_page()
    p3.goto(BASE + "/", wait_until="networkidle")
    p3.wait_for_timeout(800)
    report["overflow"]["mobile360"] = overflow(p3)
    p3.click("#burger")
    p3.wait_for_timeout(600)
    report["checks"]["drawer_scrolls_360"] = p3.evaluate("document.querySelector('#drawer').scrollHeight <= document.querySelector('#drawer').clientHeight + 2")
    p3.screenshot(path=str(OUT / "mobile360-menu.png"))
    ctx3.close()

    # ---------------- tablet 768
    ctx4 = browser.new_context(viewport={"width": 768, "height": 1024})
    p4 = ctx4.new_page()
    p4.goto(BASE + "/", wait_until="networkidle")
    p4.wait_for_timeout(800)
    report["overflow"]["tablet768"] = overflow(p4)
    p4.screenshot(path=str(OUT / "tablet-top.png"), full_page=False)
    ctx4.close()

    browser.close()

report["console"] = [c for c in report["console"] if c["type"] == "error"]
print(json.dumps(report, ensure_ascii=False, indent=2))
