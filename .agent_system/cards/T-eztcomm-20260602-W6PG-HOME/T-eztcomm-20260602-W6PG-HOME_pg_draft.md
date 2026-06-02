---
task_id: T-eztcomm-20260602-W6PG-HOME
wave: Wave6-PG
wiki_target: 06_wiki/04_dev_guide.md
section: Home 頁視覺重建
---

# Home 頁視覺重建 — 開發指南草稿

## 模組結構

```
04_src/eztravel.Community/eztravel.Community.Web/
├── Views/
│   ├── Home/
│   │   └── Index.cshtml           ← 修改：新增 hero_banner/promo_section/quick_links routing
│   └── Shared/
│       ├── _Section_Banner.cshtml       ← 不動
│       ├── _Section_CategoryNav.cshtml  ← 不動（同時處理 quick_links）
│       ├── _Section_FeaturedGrid.cshtml ← 修改：新增 <span class="btn-cta">立即預訂</span>
│       ├── _Section_PromoCard.cshtml    ← 修改：新增 badge 渲染
│       └── _Section_Generic.cshtml     ← 不動（fallback）
└── wwwroot/css/
    └── site.css  ← 修改：新增 page-section / product-card / category-nav 等組件 CSS
```

## Section 類型對照表

| homepage.json type | Partial View | 說明 |
|--------------------|-------------|------|
| `hero_banner` | `_Section_Banner` | 主 Banner，套用 `.page-section--hero_banner` 品牌綠漸層背景 |
| `category_nav` | `_Section_CategoryNav` | 分類導航，圖示 + 文字 |
| `quick_links` | `_Section_CategoryNav` | 快速連結，pill 樣式（`.page-section--quick_links` CSS 變體） |
| `featured_items` / `product_list` | `_Section_FeaturedGrid` | 商品卡 grid，含 badge + 價格 + CTA |
| `promo_section` / `promo_card` | `_Section_PromoCard` | 促銷卡，可顯示 badge |
| `search_bar` | `_Section_SearchForm` | 搜尋表單 |
| `footer` | `_Section_Footer` | 頁尾 |
| （其他） | `_Section_Generic` | fallback |

## CSS 設計原則

### 1. 全用 CSS Custom Properties（無硬編碼）

所有顏色、間距、字型大小均引用 `:root` 中的 CSS variables：

```css
.product-card__price {
  color: var(--color-accent-coral);
  font-weight: var(--font-weight-bold);
}
.btn-cta {
  background-color: var(--color-brand-primary);
}
```

### 2. Bootstrap 覆寫策略

Bootstrap class 保留在 HTML（供 grid/responsive 使用），以 `!important` 覆寫視覺 token：

```css
.navbar {
  background-color: var(--color-brand-primary) !important;
}
```

### 3. Page Section CSS 鉤子

每個 section wrapper 帶 `class="page-section page-section--{type}"`：

```css
.page-section--hero_banner {
  background: linear-gradient(135deg,
    var(--color-brand-primary) 0%, var(--color-brand-dark) 100%);
}
.page-section--quick_links .category-nav__item {
  border-radius: var(--radius-full);
}
```

### 4. CTA 按鈕用 span 非 a

外層已是 `<a class="product-card">`，HTML 規範禁止 `<a>` 嵌套 `<a>`。
改用 `<span class="btn-cta">` 搭配 CSS 模擬按鈕外觀。

## 環境配置

- **Runtime**：.NET 8（ASP.NET Core MVC）
- **CSS**：Bootstrap 5.3 + site.css（R1 CSS variables layer）
- **字型**：Google Fonts（Inter + Noto Sans TC），在 `_Layout.cshtml` 引入
- **資料**：`wwwroot/data/homepage/homepage.json`（→ PageDataViewModel）

### 啟動指令

```bash
cd 04_src/eztravel.Community
dotnet run --project eztravel.Community.Web --urls http://localhost:5150
```

## AC 驗收狀態

| AC | 描述 | 靜態驗證 | 動態驗證 |
|----|------|---------|---------|
| AC-W6-01 | body.backgroundColor = #F1F7F8 | ✅ site.css 確認 | ⏳ Playwright evaluate |
| AC-W6-02 | navbar 含 #11D073 | ✅ site.css !important | ⏳ Playwright 截圖 |
| AC-W6-03 | Index.cshtml 無硬編碼色值 | ✅ grep 確認 | — |
| AC-W6-04 | Playwright 截圖 vs Figma 153:2 ≥ 70% | — | ⏳ 需 admin build+run |

## 已知技術債

| 項目 | 說明 | 優先級 |
|------|------|--------|
| Banner 無輪播 | 多 item 時靜態顯示，不輪播 | 中 |
| Category 圖示缺資料 | homepage.json 無 ImageUrl 時無法顯示 Figma 設計的類別圖示 | 中 |
| 首頁缺 search_bar | 資料無此 section，需 BA 補 | 低 |
| product-card RWD | minmax(200px,1fr) 在 375px 可能只顯示 1 欄 | 低 |
