# W1 data 完整性驗證報告

> Owner: admin (代 QA 直接撰寫,QA worker context window 爆)
> Date: 2026-06-01 (TST)
> Task: T-eztcomm-20260601-W1-AQ-1

## 7 頁 audit 結果

| 分類 | 狀態 | 細節 |
|------|------|------|
| homepage | ✅ PASS | sections=13 | shot=1266KB | images=14 | issues=none |
| 機票 | ✅ PASS | sections=6 | shot=1435KB | images=50 | issues=none |
| 旅館 | ✅ PASS | sections=7 | shot=4936KB | images=36 | issues=none |
| 團體 | ✅ PASS | sections=5 | shot=1369KB | images=12 | issues=none |
| 自由行 | ✅ PASS | sections=6 | shot=2630KB | images=48 | issues=none |
| 票券 | ✅ PASS | sections=7 | shot=2093KB | images=37 | issues=none |
| 景點 | ✅ PASS | sections=7 | shot=2360KB | images=25 | issues=none |

## 總結

- PASS: 7/7
- WARN: 0/7
- FAIL: 0/7

## 驗證項目
- JSON parse OK + sections >= 3 + 每 section 有 id/type
- screenshot.png >= 200 KB
- images/ >= 5 圖
