# UIUX Figma MCP 診斷探針報告

**任務 ID**：T-eztcomm-20260601-UIUX-FIGMA-PROBE  
**執行時間**：2026-06-02  
**執行者**：uiux agent  
**目的**：驗證 figma-remote-mcp 工具可用性與 Figma 檔案存取權限

---

## 步驟 1：工具清單（mcp__figma-remote-mcp__*）

狀態：**TOOL_LIST_PRESENT**（共 18 個，全為 deferred，需 ToolSearch 載入 schema 後可呼叫）

| # | 工具名稱 |
|---|---------|
| 1 | mcp__figma-remote-mcp__add_code_connect_map |
| 2 | mcp__figma-remote-mcp__create_new_file |
| 3 | mcp__figma-remote-mcp__generate_diagram |
| 4 | mcp__figma-remote-mcp__generate_figma_design |
| 5 | mcp__figma-remote-mcp__get_code_connect_map |
| 6 | mcp__figma-remote-mcp__get_code_connect_suggestions |
| 7 | mcp__figma-remote-mcp__get_context_for_code_connect |
| 8 | mcp__figma-remote-mcp__get_design_context |
| 9 | mcp__figma-remote-mcp__get_figjam |
| 10 | mcp__figma-remote-mcp__get_libraries |
| 11 | mcp__figma-remote-mcp__get_metadata |
| 12 | mcp__figma-remote-mcp__get_screenshot |
| 13 | mcp__figma-remote-mcp__get_variable_defs |
| 14 | mcp__figma-remote-mcp__search_design_system |
| 15 | mcp__figma-remote-mcp__send_code_connect_mappings |
| 16 | mcp__figma-remote-mcp__upload_assets |
| 17 | mcp__figma-remote-mcp__use_figma |
| 18 | mcp__figma-remote-mcp__whoami |

---

## 步驟 2：whoami 呼叫結果

**狀態**：✅ 成功

**原文回應**：
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

**解讀**：
- 認證帳號：`ai.macisk`（ai.macisk@gmail.com）
- 主要 team：`ai macisk's team`，席位 Full / tier pro / seat_type expert → **具備讀寫設計稿的完整權限**
- 次要 team：`閔傑`，席位 View / tier starter → 只讀權限

---

## 步驟 3：get_metadata 呼叫結果

**呼叫參數**：`fileKey="6XmYJOpiSXab2gtGlmWtks"`（無 nodeId，取頂層 pages）

**狀態**：✅ 成功

**原文回應**：
```
No nodeId was provided. Listing the top-level pages of the document.
Call get_metadata again with one of the page ids below (or any node id underneath)
to get the XML metadata for that subtree.

Top-level pages of the document:
- 0:1: Tokens
```

**解讀**：
- fileKey `6XmYJOpiSXab2gtGlmWtks` 可存取，對應一個 Figma 設計檔
- 目前該檔只有一個頂層 page：`Tokens`（pageId = `0:1`）
- 後續若需讀取詳細層級，呼叫 `get_metadata(fileKey=..., nodeId="0:1")` 即可取得完整 XML

---

## 卡片狀態備註

進場時查詢 `projects/eztravel.community/.agent_system/cards/T-eztcomm-20260601-UIUX-FIGMA-PROBE/` 發現**卡本體不存在**（可能由 admin 直派未建卡）。依任務指示完成診斷後標記完成。

---

## 結論

| 檢驗項目 | 結果 |
|---------|------|
| Figma MCP 工具可見 | ✅ 18 個 deferred tool 全可見 |
| ToolSearch 載入 schema | ✅ whoami + get_metadata 成功載入 |
| whoami 認證有效 | ✅ ai.macisk / pro tier / Full seat |
| fileKey 6XmYJOpiSXab2gtGlmWtks 可存取 | ✅ 回傳 page 清單（1 page：Tokens） |
| figma-remote-mcp 整體可用性 | ✅ **全通，可用於後續 UIUX 設計任務** |
