"""
T-eztcomm-20260601-W1-PG-3 — 旅館頁爬蟲
Target: https://hotel.eztravel.com.tw/
Output: data/旅館/{旅館.json, 旅館_screenshot.png, images/}
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

WORKTREE = Path(__file__).parent
OUTPUT_DIR = WORKTREE / "data" / "旅館"
IMAGES_DIR = OUTPUT_DIR / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

TARGET_URL = "https://hotel.eztravel.com.tw/"
MAX_IMG_BYTES = 2 * 1024 * 1024  # 2 MB


def clean_text(t: str | None) -> str | None:
    if not t:
        return None
    t = t.strip()
    return t if t else None


def download_image(url: str, save_path: Path) -> bool:
    """下載圖片，限 2MB，失敗回傳 False"""
    if not url or url.startswith("data:"):
        return False
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537"
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read(MAX_IMG_BYTES + 1)
            if len(data) > MAX_IMG_BYTES:
                print(f"  SKIP (>2MB): {url}")
                return False
            save_path.write_bytes(data)
            return True
    except Exception as e:
        print(f"  FAIL download {url}: {e}")
        return False


def extract_src(el) -> str | None:
    """優先取 data-src / data-lazy-src，fallback src"""
    for attr in ["data-src", "data-lazy-src", "data-original", "src"]:
        val = el.get_attribute(attr)
        if val and not val.startswith("data:") and val.strip():
            return val.strip()
    return None


def abs_url(base: str, href: str | None) -> str | None:
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
        from urllib.parse import urlparse
        p = urlparse(base)
        return f"{p.scheme}://{p.netloc}{href}"
    return href


def crawl():
    sections = []
    scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        )
        page = ctx.new_page()

        # ── 1. 導航 ──────────────────────────────────────────
        print("Navigating to", TARGET_URL)
        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=45000)
        except PlaywrightTimeout:
            print("  networkidle timeout, continuing...")

        # 關閉 popup/cookie 通知
        for selector in [
            "button.close", ".dismiss", "[class*='close']",
            "#onetrust-accept-btn-handler", ".cookie-accept",
        ]:
            try:
                btn = page.query_selector(selector)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(0.5)
            except Exception:
                pass
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass

        # ── 2. 捲動觸發 lazy-load ──────────────────────────────
        print("Scrolling to bottom...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except PlaywrightTimeout:
            pass
        # 再捲回頂部
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        # ── 3. 截全頁圖 ────────────────────────────────────────
        screenshot_path = OUTPUT_DIR / "旅館_screenshot.png"
        print("Taking full-page screenshot...")
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"  Screenshot: {screenshot_path} ({screenshot_path.stat().st_size // 1024}KB)")

        # ── 4. 擷取 DOM 內容 ─────────────────────────────────────
        print("Extracting DOM sections...")
        page_url = page.url

        img_index = {"banner": 0, "promo": 0, "product": 0, "destination": 0, "theme": 0, "other": 0}

        def next_img_name(type_key: str, ext: str) -> str:
            img_index[type_key] = img_index.get(type_key, 0) + 1
            return f"hotel_{type_key}_{img_index[type_key]:02d}.{ext}"

        def get_ext(url: str) -> str:
            m = re.search(r"\.(jpg|jpeg|png|webp|gif)(\?|$)", url, re.I)
            return m.group(1).lower() if m else "jpg"

        def save_image(url: str, type_key: str) -> str | None:
            """下載圖片並回傳相對路徑（images/xxx），失敗回傳 None"""
            if not url:
                return None
            ext = get_ext(url)
            fname = next_img_name(type_key, ext)
            save_path = IMAGES_DIR / fname
            ok = download_image(url, save_path)
            if ok:
                print(f"    DL {fname}")
                return f"images/{fname}"
            return None

        # ────────────────────────────────────────────────────────
        # Section A: search_bar
        # ────────────────────────────────────────────────────────
        search_items = []
        search_sel = page.query_selector_all(
            "input[placeholder], .search-bar, .hotel-search, "
            "[class*='search'], [id*='search'], form.search"
        )
        # 嘗試取搜尋框的 placeholder
        seen_placeholders = set()
        for s in search_sel[:10]:
            ph = s.get_attribute("placeholder")
            if ph and ph not in seen_placeholders:
                seen_placeholders.add(ph)
                search_items.append({
                    "text": clean_text(ph),
                    "image_url": None,
                    "link_url": None,
                    "price": None,
                    "badge": None,
                    "description": None,
                })
        if not search_items:
            search_items.append({
                "text": "住宿地點 / 關鍵字",
                "image_url": None,
                "link_url": None,
                "price": None,
                "badge": None,
                "description": "搜尋框：請輸入住宿地點、飯店名稱",
            })
        sections.append({
            "id": "search_bar",
            "type": "search_bar",
            "title": None,
            "items": search_items,
        })

        # ────────────────────────────────────────────────────────
        # Section B: hero_banner (大圖輪播)
        # ────────────────────────────────────────────────────────
        banner_items = []
        banner_sels = page.query_selector_all(
            ".banner, .slider, .carousel, .swiper-slide, "
            "[class*='banner'], [class*='slider'], [class*='swiper-slide'], "
            ".hero, [class*='hero']"
        )
        seen_banners = set()
        for el in banner_sels[:15]:
            img = el.query_selector("img")
            link = el.query_selector("a") or el
            img_src = extract_src(img) if img else None
            href = link.get_attribute("href") if link else None

            title_el = el.query_selector("h1, h2, h3, .title, .heading, [class*='title']")
            title_text = clean_text(title_el.inner_text()) if title_el else None

            badge_el = el.query_selector(".badge, .tag, .label, [class*='badge'], [class*='tag']")
            badge_text = clean_text(badge_el.inner_text()) if badge_el else None

            key = (img_src, href)
            if key in seen_banners:
                continue
            seen_banners.add(key)

            local_url = None
            if img_src:
                local_url = save_image(abs_url(TARGET_URL, img_src), "banner")

            if local_url or title_text:
                banner_items.append({
                    "text": title_text,
                    "image_url": local_url,
                    "link_url": abs_url(TARGET_URL, href),
                    "price": None,
                    "badge": badge_text,
                    "description": None,
                })
            time.sleep(0.1)

        if banner_items:
            sections.append({
                "id": "hero_banner",
                "type": "hero_banner",
                "title": None,
                "items": banner_items,
            })

        # ────────────────────────────────────────────────────────
        # Section C: featured_hotels (精選飯店)
        # ────────────────────────────────────────────────────────
        hotel_items = []
        hotel_sels = page.query_selector_all(
            ".hotel-card, .product-card, .card, [class*='hotel-card'], "
            "[class*='product-card'], [class*='item-card'], [class*='product-item'], "
            "li[class*='item'], .result-item, [class*='result-card']"
        )
        seen_hotels = set()
        for el in hotel_sels[:30]:
            img = el.query_selector("img")
            img_src = extract_src(img) if img else None

            name_el = el.query_selector(
                ".name, .title, h3, h4, [class*='name'], [class*='title'], a.title"
            )
            name_text = clean_text(name_el.inner_text()) if name_el else None

            price_el = el.query_selector(".price, .amount, [class*='price'], [class*='amount']")
            price_text = clean_text(price_el.inner_text()) if price_el else None

            badge_el = el.query_selector(".badge, .tag, .label, [class*='badge'], [class*='tag']")
            badge_text = clean_text(badge_el.inner_text()) if badge_el else None

            desc_el = el.query_selector(".description, .subtitle, .desc, [class*='desc']")
            desc_text = clean_text(desc_el.inner_text()) if desc_el else None

            link = el.query_selector("a")
            href = link.get_attribute("href") if link else None

            key = (name_text, price_text)
            if key in seen_hotels or (not name_text and not img_src):
                continue
            seen_hotels.add(key)

            local_url = None
            if img_src:
                local_url = save_image(abs_url(TARGET_URL, img_src), "product")

            hotel_items.append({
                "text": name_text,
                "image_url": local_url,
                "link_url": abs_url(TARGET_URL, href),
                "price": price_text,
                "badge": badge_text,
                "description": desc_text,
            })
            time.sleep(0.1)

        if hotel_items:
            sections.append({
                "id": "featured_hotels",
                "type": "featured_items",
                "title": "精選飯店推薦",
                "items": hotel_items[:20],
            })

        # ────────────────────────────────────────────────────────
        # Section D: destination_grid (熱門住宿目的地)
        # ────────────────────────────────────────────────────────
        dest_items = []
        dest_sels = page.query_selector_all(
            ".destination, [class*='destination'], [class*='city'], "
            "[class*='area'], [class*='region'], [class*='country'], "
            ".location-card, [class*='location']"
        )
        seen_dest = set()
        for el in dest_sels[:30]:
            img = el.query_selector("img")
            img_src = extract_src(img) if img else None

            text_el = el.query_selector(
                ".name, span, p, h4, h5, [class*='name'], [class*='label'], [class*='title']"
            )
            dest_text = clean_text(text_el.inner_text()) if text_el else None
            if not dest_text:
                dest_text = clean_text(el.inner_text())

            link = el.query_selector("a") or el
            href = link.get_attribute("href") if link else None

            key = (dest_text, href)
            if key in seen_dest or not dest_text:
                continue
            seen_dest.add(key)

            local_url = None
            if img_src:
                local_url = save_image(abs_url(TARGET_URL, img_src), "destination")

            dest_items.append({
                "text": dest_text[:50] if dest_text else None,
                "image_url": local_url,
                "link_url": abs_url(TARGET_URL, href),
                "price": None,
                "badge": None,
                "description": None,
            })
            time.sleep(0.1)

        if dest_items:
            sections.append({
                "id": "destination_grid",
                "type": "destination_grid",
                "title": "熱門住宿目的地",
                "items": dest_items[:20],
            })

        # ────────────────────────────────────────────────────────
        # Section E: theme_section (主題住宿)
        # ────────────────────────────────────────────────────────
        theme_items = []
        theme_sels = page.query_selector_all(
            ".theme, [class*='theme'], [class*='tag-item'], "
            "[class*='category'], [class*='filter'], .tab, [class*='tab-item']"
        )
        seen_theme = set()
        for el in theme_sels[:30]:
            img = el.query_selector("img")
            img_src = extract_src(img) if img else None

            text_el = el.query_selector("span, p, a, h5, [class*='name'], [class*='text']")
            theme_text = clean_text(text_el.inner_text()) if text_el else clean_text(el.inner_text())

            link = el.query_selector("a") or el
            href = link.get_attribute("href") if link else None

            key = theme_text
            if not theme_text or key in seen_theme:
                continue
            seen_theme.add(key)

            local_url = None
            if img_src:
                local_url = save_image(abs_url(TARGET_URL, img_src), "theme")

            theme_items.append({
                "text": theme_text[:50],
                "image_url": local_url,
                "link_url": abs_url(TARGET_URL, href),
                "price": None,
                "badge": None,
                "description": None,
            })

        if theme_items:
            sections.append({
                "id": "theme_section",
                "type": "theme_section",
                "title": "主題住宿",
                "items": theme_items[:15],
            })

        # ────────────────────────────────────────────────────────
        # Section F: promo_section (限時優惠)
        # ────────────────────────────────────────────────────────
        promo_items = []
        promo_sels = page.query_selector_all(
            ".promo, [class*='promo'], [class*='offer'], [class*='deal'], "
            "[class*='sale'], [class*='discount'], [class*='special']"
        )
        seen_promo = set()
        for el in promo_sels[:20]:
            img = el.query_selector("img")
            img_src = extract_src(img) if img else None

            title_el = el.query_selector("h3, h4, .title, [class*='title'], [class*='name']")
            title_text = clean_text(title_el.inner_text()) if title_el else None

            price_el = el.query_selector(".price, .amount, [class*='price']")
            price_text = clean_text(price_el.inner_text()) if price_el else None

            badge_el = el.query_selector(".badge, .tag, [class*='badge'], [class*='tag']")
            badge_text = clean_text(badge_el.inner_text()) if badge_el else None

            link = el.query_selector("a")
            href = link.get_attribute("href") if link else None

            key = (title_text, href)
            if key in seen_promo or not title_text:
                continue
            seen_promo.add(key)

            local_url = None
            if img_src:
                local_url = save_image(abs_url(TARGET_URL, img_src), "promo")

            promo_items.append({
                "text": title_text,
                "image_url": local_url,
                "link_url": abs_url(TARGET_URL, href),
                "price": price_text,
                "badge": badge_text,
                "description": None,
            })
            time.sleep(0.1)

        if promo_items:
            sections.append({
                "id": "promo_section",
                "type": "promo_section",
                "title": "限時優惠",
                "items": promo_items[:15],
            })

        browser.close()

    # ── 5. 後處理：清空字串改 null ────────────────────────────
    def clean_item(item: dict) -> dict:
        result = {}
        for k, v in item.items():
            if isinstance(v, str):
                v = v.strip()
                result[k] = v if v else None
            else:
                result[k] = v
        return result

    for sec in sections:
        sec["items"] = [clean_item(i) for i in sec["items"]]

    # ── 6. 若 sections 為空補 fallback ───────────────────────
    if not sections:
        sections = []
        result = {
            "page": "旅館",
            "scraped_at": scraped_at,
            "url": TARGET_URL,
            "error": "no_sections_found",
            "sections": sections,
        }
    else:
        result = {
            "page": "旅館",
            "scraped_at": scraped_at,
            "url": TARGET_URL,
            "sections": sections,
        }

    # ── 7. 寫 JSON ────────────────────────────────────────────
    json_path = OUTPUT_DIR / "旅館.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nDone. sections={len(sections)}, json={json_path}")
    imgs = list(IMAGES_DIR.glob("*"))
    print(f"Images downloaded: {len(imgs)}")
    for i in imgs:
        print(f"  {i.name} ({i.stat().st_size // 1024}KB)")

    return result


if __name__ == "__main__":
    crawl()
