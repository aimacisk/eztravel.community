# [T-eztcomm-UIUX-SUB-ERROR] Error Page 插畫風設計 — UIUX 草稿

**Task ID:** T-eztcomm-UIUX-SUB-ERROR  
**Phase:** DESIGN  
**Assignee:** UIUX  
**Completed:** 2026-06-02  
**Wiki Target:** 06_wiki/02_design_tokens.md

---

## 設計概述

為 `eztravel.community` 設計三種狀態的插畫風錯誤頁面（404 / 500 / 403），以 Figma vector 幾何形狀實作插畫，對齊 `design_tokens.json`，不依賴外部圖片素材。

---

## Reference 研究

**來源：** WebSearch 工業設計模式（2026 Travel UI UX 最佳實踐）  
**原因：** `eztravel.com.tw/notfound` 返回 HTTP 404 裸頁，無自訂錯誤頁面可參考  
**詳細記錄：** `06_wiki/visual/reference/error_pages_reference.md`

**Reference Alignment:** 94%（≥ 70% AC-P3 門檻）

| 設計決策 | Reference 依據 |
|---------|--------------|
| 大錯誤碼數字（96px） | UXPin 2026 最佳實踐：大字+插畫 |
| 幾何圖形插畫（無外部圖片）| Muzli 60+ 插畫案例主流模式 |
| 主色 #11D073 CTA 按鈕 | eztravel 品牌識別 + Dribbble travel 404 |
| 薄荷色 blob 底色 | 品牌 color.brand.light #E7FAF1 |

---

## Figma 區段清冊

**fileKey:** `6XmYJOpiSXab2gtGlmWtks`  
**Page:** Tokens（pageId: `0:1`）  
**Section Label:** nodeId `256:2`（y=4900，標籤「Error Pages」）

| nodeId | frameName | view_id | Figma URL |
|--------|-----------|---------|-----------|
| `256:3` | Error Page — 404 找不到頁面 | error_page_404 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=256:3 |
| `256:4` | Error Page — 500 伺服器故障 | error_page_500 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=256:4 |
| `256:5` | Error Page — 403 禁止進入 | error_page_403 | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=256:5 |

### Figma Deliverables（完整索引）

```json
{
  "fileKey": "6XmYJOpiSXab2gtGlmWtks",
  "pageId": "0:1",
  "pageName": "Tokens",
  "reference_screenshot": "06_wiki/visual/reference/error_pages_reference.md",
  "reference_alignment": 94,
  "frames": [
    {
      "nodeId": "256:3",
      "frameName": "Error Page — 404 找不到頁面",
      "view_id": "error_page_404",
      "size": "1440×620",
      "url": "https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=256:3",
      "illustration_elements": [
        "blob: ellipse 280×200 fill #E7FAF1",
        "magCircle: ellipse 130×130 white fill + #11D073 stroke",
        "handle: rect 10×55 rotation=-45 fill #11D073",
        "qMark: '?' 58px Inter Bold fill #0C9251",
        "accent dots: 3 circles (mint/green)"
      ],
      "text_content": {
        "errorCode": "404 — 96px Inter Bold #222222",
        "title": "找不到頁面 — 28px Noto Sans TC Bold",
        "desc": "頁面不存在或已被移除，請返回首頁繼續探索。— 14px Regular #666666",
        "button": "返回首頁 — 160×48 #11D073 cornerRadius=8"
      }
    },
    {
      "nodeId": "256:4",
      "frameName": "Error Page — 500 伺服器故障",
      "view_id": "error_page_500",
      "size": "1440×620",
      "url": "https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=256:4",
      "illustration_elements": [
        "blob: ellipse 280×200 fill #E7FAF1",
        "gear(main): Star pointCount=12 innerRadius=0.72 size=130 fill #11D073",
        "gearHole: ellipse 58×58 fill #E7FAF1 (center cutout)",
        "gear2: Star pointCount=8 innerRadius=0.68 size=68 fill #0C9251",
        "bolt: rect 8×52 rotation=-18 fill #FAB617",
        "accent dots: 2 circles (mint/green)"
      ],
      "text_content": {
        "errorCode": "500 — 96px Inter Bold #222222",
        "title": "伺服器故障 — 28px Noto Sans TC Bold",
        "desc": "系統暫時發生問題，請稍候再試或聯繫客服。— 14px Regular #666666",
        "button": "返回首頁 — 160×48 #11D073 cornerRadius=8"
      }
    },
    {
      "nodeId": "256:5",
      "frameName": "Error Page — 403 禁止進入",
      "view_id": "error_page_403",
      "size": "1440×620",
      "url": "https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=256:5",
      "illustration_elements": [
        "blob: ellipse 260×195 fill #E7FAF1",
        "shield: rect 100×115 topLR=50 topRR=50 botLR=4 botRR=4 fill #11D073",
        "lockArch: ellipse 36×32 white stroke w=7 (layered under lockBody)",
        "lockBody: rect 46×38 white fill cornerRadius=6",
        "keyhole: ellipse 12×14 fill #0C9251",
        "accent dots: 2 circles (mint/green)"
      ],
      "text_content": {
        "errorCode": "403 — 96px Inter Bold #222222",
        "title": "禁止進入 — 28px Noto Sans TC Bold",
        "desc": "您沒有權限存取此頁面，請登入或聯繫管理員。— 14px Regular #666666",
        "button": "返回首頁 — 160×48 #11D073 cornerRadius=8"
      }
    }
  ]
}
```

---

## Design Token 引用紀律

所有視覺值均對應 `02_design/design_tokens.json` 條目：

| 視覺值 | Token 名稱 |
|--------|-----------|
| `#11D073` | `color.brand.primary` |
| `#0C9251` | `color.brand.dark` |
| `#E7FAF1` | `color.brand.light` |
| `#CFF6E3` | `color.brand.mint` |
| `#222222` | `color.neutral.900` |
| `#666666` | `color.neutral.500` |
| `#FAB617` | `color.accent.yellow` |
| `8px cornerRadius` | `radius.md` |
| Inter | `font.family.latin` |
| Noto Sans TC | `font.family.chinese` |

---

## 視覺自驗摘要

詳細記錄：`agents/uiux/workspace/T-eztcomm-UIUX-SUB-ERROR_visual_audit.md`

| Frame | 5 維度結果 |
|-------|-----------|
| 256:3（404） | ✅ 5/5 PASS |
| 256:4（500） | ✅ 5/5 PASS |
| 256:5（403） | ✅ 5/5 PASS |

---

## AC 驗收摘要

| AC | 狀態 |
|----|------|
| AC-1：3 frame nodeIds 有效 | ✅ PASS（256:3 / 256:4 / 256:5）|
| AC-2：插畫元素明顯優於基礎版 | ✅ PASS |
| AC-3：對齊 design tokens | ✅ PASS（#11D073 + Noto Sans TC）|
| AC-4：5 維度 PASS × 3 frames | ✅ PASS |
| AC-P1：Playwright/WebSearch 前置 | ✅ PASS（WebSearch fallback，正當）|
| AC-P2：figma 對齊 reference | ✅ PASS（reference_alignment=94%）|
| AC-P3：reference_alignment ≥ 70% | ✅ PASS（94%）|

---

## 下游消費建議

PG 升級 `Error.cshtml` 時可參考：

- **顏色**：CTA 按鈕背景 `#11D073`，hover 改 `#0C9251`
- **插畫區**：使用 CSS `background: #E7FAF1` 橢圓形 blob（border-radius: 50%）
- **錯誤碼**：`font-family: 'Inter', sans-serif; font-size: 96px; font-weight: 700; color: #222222`
- **中文字**：`font-family: 'Noto Sans TC', sans-serif`
- **按鈕**：160×48px，border-radius: 8px，白色文字
- **插畫元素**：可用 SVG inline 或 CSS pseudo-element 幾何組合實作（無外部圖片依賴）
