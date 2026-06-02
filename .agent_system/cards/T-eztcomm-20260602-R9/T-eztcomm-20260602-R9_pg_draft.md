---
task_id: T-eztcomm-20260602-R9
agent: pg
created_at: 2026-06-02
wiki_target: 06_wiki/04_dev_guide.md
---

# [R9] Identity 頁面視覺驗收 — 開發者指南草稿

## 模組結構

```
Areas/Identity/Pages/
  _ViewStart.cshtml           ← 強制 Identity 頁面套主 Layout（admin 已建立）

wwwroot/css/
  site.css                    ← .btn-primary 翠綠覆寫（R1 已完成）

Views/Shared/
  _Layout.cshtml              ← 主 Layout（navbar-dark，無 bg-white 覆蓋）
```

## Identity UI 架構說明

eztravel.community 使用 ASP.NET Core Identity 內建 Razor Pages（來自 `Microsoft.AspNetCore.Identity.UI` NuGet），**未做 scaffold**。
- Login / Register / Manage 等頁面由 NuGet 套件內部提供
- 這些頁面本身不在專案 source code 中（`Areas/Identity/Pages/Account/` 目錄不存在）
- 控制 layout 的唯一方式：`Areas/Identity/Pages/_ViewStart.cshtml`

### _ViewStart.cshtml 作用機制

```csharp
@{
    Layout = "/Views/Shared/_Layout.cshtml";
}
```

- Identity Pages 找到此 `_ViewStart.cshtml` 時，會套用 `/Views/Shared/_Layout.cshtml`
- 主 Layout 引入 `site.css`（含 CSS variables），讓 Identity 頁面自動套用品牌主題
- **不需要** 修改任何 Identity 頁面的 Razor markup

## CSS 驗收結果

| AC | 描述 | 驗證方式 | 結果 |
|---|---|---|---|
| AC-R9-01 | body.backgroundColor 含 '241, 247, 248' | site.css: `body { background-color: var(--color-bg-primary); }`；`--color-bg-primary: #F1F7F8` | 靜態 PASS ✓ |
| AC-R9-02 | navbar.backgroundColor 含 '17, 208, 115' | site.css: `.navbar { background-color: var(--color-brand-primary) !important; }`；`--color-brand-primary: #11D073`；_Layout.cshtml: `navbar-dark`（無 bg-white） | 靜態 PASS ✓ |
| AC-R9-03 | 登入按鈕 backgroundColor 含 '17, 208, 115' | site.css: `.btn-primary { background-color: var(--color-brand-primary); }`；Identity Login 按鈕預設 `btn btn-primary` class | 靜態 PASS ✓ |
| AC-R9-04 | Register body.backgroundColor 含 '241, 247, 248' | 同 AC-R9-01（同一 site.css body 規則，Register 頁面共用） | 靜態 PASS ✓ |
| AC-R9-05 | figma Login frame 相似度 ≥70% | 需 T-eztcomm-R-UIUX-MISSING 完成後取 figma_deliverables.json | **BLOCKED-FIGMA** ⏸ |

### Playwright 動態驗收狀態

Playwright 瀏覽器於驗收時被 admin Claude Code session 佔用（`Browser already in use for mcp-chrome-4e170cb`），無法執行 `browser_navigate` / `browser_evaluate`。

已改用靜態 CSS 分析確認 AC-R9-01~04。Admin 建置後需補跑 Playwright 動態驗證。

## btn-primary 覆寫機制

site.css（R1 完成，位於 lines 117-142）：

```css
.btn-primary {
  background-color: var(--color-brand-primary);   /* #11D073 翠綠 */
  border-color: var(--color-brand-primary);
  color: #ffffff;
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast), border-color var(--transition-fast);
}
.btn-primary:hover,
.btn-primary:focus {
  background-color: var(--color-brand-dark);      /* #0DA862 深綠 hover */
  border-color: var(--color-brand-dark);
  color: #ffffff;
}
```

Bootstrap 載入順序（確保 site.css 覆寫生效）：
1. `bootstrap.min.css`（Bootstrap 預設藍色 btn-primary）
2. `site.css`（覆寫為品牌翠綠）

## 待處理（BLOCKED-FIGMA）

AC-R9-05 等 `T-eztcomm-R-UIUX-MISSING` 完工後：
1. 讀 `.agent_system/cards/T-eztcomm-R-UIUX-MISSING/figma_deliverables.json` 取 Login frame nodeId
2. `mcp__figma-remote-mcp__get_screenshot(nodeId=...)` 取設計截圖
3. Playwright 截圖 vs Figma 截圖比對，目標相似度 ≥70%

## 環境配置

- .NET 8 SDK（`dotnet run` 啟動後 `localhost:5150`）
- Identity Login：`http://localhost:5150/Identity/Account/Login`
- Identity Register：`http://localhost:5150/Identity/Account/Register`

## 修復迴圈紀錄

| 輪次 | 問題 | 修復方式 |
|---|---|---|
| 1 | Playwright 瀏覽器鎖定，無法動態驗收 | 改用靜態 CSS 分析確認所有 color variables；動態驗收標 PENDING_PLAYWRIGHT（需 admin 建置後補跑） |
| 2 | Identity Login.cshtml 不存在（未 scaffold）| 確認使用 built-in Identity UI，_ViewStart.cshtml 機制正確；無需 scaffold |
