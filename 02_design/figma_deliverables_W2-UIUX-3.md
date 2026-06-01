# Figma Deliverables — T-eztcomm-20260601-W2-UIUX-3

> 機票分類頁 完整繪製清冊(admin 親建,對照 data/機票/full_screenshot.png + data/機票/機票.json)

**任務**:W2-UIUX-3 機票分類頁
**完成時間**:2026-06-02
**執行者**:admin(因 worker context 爆,改 admin 親建)

## Figma 索引

| 屬性 | 值 |
|------|----|
| fileKey | `6XmYJOpiSXab2gtGlmWtks` |
| pageId | `100:2` |
| pageName | Category - 機票 |
| Wrapper | `180:2` Category-機票 Wrapper (1440×1453px) |

## 區段清冊

| nodeId | 名稱 | 內容摘要 | Figma URL |
|--------|------|---------|----------|
| `180:3` | top-nav | 綠底 navigation bar + logo + 7 分類 tab(機票/機+酒/機+酒+船/訂房/高鐵假期/票券/出國通)| https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=180:3 |
| `181:2` | search_bar | 4 tab(機票/機+酒/機+酒+船/訂房)+ 3 trip-type(來回/單程/多行程)+ 5 fields(出發地/目的地/出發日/回程日/艙等與人數)+ 搜尋機票 button | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=181:2 |
| `182:2` | hero_banner | 1 main blue banner + 4 promo cards 真實:機票週3狂歡日/2026盛夏/2026台東熱氣球/日本航空 9折 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=182:2 |
| `183:2` | hot_routes | 9 cards 真實 items:長榮票規整理/華航票規整理/學生票專區/酷航無痕降落/亞航 GO 機票/星宇航空專區/泰國 RT 機票/日本 RT 機票/韓國 RT 機票 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=183:2 |
| `184:2` | airline_section | 7 chips 真實 items:泰國獅子航空/酷航 Scoot/捷星日本航空/台灣虎航/亞洲航空/濟州航空/春秋航空 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=184:2 |
| `185:2` | promo_fares | 3 cards:折扣碼管理/護照．簽證/護照簽證辦理 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=185:2 |
| `185:14` | footer | 易遊網客服 02-2537-8030 + 版權聲明 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=185:14 |

## 設計規範對齊

- **色票**:brand.primary `#11D073`(綠 nav + button)、blue `#0075A5`(hero banner)、orange `#FF8B00`(card 強調)、neutral 灰階(背景/邊框)
- **字型**:Inter Regular / Bold
- **圓角**:radius.md 6-8px
- **間距**:padding 12-48px,gap 12-24px
- **參考標的**:data/機票/full_screenshot.png(eztravel 真實機票頁長截圖)+ data/機票/機票.json(sections 真實 items)

## Rule 0a 完整性自驗

| 項目 | 狀態 |
|------|------|
| sections 數量(JSON 7 sections:search_bar / hero_banner / promo_fares / hot_routes / airline_section / visa_info / 額外 top-nav)| ✅ 完整 |
| hot_routes items 9/9 | ✅ 全建 |
| airline_section items 7/7 | ✅ 全建 |
| 不簡化 / 不自編 | ✅ 全文字取自 JSON items.text 或 screenshot 可見內容 |

## Rule 0b 重疊管理自驗

| 項目 | 狀態 |
|------|------|
| sections 全在 wrapper 180:2 VERTICAL AutoLayout 內 | ✅ 由 layout engine 自動排列無重疊 |
| 與其他 wrapper 不重疊 | ✅ 唯一 wrapper |
| bounds yMax = 1453 | ✅ |
