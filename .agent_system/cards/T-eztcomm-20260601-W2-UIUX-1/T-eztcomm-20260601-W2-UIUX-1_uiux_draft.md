# UIUX Wiki Draft — T-eztcomm-20260601-W2-UIUX-1

> 對應 wikiTarget: `06_wiki/02_design_tokens.md`

## 設計系統規範 — eztravel.community

### 建立背景

W2 Wave 設計啟動任務。透過 Playwright 爬取 `https://www.eztravel.com.tw/` 萃取真實品牌色彩系統，並在 Figma 建立 `eztravel.community design` 設計檔案，完成 Tokens page 完整視覺化。

**重要發現**：規格文件預期品牌色為橙紅色系，實際爬取確認為翠綠 `#11D073`（`rgb(17, 208, 115)`）。設計系統以真實數據為準。

---

## 1. Token 命名空間

| 命名空間 | 用途 | 範例 |
|---------|------|------|
| `color.brand.*` | 品牌色四層次 | `color.brand.primary` = #11D073 |
| `color.neutral.*` | 中性灰階 9 色 | `color.neutral.900` = #222222 |
| `color.accent.*` | 促銷/強調色 3 色 | `color.accent.orange` = #FF8B00 |
| `color.surface.*` | 頁面底色 | `color.surface.cool` = #F1F7F8 |
| `font.family.*` | 字型堆疊 | `font.family.chinese` = Noto Sans TC |
| `font.size.*` | 字型大小 7 級 | `font.size.display` = 40px |
| `font.weight.*` | 字重 3 級 | `font.weight.bold` = 700 |
| `spacing.*` | 間距 7 值 | `spacing.4` = 16px |
| `radius.*` | 圓角 4 級 | `radius.md` = 8px |
| `shadow.*` | 陰影 2 級 | `shadow.card` |
| `transition.*` | 動畫時長 2 級 | `transition.fast` = 150ms |

---

## 2. 品牌色票

| Token | Hex | 用途 |
|-------|-----|------|
| `color.brand.primary` | #11D073 | CTA 按鈕、active 狀態 |
| `color.brand.dark` | #0C9251 | hover/pressed |
| `color.brand.light` | #E7FAF1 | 淡底色、成功提示 |
| `color.brand.mint` | #CFF6E3 | chip 淡底、badge 底 |

---

## 3. 中性色票（9 tone）

#222222 → #444444 → #666666 → #999999 → #CCCCCC → #E8E8E8 → #FAFAFA → #F1F7F8 → #FFFFFF

---

## 4. Typography Scale

| 層級 | Size | Weight | 用途 |
|------|------|--------|------|
| Display/H1 | 40px | Bold 700 | Hero 主標 |
| H2 | 28px | Bold 700 | 區段標題 |
| H3 | 22px | Bold 700 | 子標題 |
| H4 | 18px | Medium 500 | 卡片主標 |
| Body | 14px | Regular 400 | 正文 |
| Small | 12px | Regular 400 | 輔助資訊 |
| Caption | 11px | Regular 400 | 版權/footnote |

---

## 5. Figma 設計檔案

- **fileKey**: `6XmYJOpiSXab2gtGlmWtks`
- **完整 nodeId 清冊**: 見 `02_design/figma_deliverables.md`
- 已完成：Tokens page（色票卡 16 個 + typography 1 個 + spacing 視覺化）

---

## 6. 6 件套落盤

| 件 | 路徑 | 狀態 |
|----|------|------|
| figma_deliverables.md | `02_design/figma_deliverables.md` | ✅ |
| sources.md | `02_design/sources.md` | ✅ |
| design_tokens.json | `02_design/design_tokens.json` | ✅ |
| view_examples/ | `02_design/view_examples/` | ✅（2 截圖） |
| motifs.md | `02_design/motifs.md` | ✅ |
| figma_template/ | `02_design/figma_template/` | ✅（README placeholder） |
