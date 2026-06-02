---
task_id: T-eztcomm-20260602-W6PG-LAYOUT
agent: pg
wiki_target: 06_wiki/04_dev_guide.md
section: Shared Layout — Navbar + Footer 視覺重建（W6）
created_at: 2026-06-02T07:30:00+00:00
---

# [W6 PG] Navbar + Footer 共用 _Layout.cshtml 視覺重建

## 模組結構

| 檔案 | 路徑 | 說明 |
|------|------|------|
| `_Layout.cshtml` | `Views/Shared/_Layout.cshtml` | 全站共用 Layout：Navbar + Footer |
| `site.css` | `wwwroot/css/site.css` | CSS Foundation + Footer 深色主題樣式 |

### _Layout.cshtml 改動重點

**Navbar**（移除 Bootstrap 白底）：
```html
<!-- 舊 -->
<nav class="navbar navbar-expand-md navbar-light bg-white border-bottom box-shadow mb-3">

<!-- 新 -->
<nav class="navbar navbar-expand-md navbar-dark">
```

- 移除 `navbar-light bg-white border-bottom box-shadow mb-3`
- 改用 `navbar-dark`（讓漢堡圖示呈白色配合深色/綠底）
- CSS `site.css` 的 `.navbar { background-color: var(--color-brand-primary) !important; }` 負責套用品牌綠

**Footer**（新增 4 欄深色結構）：
```html
<footer class="footer">
  <div class="container footer__inner">
    <div class="footer__grid"> <!-- 4 欄 grid -->
      <!-- 欄一：品牌介紹 -->
      <!-- 欄二：旅遊服務 -->
      <!-- 欄三：公司資訊 -->
      <!-- 欄四：追蹤我們 -->
    </div>
    <div class="footer__bottom"> <!-- 版權列 --> </div>
  </div>
</footer>
```

### site.css 新增內容（Footer 深色主題）

**CSS Variables（加進 `:root`）**：
```css
--color-footer-bg:         #1A1A2E;
--color-footer-text:       rgba(255, 255, 255, 0.72);
--color-footer-heading:    #ffffff;
--color-footer-link:       rgba(255, 255, 255, 0.60);
--color-footer-link-hover: var(--color-brand-primary);
--color-footer-border:     rgba(255, 255, 255, 0.10);
```

**Footer CSS classes**（line 184–260）：
- `.footer` — 深色底 `#1A1A2E` via `var(--color-footer-bg)`
- `.footer__inner` — padding via spacing tokens
- `.footer__grid` — CSS Grid `2fr 1fr 1fr 1fr`（響應式：`@991px` → 2 欄，`@575px` → 1 欄）
- `.footer__brand-name / __tagline / __col-title / __links / __bottom / __copyright`

## 環境配置

- .NET 9 + ASP.NET Core MVC
- Bootstrap 5（由 CDN 載入，site.css 後置覆寫）
- Fonts: Google Fonts Inter + Noto Sans TC（在 `_Layout.cshtml` `<head>` 引入）

## 編譯與測試（admin 執行）

```bash
cd .worktrees/T-eztcomm-20260602-W6PG-LAYOUT/04_src/eztravel.Community
dotnet build
dotnet run --project eztravel.Community.Web --urls http://localhost:5150
```

## Playwright 驗證結果（PG 自驗）

| AC | 驗證指令 | 結果 |
|----|---------|------|
| AC-W6-01 | `getComputedStyle(document.body).backgroundColor` | `rgb(241, 247, 248)` ✅ |
| AC-W6-02 | `getComputedStyle(navbar).backgroundColor` | `rgb(17, 208, 115)` = #11D073 ✅ |
| AC-W6-03 | grep `style=.*#hex` in _Layout.cshtml | No matches ✅ |
| 防線7 | grep `#11D073` in site.css | 4 matches ✅ |
| Footer | `getComputedStyle(footer).backgroundColor` | `rgb(26, 26, 46)` = #1A1A2E ✅ |

## CSS 特異度說明

Bootstrap `bg-white` 使用 `!important`，但 `site.css` 在 Bootstrap 之後載入，且 `.navbar { background-color: ...; !important }` 同等特異度，後者（site.css）覆寫生效。**禁止刪除 Bootstrap CDN**，只能在後方疊加。

## 常見錯誤排除

| 問題 | 原因 | 解法 |
|------|------|------|
| Navbar 仍顯示白色 | Bootstrap `bg-white !important` 未被覆寫 | 確認 site.css 在 Bootstrap 後引入 + `.navbar` 含 `!important` |
| Footer 文字不可見 | `--color-footer-text` 未定義 | 確認 `:root` 包含 footer variables |
| 漢堡圖示不可見 | `navbar-light` 顯示深色漢堡圖示（在深底上不可見） | 改為 `navbar-dark` |
| Footer 不顯示 grid | 瀏覽器不支援 CSS Grid | 現代瀏覽器均支援，舊 IE11 除外 |

## 已知技術債

- SUPP-LAYOUT（UIUX 卡）尚未完成 Figma 設計，PG 依 CSS Foundation + 任務規格直接實作
- 若日後有 Figma 設計稿，可能需微調 spacing/typography
- `--color-surface-cool` 在主分支 site.css 尚未定義（使用 `--color-bg-primary`），R1 merge 後需確認 variable 名稱對齊
