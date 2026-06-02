---
task_id: T-eztcomm-20260602-W6PG-CAT-TICKET
title: "[W6 PG] 票券分類頁視覺重建"
wiki_target: 06_wiki/04_dev_guide.md
sections: [模組結構, 環境配置, 編譯與測試, 常見錯誤排除, 已知技術債]
created_at: "2026-06-02T09:15:00+00:00"
---

# 票券分類頁視覺重建 — 開發指南

## 1. 模組結構

### 新增 / 修改的檔案

| 檔案 | 變更類型 | 說明 |
|------|---------|------|
| `Views/Category/Ticket.cshtml` | **新建（全量重建）** | W4-REBUILD；原始版本只有文字清單，本次完整套用 CSS variables + Figma layout |
| `Controllers/CategoryController.cs` | **修改** | 新增 `Ticket()` action，明確 `[Route("Category/Ticket")]` |

### 目錄層級

```
eztravel.Community.Web/
├── Controllers/
│   └── CategoryController.cs          ← 新增 Ticket() action
├── Views/
│   └── Category/
│       └── Ticket.cshtml              ← W4-REBUILD 全量重寫
└── wwwroot/css/
    └── site.css                       ← 唯讀；:root CSS variables 基礎
```

### Ticket.cshtml 架構

```
Ticket.cshtml（435 行）
├── @using / @model 宣告
├── @{ ViewData["Title"]; const DataFolder = "票券"; }
├── <style> block 1  — 非 @media CSS class 定義（零 hardcoded hex）
├── <style> block 2  — @@media responsive breakpoint
└── @foreach(sec) / switch(sec.Type)
    ├── "search_bar"      → .ticket-search-section（品牌綠背景搜尋列）
    ├── "hero_banner"     → .ticket-banner-tiles（8-col grid，複用 .promo-tile）
    ├── "category_nav"    → .category-nav（17 個圖示 + 文字 chip）
    ├── "featured_items"  → .ticket-product-grid（5-col，玩樂票券）
    ├── "promo_section"   → .ticket-city-grid（4-col，城市熱銷）
    ├── "theme_section"   → .ticket-theme-grid（5-col，優惠專區）
    ├── "footer_links"    → _Section_Footer partial
    └── default           → _Section_Generic partial
```

### Route 設計（CategoryController.cs）

```csharp
// class-level attribute: [Route("category")]
// ↓ 覆蓋 conventional routing，各 action 需明確宣告 route

[Route("Category/Ticket")]   // explicit，對齊 GroupTour 模式
[HttpGet]
public IActionResult Ticket()
{
    var model = _loader.Load("ticket");
    if (model is null) return NotFound();
    return View("Ticket", model);
}
```

**為什麼需要 explicit route：** class-level `[Route("category")]` 覆蓋 conventional routing，若不加 `[Route("Category/Ticket")]` 則 Ticket action 在 attribute routing 下無法以 `/Category/Ticket` 訪問。

---

## 2. 環境配置

### Runtime 要求

| 項目 | 版本 |
|------|------|
| .NET | 8.0 (SDK) |
| ASP.NET Core MVC | 8.0 |
| 瀏覽器驗證 | Playwright（MCP mcp__playwright__*） |

### 資料來源

- 票券頁 JSON：`data/票券/票券.json`（slug = `"ticket"`）
- 圖片根目錄：`data/票券/images/`
- URL 解析規則：Razor 內部使用 `Url.Content($"~/data/票券/{item.ImageUrl}")`

### CSS 基礎

`wwwroot/css/site.css` 的 `:root` 必須包含以下 variables（R1 卡已完成）：

```css
--color-brand-primary: #11D073;
--color-bg-primary:    #F1F7F8;
--color-brand-dark:    #0DA862;
--color-brand-light:   #6FEBA9;
--color-bg-card:       #FFFFFF;
--font-family-primary: 'Noto Sans TC', 'Inter', sans-serif;
--dest-tile-1 ~ --dest-tile-10   /* hotel 城市磚 fallback 色，票券城市熱銷複用 */
```

---

## 3. 編譯與測試

### 啟動指令

```bash
cd projects/eztravel.community/04_src/eztravel.Community
dotnet run --project eztravel.Community.Web -- --urls "http://localhost:5150"
```

### Playwright 驗收指令

```javascript
// AC-W6-01：body bg = #F1F7F8
getComputedStyle(document.body).backgroundColor
// 預期回傳：rgb(241, 247, 248)

// AC-W6-02：navbar 品牌綠
getComputedStyle(document.querySelector('.navbar')).backgroundColor
// 預期含：rgb(17, 208, 115) 或 #11D073

// AC-W6-03：靜態 grep（無需 server）
// grep '#[0-9A-Fa-f]' Views/Category/Ticket.cshtml  →  零輸出（已 PASS）
// grep 'style='       Views/Category/Ticket.cshtml  →  零輸出（已 PASS）

// AC-W6-04：對比 Figma nodeId 187:2 截圖目測相似度 ≥ 70%
```

### Worktree Git 流程（待 admin 執行）

```bash
cd .worktrees/T-eztcomm-20260602-W6PG-CAT-TICKET

# Rebase before merge
git fetch ../.. main
git rebase main          # fast-forward 通常不需解衝突

# Commit
git add -A
git commit -m "T-eztcomm-20260602-W6PG-CAT-TICKET: feat(views): rebuild ticket category page with CSS variables"

# dispatch 接手 merge → fast-forward 進 main
```

---

## 4. 常見錯誤排除

### 問題 1：`@media` 在 Razor `.cshtml` 內語法錯誤

**現象：** `@media` 被 Razor 解析為 C# 表達式，拋 `CS1525` 或 `CS0246`。

**解法：** 在 `.cshtml` 的 `<style>` 區塊內改寫為 `@@media`：

```css
/* ❌ 錯誤 */
@media (max-width: 575px) { ... }

/* ✅ 正確 */
@@media (max-width: 575px) { ... }
```

本次採用「分兩個 `<style>` block」策略，第一個 block 僅有非 at-rules，第二個 block 全部 `@@media`，降低混淆風險。

### 問題 2：圖片顯示 404（shared partial URL 解析問題）

**現象：** 使用 `_Section_Banner` 等 shared partial 時，圖片路徑依賴 `RouteData.Values["slug"]`；但 `/Category/Ticket` 是 explicit attribute route，`slug` 為 null，導致路徑解析為 `~/data//images/xxx.jpg`（404）。

**解法：** 所有含圖片的 section 均在 Ticket.cshtml 內 inline 渲染，使用固定 `const string DataFolder = "票券"` + `Url.Content($"~/data/{DataFolder}/{item.ImageUrl}")` 明確解析。

### 問題 3：`SectionItemViewModel.SubText` 屬性不存在

**現象：** `item.SubText` 導致 CS0117 編譯錯誤。

**原因：** `PageDataViewModel.cs` 中 `SectionItemViewModel` 沒有 `SubText` 屬性，價格欄位正確名稱為 `item.Price`。

**解法：** 一律使用 `item.Price` 取得價格資訊。

### 問題 4：CSS variable 名稱不匹配導致樣式不生效

**現象：** 套用 `--font-family-chinese`、`--shadow-sm`、`--color-accent-orange` 後樣式消失（silent fail）。

**正確名稱對照：**

| 誤用名稱 | 實際 site.css 名稱 |
|---------|------------------|
| `--font-family-chinese` | `--font-family-primary` |
| `--shadow-sm` | `--shadow-card` |
| `--shadow-md` | `--shadow-floating` |
| `--color-accent-orange` | 不存在；改用 `--color-brand-dark` 或 `--color-accent-coral` |

---

## 5. 已知技術債

| 項目 | 說明 | 建議處理時機 |
|------|------|------------|
| `figma_deliverables.json` 未建立 | RA-W2U7 卡未完工，本卡直接讀卡 JSON 取得 fileKey；未來 UIUX 補完 RA-W2U7 後可補建此檔 | Wave 7 或 UIUX 補規格時 |
| Ticket.cshtml 無 Model null guard | 若 `_loader.Load("ticket")` 回傳 null，controller 已回 404，但 view 本身沒有防禦性 null check on `Model.Sections` | 優先度低，由 QA 測試覆蓋 |
| `.category-nav` CSS 定義在 shared scope | `category-nav` / `category-nav__item` CSS 定義在 `site.css` 中，若其他頁面 nav 有差異可能干擾 | 遇到衝突時加 scope prefix |
| 城市熱銷 fallback 色複用 hotel `--dest-tile-N` | 語意上這是 hotel 頁色盤，票券城市磚借用；若未來兩者視覺分離需各自定義 | 視覺設計迭代時 |
