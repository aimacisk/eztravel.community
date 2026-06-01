---
task_id: T-eztcomm-20260601-W1-PG-5
title: "[W1] PG — Playwright 爬自由行分類頁 → data/自由行/"
agent: pg
scraped_at: 2026-06-01T09:03:28.000Z
status: DONE
---

# 自由行分類頁爬蟲實作紀錄

## 模組結構

```
data/自由行/
├── 自由行.json              # 主要資料（6 sections / 58 items）
├── 自由行_screenshot.png    # 全頁截圖（2630 KB，1920×1080 desktop）
└── images/                  # 48 張圖片（30 banner + 6 hot_packages + 12 article）
    ├── freetour_banner_01.jpg … freetour_banner_30.jpg
    └── freetour_product_01.png … freetour_product_16.jpg

scripts/
└── crawl_packages.py        # 爬蟲腳本（v2，Next.js CSS Modules 選擇器版本）
```

## 爬取環境

| 項目 | 值 |
|------|----|
| URL | https://packages.eztravel.com.tw/ |
| 瀏覽器 | Chromium 1208（`ms-playwright/chromium-1208`） |
| Viewport | 1920 × 1080 |
| Wait 策略 | `networkidle` → 捲動底部 → 二次 `networkidle` |
| 執行方式 | Python 3.12 + `playwright` async API |

## 擷取到的 Section 清單

| id | type | items | 說明 |
|----|------|-------|------|
| `search_bar` | `search_bar` | 3 | 出發地／目的地／日期搜尋欄位 |
| `hero_banner` | `hero_banner` | 30 | 促銷活動 Swiper 輪播 banner（已去重 clone slides） |
| `hot_packages` | `product_list` | 6 | 熱門機加酒套裝商品卡（含價格） |
| `hot_products` | `quick_links` | 9 | 熱門目的地快速連結 |
| `航空專區` | `featured_items` | 5 | 航空公司專屬套裝（香港快運等） |
| `主題活動` | `featured_items` | 5 | 主題行程（沖繩等熱門目的地） |

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
| R2 | v1 通用 CSS 選擇器只抓到 2 sections | 執行 DOM 分析腳本，識別 Next.js CSS Modules 實際 hash 類名 |
| R3 | Swiper 輪播含 53 slides（複製節點） | 改用 `.swiper-slide:not(.swiper-slide-duplicate)` + src 二次去重，正確得到 30 個非重複 banner |
| R4 | UnicodeEncodeError（cp950 終端輸出中文） | 非致命，JSON 落盤正確，v2 腳本改用 `sys.stdout.reconfigure(encoding='utf-8')` |

## Next.js CSS Modules 選擇器對應

| Section | CSS 選擇器 | 備註 |
|---------|-----------|------|
| hot_packages | `[class*=WidgetTrendingFareProductCard_card]` | 6 張含價格商品卡 |
| hot_products | `[class*=HotProducts_list__]` | 快速連結 li 元素 |
| article_sections | `[class*=ArticleLayout_article_layout]` | 2 個 tab 式區塊 |
| hero_banner | `.swiper-slide:not(.swiper-slide-duplicate) img` | Swiper clone 去重 |

## 已知技術債

- `search_bar` 只擷取到 3 個搜尋欄位（頁面實際有更多下拉選擇器）；若需完整，可在 `crawl_packages.py` 擴展 selector。
- `hero_banner` 的 `text` 部分為空（banner 圖片無 alt text，頁面以視覺圖為主）；`link_url` 已正確擷取。
- `航空專區`、`主題活動` 的部分項目 `text=null`（section 內商品以圖為主，無文字標題）；`link_url` 與 `image_url` 均完整。
- `freetour_banner_12.jpg` 和 `freetour_banner_13.jpg` 為 v1 run 遺留檔案（v2 同序號圖片格式為 PNG），不影響 JSON 參照正確性。

## 圖片下載統計

- JSON 參照檔案：46 張（全部對應實體存在）
- 目錄總計：48 張（含 v1 遺留 2 張 jpg）
- 格式：30 × jpg（banner）+ 12 × png + 6 × jpg（product）
- 命名符合 `freetour_{type}_{nn}.{ext}` 規範
- 全部 ≤ 2 MB 限制（最大 759 KB）
