"""
深度 DOM 探查 — 取得旅館頁面 main content 的所有 section 結構
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
    time.sleep(3)
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass

    # 取得 main / #wrapper / body 直接子 section 區塊
    structure = page.evaluate("""
    () => {
        // 找到主要內容容器
        const containers = ['main', '#wrapper', '#content', '.main-content', 'body'];
        let root = null;
        for (const sel of containers) {
            root = document.querySelector(sel);
            if (root) break;
        }
        if (!root) root = document.body;

        // 遞迴取得深度 ≤ 5 的所有 div/section/article
        function scan(el, depth) {
            if (depth > 5) return null;
            const tag = el.tagName.toLowerCase();
            const id = el.id || null;
            const cls = typeof el.className === 'string' ? el.className.trim() : null;
            const imgSrcs = Array.from(el.querySelectorAll('img')).slice(0, 3).map(img => ({
                src: img.src || null,
                dataSrc: img.getAttribute('data-src') || null,
            }));
            const anchors = Array.from(el.querySelectorAll('a')).slice(0, 3).map(a => a.href || null);
            const text = (el.innerText || '').trim().substring(0, 100);
            const children = Array.from(el.children)
                .filter(c => ['div','section','article','ul','li','aside'].includes(c.tagName.toLowerCase()))
                .slice(0, 8)
                .map(c => scan(c, depth + 1))
                .filter(Boolean);

            return { tag, id, cls, text, imgCount: el.querySelectorAll('img').length, imgSrcs, anchors, childCount: el.children.length, children };
        }

        return scan(root, 0);
    }
    """)

    out = Path(__file__).parent / "dom_structure.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"Saved structure to {out}")
    print(f"Root tag: {structure['tag']}, cls: {structure['cls']}")
    print(f"Children: {len(structure.get('children', []))}")
    for c in structure.get('children', []):
        cls_short = (c['cls'] or '')[:60]
        print(f"  [{c['tag']}] id={c['id']} cls={cls_short} imgs={c['imgCount']} children={c['childCount']}")
        print(f"    text: {repr(c['text'][:80])}")
        for cc in c.get('children', []):
            cls_short2 = (cc['cls'] or '')[:50]
            print(f"    [{cc['tag']}] id={cc['id']} cls={cls_short2} imgs={cc['imgCount']}")

    browser.close()
