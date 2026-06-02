---
task_id: T-eztcomm-20260602-W6PG-CAT-FREETOUR
title: "[W6 PG] 自由行分類頁視覺重建"
author: pg
wiki_target: 06_wiki/04_dev_guide.md
sections:
  - 模組結構
  - 環境配置
  - 編譯與測試
  - 常見錯誤排除
  - 已知技術債
---

## 模組結構

### 異動檔案

| 檔案 | 變更類型 | 說明 |
|------|---------|------|
| `Controllers/CategoryController.cs` | 新增 action | 加入 `[HttpGet("freetour")]` FreeTour() action，讓 `/category/freetour` 路由到 `Views/Category/FreeTour.cshtml` |
| `Views/Category/FreeTour.cshtml` | 新增（從零建立） | 自由行分類頁 Razor view，套用 R1 CSS variables，無硬編碼色值 |

### CategoryController 路由設計

```csharp
[Route("category")]
public class CategoryController : Controller
{
    [HttpGet("{slug}")]         // /category/{任意slug}
    public IActionResult Show(string slug) { ... }

    [HttpGet("freetour")]       // /category/freetour（專屬 action，優先於 {slug}）
    public IActionResult FreeTour() { ... }
}
```

**為何需要專屬 action**：ASP.NET Core 中 `[HttpGet("freetour")]` 比 `[HttpGet("{slug}")]` 更具體，路由選擇時優先匹配。若共用 `Show(slug)` action，`RouteData.Values["slug"]` 會是 `"freetour"`，`_Section_Banner` partial 依 slug 推導圖片路徑可正常運作；但本卡選擇專屬 action 以避免未來 slug 命名衝突，並提供更清晰的程式碼意圖。

### FreeTour.cshtml 設計決策

#### ResolveImage() Helper

```razor
@functions {
    string ResolveImage(string? img)
    {
        if (string.IsNullOrEmpty(img)) return string.Empty;
        if (img.StartsWith("http", StringComparison.OrdinalIgnoreCase)) return img;
        return Url.Content($"~/data/自由行/{img}");
    }
}
```

**問題背景**：`_Section_Banner.cshtml` 的圖片路徑邏輯為：
```csharp
var slug = ViewContext.RouteData.Values["slug"]?.ToString() ?? "homepage";
// → 有 {slug} 路由時正確；無 {slug} 時 fallback 為 "homepage" → 路徑錯誤
```

`FreeTour()` 是專屬 action（非 `{slug}` 路由），RouteData 不含 `slug` key，fallback 會變成 `~/data/homepage/images/`。因此 FreeTour.cshtml 內嵌 `ResolveImage()` 硬編碼「自由行」資料夾，繞過 partial 的 slug 推導邏輯。

#### Section Type 覆蓋範圍

| Section Type | 處理方式 | 說明 |
|------|---------|------|
| `hero_banner` | 內嵌渲染 | 需 ResolveImage()，不可用 _Section_Banner |
| `product_list` / `featured_items` / `featured_grid` | 內嵌渲染 | 需 ResolveImage()，含 product-card / featured-grid CSS classes |
| `quick_links` | 委派 `_Section_CategoryNav` partial | 無圖片路徑問題 |
| `search_bar` / `search_form` | 委派 `_Section_SearchForm` partial | 無圖片路徑問題 |
| 其他（fallback） | 委派 `_Section_Generic` partial | 通用處理 |

## 環境配置

### 資料來源

- 開發環境：`{ContentRootPath}/../../../data/自由行/自由行.json`
- 正式環境：`wwwroot/data/自由行/自由行.json`
- 圖片靜態檔：`wwwroot/data/自由行/images/`（需確保圖片存在）

### CSS Foundation（R1 依賴）

FreeTour.cshtml 的視覺效果完全依賴 `wwwroot/css/site.css` 的 R1 CSS variables：

```css
:root {
    --color-brand-primary: #11D073;   /* navbar 背景色 */
    --color-bg-primary: #F1F7F8;       /* body 背景色 */
    --font-family-primary: 'Noto Sans TC', 'Inter', sans-serif;
    /* ... 共 16 個 --color-* token */
}
body { background-color: var(--color-bg-primary); }
.navbar { background-color: var(--color-brand-primary) !important; }
```

**重要**：site.css 載入在 Bootstrap CDN 之後（`_Layout.cshtml` 的 `<link rel="stylesheet" href="~/css/site.css">`），利用 cascade 優先序 + `!important` 覆蓋 Bootstrap 預設值。

## 編譯與測試

### AC 驗證方式

| AC | 驗證方式 | 狀態 |
|----|---------|------|
| AC-W6-01：body.bg = rgb(241,247,248) | `Playwright evaluate getComputedStyle(document.body).backgroundColor` 含 `'241, 247, 248'` | ⚠️ 需 admin 在 merge 後執行 |
| AC-W6-02：navbar 含 #11D073 | `Playwright evaluate getComputedStyle(document.querySelector('.navbar')).backgroundColor` 含 `'17, 208, 115'` | ⚠️ 需 admin 在 merge 後執行 |
| AC-W6-03：無硬編碼色值 | `grep -E "#[0-9A-Fa-f]{3,6}\|rgb\(\|rgba\(" FreeTour.cshtml` 輸出空 | ✅ PASS |
| AC-W6-04：Figma 相似度 ≥70% | Playwright 截圖 vs Figma MISS-W2U6 nodeId | ❌ BLOCKED（MISS-W2U6 UIUX 未完成） |

### 防線 7 機械驗（已通過）

```bash
# 防線 7-1：site.css 含 #11D073
grep '#11D073' wwwroot/css/site.css
# → 輸出：--color-brand-primary: #11D073;（非空 PASS）

# 防線 7-2：navbar 使用 CSS variable
grep 'var(--color-brand-primary)' wwwroot/css/site.css
# → 輸出：.navbar { background-color: var(--color-brand-primary) !important; }（PASS）

# 防線 7-3：FreeTour.cshtml 無硬編碼色值
grep -E '#[0-9A-Fa-f]{3,6}|rgb\(|rgba\(' Views/Category/FreeTour.cshtml
# → 空輸出（PASS）
```

### HTTP 路由驗證（已通過）

```bash
curl -I http://localhost:5150/category/freetour
# → HTTP/1.1 200 OK（PASS）
```

## 常見錯誤排除

### 圖片路徑顯示 `/data/homepage/images/...`

**原因**：使用了 `_Section_Banner` partial，其 slug fallback 為 "homepage"。
**解法**：FreeTour.cshtml 內嵌 `ResolveImage()` helper，不委派 hero_banner 給任何 partial。

### navbar 顏色不變（仍是 Bootstrap 藍/白）

**原因**：site.css 未載入，或 CDN 連線失敗但 Bootstrap fallback 生效。
**排除**：DevTools Network tab 確認 site.css HTTP 200；Console 確認無 CSS parse error。
**注意**：`body { background-color: var(--color-bg-primary) }` 與 `.navbar { background-color: var(--color-brand-primary) !important }` 為全頁全域規則，若這兩條生效則所有頁面（包含 FreeTour）均會正確。

### Playwright 截圖 browser locked

**錯誤**：`Error: Browser is already in use for C:\Users\...\mcp-chrome-..., use --isolated to run multiple instances`
**解法**：在沒有其他佔用瀏覽器的環境中執行；或重啟 Playwright MCP server。

## 已知技術債

| 項目 | 說明 | 優先級 | 建議時機 |
|------|------|------|------|
| AC-W6-04 Figma 比對 BLOCKED | MISS-W2U6（UIUX）尚未開始，figma_deliverables.json 不存在，無法執行 Playwright vs Figma 截圖比對 | P1 | MISS-W2U6 完成後立即補驗 |
| ResolveImage() 與 _Section_Banner 邏輯重複 | 兩處都在解析圖片路徑，若未來資料夾結構改變需雙處更新 | P3 | 可在 _Section_Banner 增加 optional `folderOverride` 參數統一 |
| Show.cshtml 未處理 hero_banner 型別 | `Show.cshtml` switch 中無 `hero_banner` case，若其他 slug 頁面有此型別會 fallback 到 Generic | P2 | 視其他分類頁是否有 hero_banner 資料決定是否補齊 |
