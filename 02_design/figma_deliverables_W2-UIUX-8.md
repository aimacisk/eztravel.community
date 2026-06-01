# Figma 交付物清冊 — T-eztcomm-20260601-W2-UIUX-8

**task_id**: T-eztcomm-20260601-W2-UIUX-8  
**任務**: W2-UIUX-8 — Figma 景點分類頁  
**完成時間**: 2026-06-02  
**執行者**: uiux agent

---

## Figma 索引

| 欄位 | 值 |
|------|---|
| fileKey | `6XmYJOpiSXab2gtGlmWtks` |
| pageId | `69:2` |
| pageName | `Category - 景點` |

---

## 區塊清冊

| nodeId | 名稱 | 說明 | Figma URL |
|--------|------|------|-----------|
| `69:3` | Category - 景點（主框架）| 390×3400 行動版主框架，背景 surface.cool | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=69:3 |
| `69:4` | SearchBar | 搜尋區：高鐵假期／列車套票／巴士旅遊／高鐵團票 tab、出發地／目的地輸入、出發區間、搜尋按鈕（品牌綠） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=69:4 |
| `74:2` | HeroBanner | 精選主題：15 個橫向滑動 banner（BannerStrip1×10 + BannerStrip2×5，各 140×88 px，各別配色） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=74:2 |
| `76:2` | CategoryNav | 分類導航：2 列 chips（ChipRow1×4 + ChipRow2×3，mint 底色，7 個主題入口） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=76:2 |
| `76:19` | FeaturedItems | 主題企劃：4 列 × 2 欄 = 7 張景點卡片（圖片佔位 174×110 + 名稱 + accent.orange 價格） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=76:19 |
| `78:2` | DestinationGrid | 台中出發：4 列 × 2 欄 = 7 個目的地卡（各地區配色，含價格） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=78:2 |
| `78:42` | ThemeSection | 高雄出發：4 列 × 2 欄 = 7 個目的地卡（各地區配色，含價格） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=78:42 |
| `80:2` | Footer | 深灰頁腳，eztravel 版權標示 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=80:2 |

---

## 設計規範對齊

- **色彩**：全引自 `design_tokens.json` — brand.primary `#11D073`、accent.orange `#FF8B00`、brand.mint `#CFF6E3`、neutral scale、surface.cool `#F1F7F8`
- **字型**：Inter（Regular / Medium / Bold）
- **圓角**：radius.md 8px（卡片、按鈕、chip、輸入框）
- **間距**：spacing.4（16px）padding、spacing.3（12px）gap
- **資料來源**：`data/景點/景點.json`（search_bar / hero_banner / category_nav / featured_items / destination_grid / theme_section）

---

## 視覺自驗記錄

| nodeId | 說明 | 結果 |
|--------|------|------|
| `69:3` | 主框架 390×3400，VERTICAL auto-layout，surface.cool 背景 | ✅ OK |
| `69:4` | SearchBar — 4 tab + location/date/button 結構完整 | ✅ OK |
| `74:2` | HeroBanner — 15 banner 橫向捲動，各別配色 | ✅ OK |
| `76:2` | CategoryNav — 7 chip 分 2 列，mint 底色，綠色文字 | ✅ OK |
| `76:19` | FeaturedItems — 7 卡，2 欄 grid，orange 價格 | ✅ OK |
| `78:2` | DestinationGrid 台中出發 — 7 卡，2 欄 grid，含價格 | ✅ OK |
| `78:42` | ThemeSection 高雄出發 — 7 卡，2 欄 grid，含價格 | ✅ OK |
| `80:2` | Footer — 深灰背景，版權文字 | ✅ OK |

get_metadata Step 7 驗證（nodeId=`69:2`）：全部 8 個子節點存在，結構正確。
