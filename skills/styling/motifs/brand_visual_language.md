# 品牌視覺語言（Brand Visual Language）

> **品牌主題**：翠綠旅程（Jade Green Journey）
> **核心象徵**：翠綠 × 輕盈感 × 出發的期待

---

## 1. 色彩語言

### 四層次品牌色

品牌色以四層次漸進，建構完整的 UI 語義系統：

```
#11D073  →  #0C9251  →  #E7FAF1  →  #CFF6E3
（行動色）   （深壓色）   （底色層）   （薄荷層）
CTA/Active   Hover/Press  成功/淡底   Chip/Badge底
```

### 色彩情感地圖

| 情境 | Token | 顏色 | 語意 |
|------|-------|------|------|
| 主要動作（訂購 / 搜尋） | `color.brand.primary` | 翠綠 `#11D073` | 出發 / 確認 / 行動 |
| 深壓狀態 | `color.brand.dark` | 深綠 `#0C9251` | 完成 / 穩定 |
| 成功提示 | `color.brand.light` | 淡綠 `#E7FAF1` | 達成 / 放心 |
| 標籤底色 | `color.brand.mint` | 薄荷 `#CFF6E3` | 分類 / 標記 |
| 促銷 / 價格強調 | `color.accent.orange` | 橙 `#FF8B00` | 特惠 / 緊迫感 |
| 星評 | `color.accent.yellow` | 黃 `#FAB617` | 滿意 / 推薦 |
| 錯誤 | `color.accent.red` | 紅 `#FF7777` | 警告 / 阻止 |
| 文字主軸 | `color.neutral.900` | 深灰 `#222222` | 可讀 / 嚴肅 |

---

## 2. 陰影系統

### 兩層次陰影

| 層次 | Token | CSS 值 | 用途 |
|------|-------|--------|------|
| 標準卡片 | `shadow.card` | `0 2px 8px rgba(0,0,0,0.08)` | 商品卡、資訊卡靜態 |
| 懸浮 / 提升 | `shadow.elevated` | `0 4px 16px rgba(0,0,0,0.12)` | 卡片 hover、dropdown、modal |

### 使用原則

- 所有 card 元素預設套用 `shadow.card`
- hover 狀態切換到 `shadow.elevated`（配合 `transition.fast`）
- 無陰影：純文字區段 / 頁面背景層
- 禁止自訂非 token 陰影值

---

## 3. 圓角詞彙

| 場景 | Token | 值 | 範例元素 |
|------|-------|-----|---------|
| 微型標籤 | `radius.sm` | 4px | chip、badge、tag、小 icon button |
| 標準元件 | `radius.md` | 8px | card、input field、標準 button |
| 大型容器 | `radius.lg` | 12px | modal、bottom sheet、側邊抽屜、popup |
| 完全圓形 | `radius.full` | 9999px | avatar、pill badge、圓形 FAB |

### 鐵則

- **card 圓角固定 `radius.md`（8px）**，不允許例外
- **chip / badge 使用 `radius.sm`（4px）**，寬度 hug content（auto-layout）
- modal 容器使用 `radius.lg`，內容區不額外加圓角

---

## 4. 間距系統

### 7 步 Spacing Scale

基底：4px（1 個單位）

| Token | 值 | 用途場景 |
|-------|-----|---------|
| `spacing.1` | 4px | icon 內邊距、chip Y padding、最小間隔 |
| `spacing.2` | 8px | badge padding、緊湊元素間 gap |
| `spacing.3` | 12px | chip X padding、input 內邊距 X |
| `spacing.4` | 16px | 卡片內邊距（標準）、列表項間距 |
| `spacing.6` | 24px | 卡片間 gap（格線）、section 內分隔 |
| `spacing.8` | 32px | section padding 上下、大區塊間 |
| `spacing.12` | 48px | 頁面頂端 padding、超大區塊分隔 |

### 使用原則

- **禁止使用非 token 數值**（如 `10px`、`20px`、`15px`）
- 相鄰卡片間距固定 `spacing.6`（24px）
- 頁面左右 padding 最小 `spacing.8`（32px）

---

## 5. 字型系統

### 字型選用理由

| 語言 | 字體 | 原因 |
|------|------|------|
| 中文 | Noto Sans TC（首選）/ Heiti TC / 微軟正黑體 | 清晰易讀；Noto 跨平台一致性最佳 |
| 英文 / 數字 | Inter（首選）/ Gudea | Inter 螢幕優化；Gudea 與 eztravel 品牌字呼應 |

### 七層字型階層

| 層級 | Size | Weight | Line Height | 用途 |
|------|------|--------|-------------|------|
| Display | 40px | 700 | 1.2 | Hero 主標題 |
| H2 | 28px | 700 | 1.2 | 頁面標題 / 區段標題 |
| H3 | 22px | 700 | 1.5 | 子區段標題 |
| H4 | 18px | 500 | 1.5 | 卡片主標 / Modal title |
| Body | 14px | 400 | 1.5 | 正文 / 描述 |
| Small | 12px | 400 | 1.5 | 輔助資訊 / metadata |
| Caption | 11px | 400 | 1.75 | 版權 / timestamp / footnote |

---

## 6. 元件尺寸鐵則（UIUX 9 條紀律對齊）

### Chip / Badge

| 元件 | 高度（固定） | 最小寬度 | X Padding | 圓角 |
|------|------------|---------|-----------|------|
| badge | 24px | 48px | 8px | 4px |
| chip | 28px | 60px | 12px | 4px |

- **寬度 = hug content**（`primaryAxisSizingMode: AUTO`），禁止寫死
- `aspect = width / height ≥ 1.5`（嚴禁高 > 寬）

### Button

| 類型 | 高度（固定） | 最小寬度 | X Padding | 圓角 |
|------|------------|---------|-----------|------|
| 標準 button | 36px | 80px | 16px | 8px |

---

## 7. 圖示風格

- **線條風**（stroke，非實心填色）
- 尺寸：24×24px（標準）/ 32×32px（大型）/ 16×16px（小型 inline）
- 線寬：1.5px（一般）/ 2px（強調）
- 顏色：跟隨文字色（`color.neutral.900` / `color.neutral.500`）；active 時切換 `color.brand.primary`

---

## 8. 設計降級策略

當系統在低效能環境（老舊瀏覽器 / 低頻寬）時：

| 觸發條件 | 降級動作 | Token 變更 |
|---------|---------|-----------|
| 動畫卡頓（fps < 30） | 停用所有 transition | `transition.fast = 0ms`、`transition.normal = 0ms` |
| 圖片載入慢 | Hero 改用純色底 | Hero background = `color.brand.light`（無漸層） |
| 低對比無障礙（WCAG AA 不達標） | 深化中性色 | `color.neutral.500 → #555555` |
| 卡片陰影效能差 | 改用 border | `shadow.card = none` + `border: 1px solid #E8E8E8` |

---

> 本文件由 UIUX agent 於 T-eztcomm-20260601-W2-UIUX-10 產出。
> 下游使用：W3-UIUX-1 依此文件設計 Community Module 視覺語言。
