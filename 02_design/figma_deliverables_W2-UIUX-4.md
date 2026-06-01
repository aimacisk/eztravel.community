# Figma 交付物清冊 — T-eztcomm-20260601-W2-UIUX-4

**task_id**: T-eztcomm-20260601-W2-UIUX-4  
**任務**: W2-UIUX-4 — Figma 旅館分類頁  
**完成時間**: 2026-06-02  
**執行者**: uiux agent

---

## Figma 索引

| 欄位 | 值 |
|------|---|
| fileKey | `6XmYJOpiSXab2gtGlmWtks` |
| pageId | `54:2` |
| pageName | `Category - 旅館` |

---

## 區塊清冊

| nodeId | 名稱 | 說明 | Figma URL |
|--------|------|------|-----------|
| `54:3` | Category - 旅館（主框架）| 390×3200 行動版主框架，背景 surface.cool | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=54:3 |
| `54:4` | SearchBar | 搜尋區：訂房+高鐵 / 機+酒 tab、關鍵字輸入、入退住日期、搜尋按鈕（品牌綠） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=54:4 |
| `55:2` | PromoSection | 促銷活動：10 個橫向滑動 banner（140×88 px，各別配色） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=55:2 |
| `56:2` | ThemeSection | 大家都搜：2 列 × 4 chips（mint 底色，8 個主題入口） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=56:2 |
| `57:2` | FeaturedHotels | 精選飯店推薦：5 列 × 2 欄 = 10 張旅館卡片（圖片佔位 + 名稱 + 說明 + accent.orange 價格） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=57:2 |
| `60:2` | DestinationGrid | 熱門住宿目的地：4 列 × 3 欄 = 12 個目的地卡（各地區配色） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=60:2 |
| `60:32` | Footer | 深灰頁腳，eztravel 版權標示 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=60:32 |

---

## 設計規範對齊

- **色彩**：全引自 `design_tokens.json` — brand.primary `#11D073`、accent.orange `#FF8B00`、neutral scale、surface.cool `#F1F7F8`
- **字型**：Inter（Regular / Medium / Bold）
- **圓角**：radius.md 8px（卡片、按鈕、輸入框）
- **間距**：spacing.4（16px）padding、spacing.3（12px）gap
- **資料來源**：`data/旅館/旅館.json`（search_bar / promo_section / theme_section / featured_hotels / destination_grid）
