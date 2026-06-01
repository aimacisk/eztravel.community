"""
DOM 結構探查工具 — 列出旅館頁面主要 class/id 供 crawl 腳本調整
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

TARGET_URL = "https://hotel.eztravel.com.tw/"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537",
    )
    page = ctx.new_page()
    try:
        page.goto(TARGET_URL, wait_until="networkidle", timeout=45000)
    except PlaywrightTimeout:
        print("timeout, continuing...")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass

    # 取出 body 的前 200 個元素，列出 tag/class/id
    result = page.evaluate("""
    () => {
        const els = Array.from(document.querySelectorAll('body *')).slice(0, 400);
        return els.map(el => ({
            tag: el.tagName.toLowerCase(),
            id: el.id || null,
            cls: el.className && typeof el.className === 'string'
                ? el.className.trim().substring(0, 120)
                : null,
            text: (el.innerText || '').trim().substring(0, 60),
        }));
    }
    """)

    # 篩選有意義的
    interesting = [
        r for r in result
        if (r['id'] or r['cls']) and r['tag'] not in ('script', 'style', 'svg', 'path', 'use')
    ]

    out = Path(__file__).parent / "dom_inspect.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(interesting[:200], f, ensure_ascii=False, indent=2)
    print(f"Saved {len(interesting)} elements to {out}")

    # 也印出所有 section/div 的 class 含有關鍵詞的
    keywords = ["search", "banner", "hotel", "promo", "dest", "theme", "card", "product",
                "feature", "recommend", "section", "slider", "swiper", "carousel"]
    for r in interesting:
        cls = (r['cls'] or '').lower()
        if any(k in cls for k in keywords):
            print(f"  [{r['tag']}] id={r['id']} cls={r['cls'][:80]!r} | {r['text'][:40]!r}")

    browser.close()
