"""
爬蟲：https://flight.eztravel.com.tw/
Task: T-eztcomm-20260601-W1-PG-2
Output: data/機票/{機票.json, 機票_screenshot.png, images/}
Schema: 01_requirements/data_schema.md §7.2
"""
import asyncio
import json
import os
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

# ── 常數 ──────────────────────────────────────────────
WORKTREE = Path(__file__).parent.parent
OUT_DIR   = WORKTREE / "data" / "機票"
IMG_DIR   = OUT_DIR / "images"
TARGET_URL = "https://flight.eztravel.com.tw/"
CATEGORY   = "flight"
CHROME_EXE = r"C:\Users\micch\AppData\Local\ms-playwright\chromium-1208\chrome-win64\chrome.exe"

MAX_IMG_BYTES = 2 * 1024 * 1024   # 2 MB

# ── Helper ─────────────────────────────────────────────
def to_abs_url(base: str, href: str | None) -> str | None:
    if not href or href.startswith("data:"):
        return None
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("http"):
        return href
    return urllib.parse.urljoin(base, href)

def none_or_str(s) -> str | None:
    if s is None:
        return None
    s = str(s).strip()
    return s if s else None

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")

def img_ext(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    _, ext = os.path.splitext(path)
    ext = ext.lower().lstrip(".")
    return ext if ext in ("jpg", "jpeg", "png", "webp") else "jpg"

def download_image(url: str, dest: Path) -> bool:
    """下載單張圖片，超過 2MB 或失敗回傳 False。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read(MAX_IMG_BYTES + 1)
        if len(data) > MAX_IMG_BYTES:
            print(f"  ⚠ 超 2MB 跳過: {url}")
            return False
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"  ⚠ 下載失敗 {url}: {e}")
        return False

# ── DOM 擷取 JS ────────────────────────────────────────
EXTRACT_JS = """
() => {
  const none = v => (v && v.trim()) ? v.trim() : null;
  const absUrl = (base, href) => {
    if (!href || href.startsWith('data:')) return null;
    if (href.startsWith('//')) return 'https:' + href;
    if (href.startsWith('http')) return href;
    try { return new URL(href, base).href; } catch { return null; }
  };
  const base = location.href;

  const sections = [];

  // ── 1. search_bar ────────────────────────────────
  const searchForms = document.querySelectorAll(
    'form, [class*="search"], [class*="Search"], [id*="search"]'
  );
  if (searchForms.length > 0) {
    const items = [];
    searchForms.forEach(f => {
      const placeholders = [...f.querySelectorAll('input[placeholder]')]
        .map(i => i.placeholder).filter(Boolean);
      const labels = [...f.querySelectorAll('label,button')]
        .map(el => el.textContent?.trim()).filter(Boolean);
      [...new Set([...placeholders, ...labels])].slice(0, 6).forEach(t => {
        items.push({ text: t, image_url: null, link_url: null, price: null, badge: null, description: null });
      });
    });
    if (items.length > 0) {
      sections.push({ id: 'search_bar', type: 'search_bar', title: null, items });
    }
  }

  // ── 2. hero_banner (輪播 / 大圖) ─────────────────
  const bannerSel = [
    '[class*="banner"]','[class*="Banner"]','[class*="hero"]','[class*="Hero"]',
    '[class*="carousel"]','[class*="Carousel"]','[class*="slider"]','[class*="Slider"]',
    '[class*="swiper"]'
  ].join(',');
  const bannerEls = document.querySelectorAll(bannerSel);
  if (bannerEls.length > 0) {
    const items = [];
    bannerEls.forEach(el => {
      const imgs = el.querySelectorAll('img');
      const links = el.querySelectorAll('a');
      imgs.forEach((img, idx) => {
        const src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy-src');
        const href = links[idx]?.href || links[0]?.href || null;
        const alt = none(img.alt);
        items.push({
          text: alt,
          image_url: absUrl(base, src),
          link_url: none(href),
          price: null,
          badge: none(el.querySelector('[class*="badge"],[class*="label"],[class*="tag"]')?.textContent),
          description: null
        });
      });
    });
    const uniq = items.filter((v,i,a) => a.findIndex(x=>x.image_url===v.image_url)===i);
    if (uniq.length > 0) {
      sections.push({ id: 'hero_banner', type: 'hero_banner', title: null, items: uniq });
    }
  }

  // ── 3. promo_fares / 促銷票價 ─────────────────────
  const promoSel = [
    '[class*="promo"]','[class*="Promo"]','[class*="deal"]','[class*="Deal"]',
    '[class*="特惠"]','[class*="促銷"]','[class*="sale"]','[class*="Sale"]',
    '[class*="discount"]','[class*="Discount"]','[class*="offer"]','[class*="Offer"]'
  ].join(',');
  const promoContainers = document.querySelectorAll(promoSel);
  if (promoContainers.length > 0) {
    const items = [];
    promoContainers.forEach(c => {
      const cards = c.querySelectorAll('[class*="card"],[class*="item"],[class*="ticket"]');
      const targets = cards.length > 0 ? cards : [c];
      targets.forEach(card => {
        const aEl = card.querySelector('a') || card.closest('a');
        const imgEl = card.querySelector('img');
        const priceEl = card.querySelector('[class*="price"],[class*="Price"],[class*="amount"],[class*="fare"]');
        const badgeEl = card.querySelector('[class*="badge"],[class*="tag"],[class*="label"]');
        const titleEl = card.querySelector('[class*="title"],[class*="name"],h3,h4,h2');
        const src = imgEl ? (imgEl.src || imgEl.getAttribute('data-src') || imgEl.getAttribute('data-lazy-src')) : null;
        items.push({
          text: none(titleEl?.textContent || aEl?.textContent),
          image_url: absUrl(base, src),
          link_url: none(aEl?.href),
          price: none(priceEl?.textContent),
          badge: none(badgeEl?.textContent),
          description: null
        });
      });
    });
    const uniq = items
      .filter(v => v.text || v.image_url)
      .filter((v,i,a) => a.findIndex(x=>x.text===v.text && x.link_url===v.link_url)===i)
      .slice(0, 20);
    if (uniq.length > 0) {
      sections.push({ id: 'promo_fares', type: 'promo_section', title: '特惠票價', items: uniq });
    }
  }

  // ── 4. hot_routes / 熱門航線 ──────────────────────
  const routeSel = [
    '[class*="route"]','[class*="Route"]','[class*="航線"]','[class*="destination"]',
    '[class*="Destination"]','[class*="popular"]','[class*="Popular"]',
    '[class*="hot"]','[class*="Hot"]'
  ].join(',');
  const routeContainers = document.querySelectorAll(routeSel);
  if (routeContainers.length > 0) {
    const items = [];
    routeContainers.forEach(c => {
      const cards = c.querySelectorAll('[class*="card"],[class*="item"],[class*="list"]');
      const targets = cards.length > 0 ? cards : [c];
      targets.forEach(card => {
        const aEl = card.querySelector('a') || card.closest('a');
        const imgEl = card.querySelector('img');
        const priceEl = card.querySelector('[class*="price"],[class*="Price"],[class*="amount"],[class*="fare"]');
        const badgeEl = card.querySelector('[class*="badge"],[class*="tag"]');
        const titleEl = card.querySelector('[class*="title"],[class*="name"],h3,h4,h2');
        const src = imgEl ? (imgEl.src || imgEl.getAttribute('data-src') || imgEl.getAttribute('data-lazy-src')) : null;
        items.push({
          text: none(titleEl?.textContent || aEl?.textContent),
          image_url: absUrl(base, src),
          link_url: none(aEl?.href),
          price: none(priceEl?.textContent),
          badge: none(badgeEl?.textContent),
          description: null
        });
      });
    });
    const uniq = items
      .filter(v => v.text || v.image_url)
      .filter((v,i,a) => a.findIndex(x=>x.text===v.text && x.link_url===v.link_url)===i)
      .slice(0, 20);
    if (uniq.length > 0) {
      sections.push({ id: 'hot_routes', type: 'product_list', title: '熱門航線', items: uniq });
    }
  }

  // ── 5. airline_section / 航空公司 ─────────────────
  const airlineSel = [
    '[class*="airline"]','[class*="Airline"]','[class*="航空"]',
    '[class*="carrier"]','[class*="Carrier"]'
  ].join(',');
  const airlineContainers = document.querySelectorAll(airlineSel);
  if (airlineContainers.length > 0) {
    const items = [];
    airlineContainers.forEach(c => {
      const els = c.querySelectorAll('a,img,[class*="item"],[class*="logo"]');
      els.forEach(el => {
        const imgEl = el.tagName === 'IMG' ? el : el.querySelector('img');
        const aEl  = el.tagName === 'A'   ? el : el.querySelector('a') || el.closest('a');
        const src  = imgEl ? (imgEl.src || imgEl.getAttribute('data-src')) : null;
        const txt  = none(el.textContent || imgEl?.alt);
        if (txt || src) {
          items.push({
            text: txt,
            image_url: absUrl(base, src),
            link_url: none(aEl?.href),
            price: null, badge: null, description: null
          });
        }
      });
    });
    const uniq = items
      .filter((v,i,a) => a.findIndex(x=>x.text===v.text)===i)
      .slice(0, 30);
    if (uniq.length > 0) {
      sections.push({ id: 'airline_section', type: 'other', title: '航空公司', items: uniq });
    }
  }

  // ── 6. visa_info / 簽證資訊 ───────────────────────
  const visaLinks = [...document.querySelectorAll('a')].filter(a =>
    /簽證|visa|VISA/i.test(a.textContent + a.href)
  );
  if (visaLinks.length > 0) {
    const items = visaLinks.slice(0, 10).map(a => ({
      text: none(a.textContent),
      image_url: null,
      link_url: none(a.href),
      price: null, badge: null, description: null
    }));
    sections.push({ id: 'visa_info', type: 'quick_links', title: '簽證資訊', items });
  }

  // ── 7. footer_links ───────────────────────────────
  const footerEl = document.querySelector('footer,[class*="footer"],[class*="Footer"]');
  if (footerEl) {
    const links = [...footerEl.querySelectorAll('a')].slice(0, 20);
    const items = links.map(a => ({
      text: none(a.textContent),
      image_url: null,
      link_url: none(a.href),
      price: null, badge: null, description: null
    })).filter(v => v.text);
    if (items.length > 0) {
      sections.push({ id: 'footer_links', type: 'footer_links', title: null, items });
    }
  }

  return sections;
}
"""

# ── 主爬蟲 ─────────────────────────────────────────────
async def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_EXE,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        # ── 導航 ─────────────────────────────────────
        print(f"[1] 導航至 {TARGET_URL}")
        try:
            resp = await page.goto(TARGET_URL, wait_until="networkidle", timeout=45000)
            if resp and resp.status in (404, 403, 503):
                print(f"  HTTP {resp.status} — 記錄 error")
                result = {
                    "page": "機票",
                    "scraped_at": scraped_at,
                    "url": TARGET_URL,
                    "error": f"http_{resp.status}",
                    "sections": []
                }
                (OUT_DIR / "機票.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                await browser.close()
                return
        except Exception as e:
            # timeout / cloudflare 等 → 降速重試一次
            print(f"  ⚠ 首次導航失敗: {e}，slow-mode 重試...")
            await browser.close()
            browser = await p.chromium.launch(
                executable_path=CHROME_EXE,
                headless=True,
                slow_mo=2000,
                args=["--no-sandbox"]
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            try:
                await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            except Exception as e2:
                print(f"  ✗ 第二次導航仍失敗: {e2}")
                result = {
                    "page": "機票",
                    "scraped_at": scraped_at,
                    "url": TARGET_URL,
                    "error": "navigation_failed",
                    "sections": []
                }
                (OUT_DIR / "機票.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                await browser.close()
                return

        # ── popup 處理 ───────────────────────────────
        print("[2] 關閉可能彈出的 popup")
        await page.keyboard.press("Escape")
        for sel in ["button.close", "button.dismiss", "[class*='close']", "[aria-label='close']",
                    "[class*='Close']", ".modal-close", ".popup-close"]:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.click()
                    print(f"  點擊關閉: {sel}")
                    break
            except Exception:
                pass
        await asyncio.sleep(1)

        # ── 捲動觸發 lazy-load ───────────────────────
        print("[3] 捲動至底部觸發 lazy-load")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # ── 全頁截圖 ─────────────────────────────────
        screenshot_path = OUT_DIR / "機票_screenshot.png"
        print(f"[4] 截全頁圖 → {screenshot_path}")
        await page.screenshot(path=str(screenshot_path), full_page=True)
        sz = screenshot_path.stat().st_size
        print(f"  截圖大小: {sz/1024:.1f} KB")

        # ── DOM 擷取 ─────────────────────────────────
        print("[5] 擷取 DOM 資料")
        sections_raw = await page.evaluate(EXTRACT_JS)
        print(f"  擷取到 {len(sections_raw)} 個 section")

        # ── 圖片下載 ─────────────────────────────────
        print("[6] 下載圖片")
        img_counter: dict[str, int] = {}
        def next_index(type_slug: str) -> str:
            img_counter[type_slug] = img_counter.get(type_slug, 0) + 1
            return f"{img_counter[type_slug]:02d}"

        TYPE_SLUG_MAP = {
            "hero_banner":      "banner",
            "promo_section":    "promo",
            "product_list":     "product",
            "destination_grid": "destination",
            "featured_items":   "product",
            "search_bar":       "nav_icon",
            "other":            "product",
        }

        for sec in sections_raw:
            type_slug = TYPE_SLUG_MAP.get(sec.get("type", ""), "product")
            for item in sec.get("items", []):
                raw_url = item.get("image_url")
                if not raw_url:
                    continue
                ext = img_ext(raw_url)
                idx = next_index(type_slug)
                fname = f"{CATEGORY}_{type_slug}_{idx}.{ext}"
                dest = IMG_DIR / fname
                print(f"  ↓ {fname}")
                ok = download_image(raw_url, dest)
                if ok:
                    item["image_url"] = f"images/{fname}"
                    time.sleep(0.5)
                else:
                    item["image_url"] = None

        # ── 建構最終 JSON ────────────────────────────
        # 過濾空 items + null text / image_url 的孤立 item
        clean_sections = []
        for sec in sections_raw:
            clean_items = []
            for it in sec.get("items", []):
                # AC-items-02: 空字串改 null
                cleaned = {k: (v if v and str(v).strip() else None) for k, v in it.items()}
                # 至少有一個有意義欄位才保留
                if any(cleaned.values()):
                    clean_items.append(cleaned)
            if clean_items or sec.get("id") == "search_bar":
                sec["items"] = clean_items
                clean_sections.append(sec)

        result = {
            "page": "機票",
            "scraped_at": scraped_at,
            "url": TARGET_URL,
            "sections": clean_sections if clean_sections else []
        }
        if not clean_sections:
            result["error"] = "no_sections_found"

        json_path = OUT_DIR / "機票.json"
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✅ 完成！JSON → {json_path}")
        print(f"   sections: {len(clean_sections)}")
        imgs = list(IMG_DIR.iterdir()) if IMG_DIR.exists() else []
        print(f"   images/: {len(imgs)} 個檔案")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
