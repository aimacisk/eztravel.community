"""
DOM 探查 — activity.eztravel.com.tw 票券頁
輸出：scripts/dom_activity.json
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

TARGET_URL = "https://activity.eztravel.com.tw/"

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

    # 遞迴 DOM 結構（深度 ≤5）
    structure = page.evaluate("""
    () => {
        const containers = ['main', '#wrapper', '#content', '.main-content', 'body'];
        let root = null;
        for (const sel of containers) {
            root = document.querySelector(sel);
            if (root) break;
        }
        if (!root) root = document.body;

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
            const text = (el.innerText || '').trim().substring(0, 120);
            const children = Array.from(el.children)
                .filter(c => ['div','section','article','ul','li','aside','nav','header'].includes(c.tagName.toLowerCase()))
                .slice(0, 10)
                .map(c => scan(c, depth + 1))
                .filter(Boolean);

            return { tag, id, cls, text, imgCount: el.querySelectorAll('img').length, imgSrcs, anchors, childCount: el.children.length, children };
        }

        return scan(root, 0);
    }
    """)

    out = Path(__file__).parent / "dom_activity.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out}")
    print(f"Root: {structure['tag']} cls={structure['cls']}")
    print(f"Children: {len(structure.get('children', []))}")
    for c in structure.get('children', []):
        cls_short = (c['cls'] or '')[:70]
        print(f"  [{c['tag']}] id={c['id']} cls={cls_short!r} imgs={c['imgCount']} children={c['childCount']}")
        print(f"    text: {c['text'][:80]!r}")
        for cc in c.get('children', []):
            cls2 = (cc['cls'] or '')[:60]
            print(f"    [{cc['tag']}] id={cc['id']} cls={cls2!r} imgs={cc['imgCount']} children={cc['childCount']}")
            print(f"      text: {cc['text'][:60]!r}")

    browser.close()
