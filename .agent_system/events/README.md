# events/ — Agent 事件流匯流排

> 平輩制下,**所有 factory agent + admin** 皆可寫入事件,記錄任務生命週期的關鍵節點。
> 對齊 `agents/CHARTER.md` §7「事件紀律」與 §8「卡片紀律」。

## 命名規則

- `{ISO_timestamp}_{agent}_{type}.json`
- `ISO_timestamp` 採 `YYYY-MM-DDTHH-mm-ss`(避免檔名含 `:`)
- `agent` 採小寫(`admin` / `pm` / `ba` / `uiux` / `at` / `pg` / `qa`)
- 範例:`2026-05-10T16-45-23_pg_completed.json`

## 事件 schema(極簡 JSON)

```json
{
  "ts": "2026-05-10T16:45:23+0800",
  "task_id": "T-20260510-005",
  "agent": "pg",
  "type": "completed",
  "summary": "<一行摘要,< 200 字>",
  "ref": {
    "delivered_files": ["..."],
    "task_board_status": "TODO|IN_PROGRESS|DONE|ARCHIVED|REWORK"
  }
}
```

## 事件類型(平輩制 + 卡片生命週期)

| event_type | 何時寫 | 由誰寫 |
|-----------|------|---------|
| `dispatched` | admin 派工任務時 | admin(派 claude-sandbox-executor 同時或請 agent 進場時補寫) |
| `started` | factory agent 進場改卡 status=IN_PROGRESS 同時 | 該 agent(**強制**) |
| `progress` | 任務跑到關鍵里程碑(可選) | 該 agent(僅在重要節點寫) |
| `query` | agent 用 `[QUERY]` 標籤對 admin 提問 | 該 agent |
| `escalation` | agent 用 `[ESCALATION]` 升級 | 該 agent |
| `completed` | agent 完成填卡 status=DONE 同時 | 該 agent(**強制**) |
| `failed` | 任務無法完成(BLOCKED / FAILED) | 該 agent |
| `archived` | PM 整合進 wiki 並改卡 status=ARCHIVED 時 | PM(掃 DONE 卡 SOP 完成後寫) |

## 重要原則

- 此目錄為 **append-only**(僅新增,不修改、不刪除)
- 每個事件對應 `task_board.json` 內某 `task_id`,形成可追溯鏈
- 違反 append-only 等同竄改歷史
- 寫事件**不替代**卡片更新 — events 是「即時時序快照」,task_board 卡是「最終生命週期狀態」,兩者並存
- agent 完成任務但**沒寫 completed event 或沒填卡** → PM 在掃卡整合時視為 INCOMPLETE,改卡為 REWORK
