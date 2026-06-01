---
task_id: T-eztcomm-20260601-W1-PG-2
title: "[W1] PG — Playwright 爬機票分類頁 → data/機票/"
agent: pg
scraped_at: 2026-06-01T08:44:52.000Z
status: DONE
---

# 機票分類頁爬蟲實作紀錄

## 模組結構

```
data/機票/
├── 機票.json            # 主要資料（6 sections / 75 items）
├── 機票_screenshot.png  # 全頁截圖（1.44 MB，1920×1080 desktop）
└── images/              # 50 張圖片（43 banner + 7 product/logo）
    ├── flight_banner_01.jpg … flight_banner_43.jpg
    └── flight_product_01.png … flight_product_07.png

scripts/
└── crawl_flight.py      # 爬蟲腳本（供複用或除錯）
```

## 爬取環境

| 項目 | 值 |
|------|----|
| URL | https://flight.eztravel.com.tw/ |
| 瀏覽器 | Chromium 1208（`ms-playwright/chromium-1208`） |
| Viewport | 1920 × 1080 |
| Wait 策略 | `networkidle` → 捲動底部 → 二次 `networkidle` |
| 執行方式 | Python 3.12 + `playwright` async API |

## 擷取到的 Section 清單

| id | type | items |
|----|------|-------|
| `search_bar` | `search_bar` | 13（出發地/目的地/去回程/艙等/人數 等搜尋欄位） |
| `hero_banner` | `hero_banner` | 42（促銷活動輪播 banner） |
| `promo_fares` | `promo_section` | 1（折扣碼管理連結） |
| `hot_routes` | `product_list` | 9（航線資訊、學生票、廉航懶人包等快速連結） |
| `airline_section` | `other` | 7（廉航快速票價連結 + logo 圖片） |
| `visa_info` | `quick_links` | 2（護照簽證連結） |

## Schema AC 驗證結果

| AC | 結果 |
|----|------|
| AC-schema-01 頂層 4 欄位 | ✅ PASS |
| AC-schema-02 sections 欄位完整 | ✅ PASS |
| AC-schema-03 id 唯一性 | ✅ PASS |
| AC-schema-04 type 合法值 | ✅ PASS |
| AC-schema-05 無空字串 | ✅ PASS |
| AC-schema-08 image_url 對應圖檔存在 | ✅ PASS |
| AC-naming-01 圖檔命名規範 | ✅ PASS |

## 修復迴圈紀錄

| 輪次 | 問題 | 處置 |
|------|------|------|
| R1 | Playwright MCP 被其他 session 佔用 | Fallback → Python playwright + 指定 chromium-1208 路徑 |
| R2 | UnicodeEncodeError（print ✅ emoji on cp950） | JSON 已正常落盤，crash 在 print，不影響輸出 |
| R3 | search_bar 49 items 含重複 / visa_info 4 items 含重複 | 執行去重清洗腳本（text+link+image 三欄聯合鍵） |

## 已知技術債

- `search_bar` DOM 選擇器較寬泛（匹配多個 form 實例）；若頁面改版可在 `crawl_flight.py` 縮小 selector。
- `promo_fares` 僅擷取到 1 個有效 item（折扣碼管理）；頁面實際促銷區塊可能為 AJAX 後載入，建議 AQ 驗收時確認截圖是否有更多促銷卡片。
- `footer_links` 未擷取到（JS 動態渲染 footer，頁面結構較特殊）。

## 圖片下載統計

- 總計 50 張，全部 ≤ 2 MB 限制
- 格式：43 × jpg + 7 × png
- 命名符合 `flight_{type}_{nn}.{ext}` 規範
