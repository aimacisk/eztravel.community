# eztravel.community — 設計風格學習包

> **Figma 設計檔案**：`https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/eztravel.community-design`
> **Token 主檔**：`skills/styling/tokens.json`
> **參考來源**：`skills/styling/sources.md`
> **視覺語言**：`skills/styling/motifs/`
> **頁面索引**：`skills/styling/view_examples/`

---

## 1. 風格特徵（Style Features）

### 色彩系統

主色：**翠綠 `#11D073`**（Mint Green）

- 取自 eztravel.com.tw 真實品牌色，透過 Playwright 動態爬取確認（非規格文件預期的橙紅色系）
- 四層次品牌色：`#11D073`（CTA / active）→ `#0C9251`（hover）→ `#E7FAF1`（淡底）→ `#CFF6E3`（chip / badge 底色）
- 中性灰階 9 tone：`#222222` → `#FFFFFF`，提供完整文字/邊框/背景層次
- 促銷輔色：橙 `#FF8B00` / 黃 `#FAB617` / 紅 `#FF7777`

### 字型系統

| 語言 | 字體 | 用途 |
|------|------|------|
| 中文 | Noto Sans TC, Heiti TC, 微軟正黑體 | 主要文字內容 |
| 英文 / 數字 | Inter, Gudea | 標題、價格數字、UI label |

### 排版密度

高密度卡片式佈局，強調資訊豐富度：
- 桌機寬度：1440px（設計基準）
- 頁面高度：依頁面類型 1352px ～ 4164px
- 網格：4px 基底，間距 scale 7 級（4 / 8 / 12 / 16 / 24 / 32 / 48px）
- 圓角：4px（chip/badge）/ 8px（card/button/input）/ 12px（modal）

### 視覺元素

- **卡片陰影**：`0 2px 8px rgba(0,0,0,0.08)`（標準）/ `0 4px 16px rgba(0,0,0,0.12)`（懸浮）
- **Hero 背景**：品牌翠綠漸層，高度約 400px
- **分類 icon**：線條風（stroke，非填色），尺寸 24×24 / 32×32
- **CTA 按鈕**：solid fill `#11D073`，radius 8px，高度固定 36px，寬度 hug content

---

## 2. 動線設計（User Flow）

### 主旅程

```
Hero（品牌曝光 + 搜尋入口）
  ↓
Category Navigation（6 大分類：機票 / 旅館 / 自由行 / 團體 / 票券 / 景點）
  ↓
Category Listing（商品卡片列表 + filter / 排序）
  ↓
Product Detail（4 類型共通主版 + variant 差異區 + Community Module slot）
  ↓
Checkout（範圍外，W4 實作）
```

### 頁面群組（W2 設計範圍）

| 頁面 | Figma Page | 設計重點 |
|------|-----------|---------|
| Home | 107:2 | Hero + 6 分類快速入口 + 熱門商品 |
| 機票 Listing | 100:2 | 航班篩選 + FlightCard 水平排列 |
| 旅館 Listing | 119:2 | 地圖 / 列表雙模式 + 星級篩選 |
| 自由行 Listing | 127:2 | 行程天數 + 出發城市篩選 |
| 團體 Listing | 130:2 | 出發日期月曆 + TourCard |
| 票券 Listing | 187:2 | 地區篩選 + 有效期 badge |
| 景點 Listing | 144:2 | 類型 chip 篩選 |
| Product Detail | 88:2 | 4 類型共通版（variant）+ Community slot |

### 互動節點

- **搜尋框**：Hero 區，全寬 sticky
- **Filter chips**：每分類頁頂端，auto-layout hug content
- **商品卡片**：點擊整卡跳 ProductDetail
- **Community slot**：ProductDetail 頁下方，W3 實作 instance 點

---

## 3. 選用動機（Selection Rationale）

### 為何選 eztravel.com.tw 作為設計基準

1. **品牌一致性**：eztravel.community 為 eztravel 生態系延伸，品牌色、字型、設計語言必須與母品牌高度一致
2. **成熟設計系統**：eztravel 已有多年累積的 UX 模式，Category / Listing / Detail 三層結構清晰，可直接學習
3. **社群差異化**：Community Module（評論 / 互動 / 社群）是 eztravel.community 獨有功能，在既有設計語言上疊加，而非重頭打造新品牌
4. **工程友善**：高密度卡片 + 固定寬度 token 系統，易轉化為 ASP.NET Core Razor + Tailwind/CSS 實作

### 候選評估摘要

| 網站 | 評估結果 | 排除原因 |
|------|---------|---------|
| eztravel.com.tw | ✅ **選用** | 品牌一致 + 成熟系統 |
| klook.com | ❌ 排除 | 橙色主色，風格差距大 |
| kkday.com | ❌ 排除 | 亮橙紅 CI，與翠綠系衝突 |
| liontravel.com | ❌ 排除 | 偏向 B2B 風格，不適合社群平台 |

> 詳細評估見 `skills/styling/sources.md`

---

## 4. Tokens 使用方式

### 引用格式

本專案 token 定義於 `skills/styling/tokens.json`（W3C Design Token 格式）。

```json
{
  "color.brand.primary": "#11D073",
  "color.brand.dark": "#0C9251",
  "spacing.4": "16px",
  "radius.md": "8px"
}
```

### 常用 Token 速查

| 用途 | Token | 值 |
|------|-------|-----|
| CTA 按鈕底色 | `color.brand.primary` | `#11D073` |
| Hover 狀態 | `color.brand.dark` | `#0C9251` |
| 淡底 / 成功提示 | `color.brand.light` | `#E7FAF1` |
| Chip / Badge 底 | `color.brand.mint` | `#CFF6E3` |
| 主文字 | `color.neutral.900` | `#222222` |
| 輔助文字 | `color.neutral.500` | `#666666` |
| 促銷價格 | `color.accent.orange` | `#FF8B00` |
| 頁面底色 | `color.surface.cool` | `#F1F7F8` |
| 卡片間距 | `spacing.4` | `16px` |
| 卡片圓角 | `radius.md` | `8px` |
| 卡片陰影 | `shadow.card` | `0 2px 8px rgba(0,0,0,0.08)` |

### Figma Variables 對應

Figma 檔案 `6XmYJOpiSXab2gtGlmWtks` 的 Tokens page 包含全部視覺 token 色票卡，可直接比對命名關係。

- 品牌色：`1:6`（primary）/ `1:12`（dark）/ `1:18`（light）/ `1:24`（mint）
- 中性色：`1:33`～`1:75`（9 tone）
- Typography block：`1:111`
- Spacing Scale：`1:132` / `1:135`

---

> 本文件由 UIUX agent 於 W2 收尾任務（T-eztcomm-20260601-W2-UIUX-10）自動生成。
> 下游使用：W3-UIUX-1（Community module 視覺語言）、W4-PG-2/3/4（Razor 實作定位 nodeId）
