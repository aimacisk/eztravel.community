# UIUX Wiki Draft — T-eztcomm-20260601-W2-UIUX-10

> 對應 wikiTarget：`06_wiki/02_design_tokens.md`
> W2 收尾任務：6 件套風格學習包彙整交付

---

## W2 設計系統完整交付清單

### 6 件套位置（skills/styling/）

| 件 | 路徑 | 說明 |
|----|------|------|
| README.md | `skills/styling/README.md` | 3 維度風格描述 + Figma URL + token 使用方式 |
| sources.md | `skills/styling/sources.md` | 設計參考來源、爬取日期、候選評估 |
| tokens.json | `skills/styling/tokens.json` | W3C Design Token 格式完整 token 集 |
| view_examples/ | `skills/styling/view_examples/index.json` | 10 頁面 nodeId + Figma URL 索引 |
| motifs/ | `skills/styling/motifs/brand_visual_language.md` | 品牌視覺語言：陰影 / 圓角 / 間距 / 字型 |
| figma_template.json | `skills/styling/figma_template.json` | fileKey + 全 W2 nodeId 索引 + PG quick_reference |

---

## Figma 設計檔案資訊

- **fileKey**：`6XmYJOpiSXab2gtGlmWtks`
- **URL**：`https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/eztravel.community-design`
- **W2 覆蓋頁面**：Tokens / Home / 機票 / 旅館 / 自由行 / 團體 / 票券 / 景點 / ProductDetail（共 9 頁）

---

## 頁面 nodeId 清冊（完整索引）

| 頁面 | Page Node | Primary Frame | Figma URL |
|------|-----------|---------------|-----------|
| Tokens | (page 1) | 1:2 | `?node-id=1:2` |
| Home | 107:2 | 153:2 | `?node-id=107:2` |
| 機票 | 100:2 | 180:2 | `?node-id=100:2` |
| 旅館 | 119:2 | 119:2 | `?node-id=119:2` |
| 自由行 | 127:2 | 127:2 | `?node-id=127:2` |
| 團體 | 130:2 | 130:2 | `?node-id=130:2` |
| 票券 | 187:2 | 187:3 | `?node-id=187:2` |
| 景點 | 144:2 | 144:2 | `?node-id=144:2` |
| ProductDetail | 88:2 | 88:471（ComponentSet） | `?node-id=88:2` |

### ProductDetail 4 Variant

| Variant | NodeId | Size |
|---------|--------|------|
| Category=GroupTour | 88:3 | 1440×1600 |
| Category=FreeTour | 88:123 | 1440×1600 |
| Category=Hotel | 88:243 | 1440×1600 |
| Category=Ticket | 88:355 | 1440×1600 |

---

## 核心設計決策記錄

### 品牌主色修正

- **規格預期**：橙紅色系
- **實際確認**：翠綠 `#11D073`（2026-06-01 Playwright 爬取 eztravel.com.tw 確認）
- **決策**：以真實品牌色為準，橙 `#FF8B00` 降為促銷輔色

### Token 架構

- 命名空間：`color.brand.*`、`color.neutral.*`、`color.accent.*`、`color.surface.*`、`font.*`、`spacing.*`、`radius.*`、`shadow.*`、`transition.*`
- 格式：W3C Design Token Draft（`$value`、`$type`、`$description`、`_figma_node`）
- 所有視覺值必須引用 token，禁止 hard-code

### 設計系統層次

1. Token 層（`skills/styling/tokens.json`）— 原子變數
2. Motif 層（`skills/styling/motifs/`）— 使用語意 + 降級策略
3. Component 層（Figma ComponentSet）— 可複用元件
4. View 層（Figma Page frames）— 完整頁面

---

## 下游使用指引

### W3-UIUX-1（Community Module 設計）

- 讀 `skills/styling/README.md` 取風格 3 維度
- 讀 `skills/styling/motifs/brand_visual_language.md` 取色彩情感地圖 + 元件尺寸鐵則
- Community slot 位置：`figma_template.json` 的 `pages.product_detail.community_slot`
  - nodeId：`88:471` 內每 variant 的 `Community_Area` 子區塊
  - 高度：380px

### W4-PG-2（Home Razor 實作）

- 主 frame：`153:2`（Figma page `107:2`）
- token 引用：`skills/styling/tokens.json`
- 關鍵區段：Hero `153:3`、Category Nav `153:20`、Hot Products `153:40`

### W4-PG-3（ProductDetail Razor 實作）

- ComponentSet：`88:471`（包含 4 variant）
- 每 variant 高度：1440×1600px，分為 5 區段
  - Hero（400px）、MainContent（500px）、Community_Area（380px）、Recommendation（220px）、Footer（100px）
- Community_Area slot：保留空白，不實作 Community 功能（W3 scope）

### W4-PG-4（6 分類 Category Listing）

- 機票：page `100:2`，wrapper `180:2`
- 旅館：page `119:2`，wrapper `119:2`
- 自由行：page `127:2`，wrapper `127:2`
- 團體：page `130:2`，wrapper `130:2`
- 票券：page `187:2`，wrapper `187:3`
- 景點：page `144:2`，wrapper `144:2`

---

> 本 wiki draft 由 UIUX agent 於 T-eztcomm-20260601-W2-UIUX-10 產出。
> 待 PM 整合至 `06_wiki/02_design_tokens.md`。
