---
task_id: T-eztcomm-20260602-R1
agent: uiux
wiki_target: 06_wiki/04_dev_guide.md
status: DONE
completed_at: 2026-06-02T05:15:14+00:00
commit_sha: 4173f0d
---

# CSS Foundation — Design Token → CSS Variables

## 概述

T-eztcomm-20260602-R1 將 `skills/styling/tokens.json`（W3C Design Token v1.0.0）完整轉譯為 `site.css` CSS Custom Properties，並在 `_Layout.cshtml` 引入 Google Fonts，作為所有後續 Razor 視圖的樣式基礎。

## 變更檔案

| 檔案 | 變更內容 |
|------|---------|
| `wwwroot/css/site.css` | 全部重寫：新增 `:root` CSS variables（43 個）+ 全域樣式 |
| `Views/Shared/_Layout.cshtml` | `<head>` 新增 Google Fonts preconnect + stylesheet 引入 |

## CSS Variables 清單（:root 區段）

### Color tokens（16 個）

```css
--color-brand-primary:  #11D073;   /* 品牌主色，CTA / active 狀態 */
--color-brand-dark:     #0DA862;   /* hover / pressed 狀態 */
--color-brand-light:    #6FEBA9;   /* success 提示背景 */
--color-accent-coral:   #FF6B6B;   /* 錯誤 / 警告輔助色 */
--color-accent-sky:     #4ECDC4;   /* 特色功能強調色 */
--color-bg-primary:     #F1F7F8;   /* 頁面背景（body） */
--color-bg-card:        #FFFFFF;   /* 卡片底色 */
--color-bg-overlay:     rgba(0, 0, 0, 0.5);  /* modal 遮罩 */
--color-text-primary:   #1A2B3C;   /* 主要文字 */
--color-text-secondary: #5A7184;   /* 次要文字 */
--color-text-muted:     #9BABB8;   /* 輔助 / 說明文字 */
--color-border-light:   #E8F0F3;   /* 淡邊框 */
--color-border-medium:  #C5D5DC;   /* 標準邊框 */
--color-status-success: #11D073;   /* 成功狀態 */
--color-status-warning: #FFB800;   /* 警告狀態 */
--color-status-error:   #FF4757;   /* 錯誤狀態 */
```

### Font tokens（12 個）

```css
--font-family-primary: 'Noto Sans TC', 'Inter', sans-serif;
--font-family-display: 'Noto Sans TC', serif;
--font-size-xs:   11px;   --font-size-sm:   12px;
--font-size-base: 14px;   --font-size-lg:   18px;
--font-size-xl:   22px;   --font-size-2xl:  28px;   --font-size-4xl: 40px;
--font-weight-regular: 400;  --font-weight-medium: 500;  --font-weight-bold: 700;
```

### Spacing（7 個）、Radius（4 個）、Shadow（2 個）、Transition（2 個）

```css
--spacing-1: 4px; --spacing-2: 8px; --spacing-3: 12px; --spacing-4: 16px;
--spacing-6: 24px; --spacing-8: 32px; --spacing-12: 48px;

--radius-sm: 4px; --radius-md: 8px; --radius-lg: 16px; --radius-full: 9999px;

--shadow-card:     0 2px 8px rgba(0,0,0,0.08);
--shadow-floating: 0 4px 16px rgba(0,0,0,0.12);

--transition-fast: 150ms ease;  --transition-base: 300ms ease;
```

## 全域樣式重點

- `body` → `background-color: var(--color-bg-primary)` (#F1F7F8)，`font-family: var(--font-family-primary)`
- `.navbar` → `background-color: var(--color-brand-primary) !important` (#11D073)
- `.btn-primary` → 套用 `--color-brand-primary` / `--color-brand-dark`（hover）
- `.card` → `border-radius: var(--radius-md)`, `box-shadow: var(--shadow-card)`
- `.price` → `color: var(--color-brand-primary)`, `font-weight: var(--font-weight-bold)`
- focus-ring → 覆寫 Bootstrap #258cfb 為 `var(--color-brand-primary)`

## Google Fonts

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
```

## AC 驗收結果

| AC | 描述 | 結果 |
|----|------|------|
| AC-R1-01 | `grep -i '11D073' site.css` 包含 `--color-brand-primary` | ✅ PASS |
| AC-R1-02 | `grep -c 'color-' site.css` ≥ 16 | ✅ PASS（31）|
| AC-R1-03 | body background-color = var(--color-bg-primary) | ✅ PASS |
| AC-R1-04 | _Layout.cshtml 含 Google Fonts 引入 | ✅ PASS |
