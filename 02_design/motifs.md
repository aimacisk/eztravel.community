# Visual Motifs — eztravel.community

> 此檔定義 eztravel.community 的視覺主題語彙（motifs），為 UI 開發的視覺語言說明書。
> 所有視覺值均引用 `design_tokens.json` 內的 token，禁止 hard-code。

---

## 品牌語彙

### 核心隱喻：「翠綠旅程」

eztravel.community 以**翠綠色**為品牌識別核心，象徵「自由、自然、世界開闊」。
翠綠從飽和到淺淡的四個層次，對應從「重要行動」到「背景氛圍」的視覺權重階梯。

| 層次 | Token | Hex | 使用場景 |
|------|-------|-----|---------|
| 行動色 | `color.brand.primary` | #11D073 | CTA 按鈕、已選狀態、active 標籤 |
| 強化色 | `color.brand.dark` | #0C9251 | hover、pressed 狀態、深色 badge |
| 底色 | `color.brand.light` | #E7FAF1 | 淡背景 highlight、成功提示 |
| 點綴色 | `color.brand.mint` | #CFF6E3 | chip 淡底、卡片標記底色 |

---

## 視覺節奏

### 間距系統：4px 基準格

spacing scale 以 4px 為最小單位，遞增至 48px：

```
4 → 8 → 12 → 16 → 24 → 32 → 48
```

- 緊湊 UI 元素（badge、chip 內距）：`spacing.1`（4px）/ `spacing.2`（8px）
- 標準元素（button、input、卡片內距）：`spacing.4`（16px）
- 區段間距（section gap、卡片間距）：`spacing.6`（24px）/ `spacing.8`（32px）
- 頁面層級大間距（hero padding、section 頂底）：`spacing.12`（48px）

### 圓角語彙

| 類型 | Radius | 使用元素 |
|------|--------|---------|
| 微圓角 | 4px | chip、badge、小按鈕 |
| 標準圓角 | 8px | 卡片、input、按鈕 |
| 大圓角 | 12px | modal、底部 sheet |
| 全圓 | 50% | avatar、圓形 icon 按鈕 |

---

## 色彩情感地圖

| 情境 | 顏色 | Token |
|------|------|-------|
| 成功 / 確認 / 品牌 | 翠綠 | `color.brand.primary` |
| 促銷 / 限時 / CTA | 橙 | `color.accent.orange` |
| 星等 / 精選 / 重點 | 琥珀黃 | `color.accent.yellow` |
| 警示 / 折扣徽章 | 珊瑚紅 | `color.accent.red` |
| 主文字 | 深炭 | `color.neutral.900` |
| 次文字 | 中灰 | `color.neutral.500` |
| 邊框 / 分隔 | 淺灰 | `color.neutral.200` |
| 背景卡片 | 近白 | `color.neutral.100` |
| 頁面底色（冷色調） | 冷白 | `color.surface.cool` |

---

## 排版主題

### 字體選用邏輯

- **繁體中文優先**：Noto Sans TC → PingFang TC → 微軟正黑體（fallback）
- **Latin / 數字**：Inter（Figma 標準）→ Gudea（web，參考自 eztravel 現有網站）
- **風格定調**：「商務旅遊感」— 無襯線、清晰、有重量但不沉重

### 層級映射

| 層級 | 用途 | Token |
|------|------|-------|
| Display/H1 | 頁面主標、Hero 文字 | `font.size.display` (40px) |
| H2 | 區段標題 | `font.size.h2` (28px) |
| H3 | 子區段標題、卡片主標 | `font.size.h3` (22px) |
| H4 | 小標題、卡片副標 | `font.size.h4` (18px) |
| Body | 正文、說明文字 | `font.size.body` (14px) |
| Small | 輔助資訊、標籤 | `font.size.small` (12px) |
| Caption | 版權、footnote | `font.size.caption` (11px) |

---

## 設計降級策略

| 情境 | 降級行動 | 影響 Token |
|------|---------|-----------|
| 動畫效能不足 | 關閉 transition（改 0ms） | 不影響 token |
| 深色模式尚未支援 | 以淺色模式為主，深色留 roadmap | — |
| 低解析度裝置 | 陰影簡化為無陰影 | shadow.card |
| 字體載入失敗 | fallback 到系統 sans-serif | font.family.* |
