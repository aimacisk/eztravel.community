---
task_id: T-eztcomm-R-UIUX-MISSING
agent: uiux
phase: DESIGN
status: DONE
completed_at: "2026-06-02T07:30:00+00:00"
wiki_target: 06_wiki/02_design_tokens.md
figma_file_key: 6XmYJOpiSXab2gtGlmWtks
---

# UIUX 補漏設計草稿 — T-eztcomm-R-UIUX-MISSING

## 任務背景

W4-AQ-1 BUG-001 揭發 `_LoginPartial.cshtml` 在 Figma 中沒有設計稿；由此延伸發現
navbar、footer、Error、404、Privacy 等通用元件均缺乏 Figma 設計規格，導致 PG
無法對齊設計進行實作。本任務補建全部 6 個缺漏元件。

## Figma 索引清冊（完整）

| 元件 | nodeId | 尺寸 | Figma URL |
|------|--------|------|-----------|
| Navbar | 249:3 | 1440×64 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=249:3 |
| Footer | 250:2 | 1440×64 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=250:2 |
| LoginPartial/未登入 | 250:6 | 124×48 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=250:6 |
| LoginPartial/已登入 | 251:3 | 198×48 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=251:3 |
| Error.cshtml/500 | 251:7 | 1440×480 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=251:7 |
| Error.cshtml/404 | 252:3 | 1440×480 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=252:3 |
| Privacy.cshtml | 253:2 | 1440×540 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=253:2 |

所有 nodeId 已通過 `get_metadata` 驗真 + `get_screenshot` 視覺自驗。

## 設計規格說明

### Navbar（249:3）

- **尺寸**：1440×64px，白底（#FFFFFF），SPACE_BETWEEN 橫向佈局
- **左區（Logo）**：`eztravel.community` — Inter Bold 18px，顏色 `color.brand.primary` (#11D073)
- **中區（導覽）**：機票 / 旅館 / 團體 / 自由行 / 票券 / 景點 — Noto Sans TC Regular 14px，顏色 `color.neutral.900` (#222222)；對應 `_Layout.cshtml` 6 個 categories
- **右區（LoginPartial）**：參見 LoginPartial 元件規格
- **Token 對應**：`color.brand.primary`、`color.neutral.900`、`font.family.latin Bold 18`、`font.family.chinese Regular 14`

### Footer（250:2）

- **尺寸**：1440×64px，背景 `color.neutral.700` (#444444)，SPACE_BETWEEN 橫向佈局
- **左文字**：`© 2026 - eztravel.community` — Inter Regular 13px，白色 opacity 0.8
- **右連結**：`隱私權` — Noto Sans TC Regular 13px，顏色 `color.brand.primary` (#11D073)
- **Token 對應**：`color.neutral.700`（footer 背景）、`color.brand.primary`（連結色）

### LoginPartial / 未登入（250:6）— BUG-001 修補

- **尺寸**：124×48px，白底，`color.neutral.200` (#E8E8E8) 1px 邊框
- **內容**：
  - 「註冊」文字：Noto Sans TC Regular 14px，`color.neutral.900` (#222222)
  - 「登入」按鈕 frame（60×32）：`color.brand.primary` (#11D073) 背景，`radius.md` (8px) 圓角，白色文字
- **對應 Razor**：`_LoginPartial.cshtml` `@else` 分支（未登入）
- **Token 對應**：`color.brand.primary`、`color.neutral.200`、`radius.md`

### LoginPartial / 已登入（251:3）— BUG-001 修補

- **尺寸**：198×48px，白底，`color.neutral.200` (#E8E8E8) 1px 邊框
- **內容**：
  - 使用者名稱（如 `user@example.com`）：Inter Regular 14px，`color.brand.primary` (#11D073)；對應帳戶管理連結
  - 「登出」文字：Noto Sans TC Regular 14px，`color.neutral.500` (#666666)
- **對應 Razor**：`_LoginPartial.cshtml` `@if (SignInManager.IsSignedIn(User))` 分支
- **Token 對應**：`color.brand.primary`（使用者名稱/管理帳戶）、`color.neutral.500`（登出）

### Error.cshtml / 500（251:7）

- **尺寸**：1440×480px，白底，VERTICAL CENTER 佈局，水平居中
- **主標**：`500` — Inter Bold 96px，`color.accent.red` (#FF7777)；對應 `Error.cshtml` `var(--color-status-error)`
- **副標**：`伺服器錯誤` — Noto Sans TC Regular 28px，`color.neutral.900`
- **描述**：`很抱歉，系統處理您的請求時發生問題，我們已記錄此事件。` — Noto Sans TC 14px，`color.neutral.500`
- **按鈕**：`返回首頁`（140×44）— `color.brand.primary` 背景，`radius.md` (8px)，白色文字
- **Token 對應**：`color.accent.red`、`color.brand.primary`（按鈕）

### Error.cshtml / 404（252:3）

- **尺寸**：1440×480px，白底，VERTICAL CENTER 佈局，水平居中
- **主標**：`404` — Inter Bold 96px，`color.brand.primary` (#11D073)；對應 `Error.cshtml` `var(--color-brand-primary)` 規格
- **副標**：`找不到頁面` — Noto Sans TC Regular 28px，`color.neutral.900`
- **描述**：`您嘗試訪問的網址不存在，可能已被移除或輸入錯誤。` — Noto Sans TC 14px，`color.neutral.500`
- **按鈕**：`返回首頁`（140×44）— `color.brand.primary` 背景，`radius.md` (8px)，白色文字
- **Token 對應**：`color.brand.primary`（主標 + 按鈕）

### Privacy.cshtml（253:2）

- **尺寸**：1440×540px，白底，VERTICAL MIN-start 佈局，paddingLeft/Right 80px，paddingTop 48px
- **主標**：`隱私政策` — Noto Sans TC Bold 32px，`color.neutral.900`
- **日期**：`最後更新：2026 年 6 月 1 日` — Inter Regular 12px，`color.neutral.500`
- **說明段落**：Noto Sans TC Regular 14px，`color.neutral.700`，textAutoResize HEIGHT，width 1280px
- **章節標題**：`我們收集的資訊` — Noto Sans TC Bold 18px，`color.neutral.900`
- **子項目清單**：3 條 bullet，Noto Sans TC Regular 14px，`color.neutral.700`
- **聯絡資訊**：`如有任何隱私相關問題，請聯絡 privacy@eztravel.community`

## 視覺自驗報告（8 維度）

| nodeId | ①比例 | ②密度 | ③層級 | ④對齊 | ⑤樣式 | ⑥容器 | ⑦不重疊 | ⑧文字 | 結論 |
|--------|------|------|------|------|------|------|------|------|------|
| 249:3 Navbar | OK | OK | OK | OK | OK | OK | OK | OK | **PASS** |
| 250:2 Footer | OK | OK | OK | OK | OK | OK | OK | OK | **PASS** |
| 250:6 LP/未登入 | OK | OK | OK | OK | OK | OK | OK | OK | **PASS** |
| 251:3 LP/已登入 | OK | OK | OK | OK | OK | OK | OK | OK | **PASS** |
| 251:7 Error 500 | OK | OK | OK | OK | OK | OK | OK | OK | **PASS** |
| 252:3 Error 404 | OK | OK | OK | OK | OK | OK | OK | OK | **PASS** |
| 253:2 Privacy | OK | OK | OK | OK | OK | OK | OK | OK | **PASS** |

## AC 驗收對照

| AC | 狀態 | 證據 |
|----|------|------|
| figma 有 6 個新建 frame（navbar/footer/Error/404/LoginPartial/Privacy）且 nodeId 真存在 | ✅ | 7 個 nodeId（含 LP 兩狀態）全部 get_metadata 回傳有效 |
| LoginPartial 有已登入/未登入兩種設計各自 frame | ✅ | 250:6（未登入）+ 251:3（已登入）各自獨立 frame |
| 每個元件 get_screenshot 可見品牌色 #11D073（非 Bootstrap 預設白） | ✅ | Navbar logo/登入按鈕、Footer 隱私權連結、LP/未登入登入按鈕、LP/已登入帳號名稱、404 主標、返回按鈕均為品牌綠 |
| 本卡 figma_deliverables 欄位包含全部 6 元件的 fileKey/nodeIds/page_url/screenshots | ✅ | 卡本體 figma_deliverables.components 7 條完整記錄 |
