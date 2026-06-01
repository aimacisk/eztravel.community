"""
crawl_packages.py v2 — eztravel 自由行分類頁爬蟲（Next.js CSS Modules 版）
目標 URL: https://packages.eztravel.com.tw/
輸出:
  data/自由行/自由行.json
  data/自由行/自由行_screenshot.png
  data/自由行/images/freetour_{type}_{nn}.{ext}

頁面架構（分析後確認）:
  - search_bar:       .container[class*=has-search-engine] 內的搜尋表單
  - hero_banner:      .swiper-slide img（需去重 Swiper clone）
  - hot_packages:     [class*=WidgetTrendingFareProductCard_card]（6張有價格商品卡）
  - hot_products:     [class*=HotProducts_list__]（快速連結列表）
  - article_section:  [class*=ArticleLayout_article_layout]（2個 tab 式區塊）
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request

# ── 設定 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR  = BASE_DIR / "data" / "自由行"
IMG_DIR  = OUT_DIR / "images"
JSON_OUT = OUT_DIR / "自由行.json"
SS_OUT   = OUT_DIR / "自由行_screenshot.png"

TARGET_URL    = "https://packages.eztravel.com.tw/"
CATEGORY      = "freetour"
MAX_IMG_BYTES = 2 * 1024 * 1024
IMG_DELAY     = 0.5
CHROME_EXE    = r"C:\Users\micch\AppData\Local\ms-playwright\chromium-1208\chrome-win64\chrome.exe"

_img_counters: dict[str, int] = {}

def next_img_name(img_type: str, ext: str) -> str:
    idx = _img_counters.get(img_type, 0) + 1
    _img_counters[img_type] = idx
    return f"{CATEGORY}_{img_type}_{idx:02d}.{ext}"

def dedup_items(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in items:
        key = (it.get("text"), it.get("link_url"), it.get("image_url"))
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out

def clean_item(it: dict) -> dict:
    return {k: (v if (v is not None and str(v).strip() != "") else None)
            for k, v in it.items()}

# ── JS 擷取腳本（對應 packages.eztravel.com.tw 的 Next.js 架構） ──
EXTRACT_JS = r"""
() => {
  const txt = (el) => el ? (el.innerText.trim() || null) : null;
  const href = (el) => {
    if (!el) return null;
    const a = (el.tagName === 'A') ? el : el.closest('a');
    if (a && a.href && !a.href.startsWith('javascript')) return a.href;
    return null;
  };
  const imgSrc = (el) => {
    if (!el) return null;
    const src = el.getAttribute('data-src') || el.getAttribute('src') || null;
    if (!src || src.startsWith('data:')) return null;
    if (src.startsWith('http')) return src;
    if (src.startsWith('//')) return 'https:' + src;
    return null;
  };

  const sections = [];

  // ─── 1. search_bar ──────────────────────────────────────
  const searchWrapper = document.querySelector(
    '[class*="has-search-engine"], [class*="search-engine"], '+
    '[class*="SearchEngine"], form[class*="search"], .search-bar'
  );
  if (searchWrapper) {
    const inputs = Array.from(searchWrapper.querySelectorAll(
      'input, select, button[type="submit"], [class*="selector"], [class*="Selector"], '+
      '[class*="tab"][class*="active"], [class*="Tab"]'
    ));
    const items = inputs.slice(0, 20).map(el => ({
      text: (txt(el) || el.placeholder || el.getAttribute('aria-label') || el.getAttribute('title') || null),
      image_url: null,
      link_url: null,
      price: null,
      badge: null,
      description: (el.tagName === 'INPUT' ? (el.placeholder || null) : null)
    })).filter(i => i.text || i.description);
    if (items.length > 0) {
      sections.push({ id: 'search_bar', type: 'search_bar', title: null, items: items });
    }
  }

  // ─── 2. hero_banner (Swiper, dedup by src) ───────────────
  const swiperImgs = document.querySelectorAll(
    '.swiper-slide:not(.swiper-slide-duplicate) img, '+
    '.swiper-wrapper .swiper-slide img'
  );
  // dedup by src
  const bannerSeen = new Set();
  const bannerItems = [];
  for (const img of swiperImgs) {
    const src = imgSrc(img);
    if (!src || bannerSeen.has(src)) continue;
    bannerSeen.add(src);
    bannerItems.push({
      text: img.alt || txt(img.closest('[class*="banner"],[class*="slide-content"]')) || null,
      image_url: src,
      link_url: href(img),
      price: null,
      badge: null,
      description: null
    });
    if (bannerItems.length >= 30) break;
  }
  if (bannerItems.length > 0) {
    sections.push({ id: 'hero_banner', type: 'hero_banner', title: null, items: bannerItems });
  }

  // ─── 3. hot_packages (WidgetTrendingFareProductCard) ─────
  const trendingCards = document.querySelectorAll('[class*=WidgetTrendingFareProductCard_card]');
  if (trendingCards.length > 0) {
    const items = Array.from(trendingCards).map(card => {
      const img = card.querySelector('img');
      const src = imgSrc(img);
      const titleEl = card.querySelector('h3,h4,[class*=title],[class*=Title],[class*=name]');
      const priceEl = card.querySelector('[class*=price],[class*=Price],strong');
      const badgeEl = card.querySelector('[class*=badge],[class*=Badge],[class*=tag],[class*=label]');
      const descEl  = card.querySelector('[class*=desc],[class*=Desc],[class*=sub],[class*=info]:not([class*=price])');
      const linkEl  = card.closest('a') || card.querySelector('a');
      if (!txt(titleEl) && !src) return null;
      return {
        text: txt(titleEl) || txt(card.querySelector('[class*=name]')),
        image_url: src || null,
        link_url: linkEl ? linkEl.href : null,
        price: txt(priceEl),
        badge: txt(badgeEl),
        description: txt(descEl)
      };
    }).filter(Boolean);
    if (items.length > 0) {
      sections.push({ id: 'hot_packages', type: 'product_list', title: null, items: items });
    }
  }

  // ─── 4. hot_products (HotProducts quick links) ───────────
  const hotListItems = document.querySelectorAll('[class*=HotProducts_list__]');
  if (hotListItems.length > 0) {
    const items = Array.from(hotListItems).map(li => {
      const a = li.querySelector('a');
      const label = txt(a) || txt(li);
      if (!label) return null;
      return {
        text: label,
        image_url: null,
        link_url: a ? a.href : null,
        price: null,
        badge: null,
        description: null
      };
    }).filter(Boolean);
    if (items.length > 0) {
      sections.push({ id: 'hot_products', type: 'quick_links', title: null, items: items });
    }
  }

  // ─── 5. article_sections (ArticleLayout tabs) ────────────
  const articleSecs = document.querySelectorAll('[class*=ArticleLayout_article_layout]');
  articleSecs.forEach((sec, idx) => {
    const titleEl = sec.querySelector('h2');
    const title = txt(titleEl);
    const secId = title
      ? title.replace(/[^a-z0-9一-龥]/gi, '_').toLowerCase().substring(0, 30)
      : `article_${idx + 1}`;

    // Inner product links (a tags with img)
    const innerLinks = Array.from(sec.querySelectorAll('a')).filter(a => {
      return a.href && !a.href.startsWith('javascript') && a.querySelector('img');
    }).slice(0, 20);

    if (innerLinks.length === 0) {
      // fallback: all a with text
      const textLinks = Array.from(sec.querySelectorAll('a')).filter(a => txt(a)).slice(0, 20);
      if (textLinks.length > 0) {
        const items = textLinks.map(a => ({
          text: txt(a),
          image_url: imgSrc(a.querySelector('img')),
          link_url: a.href,
          price: null,
          badge: null,
          description: null
        }));
        sections.push({ id: secId, type: 'featured_items', title: title, items: items });
      }
    } else {
      const items = innerLinks.map(a => {
        const img = a.querySelector('img');
        const nameEl = a.querySelector('h3,h4,[class*=name],[class*=title]');
        const priceEl = a.querySelector('[class*=price]');
        return {
          text: txt(nameEl) || txt(a),
          image_url: imgSrc(img),
          link_url: a.href,
          price: txt(priceEl),
          badge: null,
          description: null
        };
      });
      sections.push({ id: secId, type: 'featured_items', title: title, items: items });
    }
  });

  return sections;
}
"""

async def download_image(url: str, save_path: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > MAX_IMG_BYTES:
                return False
            save_path.write_bytes(data)
            return True
    except Exception:
        return False

async def main():
    from playwright.async_api import async_playwright

    IMG_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=CHROME_EXE,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await ctx.new_page()

        print("Navigating...", flush=True)
        try:
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=45000)
        except Exception as e:
            print(f"WARN load: {e}", flush=True)

        # 關閉 popup
        for sel in [".close", "[aria-label='Close']", "[class*='modal-close']", ".btn-close"]:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    await el.click()
                    await asyncio.sleep(0.5)
                    break
            except Exception:
                pass

        # scroll down
        print("Scrolling...", flush=True)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        try:
            await page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            await asyncio.sleep(3)

        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

        scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        print("Taking screenshot...", flush=True)
        await page.screenshot(path=str(SS_OUT), full_page=True)
        ss_size = SS_OUT.stat().st_size
        print(f"Screenshot: {ss_size/1024:.0f} KB", flush=True)

        print("Extracting DOM...", flush=True)
        raw_sections = await page.evaluate(EXTRACT_JS)
        await browser.close()

    # ── 後處理 ──────────────────────────────────────────
    sections = []
    download_queue: list[tuple[str, Path]] = []

    for sec in raw_sections:
        sec_type = sec.get("type", "other")
        type_map = {
            "hero_banner":      "banner",
            "search_bar":       "banner",
            "product_list":     "product",
            "featured_items":   "product",
            "destination_grid": "destination",
            "promo_section":    "promo",
            "quick_links":      "banner",
            "other":            "product",
        }
        img_type_tag = type_map.get(sec_type, "banner")

        items_out = []
        for it in (sec.get("items") or []):
            it_c = clean_item(it)
            img_url = it_c.get("image_url")
            if img_url and img_url.startswith("http"):
                ext_raw = img_url.split("?")[0].rsplit(".", 1)[-1].lower() if "." in img_url.split("?")[0] else "jpg"
                ext = ext_raw if ext_raw in ("jpg", "jpeg", "png", "webp") else "jpg"
                local_name = next_img_name(img_type_tag, ext)
                local_rel  = f"images/{local_name}"
                download_queue.append((img_url, IMG_DIR / local_name))
                it_c["image_url"] = local_rel
            items_out.append(it_c)

        items_out = dedup_items(items_out)
        sec["items"] = items_out
        sections.append(sec)

    print(f"\nDownloading {len(download_queue)} images...", flush=True)
    downloaded = 0
    for url, path in download_queue:
        ok = await download_image(url, path)
        if ok:
            downloaded += 1
        await asyncio.sleep(IMG_DELAY)
    print(f"Downloaded: {downloaded}/{len(download_queue)}", flush=True)

    # AC-schema-08: 驗證圖片實際存在
    for sec in sections:
        for it in sec.get("items", []):
            img_rel = it.get("image_url")
            if img_rel and img_rel.startswith("images/"):
                if not (OUT_DIR / img_rel).exists():
                    it["image_url"] = None

    result = {
        "page": "自由行",
        "scraped_at": scraped_at,
        "url": TARGET_URL,
        "sections": sections
    }
    JSON_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    json_size = JSON_OUT.stat().st_size

    total_items = sum(len(s.get("items", [])) for s in sections)
    print(f"\n=== Done ===", flush=True)
    print(f"sections: {len(sections)}", flush=True)
    print(f"total items: {total_items}", flush=True)
    print(f"images: {downloaded}/{len(download_queue)}", flush=True)
    print(f"JSON: {json_size/1024:.1f} KB", flush=True)
    print(f"Screenshot: {ss_size/1024:.1f} KB", flush=True)
    for s in sections:
        print(f"  [{s['id']}] type={s['type']} items={len(s['items'])}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
