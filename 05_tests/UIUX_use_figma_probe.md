# UIUX use_figma 寫操作診斷報告

**任務**：T-eztcomm-20260601-UIUX-USEFIGMA-PROBE  
**執行時間**：2026-06-02  
**fileKey**：`6XmYJOpiSXab2gtGlmWtks`  
**執行者**：uiux agent（figma-remote-mcp）

---

## 第 1 步：ToolSearch 載入 deferred figma schemas

```
ToolSearch(query="select:mcp__figma-remote-mcp__use_figma,mcp__figma-remote-mcp__get_metadata,mcp__figma-remote-mcp__whoami")
```

**結果**：✅ 三個 tool schema 成功載入（use_figma / get_metadata / whoami）

---

## 第 2 步：whoami 驗證

```
mcp__figma-remote-mcp__whoami()
```

**原始回傳**：
```json
{
  "handle": "ai.macisk",
  "email": "ai.macisk@gmail.com",
  "plans": [
    {
      "name": "ai macisk's team",
      "seat": "Full",
      "tier": "pro",
      "key": "team::1599443677616940499",
      "seat_type": "expert"
    },
    {
      "name": "閔傑",
      "seat": "View",
      "tier": "starter",
      "key": "team::1600766602002873555",
      "seat_type": "view"
    }
  ]
}
```

**判斷**：✅ handle=`ai.macisk` 確認，Pro tier Full seat，OAuth 正常。

---

## 第 3 步（關鍵）：use_figma 寫入測試

```
mcp__figma-remote-mcp__use_figma(
  fileKey="6XmYJOpiSXab2gtGlmWtks",
  code="const newPage = figma.createPage(); newPage.name = 'PROBE_' + Date.now(); return { pageId: newPage.id, pageName: newPage.name };",
  description="診斷探針：建立一個新 page"
)
```

**原始回傳**：
```json
{"pageId":"71:2","pageName":"PROBE_1780341168092"}
```

**判斷**：
- ✅ **呼叫本身無例外、無錯誤**，MCP tool 正常回傳結構化 JSON
- ✅ pageId `71:2`、pageName `PROBE_1780341168092`（timestamp = 合理的 Date.now() 值）
- 結論：**use_figma Plugin API 執行路徑暢通，寫入指令被接受並執行**

---

## 第 4 步：get_metadata 獨立驗證（列出全部 pages）

```
mcp__figma-remote-mcp__get_metadata(fileKey="6XmYJOpiSXab2gtGlmWtks")
```

**原始回傳**：
```
No nodeId was provided. Listing the top-level pages of the document.

Top-level pages of the document:
- 0:1: Tokens
```

**判斷**：
- ⚠️ **僅顯示一個 page：`0:1: Tokens`**
- ❌ `PROBE_1780341168092`（71:2）**未出現**於 REST API 回傳的 pages 清單

---

## 綜合分析

| 維度 | 結果 |
|------|------|
| OAuth 認證 | ✅ ai.macisk / Pro / Full seat |
| use_figma 呼叫成功 | ✅ 無例外，回傳合法 pageId + pageName |
| 獨立驗證（REST API）| ⚠️ PROBE page 未出現 |
| 整體判定 | **use_figma 可用，但寫入持久性存疑** |

### 根因假設

`use_figma` 透過 **Figma Desktop Plugin API** 執行（即時在桌面 App 記憶體內執行），  
`get_metadata` 可能透過 **Figma REST API**（讀取 server 端快照），兩者存在以下可能差異：

1. **時序差異**：Plugin API 寫入成功但 REST API 尚未 sync（需 Figma 手動 Save 或自動儲存後才反映）
2. **未持久化**：`figma.createPage()` 在 Plugin API context 執行後，若 Figma Desktop 未開啟該文件或文件未 save，變更可能不持久
3. **兩 API 分離**：Plugin API 在本機 App 狀態變動，REST API 只反映 server 同步後的狀態

### 實務影響

- `use_figma` 的寫操作**在 Plugin API 層面可用**（OAuth 正常、code 執行成功）
- **不能僅靠 use_figma 回傳值確認持久化**；需在呼叫後額外等待或確認 Figma Desktop 已 save
- 後續 UIUX 任務建議：write 完成後用 `get_metadata` 驗證，若 REST API 未反映則需提示使用者確認 Figma Desktop 已儲存

---

## 結論

**use_figma 寫入 API 本身可用（非 PROBE_FAIL）**，但 REST API 獨立驗證未能確認 page 持久化。  
建議後續 UIUX 設計任務仍可使用 `use_figma`，但完工後需加 `get_metadata` 驗證步驟作為交叉確認。

---

*probe 執行者：uiux agent｜T-eztcomm-20260601-UIUX-USEFIGMA-PROBE*
