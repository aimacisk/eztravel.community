# 04 — 模組結構與編譯指南

> **Author**: PG agent
> **Source**: `04_src/`

## 模組結構

(PG 填寫 — 主要資料夾、命名空間、層級職責)

## 環境配置

(PG 填寫 — runtime 版本、套件管理、環境變數、本機啟動指令)

## 編譯與測試

(PG 填寫 — build 指令、test 指令、lint 指令、預期輸出)

## 常見錯誤與排除

(PG 填寫 — 自帶修復迴圈中常見遇到的編譯/相依錯誤)

---

## DevOps 規範 (CI/CD + 監看 + 錯誤回報)

> 對齊 AT 原則 (project_spec.md §🏛 AT 原則) + dotnet-cicd-builder-github-gcp skill
> 完整參考: ai-factory-relay/06_wiki/promotion/04_design_principles_deep_dive.md

### A. 原始碼控管
- GitFlow: main / uat / develop 常駐分支 + feature/* + hotfix/* 功能分支
- commit message: 動詞+對象 (例: feat: ... / fix: ... / docs: ...)
- 各專案獨立 git repo (memory: project_per_project_git)
- worktree 紀律: PG 開發走 `.worktrees/{tid}` + `feat/{tid}` 分支

### B. 雲端佈署 (GCP Cloud Run)
- 容器化: Dockerfile multi-stage build
- 基建: setup-gcp.sh 一次性建立 Project / IAM / Artifact Registry / Cloud Run
- CI/CD: GitHub Actions deploy.yml 對應分支 (main → prod / stage → staging / dev → dev)
- 必啟用服務 (gcloud CLI):
  - logging.googleapis.com
  - monitoring.googleapis.com
  - clouderrorreporting.googleapis.com
  - run.googleapis.com
  - artifactregistry.googleapis.com

### C. 本地佈署 / 本機開發
- 應用層 (Host/Web/API/Hangfire) 必有 appsettings.{Local,Dev,UAT,Prod}.json + .env.{envName}
- dotenv.net 套件統一載入 env
- .env 嚴禁進 git, .env.example 範本進 git
- 本機啟動: dotnet run --environment Local

### D. 監看機制 / 錯誤回報 (.NET 專案適用)

#### Serilog → Cloud Logging stdout (強制)
所有應用層必用 Serilog + stdout JSON, Cloud Run runtime 自動轉發到 Cloud Logging.

```csharp
builder.Host.UseSerilog((ctx, lc) => lc
    .ReadFrom.Configuration(ctx.Configuration)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .WriteTo.Console(new RenderedCompactJsonFormatter()));
```

#### Severity 6 級 ↔ Cloud Logging 9 級 mapping
| Serilog | Cloud Logging | 使用情境 |
|---------|--------------|---------|
| Trace/Verbose | DEBUG | 細節 (local only) |
| Debug | DEBUG | 開發除錯 |
| Information | INFO | 業務事件 |
| Warning | WARNING | 異常但可繼續 |
| Error | ERROR | 錯誤 / catch 區塊 |
| Fatal/Critical | CRITICAL | 嚴重 + alert + on-call |

#### PG 強制規範
- 必用 message template: `Log.Error(ex, "user {UserId} failed", userId)`
- 嚴禁字串拼接: `Log.Error($"user {userId} failed")`
- 嚴禁 catch swallow: 至少 Log.Warning 或更高
- 嚴禁敏感資訊入 log (密碼 / Token / PII)
- production MinimumLevel = Information (絕不開 Trace/Debug)

#### gcloud CLI 開設 stdout 服務
```bash
# 1. 啟用 API
gcloud services enable logging.googleapis.com monitoring.googleapis.com

# 2. 設 retention (預設 30 天免費)
gcloud logging buckets update _Default --location=global --retention-days=30

# 3. 健康檢查 access log 排除 (省成本)
gcloud logging sinks update _Default \
  --add-exclusion='name=exclude_health,filter=httpRequest.requestUrl=~"/(health|metrics)$"'

# 4. 建 log-based metric (給 alert)
gcloud logging metrics create app_errors \
  --description="App Error log 計數" \
  --log-filter='resource.type="cloud_run_revision" AND severity>=ERROR'

# 5. 查詢 ERROR log
gcloud logging read 'severity>=ERROR AND resource.type="cloud_run_revision"' --limit 50
```

#### API 查詢能力 (必驗)
- log backend 必須提供 API 查詢 (REST / SDK / 查詢語言 LQL)
- 不提供 API 查詢的 backend (純檔案 log) production 禁用
- dashboard / QA / SLO 報表都依賴此能力

#### Trace ID 串接
- Cloud Run 環境變數 ASPNETCORE_FORWARDEDHEADERS_ENABLED=true
- log 帶 logging.googleapis.com/trace + spanId 欄位

#### 成本控制 (Cloud Logging)
- 50 GB/月 ingestion 免費 (小流量 = $0)
- 超過 $0.50/GB ingest + $0.50/GB query
- 控制手段: severity 過濾 + log exclusion + access log 採樣 1%

### E. 修復發布
- PENDING_RESTART 累記卡 (memory feedback_restart_needed_accumulator_card)
- PG 完工標 PENDING_RESTART (非 DONE), 使用者主動 restart 才驗證
- hotfix 流程: hotfix/* 分支 → 通過 review → merge main + stage + develop
- release 版本管理: semver (major.minor.patch), release notes 在 06_wiki/_v*_release_notes.md
