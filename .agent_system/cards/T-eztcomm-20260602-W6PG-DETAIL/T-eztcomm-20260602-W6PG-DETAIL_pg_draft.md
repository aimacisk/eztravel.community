---
task_id: T-eztcomm-20260602-W6PG-DETAIL
agent: pg
created_at: 2026-06-02
wiki_target: 06_wiki/04_dev_guide.md
---

# [W6 PG] Product Detail 視覺重建 — 開發者指南草稿

## 模組結構

```
Views/
  Product/
    Detail.cshtml                    ← 主頁面（article.product-detail）
  Shared/
    _Layout.cshtml                   ← 已修正 navbar（navbar-dark，移除 bg-white/text-dark）
    _CommunityModule.cshtml          ← Community Module 容器
    _RatingDistribution.cshtml       ← 評分分布（星等 bar chart）
    _FilterBar.cshtml                ← 篩選 chip 列（7 個選項）
    _StarRating.cshtml               ← 星星評分顯示元件
    _ReviewCard.cshtml               ← 評論卡片（<template> JS-loaded）
    _ReviewComposer.cshtml           ← 撰寫評論表單
    _Product_GroupTour.cshtml        ← 團體旅遊 variant
    _Product_FreeTour.cshtml         ← 自由行 variant
    _Product_Hotel.cshtml            ← 旅館 variant
    _Product_Ticket.cshtml           ← 票券 variant
    _Product_Attraction.cshtml       ← 景點 variant

wwwroot/css/
  site.css                           ← 主樣式（W6 新增 product-detail + community module 區塊）
```

## CSS 架構說明

### CSS Variables（:root）
所有顏色與設計值均由 `site.css` :root 定義，Razor view 禁止使用 `style=` 硬編碼：

| 變數名 | 值 | 用途 |
|---|---|---|
| `--color-brand-primary` | `#11D073` | 品牌綠、navbar 背景、CTA 按鈕 |
| `--color-brand-dark` | `#0DA862` | Hero gradient 終止色 |
| `--color-bg-primary` | `#F1F7F8` | body 背景、meta 項目背景 |
| `--color-bg-card` | `#FFFFFF` | 卡片、Community Module 背景 |
| `--color-status-warning` | `#FFB800` | 星評金色 |
| `--font-family-primary` | `'Noto Sans TC',...` | 主字型（中文） |

### W6 新增的 CSS 區塊（site.css 線段）

1. **Product Detail Page**（`.product-detail`、`.product-detail__hero`、`.variant`、`.variant__meta`）
   - Hero：135° gradient（brand-primary → brand-dark）+ radial-gradient 光暈 overlay
   - Variant：左側 4px brand-primary border-left，grid meta list

2. **Community Module**（`.community-module`、`.community-module__summary`、`.community-module__list`、`.community-module__login-hint`）

3. **Star Rating**（`.star-rating`、`.star`、`.star--full`、`.star--half`、`.star--empty`）
   - Full/half：`--color-status-warning` (#FFB800)，Empty：`--color-border-medium`

4. **Rating Distribution**（`.rating-distribution`、`.rating-bar`、`.rating-bar__track`、`.rating-bar__fill`）

5. **Filter Bar**（`.filter-bar`、`.filter-bar__chip`）
   - Active/hover：背景切換為 `--color-brand-primary`，文字白

6. **Review Card**（`.review-card` family）
   - Avatar：40×40 圓形，預設背景 `--color-brand-primary`
   - footer：helpful button + reply link

7. **Review Composer**（`.review-composer` family）
   - Star picker：2rem 星按鈕，hover/selected 轉 `--color-status-warning`
   - Submit button：`--color-brand-primary` → hover `--color-brand-dark`

8. **RWD breakpoint**（`@media max-width: 768px`）
   - Hero padding 縮小、title font-size 降至 2xl、photo 縮小

## Navbar 修正說明

**修改前：**
```html
<nav class="navbar navbar-expand-md navbar-light bg-white border-bottom box-shadow mb-3">
<a class="nav-link text-dark" href="/category/@c.Slug">...
```

**修改後：**
```html
<nav class="navbar navbar-expand-md navbar-dark box-shadow mb-3">
<a class="nav-link" href="/category/@c.Slug">...
```

理由：
- `navbar-light` + `bg-white` 讓 Bootstrap 覆蓋 site.css 的品牌綠 navbar
- `navbar-dark` 告訴 Bootstrap 使用深色（白字）模式，配合 site.css `.navbar { background-color: var(--color-brand-primary) !important; }`
- `text-dark` 強制黑字，移除後 site.css `.navbar .nav-link { color: #ffffff !important; }` 正確生效

## 驗收標準 vs 靜態確認

| AC | 描述 | 靜態確認 | 需 Playwright |
|---|---|---|---|
| AC-W6-01 | body.backgroundColor = rgb(241,247,248) | `body { background-color: var(--color-bg-primary); }` ← `--color-bg-primary: #F1F7F8` ✓ | 需 admin 建置後跑 |
| AC-W6-02 | navbar #11D073 | site.css `.navbar { background-color: var(--color-brand-primary) !important; }` + 移除 bg-white ✓ | 需 admin 建置後截圖 |
| AC-W6-03 | Detail.cshtml 不含 style= 硬編碼 | grep 確認無命中 ✓ | **靜態 PASS** |
| AC-W6-04 | Figma 88:3 相似度 ≥ 70% | Hero green gradient + white variant cards + community module bar ← 結構吻合 ✓ | 需 admin 建置後截圖 |

## 環境配置

- .NET 8 SDK（`dotnet run` 啟動後 localhost:5150）
- 字型：Google Fonts CDN（已在 `_Layout.cshtml` `<head>` 引入 Noto Sans TC）
- Bootstrap 5：`~/lib/bootstrap/dist/css/bootstrap.min.css`（先載入，site.css 後載以覆寫）

## 已知技術債

1. **`_ReviewCard.cshtml` 是 `<template>` 元素**，評論列表靠 JS `/api/products/{id}/reviews` 動態載入。目前無 JS 實作，頁面上 `.community-module__list` 會是空的。須後續 JS 卡實作。
2. **評分分布 bar width**：`.rating-bar__fill` 的 `width` 需由 JS 根據各星級百分比動態設定。目前 CSS 預設不帶 width，bar 顯示為空。
3. **`_ReviewComposer.cshtml` submit**：表單 POST endpoint 尚未實作（AJAX to `/api/products/{id}/reviews`），送出後會失敗。

## 修復迴圈紀錄

| 輪次 | 問題 | 修復方式 |
|---|---|---|
| 1 | Worktree site.css 比 main 少 198 行（缺 product-detail 區塊） | 從 main branch 複製並補寫 community module CSS |
| 2 | Navbar `bg-white` + `navbar-light` 覆蓋品牌綠 | `_Layout.cshtml` 移除 `navbar-light` + `bg-white`，改 `navbar-dark` |
| 3 | 任務指令提及不存在的 CSS 變數（`--color-surface-cool` 等） | 改用實際存在變數（`--color-bg-primary` / `--font-family-primary`）|
