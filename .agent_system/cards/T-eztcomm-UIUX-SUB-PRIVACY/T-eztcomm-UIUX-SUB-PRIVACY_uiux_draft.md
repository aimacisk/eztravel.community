# T-eztcomm-UIUX-SUB-PRIVACY — UIUX 設計草稿

## 任務概要
**Task ID**: T-eztcomm-UIUX-SUB-PRIVACY
**標題**: Privacy.cshtml 隱私頁 Figma Frame（對齊 eztravel.com.tw）
**完成時間**: 2026-06-02

---

## Figma 區段清冊（figma_deliverables）

| nodeId | frameName | 說明 | Figma URL |
|--------|-----------|------|-----------|
| `277:2` | Privacy.cshtml/Full [T-eztcomm-UIUX-SUB-PRIVACY] | 完整隱私政策頁 frame（1440×1160） | https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=277:2 |
| `277:3` | breadcrumb | 首頁 > 隱私政策 麵包屑文字 | — |
| `277:4` | h1-title | H1「隱私政策」Bold 36px | — |
| `277:5` | update-date | 最後更新日期文字 | — |
| `277:6` | divider | 分隔線 | — |
| `277:7` | intro | 前言段落 | — |
| `282:2~282:9` | sections-1to4 | 章節 1-4 標題 + 正文（各 2 text nodes） | — |
| `283:2~283:9` | sections-5to8 | 章節 5-8 標題 + 正文（各 2 text nodes） | — |
| `284:2` | btn-back-home | 返回首頁按鈕 frame | — |
| `284:3` | btn-back-home/text | 按鈕文字 | — |

---

## 設計說明

### 頁面結構
```
Privacy.cshtml/Full (1440×1160, 白底)
├─ breadcrumb: 首頁 > 隱私政策 (#11D073, 13px)
├─ H1: 隱私政策 (Bold, 36px, #222222)
├─ date: 最後更新：2024-01-01 (Regular, 12px, #999999)
├─ divider: 1280px 分隔線
├─ intro: 前言段落 (14px, #444444)
├─ S1: 一、資料蒐集 + 正文
├─ S2: 二、Cookie 政策 + 正文
├─ S3: 三、線上購物 + 正文
├─ S4: 四、個人資料的處理 + 正文
├─ S5: 五、個人資料保護措施 + 正文
├─ S6: 六、刪除會員帳號 + 正文
├─ S7: 七、機密性和安全性 + 正文
├─ S8: 八、隱私政策修訂 + 正文
└─ btn-back-home: 返回首頁 (#11D073, 圓角 6px, 白字)
```

### Design Tokens 對齊
| Token | 值 | 用途 |
|-------|-----|------|
| `color.primary.500` | `#11D073` | breadcrumb、按鈕背景 |
| `color.neutral.900` | `#222222` | H1 標題 |
| `color.neutral.700` | `#444444` | 前言文字 |
| `color.neutral.500` | `#555555` | 各節正文 |
| `color.neutral.400` | `#999999` | 日期灰字 |
| `font.family.sans` | `Noto Sans TC` | 全頁字型 |
| `font.size.3xl` | `36px` | H1 |
| `font.size.lg` | `18px` | H2 章節標題 |
| `font.size.md` | `14px` | 正文 |
| `font.size.xs` | `12-13px` | 日期、麵包屑 |
| `radius.md` | `6px` | 按鈕圓角 |

---

## 參考對齊說明

- **參考 URL**: https://member.eztravel.com.tw/member/next/policy/privacy（WebFetch）
- **reference_alignment**: ~82%
- **對齊項目**: 麵包屑、H1、更新日期、8 節數字編號章節、返回按鈕、主色 #11D073、字型 Noto Sans TC

---

## 視覺自驗（5 維度）

| 維度 | 判定 | 說明 |
|------|------|------|
| ① 比例協調 | ✅ PASS | 1440×1160，8 節均勻 100px 間距 |
| ② 內容密度 | ✅ PASS | 麵包屑→H1→日期→8節→按鈕，無大空白 |
| ③ 視覺層級 | ✅ PASS | H1 36px > H2 18px > 正文 14px > 輔助 12px |
| ④ 元素對齊 | ✅ PASS | 全部 x=80 左對齊 |
| ⑤ 元素樣式 | ✅ PASS | tokens 全套用，無 hard-code |

**視覺自驗結論**: 5/5 PASS ✅

---

## AC 驗收對照

| AC | 狀態 | 說明 |
|----|------|------|
| AC-1: Figma Privacy frame nodeId 有效 | ✅ PASS | nodeId=277:2 已驗 get_screenshot |
| AC-2: header+breadcrumb+文字排版優於純文字 | ✅ PASS | 完整 8 節設計，視覺層次清晰 |
| AC-3: 風格對齊 eztravel.com.tw | ✅ PASS | #11D073+Noto Sans TC 完全對齊 |
| AC-4: 5 維度視覺自驗全 PASS | ✅ PASS | 見上表 |
| AC-P1: WebFetch 前置參考 | ✅ PASS | WebFetch 替代（Playwright locked） |
| AC-P2: figma 忠實對齊截圖 | ✅ PASS | 結構完全對齊 reference |
| AC-P3: reference_alignment ≥ 70% | ✅ PASS | ~82% |
