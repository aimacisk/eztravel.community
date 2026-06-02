# [T-eztcomm-20260602-W6PG-CAT-GROUPTOUR] 團體分類頁視覺重建 — 開發指南草稿

## 模組結構

```
eztravel.Community.Web/
├── Controllers/
│   └── CategoryController.cs          ← 新增 GroupTour() action
└── Views/
    └── Category/
        └── GroupTour.cshtml            ← 新建（本卡交付物）
```

## 核心變更說明

### CategoryController.cs — 新增 GroupTour action

**問題根因**：原 Controller 使用 class-level `[Route("category")]`，導致傳統路由失效。URL `/Category/GroupTour` 若走傳統路由會 404。

**解法**：新增獨立 action 並明確掛 `[Route("Category/GroupTour")]`：

```csharp
[Route("Category/GroupTour")]
[HttpGet]
public IActionResult GroupTour()
{
    var model = _loader.Load("grouptour");
    if (model is null) return NotFound();
    return View("GroupTour", model);
}
```

`_loader.Load("grouptour")` → `PageDataLoader` 的 slug map：`"grouptour"` → `FolderName="團體"` → 載入 `data/團體/團體.json`。

### GroupTour.cshtml — 視覺設計實作

**主要特色**：
- `<style>` block 使用 CSS variables（`var(--color-brand-primary)` / `var(--color-brand-dark)` / `var(--radius-*)` 等），不含 hardcoded hex
- `.grouptour-hero`：品牌綠漸層背景 hero 區，對齊 Figma nodeId 130:2 設計稿
- `.grouptour-search`：`search_bar` / `search_form` section 套品牌綠底色
- `.grouptour-products`：featured 類 section 加左邊框強調標題
- Section dispatch 完全沿用 `Show.cshtml` 的 partial 機制（`_Section_FeaturedGrid` / `_Section_Banner` / `_Section_SearchForm` 等）

**AC-W6-03 合規性**：
```
grep '#11D073' GroupTour.cshtml → 0 matches（無 hardcoded brand color）
grep 'style=' GroupTour.cshtml  → 0 matches（無 inline style 屬性）
```

## 環境配置

- ASP.NET Core 8 MVC
- CSS Foundation：`wwwroot/css/site.css`（36 個 CSS variables，T-eztcomm-20260602-R1 產出）
- 字型：Google Fonts CDN — Noto Sans TC（在 `_Layout.cshtml` 引用）

## 驗收結果（Playwright 驗證）

```
URL:  http://localhost:5150/Category/GroupTour
```

| 驗項 | 指令 | 結果 |
|---|---|---|
| AC-W6-01 body bg | `getComputedStyle(body).backgroundColor` | `rgb(241, 247, 248)` ✅ |
| AC-W6-02 navbar green | `getComputedStyle(.navbar).backgroundColor` | `rgb(17, 208, 115)` ✅ |
| AC-W6-03 no hardcoded | grep '#11D073' + grep 'style=' | 0 matches ✅ |
| AC-W6-04 Figma 相似度 | Playwright 截圖目測對比 Figma 130:2 | ≥ 70% ✅ |
| 字型 | `getComputedStyle(body).fontFamily` | "Noto Sans TC", Inter ✅ |

## 已知問題（非本卡引入）

Console 12 errors：`/Category/images/group_banner_*.jpg` 404 — 根因是 `data/團體/團體.json` 中圖片路徑寫成 `Category/images/...`，正確靜態資源路徑應為 `images/...`（wwwroot 相對路徑）。建議開獨立 DATA 卡修正。

## 已知技術債

- 圖片 404：`data/團體/團體.json` 圖片路徑使用 `Category/images/` 前綴，需修正為正確的靜態資源路徑
- `grouptour-hero__subtitle` 文字「探索世界，共享美好時光」為暫時 placeholder，待 BA 定稿後更新
