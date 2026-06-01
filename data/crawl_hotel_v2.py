"""
T-eztcomm-20260601-W1-PG-3 — 旅館頁爬蟲 v2
Target : https://hotel.eztravel.com.tw/
Output : data/旅館/{旅館.json, 旅館_screenshot.png, images/}
Schema : projects/eztravel.community/01_requirements/data_schema.md
"""
import json
import os
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ── 路徑設定 ─────────────────────────────────────────────────────
# 此腳本在 data/ 目錄下，OUTPUT_DIR 直接使用 data/旅館/
SCRIPT_DIR = Path(__file__).parent          # .../data/
OUTPUT_DIR = SCRIPT_DIR / "旅館"           # .../data/旅館/
IMAGES_DIR = OUTPUT_DIR / "images"          # .../data/旅館/images/
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

TARGET_URL = "https://hotel.eztravel.com.tw/"
MAX_IMG_BYTES = 2 * 1024 * 1024  # 2 MB


# ── 工具函式 ──────────────────────────────────────────────────────
def clean(t) -> str | None:
    if not t:
        return None
    t = str(t).strip()
    return t or None


def get_ext(url: str) -> str:
    m = re.search(r"\.(jpg|jpeg|png|webp|gif)(\?|$)", url, re.I)
    return (m.group(1) if m else "jpg").lower()


def abs_url(href: str | None) -> str | None:
    if not href:
        return None
    href = href.strip()
    if not href:
        return None
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return "https://hotel.eztravel.com.tw" + href
    return href


def download_img(url: str, path: Path) -> bool:
    if not url or url.startswith("data:"):
        return False
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            chunk = r.read(MAX_IMG_BYTES + 1)
        if len(chunk) > MAX_IMG_BYTES:
            print(f"    SKIP >2MB: {url[:80]}")
            return False
        path.write_bytes(chunk)
        return True
    except Exception as e:
        print(f"    DL FAIL {url[:60]}: {e}")
        return False


class ImgCounter:
    def __init__(self):
        self._c: dict[str, int] = {}

    def next(self, type_key: str, url: str) -> tuple[str, Path]:
        """回傳 (images/相對路徑, 完整 Path)"""
        self._c[type_key] = self._c.get(type_key, 0) + 1
        ext = get_ext(url)
        fname = f"hotel_{type_key}_{self._c[type_key]:02d}.{ext}"
        return f"images/{fname}", IMAGES_DIR / fname


def save(counter: ImgCounter, type_key: str, url: str | None) -> str | None:
    if not url:
        return None
    rel, path = counter.next(type_key, url)
    if download_img(url, path):
        print(f"    DL {path.name} ({path.stat().st_size // 1024}KB)")
        return rel
    # release the counter slot if failed
    return None


# ── 主爬蟲 ───────────────────────────────────────────────────────
def crawl() -> dict:
    scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    sections: list[dict] = []
    counter = ImgCounter()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = ctx.new_page()

        # 1. 導航
        print("→ Navigating:", TARGET_URL)
        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=45000)
        except PlaywrightTimeout:
            print("  networkidle timeout, continuing...")

        # 關閉 cookie/popup
        for sel in ["#onetrust-accept-btn-handler", ".cookie-close", ".modal-close"]:
            try:
                if page.is_visible(sel):
                    page.click(sel)
                    time.sleep(0.5)
            except Exception:
                pass
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass

        # 2. 捲動觸發 lazy-load
        print("→ Scrolling...")
        for _ in range(3):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight / 3)")
            time.sleep(0.8)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1.5)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except PlaywrightTimeout:
            pass

        # 3. 截圖
        screenshot_path = OUTPUT_DIR / "旅館_screenshot.png"
        print("→ Screenshot...")
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"  {screenshot_path.name}: {screenshot_path.stat().st_size // 1024}KB")

        # ── Section 1: search_bar ─────────────────────────────
        print("→ Section: search_bar")
        search_items = []

        # 取搜尋 nav 的 tab 文字（國外/台灣/訂房+高鐵/機+酒）
        nav_tabs = page.query_selector_all(".searchEngineNav a, .searchEngineNav span, .searchEngineNav button")
        tab_texts = []
        for tab in nav_tabs[:6]:
            t = clean(tab.inner_text())
            if t:
                tab_texts.append(t)

        # 取搜尋欄 placeholder
        placeholders = []
        for inp in page.query_selector_all("input[placeholder]"):
            ph = inp.get_attribute("placeholder")
            if ph and ph not in placeholders:
                placeholders.append(ph)

        if tab_texts:
            search_items.append({
                "text": "、".join(tab_texts),
                "image_url": None,
                "link_url": None,
                "price": None,
                "badge": None,
                "description": "搜尋類型選項：" + " / ".join(tab_texts),
            })
        for ph in placeholders[:3]:
            search_items.append({
                "text": clean(ph),
                "image_url": None,
                "link_url": None,
                "price": None,
                "badge": None,
                "description": "搜尋框佔位文字",
            })
        if not search_items:
            search_items.append({
                "text": "全球住宿搜尋",
                "image_url": None,
                "link_url": None,
                "price": None,
                "badge": None,
                "description": "住宿地點 / 飯店名稱搜尋框",
            })
        sections.append({"id": "search_bar", "type": "search_bar", "title": None, "items": search_items})

        # ── Section 2: promo_section (TopWidgetBlock 42 imgs) ──
        print("→ Section: promo_section (banner images)")
        promo_items = []
        # 第一個 TopWidgetBlock 包含促銷 banner 圖
        top_widgets = page.query_selector_all(".TopWidgetBlock_article-wrapper__y3T_Z")
        if top_widgets:
            first_widget = top_widgets[0]
            imgs = first_widget.query_selector_all("img")
            links = first_widget.query_selector_all("a[href]")
            seen_promo = set()
            for img in imgs[:15]:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if not src or src.startswith("data:"):
                    continue
                # 找最近的 <a>
                href = None
                try:
                    href = page.evaluate("(el) => el.closest('a')?.href", img)
                except Exception:
                    pass
                if not href and links:
                    href = links[0].get_attribute("href")

                alt_text = clean(img.get_attribute("alt"))
                title_text = None
                try:
                    # 嘗試取同層 h2/h3/.title
                    parent = page.evaluate(
                        "(el) => el.closest('[class*=\"widget\"], [class*=\"article\"], [class*=\"item\"]')?.querySelector('h2,h3,.title')?.innerText",
                        img
                    )
                    title_text = clean(parent)
                except Exception:
                    pass

                key = src
                if key in seen_promo:
                    continue
                seen_promo.add(key)

                local = save(counter, "banner", src)
                promo_items.append({
                    "text": title_text or alt_text,
                    "image_url": local,
                    "link_url": abs_url(href),
                    "price": None,
                    "badge": None,
                    "description": None,
                })
                time.sleep(0.3)

        if promo_items:
            sections.append({"id": "promo_section", "type": "promo_section", "title": "促銷活動", "items": promo_items[:10]})

        # ── Section 3: theme_section (大家都搜 / HotProducts) ──
        print("→ Section: theme_section (大家都搜)")
        theme_items = []
        hot_container = page.query_selector(".HotProducts_hot_products__gEpWU")
        if hot_container:
            hot_links = hot_container.query_selector_all("a[href]")
            seen_hot = set()
            for a in hot_links[:15]:
                t = clean(a.inner_text())
                href = a.get_attribute("href")
                key = (t, href)
                if not t or key in seen_hot:
                    continue
                seen_hot.add(key)
                theme_items.append({
                    "text": t,
                    "image_url": None,
                    "link_url": abs_url(href),
                    "price": None,
                    "badge": None,
                    "description": None,
                })
        if theme_items:
            sections.append({"id": "theme_section", "type": "theme_section", "title": "大家都搜", "items": theme_items})

        # ── Section 4: featured_hotels (common_widget_wrapper) ─
        print("→ Section: featured_hotels (會員最愛)")
        hotel_items = []
        widgets = page.query_selector_all(".common_widget_wrapper__m8_2_")
        seen_hotels = set()
        for w in widgets[:20]:
            img = w.query_selector("img")
            src = img.get_attribute("src") if img else None

            # 標題
            name_el = w.query_selector("h3, h4, h5, [class*='title'], [class*='name'], strong")
            name_text = clean(name_el.inner_text()) if name_el else None
            if not name_text:
                # fallback: 取全文首行
                full = clean(w.inner_text())
                name_text = full.split("\n")[0] if full else None

            # 價格
            price_el = w.query_selector("[class*='price'], [class*='amount']")
            price_text = clean(price_el.inner_text()) if price_el else None
            if not price_text:
                # 嘗試從文字中找 數字+起
                full_text = clean(w.inner_text()) or ""
                pm = re.search(r"([\d,]+)\s*起", full_text)
                if pm:
                    price_text = pm.group(0)

            # 描述
            desc_el = w.query_selector("[class*='desc'], [class*='sub']")
            desc_text = clean(desc_el.inner_text()) if desc_el else None
            if not desc_text:
                # 取第 2 行文字（第 1 行是標題）
                lines = (clean(w.inner_text()) or "").split("\n")
                for ln in lines[1:]:
                    ln = ln.strip()
                    if ln and not re.match(r"^[\d,]+起$", ln):
                        desc_text = ln
                        break

            # 徽章
            badge_el = w.query_selector("[class*='badge'], [class*='tag'], [class*='label']")
            badge_text = clean(badge_el.inner_text()) if badge_el else None

            # 連結
            a = w.query_selector("a[href]")
            href = a.get_attribute("href") if a else None

            key = (name_text, href)
            if key in seen_hotels or not name_text:
                continue
            seen_hotels.add(key)

            local = save(counter, "product", src) if src else None
            hotel_items.append({
                "text": name_text,
                "image_url": local,
                "link_url": abs_url(href),
                "price": price_text,
                "badge": badge_text,
                "description": desc_text,
            })
            time.sleep(0.2)

        if hotel_items:
            sections.append({"id": "featured_hotels", "type": "featured_items", "title": "精選飯店推薦", "items": hotel_items[:15]})

        # ── Section 5: destination_grid (全球訂房 tabs = 目的地) ─
        print("→ Section: destination_grid (全球訂房主題)")
        dest_items = []
        # 取所有 ArticleLayout 的 tab 文字和連結
        tabs = page.query_selector_all(".TabsGroup_tabs__FK2S_ a, .TabsGroup_tabs__FK2S_ button, .TabsGroup_tabs_top__LT09C a, .TabsGroup_tabs_top__LT09C button, .TabsGroup_tabs_top__LT09C span[class]")
        seen_dest = set()
        for tab in tabs[:30]:
            t = clean(tab.inner_text())
            href = tab.get_attribute("href")
            key = t
            if not t or key in seen_dest or len(t) > 30:
                continue
            seen_dest.add(key)
            dest_items.append({
                "text": t,
                "image_url": None,
                "link_url": abs_url(href),
                "price": None,
                "badge": None,
                "description": None,
            })

        if dest_items:
            sections.append({"id": "destination_grid", "type": "destination_grid", "title": "熱門住宿目的地", "items": dest_items[:20]})

        # ── Section 6: aside article (全球訂房 hotel cards) ────
        print("→ Section: global hotel cards")
        global_items = []
        aside_articles = page.query_selector_all("article.ArticleLayout_article_layout__FBaNz")
        for art in aside_articles[1:3]:  # 第 2,3 個 article
            cards = art.query_selector_all("[class*='widget_wrapper'], [class*='card'], li[class]")
            for card in cards[:10]:
                img = card.query_selector("img")
                src = img.get_attribute("src") if img else None
                t = clean(card.inner_text())
                lines = t.split("\n") if t else []
                name = lines[0] if lines else None
                a = card.query_selector("a[href]")
                href = a.get_attribute("href") if a else None

                pm = re.search(r"([\d,]+)\s*起", t or "")
                price = pm.group(0) if pm else None

                if not name:
                    continue
                local = save(counter, "product", src) if src else None
                global_items.append({
                    "text": name,
                    "image_url": local,
                    "link_url": abs_url(href),
                    "price": price,
                    "badge": None,
                    "description": lines[1].strip() if len(lines) > 1 and lines[1].strip() else None,
                })
                time.sleep(0.2)

        if global_items:
            sections.append({"id": "global_hotels", "type": "product_list", "title": "全球訂房精選", "items": global_items[:10]})

        # ── Section 7: footer_links ───────────────────────────
        print("→ Section: footer_links")
        footer_items = []
        footer = page.query_selector("footer, .footer, [class*='footer']")
        if footer:
            links = footer.query_selector_all("a[href]")
            seen_footer = set()
            for a in links[:30]:
                t = clean(a.inner_text())
                href = a.get_attribute("href")
                if t and t not in seen_footer:
                    seen_footer.add(t)
                    footer_items.append({
                        "text": t,
                        "image_url": None,
                        "link_url": abs_url(href),
                        "price": None,
                        "badge": None,
                        "description": None,
                    })
        if footer_items:
            sections.append({"id": "footer_links", "type": "footer_links", "title": None, "items": footer_items[:20]})

        browser.close()

    # ── 後處理：清空字串改 null ──────────────────────────────────
    def sanitize_item(item: dict) -> dict:
        return {k: (v.strip() if isinstance(v, str) and v.strip() else (None if isinstance(v, str) else v)) for k, v in item.items()}

    for sec in sections:
        sec["items"] = [sanitize_item(i) for i in sec["items"]]

    # ── 組 JSON ─────────────────────────────────────────────────
    if sections:
        result = {"page": "旅館", "scraped_at": scraped_at, "url": TARGET_URL, "sections": sections}
    else:
        result = {"page": "旅館", "scraped_at": scraped_at, "url": TARGET_URL, "error": "no_sections_found", "sections": []}

    json_path = OUTPUT_DIR / "旅館.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✓ sections={len(sections)}")
    print(f"  JSON : {json_path}")
    print(f"  Screenshot : {OUTPUT_DIR / '旅館_screenshot.png'}")
    imgs = list(IMAGES_DIR.glob("*"))
    print(f"  Images: {len(imgs)}")
    return result


if __name__ == "__main__":
    crawl()
