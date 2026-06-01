---
task_id: T-eztcomm-20260602-W4-AQ-2
parent_task: T-eztcomm-20260601-W4-AQ-1
phase: QA
generated_at: 2026-06-02T07:50:00+08:00
generated_by: admin-relay
wiki_target: 06_wiki/05_qa_report.md
---

# W4-AQ-2 重驗報告 — T-eztcomm-20260602-W4-AQ-2

## 執行摘要

| 項目 | 結果 |
|------|------|
| 驗收任務 | T-eztcomm-20260602-W4-AQ-2 |
| 修復 commit | 8e75a53 |
| 測試範圍 | TC-01 ~ TC-06（curl + Python urllib + dotnet run） |
| 環境 | ASPNETCORE_ENVIRONMENT=Development，InMemory DB，種子 3 筆 Product |
| AC-5（本機可運作）| ✅ **達標** |
| TC 全 PASS | **6 / 6** ✅ |

---

## 一、TC 執行結果

| TC | 標題 | 狀態 | HTTP | 關鍵證據 |
|----|------|------|------|---------|
| TC-01 | 首頁可正常載入 | ✅ PASS | 200 | body 含 eztravel 品牌文字 |
| TC-02 | 分類頁顯示商品列表 | ✅ PASS | 200 | /category/flight 成功載入 data/機票.json |
| TC-03 | 商品詳情頁顯示社群區塊 | ✅ PASS | 200 | body 含 class="community-module" |
| TC-04 | 已登入使用者可送出留言 | ✅ PASS | 201 | review id=1 建立，userId 確認 |
| TC-05 | 評論列表 API 可查詢 | ✅ PASS | 200 | `{items:[1], total:1, page:1}` |
| TC-06 | 未登入無法送出留言 | ✅ PASS | **401** | 非 302（BUG-006 修復確認）|

---

## 二、修復驗證對照

| Bug | 嚴重度 | 修復方式 | 驗證 TC | 結果 |
|-----|--------|---------|---------|------|
| BUG-001 | CRITICAL | 建立 `_LoginPartial.cshtml` | TC-01~06 | ✅ 全站不再 500 |
| BUG-002 | HIGH | PageDataLoader 路徑 5→3 層 | TC-02 | ✅ 分類頁 200 |
| BUG-003 | HIGH | 移除重複 /health MapGet | 間接 | ✅ build 0 error |
| BUG-004 | HIGH | InMemory DB + 種子資料 | TC-03, TC-04 | ✅ product/detail/1 200, review 201 |
| BUG-005 | MEDIUM | test_cases.json 路由修正 | TC-02~06 | ✅ 規格與實作一致 |
| BUG-006 | MEDIUM | ConfigureApplicationCookie → 401 | TC-06 | ✅ 401 而非 302 |

---

## 三、AC 對照矩陣

| AC | 達標 | 說明 |
|----|------|------|
| AC-W4AQ2-01：6/6 PASS | ✅ | |
| AC-W4AQ2-02：TC-06 回 401 | ✅ | curl 回傳 401 Unauthorized |
| AC-W4AQ2-03：TC-03 community-module | ✅ | grep 3 matches |
| AC-W4AQ2-04：TC-05 items+total | ✅ | total=1 items=1 |
| AC-W4AQ2-05：wiki_draft 完整 | ✅ | 本文件 |

**W4 AC-5（本機可運作）：✅ 達標**

---

## 四、W5 前置需求

W4 驗收通過，下一步為 W5 部署階段。以下為使用者行動項目：

| 項目 | 說明 | 負責方 |
|------|------|--------|
| W5-ADMIN-1 | `gcloud auth login` — GCP Cloud SQL / Artifact Registry 授權 | 使用者 |
| W5-ADMIN-2 | 建立 GitHub repo，提供 PAT 或 deploy key | 使用者 |

---

**結論：W4 AC-5 ✅ 達標。6/6 TC PASS。可啟動 W5 GCP 部署流程。**

[TASK_DONE]
