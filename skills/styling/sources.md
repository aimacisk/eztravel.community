# 設計參考來源（Design Sources）

> W2 設計學習資料彙整。單一代表性網站原則：一風格 = 一 URL，避免混學產生四不像。

---

## 主要參考網站

| 欄位 | 資料 |
|------|------|
| **來源 URL** | `https://www.eztravel.com.tw/` |
| **爬取日期** | 2026-06-01 |
| **爬取工具** | Playwright MCP（`browser_navigate` + `browser_take_screenshot` + `browser_snapshot`） |
| **爬取重點** | 首頁（Hero + Category nav + 商品卡片）、品牌色提取、字型識別 |
| **截圖存放** | `02_design/view_examples/01_homepage_hero.png`、`02_design/view_examples/02_homepage_full.png` |

---

## 採色方法說明

### 主色確認

透過 Playwright 爬取 eztravel.com.tw，使用 `browser_snapshot` 取得 DOM 結構，並對 Hero 區域 CTA 按鈕 + navigation active 狀態進行 computed style 分析。

**結果**：品牌主色確認為 `#11D073`（翠綠 RGB 17,208,115），非規格文件中預期的橙紅色系。

> ⚠️ 重要發現：原設計規格預期品牌色為橙紅，但實際 eztravel.com.tw 線上版本已更新為翠綠系。本設計系統以爬取真實數據為準。

### 色票萃取步驟

1. `browser_navigate` 開啟 `https://www.eztravel.com.tw/`
2. `browser_snapshot` 取得頁面 accessibility tree + 樣式
3. 識別 `.btn-primary`、`nav a.active`、hero CTA 按鈕的 `background-color` computed style
4. 識別 `color.brand.primary` = `#11D073`
5. 推導四層次：primary → dark（-30% lightness）→ light（+80% lightness）→ mint（+90% lightness）
6. `browser_take_screenshot` 截全頁存 `view_examples/`

### 字型識別

- 英文標題 / 數字：`Gudea`（Google Fonts）確認於 font-face 宣告
- 中文：`Heiti TC`、`Microsoft JhengHei`（系統字）
- 替換方案：`Inter`（英）、`Noto Sans TC`（中）— 同樣為開源免費授權

---

## 候選網站評估

| 網站 | URL | 主色 | 風格 | 評估 |
|------|-----|------|------|------|
| **eztravel.com.tw** | `https://www.eztravel.com.tw/` | 翠綠 `#11D073` | 高密度商旅 | ✅ **選用**：品牌一致，系統成熟 |
| klook.com | `https://www.klook.com/zh-TW/` | 橙 `#FF5722` | 活動體驗 | ❌：主色差距大，非旅行交通品牌 |
| kkday.com | `https://www.kkday.com/zh-tw/` | 亮橙紅 `#F86040` | 體驗旅遊 | ❌：CI 與翠綠衝突，風格偏年輕 |
| liontravel.com | `https://www.liontravel.com/` | 深藍 `#003399` | B2B / 團體 | ❌：偏傳統旅行社風格，非社群平台 |

**選用邏輯**：
- 品牌一致性優先（eztravel.community 是 eztravel 延伸服務）
- 色彩系統能直接繼承，無需重新建立品牌識別
- Community 功能作為差異化疊加點，而非品牌重建

---

## 版權與使用限制

- 截圖僅用於設計研究參考，不納入程式資產
- 設計 token 已重新命名，非直接複製 CSS 變數
- Noto Sans TC / Inter 字型為 Google Fonts OFL 授權，可商用
- Gudea 字型為 SIL Open Font License，可商用

---

> 本文件由 UIUX agent 於 T-eztcomm-20260601-W2-UIUX-10 產出。
