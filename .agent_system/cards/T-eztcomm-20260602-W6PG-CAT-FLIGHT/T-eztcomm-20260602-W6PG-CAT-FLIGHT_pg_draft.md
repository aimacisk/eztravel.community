---
task_id: T-eztcomm-20260602-W6PG-CAT-FLIGHT
title: "[W6 PG] 機票分類頁視覺重建"
author: pg
created_at: 2026-06-02T06:08:14+00:00
wiki_target: 06_wiki/04_dev_guide.md
sections:
  - module_structure
  - environment_config
  - build_and_test
  - known_issues
  - tech_debt
---

# 機票分類頁視覺重建 — Dev Guide 草稿

## 1. 模組結構

### 新增 / 修改的檔案

```
04_src/eztravel.Community/eztravel.Community.Web/
├── Controllers/
│   └── CategoryController.cs          ← [修改] 新增 Flight() action
└── Views/
    └── Category/
        └── Flight.cshtml              ← [新建] 機票分類頁 Razor view
```

### 路由設計

- `GET /category/flight` → `CategoryController.Flight()` → `Views/Category/Flight.cshtml`
- `GET /category/{slug}` → `CategoryController.Show()` → `Views/Category/Show.cshtml`

ASP.NET Core attribute routing 中，literal route `[HttpGet("flight")]` 優先於參數化 `[HttpGet("{slug}")]`，因此不需修改既有 Show() 邏輯。

### 資料流

```
/category/flight
  → CategoryController.Flight()
  → IPageDataLoader.Load("flight")
  → PageDataLoader.Load("flight")          // 讀 wwwroot/data/機票/機票.json
  → PageDataViewModel (6 sections)
  → Flight.cshtml (Razor)
```

### Section 對應表

| JSON section.type | Razor 變數 | UI 元件 |
|---|---|---|
| `search_bar` | `searchSec` | SearchBar widget（4 tab + 3 radio + 5 欄 grid） |
| `hero_banner` | `heroSec` | 4-col HeroBanner grid（取前 4 項） |
| `product_list` | `routesSec` | 3-col HotRoutes grid |
| `other` | `airlineSec` | Airline Pills 橫排 |
| `promo_section` | `promoSec` | Promo + Visa 3-card grid（與 quick_links 合併） |
| `quick_links` | `visaSec` | 同上合併（`.Concat().Take(3)`） |

---

## 2. 環境配置

### Runtime

- .NET 8 ASP.NET Core MVC
- 無新增 NuGet 依賴

### CSS Foundation 前置條件

`wwwroot/css/site.css` 必須存在且含 R1 CSS variables（T-eztcomm-20260602-R1 已完成）：

```css
:root {
  --color-brand-primary:  #11D073;
  --color-bg-primary:     #F1F7F8;
  --font-family-primary: 'Noto Sans TC', 'Inter', sans-serif;
  /* ... 40+ variables ... */
}
body { background-color: var(--color-bg-primary); }
.navbar { background-color: var(--color-brand-primary) !important; }
```

### 靜態資源路徑

機票 JSON 資料：`wwwroot/data/機票/機票.json`  
機票圖片：`wwwroot/data/機票/images/`（`<img src="/data/機票/@item.ImageUrl">`）

---

## 3. 編譯與測試

### Build

```bash
dotnet build 04_src/eztravel.Community/eztravel.Community.sln
```

### Run（開發）

```bash
dotnet run --project 04_src/eztravel.Community/eztravel.Community.Web --urls http://localhost:5150
```

### 視覺驗證（Playwright）

```js
// AC-W6-01: body 背景
await page.goto('http://localhost:5150/Category/Flight');
const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
// 預期: 包含 '241, 247, 248'（#F1F7F8）

// AC-W6-02: navbar 綠色
const screenshot = await page.screenshot();
// 目視確認 navbar 含綠色 #11D073

// AC-W6-03: 無硬編碼顏色
// grep -nE "style=|#[0-9A-Fa-f]{3,6}|rgba?\(" Views/Category/Flight.cshtml
// 預期: 無輸出（CLEAN）

// AC-W6-04: Figma 對齊
// 目視比對 Figma nodeId 180:2（file key: 6XmYJOpiSXab2gtGlmWtks）相似度 ≥ 70%
```

### 靜態 grep 驗證（已通過）

```
grep -n "style=" Flight.cshtml       → NO MATCH ✅
grep -nE "#[0-9A-Fa-f]{3,6}" Flight.cshtml → NO MATCH ✅
grep -n "rgba\|rgb(" Flight.cshtml   → NO MATCH ✅
grep -n "#11D073" site.css           → L9: --color-brand-primary ✅
grep -n "var(--color-brand-primary)" site.css → 6 hits including .navbar ✅
```

---

## 4. 常見錯誤排除

### `/Category/Flight` 回 404

- 確認 `CategoryController.cs` 含 `[HttpGet("flight")] public IActionResult Flight()` 方法
- 確認 `Views/Category/Flight.cshtml` 存在
- 確認 `IPageDataLoader.Load("flight")` 能正確解析到 `wwwroot/data/機票/機票.json`

### 頁面顯示但 body 背景是白色

- 確認 `_Layout.cshtml` 已載入 `site.css`（在 Bootstrap CDN 之後）
- 確認 `site.css` 的 `body` rule 有 `background-color: var(--color-bg-primary)` 且 `:root` 定義了 `--color-bg-primary: #F1F7F8`

### Navbar 顯示 Bootstrap 預設藍

- 確認 `_Layout.cshtml` 中 Bootstrap CDN link 在 `<link rel="stylesheet" href="~/css/site.css" />` 之前
- 確認 `site.css` 有 `.navbar { background-color: var(--color-brand-primary) !important; }`

### 機票圖片 404

- 確認圖片實際存在於 `wwwroot/data/機票/images/`
- JSON 中 `image_url` 欄位值為相對路徑（例 `images/flight_banner_01.jpg`）；Razor 自動補前綴為 `/data/機票/images/flight_banner_01.jpg`

---

## 5. 已知技術債

| 項目 | 說明 | 建議處理時機 |
|---|---|---|
| 搜尋欄位為靜態 HTML | 出發地/目的地/日期/人數均為 placeholder，無實際搜尋功能 | Wave 7 或搜尋功能卡 |
| 機票 JSON 資料為靜態 | `機票.json` 硬編碼，無 API 動態拉取 | 後端整合卡 |
| HeroBanner 僅取前 4 項 | `.Take(4)` 硬編碼，超過 4 張無 carousel | 需求確認後處理 |
| Promo+Visa 合併邏輯 | `.Concat().Take(3)` 僅取 3 項，若 section 有更多資料會截斷 | 確認 PM 規格後處理 |
| AC-W6-04 Playwright 驗證待完成 | browser locked（sandbox），需 admin build+run 後跑 Playwright 截圖比對 | 系統維護卡 verify_after_restart |
