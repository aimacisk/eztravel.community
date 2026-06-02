---
task_id: T-eztcomm-20260602-W6PG-CAT-HOTEL
title: "[W6 PG] 旅館分類頁視覺重建"
agent: pg
wiki_target: 06_wiki/04_dev_guide.md
sections: [模組結構, 環境配置, 元件 CSS 規格, 常見錯誤排除, 已知技術債]
---

# [W6 PG] 旅館分類頁視覺重建 — 開發指南草稿

## 模組結構

### 新增 / 修改檔案

```
04_src/eztravel.Community/eztravel.Community.Web/
├── Controllers/
│   └── CategoryController.cs          ← 新增 [HttpGet("hotel")] Hotel() action
├── Views/
│   └── Category/
│       └── Hotel.cshtml               ← 全新（7 種 section type 完整處理）
│   └── Shared/
│       └── _Section_DestinationGrid.cshtml  ← 全新（colored tile grid）
└── wwwroot/css/
    └── site.css                       ← 追加 Hotel 頁元件 CSS（~80 行）
```

### 頁面 Section Type 對應表

| section.Type | 渲染方式 | 關鍵元件 |
|---|---|---|
| `search_bar` | 內嵌（Hotel.cshtml）| `.hotel-searchbar` + tabs + input row |
| `promo_section` | 內嵌（Hotel.cshtml）| `.promo-tiles` + `.promo-tile`（bg-img overlay）|
| `theme_section` | 內嵌（Hotel.cshtml）| `.theme-chips` + `.theme-chip` pill |
| `featured_items` / `product_list` | `_Section_FeaturedGrid` partial | `.featured-grid` + `.product-card` |
| `destination_grid` | `_Section_DestinationGrid` partial | `.destination-grid` + `.destination-tile` |
| `footer_links` | `_Section_Footer` partial | `.site-footer-content` |
| 其他 | `_Section_Generic` partial | `.generic-section` |

### 資料流

```
GET /category/hotel
→ CategoryController.Hotel()
→ _loader.Load("hotel")
→ PageDataLoader 讀 wwwroot/data/旅館/旅館.json
→ PageDataViewModel { Sections: [ ... ] }
→ Views/Category/Hotel.cshtml
→ partial views / inline rendering
```

---

## 環境配置

### 執行條件

- .NET 8 SDK
- `wwwroot/data/旅館/旅館.json` — 旅館頁資料（已存在）
- Bootstrap 5 CDN（_Layout.cshtml 已引入）
- `wwwroot/css/site.css` — R1 CSS Foundation + W6PG-HOME + W6PG-CAT-HOTEL 元件 CSS

### 路由

```
GET /category/hotel  →  CategoryController.Hotel()  →  Views/Category/Hotel.cshtml
```

### CSS 載入順序（重要）

`_Layout.cshtml` 引用順序：
1. Bootstrap 5 CDN（base reset + grid + utilities）
2. `~/css/site.css`（CSS variables 覆寫 + 所有自訂元件）

**Bootstrap 之後**才載入 site.css，才能正確覆寫 Bootstrap 預設值（如 `.navbar` 背景色）。

---

## 元件 CSS 規格

### CSS Custom Properties（:root）

本卡新增 `--dest-tile-1` 至 `--dest-tile-10` 共 10 個目的地磁磚顏色 token：

| Token | 顏色 | 語意 |
|---|---|---|
| `--dest-tile-1` | `#FF8B00` | 暖橙（accent） |
| `--dest-tile-2` | `#11D073` | 品牌綠 |
| `--dest-tile-3` | `#26C281` | 青綠 |
| `--dest-tile-4` | `#1A8C82` | 深青 |
| `--dest-tile-5` | `#1A3C5A` | 海軍藍 |
| `--dest-tile-6` | `#C0392B` | 深紅 |
| `--dest-tile-7` | `#8E44AD` | 紫色 |
| `--dest-tile-8` | `#2980B9` | 藍綠 |
| `--dest-tile-9` | `#27AE60` | 森林綠 |
| `--dest-tile-10` | `#1565C0` | 海洋藍 |

循環方式：`.destination-tile:nth-child(10n+N)` selectors，無需 JS 或 inline style。

### 主要元件

#### `.hotel-searchbar`
- 搜尋列容器，白底卡片（`--color-bg-card`）+ 陰影
- `.hotel-searchbar__tabs`：tab button 列，active tab 底線用品牌綠
- `.hotel-searchbar__input`：搜尋文字輸入，focus 邊框用品牌綠
- `.hotel-searchbar__btn`：搜尋按鈕，品牌綠背景（`--color-brand-primary`）

#### `.promo-tiles` / `.promo-tile`
- 5 欄 grid（RWD：≤991px 3欄，≤575px 2欄）
- `aspect-ratio: 4/3` 固定比例
- `<img class="promo-tile__bg">` 絕對定位滿版 cover（取代 `background-image: url()` inline style）
- `<span class="promo-tile__overlay">` 黑色漸層遮罩
- `<span class="promo-tile__text">` 白色文字覆蓋

#### `.destination-grid` / `.destination-tile`
- 10 欄 grid（RWD：≤1199px 5欄，≤575px 4欄）
- 每格固定色塊（nth-child 循環 10 色）
- 白色文字，hover opacity 0.85

#### `.theme-chips` / `.theme-chip`
- flex-wrap pill 標籤
- hover 變品牌綠背景 + 白字

---

## 常見錯誤排除

### 1. Hotel.cshtml 找不到 View 模板

**症狀**：`GET /category/hotel` 回 500 InvalidOperationException：找不到 view  
**原因**：`CategoryController` 沒有 `[HttpGet("hotel")]` action，或 `Views/Category/Hotel.cshtml` 不存在  
**解法**：確認 `Controllers/CategoryController.cs` 有 `Hotel()` 方法，`Views/Category/Hotel.cshtml` 存在

### 2. promo_section 仍顯示 style= 警告

**症狀**：AC-W6-03 grep 找到 `style=` 屬性  
**原因**：舊版本用 `style="background-image: url(...)"` 渲染背景圖  
**解法**：改用 `<img class="promo-tile__bg">` + CSS `object-fit: cover` + `position: absolute`

### 3. destination-tile 全部顯示同一顏色

**症狀**：所有目的地磁磚顯示 `--dest-tile-1`（橙色）  
**原因**：`:nth-child` CSS 沒有套用，或 site.css 沒有正確載入  
**解法**：檢查瀏覽器 DevTools → Elements → `.destination-tile` 元素 computed style，確認 nth-child selector 命中

### 4. Navbar 仍顯示 Bootstrap 預設深藍

**症狀**：AC-W6-02 失敗，navbar 非品牌綠  
**原因**：Bootstrap CDN 在 site.css 之後載入，導致 Bootstrap 覆寫了自訂顏色  
**解法**：確認 `_Layout.cshtml` 的 `<link>` 順序：Bootstrap CSS 必須在 site.css **之前**；或確認 `.navbar` 規則有 `!important`

---

## 已知技術債

1. **figma_deliverables.json 缺失**：T-eztcomm-20260602-RA-W2U4（UIUX-4 翻頁卡）從未執行，導致本卡無 figma_deliverables.json 可讀。目前改以目測 Figma nodeId 119:2 截圖實作，精確度略低。建議後續補執行 RA-W2U4 並以 deliverables 驗收。

2. **promo_section bg-image 資料未對齊**：`旅館.json` 的 `promo_section` items 有 `imageUrl` 欄位，但目前旅館資料 imageUrl 為空或使用佔位路徑，會顯示灰色背景。待資料補充後自動生效。

3. **hotel-searchbar 功能層未實作**：搜尋按鈕點擊、tab 切換均無 JS 行為，目前純靜態 UI。功能層屬 AT/PG 後續卡片任務。
