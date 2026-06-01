"""
T-eztcomm-20260601-W1-PG-6 — 票券頁爬蟲
Target : https://activity.eztravel.com.tw/
Output : data/票券/{票券.json, 票券_screenshot.png, images/}
"""
import json
import re
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ── 路徑設定 ────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent                       # .../scripts/
WORKTREE    = SCRIPT_DIR.parent                           # .../T-eztcomm-20260601-W1-PG-6/
OUTPUT_DIR  = WORKTREE / "data" / "票券"                  # .../data/票券/
IMAGES_DIR  = OUTPUT_DIR / "images"                       # .../data/票券/images/
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

TARGET_URL  = "https://activity.eztravel.com.tw/"
CATEGORY    = "ticket"
MAX_IMG_BYTES = 2 * 1024 * 1024   # 2 MB

# ── 工具函式 ────────────────────────────────────────────────────

class ImgCounter:
    """產生 ticket_{type}_{index:02d}.{ext} 命名"""
    def __init__(self):
        self._c: dict[str, int] = {}

    def next(self, type_key: str, url: str) -> tuple[str, Path]:
        self._c[type_key] = self._c.get(type_key, 0) + 1
        ext = get_ext(url)
        fname = f"{CATEGORY}_{type_key}_{self._c[type_key]:02d}.{ext}"
        return f"images/{fname}", IMAGES_DIR / fname


def get_ext(url: str) -> str:
    """從 URL 取副檔名，fallback jpg"""
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix.lstrip(".").lower()
    return suffix if suffix in ("jpg", "jpeg", "png", "webp", "gif") else "jpg"


def abs_url(href: str) -> str | None:
    if not href:
        return None
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    return urllib.parse.urljoin(TARGET_URL, href)


def sanitize(val: str | None) -> str | None:
    if val is None:
        return None
    v = val.strip()
    return v if v else None


def sanitize_item(item: dict) -> dict:
    return {k: sanitize(v) for k, v in item.items()}


def download_img(url: str, dest: Path) -> bool:
    """下載單張圖片，>2MB 跳過，回傳 True/False"""
    if not url or dest.exists():
        return dest.exists()
    try:
        r = requests.get(url, timeout=15,
                         headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"},
                         stream=True)
        r.raise_for_status()
        size = 0
        buf = b""
        for chunk in r.iter_content(8192):
            buf += chunk
            size += len(chunk)
            if size > MAX_IMG_BYTES:
                print(f"    SKIP (>2MB): {dest.name}")
                return False
        dest.write_bytes(buf)
        print(f"    DL {dest.name} ({size//1024}KB)")
        return True
    except Exception as e:
        print(f"    ERR {dest.name}: {e}")
        return False


# ── 主爬蟲 ──────────────────────────────────────────────────────

def crawl():
    counter = ImgCounter()
    sections: list[dict] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537",
        )
        page = ctx.new_page()

        print("Navigating:", TARGET_URL)
        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=45000)
        except PlaywrightTimeout:
            print("  timeout, continuing...")

        # Escape any popup
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass

        # 多次捲動確保 lazy-load 全部觸發
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

        # ── 截圖 ──────────────────────────────────────────────
        ss_path = OUTPUT_DIR / "票券_screenshot.png"
        page.screenshot(path=str(ss_path), full_page=True)
        print(f"  Screenshot: {ss_path.stat().st_size//1024}KB")

        # ── §1 search_bar ─────────────────────────────────────
        print("Section: search_bar")
        sb_items = page.evaluate("""
        () => {
            const block = document.querySelector('.Layout_searchEngineBlock__kAV_R');
            if (!block) return [];
            const items = [];
            // 搜尋框 placeholder
            for (const inp of block.querySelectorAll('input[placeholder]')) {
                items.push({ text: inp.placeholder || null, image_url: null,
                    link_url: null, price: null, badge: null, description: null });
            }
            // 按鈕 / 標籤文字
            for (const el of block.querySelectorAll('button, a, span')) {
                const t = (el.innerText || '').trim();
                if (t && t.length < 40 && !items.some(i => i.text === t)) {
                    items.push({ text: t, image_url: null,
                        link_url: el.tagName === 'A' ? el.href || null : null,
                        price: null, badge: null, description: null });
                }
                if (items.length >= 8) break;
            }
            return items;
        }
        """)
        sections.append({
            "id": "search_bar",
            "type": "search_bar",
            "title": None,
            "items": [sanitize_item(i) for i in sb_items],
        })

        # ── §2 hero_banner（輪播 banner）────────────────────────
        print("Section: hero_banner (promo banners)")
        banner_items_raw = page.evaluate("""
        () => {
            // 第一個 TopWidgetBlock article-wrapper — 包含輪播 banner
            const wrappers = document.querySelectorAll('.TopWidgetBlock_article-wrapper__y3T_Z');
            if (!wrappers.length) return [];
            const first = wrappers[0];
            const slides = first.querySelectorAll('img');
            const result = [];
            for (const img of slides) {
                const src = img.src || img.getAttribute('data-src') || null;
                if (!src || src.startsWith('data:')) continue;
                const a = img.closest('a');
                result.push({
                    text: img.alt || null,
                    image_url: src,
                    link_url: a ? a.href : null,
                    price: null,
                    badge: null,
                    description: null,
                });
            }
            return result;
        }
        """)
        banner_items = []
        for raw in banner_items_raw[:15]:
            rel_path, local = counter.next("banner", raw["image_url"])
            if download_img(raw["image_url"], local):
                raw["image_url"] = rel_path
            else:
                raw["image_url"] = None
            banner_items.append(sanitize_item(raw))
            time.sleep(0.3)
        sections.append({
            "id": "hero_banner",
            "type": "hero_banner",
            "title": None,
            "items": banner_items,
        })

        # ── §3 category_nav（分類捷徑）──────────────────────────
        print("Section: category_nav (ticket types)")
        nav_items = page.evaluate("""
        () => {
            const result = [];
            // ActivityWidget 票券類型 icon swiper
            const swiperSlides = document.querySelectorAll(
                '.ArticleSwiper_swiper__Lyg_N .swiper-wrapper .swiper-slide, ' +
                '.ArticleSwiper_swiper__Lyg_N .swiper-wrapper > div'
            );
            for (const slide of swiperSlides) {
                const a = slide.querySelector('a');
                const img = slide.querySelector('img');
                const span = slide.querySelector('span, p, div');
                const text = (span && span.innerText ? span.innerText : (a ? a.innerText : '')).trim();
                const src = img ? (img.src || img.getAttribute('data-src') || null) : null;
                if (!text && !src) continue;
                result.push({
                    text: text || null,
                    image_url: src && !src.startsWith('data:') ? src : null,
                    link_url: a ? a.href : null,
                    price: null, badge: null, description: null,
                });
                if (result.length >= 12) break;
            }
            // HotProducts 熱搜主題 (如：國際大廠票/體驗活動/日本電車JR)
            const hotLinks = document.querySelectorAll('.HotProducts_hot_products__gEpWU a');
            for (const a of hotLinks) {
                const t = (a.innerText || '').trim();
                if (t && t.length < 30) {
                    result.push({
                        text: t,
                        image_url: null,
                        link_url: a.href || null,
                        price: null, badge: null, description: null,
                    });
                }
                if (result.length >= 20) break;
            }
            return result;
        }
        """)
        # nav icon 圖片下載
        nav_final = []
        for item in nav_items:
            if item.get("image_url"):
                rel_path, local = counter.next("nav_icon", item["image_url"])
                if download_img(item["image_url"], local):
                    item["image_url"] = rel_path
                else:
                    item["image_url"] = None
                time.sleep(0.2)
            nav_final.append(sanitize_item(item))
        sections.append({
            "id": "category_nav",
            "type": "category_nav",
            "title": None,
            "items": nav_final,
        })

        # ── §4 hot_tickets（熱銷票券 — flagshipProduct）────────
        print("Section: hot_tickets (featured products)")
        hot_raw = page.evaluate("""
        () => {
            // 第一個 ArticleLayout，含 flagshipProduct class 的 article
            const articles = document.querySelectorAll('.ArticleLayout_article_layout__FBaNz');
            if (!articles.length) return { title: null, items: [] };
            const first = articles[0];
            // section title
            const header = first.querySelector('.ArticleLayout_header__derLe');
            let title = null;
            if (header) {
                // 找第一個 h2/h3 或直接讀 innerText 第一行
                const h = header.querySelector('h2, h3, .title, [class*="title"]');
                title = h ? h.innerText.trim() : header.innerText.trim().split('\\n')[0].trim();
            }
            // 產品卡 (common_widget_wrapper)
            const cards = first.querySelectorAll('.common_widget_wrapper__m8_2_');
            const items = [];
            for (const card of cards) {
                const a = card.querySelector('a') || card.closest('a');
                const img = card.querySelector('img');
                // price
                const priceEl = card.querySelector('[class*="price"], [class*="amount"], .price');
                let price = priceEl ? priceEl.innerText.trim() : null;
                if (!price) {
                    const m = (card.innerText || '').match(/[\d,]+起/);
                    price = m ? m[0] : null;
                }
                // badge
                const badgeEl = card.querySelector('[class*="badge"], [class*="tag"], [class*="label"]');
                const badge = badgeEl ? badgeEl.innerText.trim() : null;
                // title text
                const titleEl = card.querySelector('[class*="title"], [class*="name"], h3, h4, strong');
                let text = titleEl ? titleEl.innerText.trim() : (a ? a.innerText.trim().split('\\n')[0] : null);
                if (text && text.length > 80) text = text.substring(0, 80);
                const src = img ? (img.src || img.getAttribute('data-src') || null) : null;
                items.push({
                    text: text || null,
                    image_url: src && !src.startsWith('data:') ? src : null,
                    link_url: a ? a.href : null,
                    price: price || null,
                    badge: badge || null,
                    description: null,
                });
                if (items.length >= 12) break;
            }
            return { title, items };
        }
        """)
        hot_items = []
        for item in hot_raw.get("items", []):
            if item.get("image_url"):
                rel_path, local = counter.next("product", item["image_url"])
                if download_img(item["image_url"], local):
                    item["image_url"] = rel_path
                else:
                    item["image_url"] = None
                time.sleep(0.3)
            hot_items.append(sanitize_item(item))
        sections.append({
            "id": "hot_tickets",
            "type": "featured_items",
            "title": sanitize(hot_raw.get("title")),
            "items": hot_items,
        })

        # ── §5 promo_section（主題活動 — ArticleChunkedItems）───
        print("Section: promo_section (themed product list)")
        promo_raw = page.evaluate("""
        () => {
            const articles = document.querySelectorAll('.ArticleLayout_article_layout__FBaNz');
            if (articles.length < 2) return { title: null, items: [] };
            const second = articles[1];
            const header = second.querySelector('.ArticleLayout_header__derLe');
            let title = null;
            if (header) {
                const h = header.querySelector('h2, h3');
                title = h ? h.innerText.trim() : header.innerText.trim().split('\\n')[0].trim();
            }
            // ArticleChunkedItems 內的所有卡
            const items = [];
            for (const card of second.querySelectorAll('[class*="card"], [class*="widget"], a[href]')) {
                const img = card.querySelector('img');
                const a = card.tagName === 'A' ? card : card.querySelector('a');
                const priceEl = card.querySelector('[class*="price"]');
                let price = priceEl ? priceEl.innerText.trim() : null;
                if (!price) {
                    const m = (card.innerText || '').match(/[\d,]+起/);
                    price = m ? m[0] : null;
                }
                const titleEl = card.querySelector('[class*="title"], [class*="name"], strong, h4');
                let text = titleEl ? titleEl.innerText.trim() : null;
                if (!text && a) text = a.innerText.trim().split('\\n')[0].trim().substring(0, 60);
                const src = img ? (img.src || img.getAttribute('data-src') || null) : null;
                if (!text) continue;
                items.push({
                    text: text || null,
                    image_url: src && !src.startsWith('data:') ? src : null,
                    link_url: a ? a.href : null,
                    price: price || null,
                    badge: null,
                    description: null,
                });
                if (items.length >= 12) break;
            }
            return { title, items };
        }
        """)
        promo_items = []
        for item in promo_raw.get("items", []):
            if item.get("image_url"):
                rel_path, local = counter.next("promo", item["image_url"])
                if download_img(item["image_url"], local):
                    item["image_url"] = rel_path
                else:
                    item["image_url"] = None
                time.sleep(0.3)
            promo_items.append(sanitize_item(item))
        sections.append({
            "id": "promo_section",
            "type": "promo_section",
            "title": sanitize(promo_raw.get("title")),
            "items": promo_items,
        })

        # ── §6 theme_section（旅遊服務 — blockThree layout）────
        print("Section: theme_section (travel services)")
        theme_raw = page.evaluate("""
        () => {
            const articles = document.querySelectorAll('.ArticleLayout_article_layout__FBaNz');
            if (articles.length < 3) return { title: null, items: [] };
            const third = articles[2];
            const header = third.querySelector('.ArticleLayout_header__derLe');
            let title = null;
            if (header) {
                const h = header.querySelector('h2, h3');
                title = h ? h.innerText.trim() : header.innerText.trim().split('\\n')[0].trim();
            }
            const items = [];
            for (const card of third.querySelectorAll('.common_widget_wrapper__m8_2_')) {
                const a = card.querySelector('a') || card.closest('a');
                const img = card.querySelector('img');
                const priceEl = card.querySelector('[class*="price"]');
                let price = priceEl ? priceEl.innerText.trim() : null;
                if (!price) {
                    const m = (card.innerText || '').match(/[\d,]+起/);
                    price = m ? m[0] : null;
                }
                const titleEl = card.querySelector('[class*="title"], [class*="name"], h3, h4, strong');
                let text = titleEl ? titleEl.innerText.trim() : (a ? a.innerText.trim().split('\\n')[0] : null);
                if (text && text.length > 80) text = text.substring(0, 80);
                const src = img ? (img.src || img.getAttribute('data-src') || null) : null;
                items.push({
                    text: text || null,
                    image_url: src && !src.startsWith('data:') ? src : null,
                    link_url: a ? a.href : null,
                    price: price || null,
                    badge: null,
                    description: null,
                });
                if (items.length >= 10) break;
            }
            return { title, items };
        }
        """)
        theme_items = []
        for item in theme_raw.get("items", []):
            if item.get("image_url"):
                rel_path, local = counter.next("theme", item["image_url"])
                if download_img(item["image_url"], local):
                    item["image_url"] = rel_path
                else:
                    item["image_url"] = None
                time.sleep(0.3)
            theme_items.append(sanitize_item(item))
        sections.append({
            "id": "theme_section",
            "type": "theme_section",
            "title": sanitize(theme_raw.get("title")),
            "items": theme_items,
        })

        # ── §7 footer_links ───────────────────────────────────
        print("Section: footer_links")
        footer_items = page.evaluate("""
        () => {
            const footer = document.querySelector('footer');
            if (!footer) return [];
            return Array.from(footer.querySelectorAll('a')).slice(0, 20).map(a => ({
                text: (a.innerText || '').trim() || null,
                image_url: null,
                link_url: a.href || null,
                price: null,
                badge: null,
                description: null,
            })).filter(i => i.text);
        }
        """)
        sections.append({
            "id": "footer_links",
            "type": "footer_links",
            "title": None,
            "items": [sanitize_item(i) for i in footer_items],
        })

        browser.close()

    # ── 組合 JSON ────────────────────────────────────────────────
    result = {
        "page": "票券",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "url": TARGET_URL,
        "sections": sections,
    }

    json_path = OUTPUT_DIR / "票券.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── 摘要 ────────────────────────────────────────────────────
    imgs_count = len(list(IMAGES_DIR.glob("*")))
    print(f"\nDone: sections={len(sections)}, images={imgs_count}")
    for s in sections:
        print(f"  [{s['id']}] type={s['type']} items={len(s['items'])}")
    print(f"JSON: {json_path.stat().st_size//1024}KB")
    print(f"Screenshot: {(OUTPUT_DIR/'票券_screenshot.png').stat().st_size//1024}KB")


if __name__ == "__main__":
    crawl()
