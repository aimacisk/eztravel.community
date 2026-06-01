# eztravel.community — 爬蟲摘要 (Crawler Brief)

> **Owner**: BA agent (T-eztcomm-20260601-W1-BA-1)
> **Version**: 1.0.0
> **建立日期**: 2026-06-01 (TST)
> **對應 Wish**: W-eztcomm-20260601-REBUILD
> **下游**: PG (W1-PG-1~7)、AQ (W1-AQ-1)
> **Schema 規範**: [data_schema.md](./data_schema.md)

---

## §1 爬取目標一覽

| # | 資料夾 | 目標 URL | 備註 |
|---|--------|---------|------|
| 1 | `homepage` | `https://www.eztravel.com.tw/` | 主站首頁 |
| 2 | `機票` | `https://flight.eztravel.com.tw/` | 機票搜尋主頁 |
| 3 | `旅館` | `https://hotel.eztravel.com.tw/` | 旅館/住宿主頁 |
| 4 | `團體` | `https://vacation.eztravel.com.tw/` | 國外旅遊/團體跟團主頁 |
| 5 | `自由行` | `https://packages.eztravel.com.tw/` | 機加酒自由行主頁 |
| 6 | `票券` | `https://activity.eztravel.com.tw/` | 票券活動（饗玩樂）主頁 |
| 7 | `景點` | `https://trip.eztravel.com.tw/` | 台灣旅遊／景點主頁 |

> **URL 確認來源**：2026-06-01 TST 實際訪問 `https://www.eztravel.com.tw/` 導覽列確認。
> **注意**：上述為 PG 爬取時應優先嘗試的 URL；若 URL 發生 redirect 或 404，依 §5 升級規則處理。

---

## §2 每頁預期輸出

| 資料夾 | JSON 檔 | 截圖 | images/ | 備註 |
|--------|---------|------|---------|------|
| `homepage` | `homepage.json` | `homepage_screenshot.png` | 各 section 圖片 | 首頁 sections 最多，預期 6~10 個 |
| `機票` | `機票.json` | `機票_screenshot.png` | 促銷圖/航線圖 | 以 search_bar + hot_routes 為主 |
| `旅館` | `旅館.json` | `旅館_screenshot.png` | 飯店/目的地圖片 | 含 destination_grid |
| `團體` | `團體.json` | `團體_screenshot.png` | 行程/目的地圖片 | 含 featured_tours |
| `自由行` | `自由行.json` | `自由行_screenshot.png` | 套裝/目的地圖片 | 含 hot_packages |
| `票券` | `票券.json` | `票券_screenshot.png` | 票券/活動圖片 | 含 category_nav |
| `景點` | `景點.json` | `景點_screenshot.png` | 景點圖片 | 含 destination_grid |

### 截圖規格

| 項目 | 規格 |
|------|------|
| 每頁截圖數量 | **1 張全頁截圖** |
| 截圖格式 | PNG |
| 截圖模式 | full-page（完整頁面，含需 scroll 才能看到的內容） |
| 裝置模擬 | Desktop 1920×1080（不做行動版） |
| 檔名 | `{資料夾名稱}_screenshot.png` |

---

## §3 爬取技術規格（Playwright）

### 3.1 工具選擇

- **工具**：Playwright（Python 或 Node.js；建議 Python 對應平台工具鏈）
- **瀏覽器**：Chromium（headless）
- **理由**：eztravel 為重度動態 JS 渲染網站，需真實瀏覽器才能正確取得內容

### 3.2 必要等待策略

```
IF 頁面含大量商品卡片 THEN
  等待策略 = networkidle（網路空閒）
  timeout = 30000ms
ELSE IF 頁面含 lazy-load 圖片 THEN
  等待策略 = scroll_to_bottom（捲動至底部觸發 lazy load），再等 networkidle
  timeout = 45000ms
```

**等待順序（必須依序執行）**：

1. `page.goto(url, wait_until='networkidle', timeout=30000)`
2. 捲動至頁面底部（觸發 lazy-load）：`page.evaluate("window.scrollTo(0, document.body.scrollHeight)")`
3. 再次等待 networkidle：`page.wait_for_load_state('networkidle')`
4. 截全頁圖：`page.screenshot(path=..., full_page=True)`
5. 擷取 DOM 內容

### 3.3 動態 JS 載入注意事項

| 問題 | 症狀 | 對應策略 |
|------|------|---------|
| SPA 首次渲染延遲 | 截圖為空白或 loading 動畫 | 等待特定 CSS selector 出現：`.product-card`, `.banner`, `.promo-item` |
| Lazy-load 圖片未載入 | `image_url` 為空或為佔位圖 URL | 擷取 `data-src` 屬性替代 `src`；若仍為空填 null |
| 無限捲動分頁 | 首次僅顯示 N 筆，需捲動才出現更多 | **不**做 infinite scroll；只擷取初始載入可見的所有項目 |
| Popup / Cookie 通知 | 蓋住內容 | `page.keyboard.press('Escape')` 或點擊 `.close`, `.dismiss` 按鈕 |
| Cloudflare Bot 防護 | 出現 challenge page | 見 §5 升級規則 |

### 3.4 圖片下載規格

- **下載策略**：對 `items[].image_url` 中的絕對 URL 進行下載
- **命名**：依 §6 of data_schema.md 規範：`{category}_{type}_{index}.{ext}`
- **儲存位置**：`data/{資料夾名稱}/images/`
- **跳過條件**：GIVEN image_url 為 null 或為 base64 data URI，THEN 跳過下載

### 3.5 速率控制

| 設定 | 值 | 說明 |
|------|----|------|
| 頁間間隔 | ≥ 3 秒 | 7 頁依序爬取，每頁之間 sleep(3) |
| 圖片下載間隔 | ≥ 0.5 秒 | 每張圖片下載間隔 sleep(0.5) |
| 並行度 | 1（序列） | 不做並行爬取，避免觸動防護 |

---

## §4 JSON 欄位擷取對應表

PG 依此對應從 DOM 擷取欄位：

| JSON 欄位 | DOM 擷取來源（參考） |
|-----------|------------------|
| `sections[].title` | section 標題：`h2`, `h3`, `.section-title`, `.heading` |
| `items[].text` | 商品/連結標題：`a.title`, `.product-name`, `.card-title`, `span.name` |
| `items[].image_url` | `img.src`；lazy-load 用 `img[data-src]` 或 `img[data-lazy-src]` |
| `items[].link_url` | 最近父層的 `a.href` |
| `items[].price` | `.price`, `.amount`, `[class*="price"]`，保留原始文字 |
| `items[].badge` | `.badge`, `.tag`, `.label`, `[class*="badge"]`，保留原始文字 |
| `items[].description` | `.description`, `.subtitle`, `.card-desc` |

> **精確性要求**：所有擷取值保留原始頁面文字，**不做摘要或改寫**。

---

## §5 升級規則（Escalation）

| 情況 | 條件 | 處理方式 |
|------|------|---------|
| URL 404 或永久 Redirect | `response.status == 404` 或重定向超過 3 次 | 記錄於 `{資料夾名稱}.json` 頂層 `error` 欄位；繼續其他頁；完工前通知 admin |
| Cloudflare 攔截 | 頁面標題含 "Just a moment" 或 status 403/503 | 嘗試 1 次 slow-mode（slowMo=2000）；仍失敗則記錄 `error`；升級通知 admin |
| 截圖全空白 | PNG 有效但像素多為白色 | 增加 wait_for_selector 等待 3 秒再截；仍失敗記錄 `error` |
| JSON 結構異常 | 無法識別任何 section | 至少輸出 `{"page":..., "scraped_at":..., "url":..., "sections":[], "error":"no_sections_found"}` |
| 爬取被 IP 封鎖 | 全部請求均 timeout | 停止；升級通知 admin；**不**重試，等待人工處理 |

### error 欄位格式（選填，僅異常時使用）

```json
{
  "page": "機票",
  "scraped_at": "2026-06-01T08:05:00.000Z",
  "url": "https://flight.eztravel.com.tw/",
  "error": "cloudflare_blocked",
  "sections": []
}
```

---

## §6 輸出驗收標準（AC）

| AC | 條件 | 驗證方式 |
|----|------|---------|
| AC-crawl-01 | GIVEN 7 個資料夾，WHEN 爬取完成，THEN 每個資料夾存在對應 `.json` 檔 | AQ Glob |
| AC-crawl-02 | GIVEN 7 個截圖，WHEN 爬取完成，THEN 每個 `{資料夾名稱}_screenshot.png` 存在且大小 > 10KB | AQ Glob + 檔案大小檢查 |
| AC-crawl-03 | GIVEN 每個 JSON，WHEN 驗證 `sections` 陣列，THEN 元素數量 ≥ 1（除非該頁有 `error` 欄位記錄） | AQ 程式驗證 |
| AC-crawl-04 | GIVEN 所有 JSON 中的 `items[].image_url` 非 null 值，WHEN 對應到 `images/` 目錄，THEN 對應圖檔物理存在 | AQ 程式驗證 |
| AC-crawl-05 | GIVEN 截圖，WHEN 以肉眼比對 `sections` 陣列數量，THEN 至少 80% 的畫面可見區塊有對應 section 記錄 | AQ 人工比對 |
| AC-crawl-06 | GIVEN JSON `scraped_at`，WHEN 與現在時間比較，THEN 差距 ≤ 48 小時（確保資料新鮮度） | AQ 時間戳驗證 |

---

## §7 相關資源

| 資源 | 路徑/連結 |
|------|---------|
| JSON Schema 規範 | `projects/eztravel.community/01_requirements/data_schema.md` |
| PG 實作卡 | T-eztcomm-20260601-W1-PG-1（homepage）～T-eztcomm-20260601-W1-PG-7（景點） |
| AQ 驗收卡 | T-eztcomm-20260601-W1-AQ-1 |
| Design Spec | `docs/superpowers/specs/2026-06-01-eztravel-community-rebuild-design.md` §3 Wave 1 |
| robots.txt | `https://www.eztravel.com.tw/robots.txt`（爬取前必讀） |
