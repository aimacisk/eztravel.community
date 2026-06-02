---
task_id: T-eztcomm-20260602-W6PG-COMMUNITY
title: "[W6 PG] Community ReviewController + AJAX 視覺重建"
wiki_target: 06_wiki/04_dev_guide.md
author: pg
sections:
  - 模組結構
  - 環境配置
  - 編譯與測試
  - 常見錯誤排除
  - 已知技術債
---

# Community Module — 開發指南（W6 PG 重建）

## 模組結構

本次重建聚焦 `eztravel.Community.Web` 專案的 Community 評論模組，路徑如下：

```
04_src/eztravel.Community/eztravel.Community.Web/
├── Controllers/
│   └── ReviewController.cs          ← [新增] MVC non-API，/Review/Submit Playwright 測試頁
├── Views/
│   ├── Review/
│   │   └── Submit.cshtml            ← [新增] Playwright 視覺驗證用頁面
│   └── Shared/
│       ├── _Layout.cshtml           ← [修改] 移除 navbar-light bg-white，改 navbar-dark
│       ├── _CommunityModule.cshtml  ← [修改] 改為薄包裝，delegate 到 _ReviewSection
│       ├── _ReviewSection.cshtml    ← [新增] BEM 結構主 partial，無硬編碼顏色
│       ├── _FilterBar.cshtml        ← [修改] 加 id="filter-bar" 供 JS 定位
│       └── _ReviewComposer.cshtml   ← [修改] 加 #review-feedback div
├── wwwroot/
│   ├── css/site.css                 ← [修改] 新增 Community Module CSS 區塊（CSS variables only）
│   └── js/site.js                   ← [重寫] 完整 AJAX Community JS 模組
```

### 職責分層

| 檔案 | 職責 |
|------|------|
| `ReviewController.cs` | 提供 `/Review/Submit` MVC 路由，注入假 ViewModel 給 Playwright 測試 |
| `_ReviewSection.cshtml` | 評論區主結構：評分分佈 + 篩選列 + 評論清單 + 撰寫表單 |
| `_CommunityModule.cshtml` | 薄包裝（section.community-module + data-product-id），delegate 到 _ReviewSection |
| `site.css` Community 區塊 | 全部 BEM CSS class，100% 使用 CSS variables，零硬編碼色值 |
| `site.js` | 評論 AJAX 加載、星級選取、篩選列、分頁、表單送出、Helpful 按鈕 |

## 環境配置

### 執行環境

- .NET 9 SDK（`dotnet run` 在 `04_src/eztravel.Community/eztravel.Community.Web/`）
- 預設埠：`http://localhost:5150`
- Playwright MCP：必須 `browser_close` 後再 `browser_navigate`，或確保 MCP server 獨佔

### CSS Variables 依賴（R1 已建立）

community CSS 完全依賴 `site.css` `:root` 定義的 CSS variables。若移除 R1 的 `:root` 區塊，
所有 community 樣式將失效（顏色變 `initial`）。關鍵 variables：

```css
--color-brand-primary: #11D073;    /* navbar 綠、active chip 綠 */
--color-surface-cool: #F1F7F8;     /* body 背景淺灰 */
--color-status-warning: #FFB800;   /* 星星黃色 */
--color-accent-orange: #FF8B00;    /* 強調橘 */
--font-family-chinese: 'Noto Sans TC', ...;
```

### 新增依賴

無新 NuGet 套件。所有 JS 為 vanilla（無 npm 依賴）。

## 編譯與測試

### 靜態驗證（已通過）

```bash
# 防線 7：CSS 含品牌綠定義
grep '#11D073' wwwroot/css/site.css
# → 4 行命中 ✅

# CSS 使用 CSS variables（不硬編碼）
grep 'var(--color-brand-primary)' wwwroot/css/site.css
# → 33 行命中 ✅

# AC-W6-03：ReviewSection 無硬編碼顏色
grep 'style=' Views/Shared/_ReviewSection.cshtml
# → 0 行（PASS） ✅

grep '#11D073' Views/Shared/_ReviewSection.cshtml
# → 0 行（PASS） ✅
```

### Playwright 視覺驗證（需 browser 可用 + app 啟動）

```bash
# 啟動應用程式
cd 04_src/eztravel.Community/eztravel.Community.Web
dotnet run

# Playwright 驗證指令（需 admin 執行）
# AC-W6-01
browser_navigate url=http://localhost:5150/Review/Submit
browser_evaluate function="() => getComputedStyle(document.body).backgroundColor"
# 預期：包含 '241, 247, 248'

# AC-W6-02
browser_take_screenshot filename=review-submit-navbar.png
# 目測 navbar 含綠色 #11D073

# AC-W6-04：與 Figma nodeId 87:2 比對
# fileKey: 6XmYJOpiSXab2gtGlmWtks，nodeId: 87:2（600×1570 Community Full Module）
```

## 常見錯誤排除

### Bootstrap `!important` 覆蓋 site.css

**症狀**：`navbar-light bg-white` 類讓 Bootstrap 的 `bg-white: !important` 覆蓋 site.css 的 `.navbar { background-color: var(--color-brand-primary) !important }`。

**解決**：在 `_Layout.cshtml` 的 `<nav>` 移除 `navbar-light bg-white`，改為 `navbar-dark`（讓文字自動變白）。已修正。

### Razor 語法錯誤（Handlebars 混用）

**症狀**：Razor partial 使用 `{{!-- --}}` 而非 `@* *@`，導致編譯錯誤。

**解決**：所有 `.cshtml` 注釋一律用 `@* *@`，Razor expression 用 `@Model.Property`。

### `decimal` vs `double` 型別不符

**症狀**：`AverageRating = 4.6m` 編譯失敗，因 `ProductDetailViewModel.AverageRating` 為 `double`。

**解決**：使用 `AverageRating = 4.6`（無後綴）。

### Playwright browser 已在使用

**症狀**：所有 Playwright MCP call 回傳 `Browser is already in use for ...mcp-chrome-4e170cb`。

**解決**：關閉其他佔用 Playwright MCP 的 Claude Code session，或重啟 Playwright MCP server。

### `#filter-bar` JS 定位失敗

**症狀**：`initFilterBar()` 中 `qs('#filter-bar')` 回傳 null，篩選列無互動。

**解決**：在 `_FilterBar.cshtml` 的 `<nav>` 加 `id="filter-bar"`。已修正。

## 已知技術債

| 項目 | 說明 | 建議時機 |
|------|------|---------|
| Playwright 視覺 AC 仍待驗 | browser locked，AC-W6-01/02/04 未完成機器驗證 | admin 重啟 Playwright MCP 後，Wave 7 GATE-PG 覆驗前必完成 |
| `figma_deliverables.json` 手建 | T-eztcomm-20260602-RA-W3U1 上游 UIUX 卡未完交付，PG 從卡 JSON 手建 | 補上游 UIUX 卡的真實 Figma 標記 |
| Review list 空狀態 UX | 資料庫無評論時顯示「尚無評論」純文字，未對齊 Figma empty state 設計 | Wave 7 QA 後視需求補 |
| 星星半星 CSS | `.star--half` 目前僅靠文字 `★`，無真正半星遮罩效果 | 美觀提升時處理 |
| 評論表單驗證回饋 a11y | `role="alert"` 已加，但未做 focus management | 無障礙需求確認後補 |
