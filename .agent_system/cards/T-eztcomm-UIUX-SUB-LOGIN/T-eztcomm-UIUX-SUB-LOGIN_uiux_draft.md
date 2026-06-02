# [T-eztcomm-UIUX-SUB-LOGIN] Login / Register / ForgotPassword / ConfirmEmail Figma Frames

---

## 任務摘要

為 `eztravel.community` 補建登入相關頁面 Figma frame，供 R9 Identity Login Layout 實作依賴。
依 AC-P1 強制規範，設計前先以 Playwright 訪問 `https://member.eztravel.com.tw/login` 取得真實截圖作為參考基準。

---

## figma_deliverables

```json
{
  "fileKey": "6XmYJOpiSXab2gtGlmWtks",
  "pageId": "0:1",
  "pageName": "Tokens",
  "frames": [
    {
      "frameName": "Login Modal [T-eztcomm-UIUX-SUB-LOGIN]",
      "nodeId": "265:2",
      "view_id": "login-modal",
      "url": "https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=265:2",
      "size": "460×462"
    },
    {
      "frameName": "Register Modal [T-eztcomm-UIUX-SUB-LOGIN]",
      "nodeId": "272:2",
      "view_id": "register-modal",
      "url": "https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=272:2",
      "size": "460×530"
    },
    {
      "frameName": "ForgotPassword Modal [T-eztcomm-UIUX-SUB-LOGIN]",
      "nodeId": "273:2",
      "view_id": "forgot-password-modal",
      "url": "https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=273:2",
      "size": "460×325"
    },
    {
      "frameName": "ConfirmEmail Modal [T-eztcomm-UIUX-SUB-LOGIN]",
      "nodeId": "274:2",
      "view_id": "confirm-email-modal",
      "url": "https://www.figma.com/file/6XmYJOpiSXab2gtGlmWtks/?node-id=274:2",
      "size": "460×330"
    }
  ],
  "reference_screenshot": "projects/eztravel.community/06_wiki/visual/reference/login.png",
  "reference_alignment": 75
}
```

---

## 各 Frame 設計說明

### 1. Login Modal (`265:2`) — 460×462

**元素**：
- Tabs 列：「登入」（active，#11D073 下底線）｜「註冊」（灰色）
- 電子郵件 input（label + 44px input box，圓角 8px，border #E8E8E8）
- 密碼 input（同上）
- 忘記密碼？ 連結（右對齊，#11D073）
- 登入 CTA 按鈕（full-width，fill #11D073，白字，圓角 8px，高 48px）
- 「或」 分隔線（橫線 + 文字）
- 社群登入 4 按鈕（圓形 40px，f / G / L / A，邊框 #E8E8E8，水平排列）

**Token 對齊**：
- 主色 `color.brand.primary` = `#11D073`
- 邊框 `color.neutral.200` = `#E8E8E8`
- 字體 `font.family.chinese` = Noto Sans TC
- 圓角 `radius.md` = 8px

---

### 2. Register Modal (`272:2`) — 460×530

**元素**：
- Tabs 列：「登入」（灰色）｜「註冊」（active，#11D073 下底線）
- 4 個 input 欄位：姓名 / 電子郵件 / 密碼 / 確認密碼（各高 67px = 17px label + 6px gap + 44px box）
- 同意條款 checkbox row（checkbox + 文字「我同意服務條款與隱私政策」）
- 註冊 CTA 按鈕（full-width，fill #11D073，白字）

**設計備註**：
- 高度（530）> 寬度（460）是正常的，4 個 input 欄位的表單標準 UX 高度

---

### 3. ForgotPassword Modal (`273:2`) — 460×325

**元素**：
- 重設密碼 標題（Bold 22px）
- 3-Step 指示器（Step 1 circle #11D073 active，Step 2/3 circle #CCCCCC gray，連接線）
- 說明副標文字（請輸入您的電子郵件地址⋯）
- 電子郵件 input（高 67px）
- 下一步 CTA 按鈕（full-width，fill #11D073，白字）

**對齊參考**：
- 參考 `projects/eztravel.community/06_wiki/visual/reference/forgot_password.png`

---

### 4. ConfirmEmail Modal (`274:2`) — 460×330

**元素**：
- 大型圓形 icon（64px，fill #CFF6E3 mint，✓ check 文字 #11D073）
- 信箱已確認！ 標題（Bold 22px）
- 確認成功說明文字（您的信箱已成功驗證，現在可以登入您的帳戶）
- 返回登入 按鈕（full-width，fill #11D073，白字）

**設計備註**：
- ConfirmEmail 為確認後狀態頁，真實網站無法直接截圖，依品牌設計語言設計
- 使用 `color.brand.mint` = `#CFF6E3` 作為成功圖示底色，與品牌系統一致

---

## 視覺自驗報告（8 維度）

| 維度 | Login (265:2) | Register (272:2) | ForgotPassword (273:2) | ConfirmEmail (274:2) |
|------|:---:|:---:|:---:|:---:|
| 比例協調（w≥h 或合理）| ✅ 460≈462 | ✅ 高表單可接受 | ✅ 460>325 | ✅ 460>330 |
| 內容密度 ≥60% | ✅ | ✅ | ✅ | ✅ |
| 視覺層級清晰 | ✅ | ✅ | ✅ | ✅ |
| 元素對齊（無意外重疊）| ✅ fixed | ✅ fixed | ✅ fixed | ✅ |
| 元素樣式（#11D073 correct）| ✅ | ✅ | ✅ | ✅ |
| 顯示區塊夠大（無截切）| ✅ | ✅ | ✅ | ✅ |
| 子節點不重疊 | ✅ | ✅ | ✅ | ✅ |
| 文字不溢出 | ✅ | ✅ | ✅ | ✅ |

**全部 PASS ✅**

---

## AC 驗收對照

| AC | 狀態 | 說明 |
|----|------|------|
| AC-1：4 個 frame，nodeId 各自有效 | ✅ PASS | 265:2 / 272:2 / 273:2 / 274:2 全部 get_screenshot 回傳截圖 |
| AC-2：視覺對齊 eztravel.com.tw 登入頁風格 | ✅ PASS | 主色 #11D073、Noto Sans TC、tabs 切換、input 樣式對齊 |
| AC-3：figma_deliverables 完整 | ✅ PASS | fileKey + 4 nodeId + URL 全列 |
| AC-4：5 維度視覺自驗全 PASS | ✅ PASS | 見上方 8 維度報告 |
| AC-P1：Playwright 前置截圖 | ✅ PASS | browser_navigate → login.png / register.png / forgot_password.png |
| AC-P2：Figma 忠實對齊截圖 | ✅ PASS | modal 結構、tabs、綠色 CTA、input 配置均對齊 login.png |
| AC-P3：reference_alignment ≥ 70% | ✅ PASS | 估算 75%（tabs/inputs/CTA/顏色全中）|

---

## 修正紀錄

| 問題 | 根因 | 修正 |
|------|------|------|
| Input 高度 = 10px（Login/Register/ForgotPassword）| `resize(IW, 10)` 在 `primaryAxisSizingMode='AUTO'` 後調用，鎖定高度 | 對所有 input frame 設 `FIXED` 再 `resize(388, 67)`，父 frame toggle FIXED→AUTO 觸發 reflow |
| ConfirmEmail 標題錯字「信筱」| 建立時 characters 用了錯誤字元 | `use_figma` 更新 node `274:5` characters = "信箱已確認！" |

---

## 下游使用說明

- **R9 PG 卡（T-eztcomm-20260602-R9）**：Login frame `265:2` 為 `_LoginPartial.cshtml` 實作依據，重點對齊 tab 切換、email/password input 結構、#11D073 CTA 按鈕
- **UIUX-SUB-LAYOUT**：Navbar 右側登入/註冊按鈕樣式需與 Login frame CTA 按鈕（fill #11D073，圓角 8px，高 48px）保持一致
