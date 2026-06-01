# {{ProjectName}} — DevOps 規劃 (devops.md)

> **Owner**: AT agent
> **Phase**: ARCHITECTURE
> 由 AT 撰寫,涵蓋 DevOps 4 子塊(原始碼控管 / 自動佈署 / 錯誤回報 / 修復發布)。

---

## §0 部署目標宣告

(AT 填寫:本專案部署目標為何 — GCP Cloud Run / Azure / on-prem / 多目標)

---

## §0.X 基底專案實作 checklist (2026-05-26 使用者明定)

對齊 [memory: project_at_implements_baseline_project]

### 階段 A — 必跑 (專案起始強制)

- [ ] 基底專案 `04_src/` 含 csproj / Program.cs / Dockerfile / docker-compose.yml / launchSettings.json
- [ ] 預留分層空殼 (Controllers / Services / Repositories) **不含業務功能**
- [ ] 可運行驗收 — ai.factory 開發環境: `dotnet run` 或 `docker compose up` 不報錯
- [ ] 可運行驗收 — 需佈署環境: 本機 IIS / Docker / systemd 啟動成功
- [ ] 含配套 1: **原始碼控管** — git init + `.gitignore` + branch 策略 + worktree 配置
- [ ] 含配套 2: **佈署環境** — Dockerfile / docker-compose 本機可跑
- [ ] 含配套 3: **Log 規劃** — Serilog + Console sink + Severity 分級 (對齊 §3)
- [ ] 含配套 4: **代理設定** — `../global_registry.json` `reverse_proxy` 欄位註冊, apphost YARP routing 可代理 `/{short_name}/...`

### 階段 B — 使用者觸發 (關鍵字「佈署雲端」/「上雲」/「Cloud Run」/「Azure App」)

- [ ] 兼容 ai.factory + 雲端的 Dockerfile (同份 image 雙環境可跑)
- [ ] `appsettings.{Cloud}.json` 雲端環境配置
- [ ] Serilog 雙 sink — 本機 Console (純文字) + 雲端 Console (JSON stdout-first)
- [ ] 雲端 endpoint 連線驗證 (Cloud Run URL `/health` 200)
- [ ] 對齊 [memory: project_dotnet_gcp_serilog_stdout]

### 階段 C — 使用者觸發 (關鍵字「DevOps」/「CICD」/「pipeline」/「監看」)

- [ ] GitHub Actions yaml (對齊 skill `dotnet-cicd-builder-github-gcp` §3)
- [ ] Cloud Monitoring alert policy + Notification Channel (對齊 §3.6)
- [ ] 多環境分支策略 (dev/stage/prod 對應分支)
- [ ] 新 endpoint: `/health` `/metrics`
- [ ] 新 IAM: service account + minimum role
- [ ] 新 secret: Cloud Secret Manager 註冊

---

## §1 原始碼控管 (Source Control)

| 項目 | 規範 |
|------|------|
| Git repo 結構 | (待填) |
| Branch 策略 | (待填:GitFlow / Trunk-based / Env-branch) |
| Worktree 配置 | 對齊 ai.factory [memory: project_pg_worktree_discipline](file:///c%3A/Users/micch/.claude/projects/d--Projects-ai-factory/memory/project_pg_worktree_discipline.md) |
| Commit 規範 | (待填:Conventional Commits / 自訂) |
| PR / Code Review | (待填) |
| `.gitignore` 必含 | bin/ obj/ .vs/ *.user appsettings.Local.json |

---

## §2 自動佈署 (Auto Deployment)

### §2.1 部署目標
- **雲端**: (GCP Cloud Run / Azure Container Apps / 其他)
- **地端**: (Docker Compose / IIS / systemd / 其他)

### §2.2 CI/CD Pipeline
- **觸發**: 哪個 branch 觸發哪個環境部署
- **階段**: build → test → image scan → push → deploy → smoke test
- **Artefacts**: container image / nupkg / static files
- **Secret 管理**: 雲端 Secret Manager / GitHub Secrets
- **Rollback**: revision pinning / blue-green / canary

### §2.3 環境策略
- **dev** 對應 dev branch
- **stage** 對應 stage branch
- **prod** 對應 main branch

(對齊 dotnet-cicd-builder-github-gcp skill §2「多環境分支策略」)

---

## §3 錯誤回報 (Error Reporting / Observability)

### §3.1 Log Stack 選型

(AT 依部署目標填寫:Cloud Logging / Loki / ELK / Datadog / 本機檔案)

### §3.2 .NET on GCP 強制紀律 — Serilog + stdout JSON

**若本專案部署目標含 GCP**, 必須遵守 [memory: project_dotnet_gcp_serilog_stdout](file:///c%3A/Users/micch/.claude/projects/d--Projects-ai-factory/memory/project_dotnet_gcp_serilog_stdout.md):

**必要 NuGet 套件**:
- `Serilog.AspNetCore`
- `Serilog.Formatting.Compact`
- `Serilog.Enrichers.Environment`
- `Serilog.Enrichers.Span`

**Program.cs 必要 boot 配置**:
```csharp
builder.Host.UseSerilog((ctx, services, lc) => lc
    .ReadFrom.Configuration(ctx.Configuration)
    .Enrich.FromLogContext()
    .Enrich.WithEnvironmentName()
    .Enrich.WithSpan()
    .WriteTo.Console(new Serilog.Formatting.Compact.RenderedCompactJsonFormatter()));
```

**Cloud Run env**:
```
ASPNETCORE_FORWARDEDHEADERS_ENABLED=true
```

### §3.3 Severity 分級規範 (給 PG)

| Serilog Level | Cloud Logging | 業務情境 | 範例 |
|--------------|--------------|---------|------|
| Verbose | DEBUG | trace/method 進出 (僅 dev) | `Log.Verbose("enter {Method}", nameof(X))` |
| Debug | DEBUG | 變數內容 / SQL | `Log.Debug("SQL: {Sql}", sql)` |
| Information | INFO | 業務事件 | `Log.Information("user {UserId} logged in", uid)` |
| Warning | WARNING | 可恢復異常 (retry 成功) | `Log.Warning(ex, "retry {N}/{Max}", n, max)` |
| Error | ERROR | 業務失敗 | `Log.Error(ex, "failed {Service}", svc)` |
| Fatal | CRITICAL | 服務不可用 | `Log.Fatal(ex, "cannot connect {Conn}", conn)` |

### §3.4 PG 強制紀律 (寫進 PG 卡 AC)

PG 開發**任何** service / controller / repository / background task 時:

1. **必須用 Serilog**,禁 `Console.WriteLine`
2. **必須 structured log** (用 `{Placeholder}` 不可字串拼接)
3. **必須對應 Severity 與業務語意** (見 §3.3 表)
4. **必須帶 trace ID** (`LogContext.PushProperty("RequestId", ...)`)
5. **必須過濾 PII** (不 log 密碼 / token / 信用卡號)
6. **例外處理必須 retry-aware** (對齊 [memory: feedback_three_retry_on_error](file:///c%3A/Users/micch/.claude/projects/d--Projects-ai-factory/memory/feedback_three_retry_on_error.md))

```csharp
// ✅ 正確範例
try { await service.DoWork(payload); }
catch (RetryableException ex) {
    Log.Warning(ex, "retryable failure in {Op}", nameof(DoWork));
    throw;  // 上層 retry
}
catch (Exception ex) {
    Log.Error(ex, "unexpected failure in {Op} payload={@Payload}", nameof(DoWork), payload);
    throw;
}

// ❌ 錯誤範例
Console.WriteLine("user " + userId + " failed");  // 不可
Log.Error("user " + userId + " failed: " + ex.Message);  // 字串拼接不可
Log.Information("login {User} pw {Password}", user, password);  // PII 露出不可
```

### §3.5 API 查詢能力
- **要求**: log backend 必須提供 query API (REST/SDK)
- **Cloud Logging**: ✅ REST + gRPC + .NET SDK + LQL
- **本機檔案**: ❌ 無 API → production 不可用

### §3.6 主動通知管道分級

| Severity | 通知管道 |
|---------|---------|
| DEBUG / INFO | 不通知 (僅 log) |
| WARNING | Slack #monitoring (低優先) |
| ERROR | TG + Slack (中優先) |
| CRITICAL / FATAL | TG + Email + PagerDuty (24/7 oncall) |

### §3.7 成本控制
- production 設 `MinimumLevel.Information`(關 Trace/Debug)
- Log Exclusion 過濾 `/health` access log
- Retention 30 天內免費(預設)

---

## §4 修復發布 (Fix Release)

### §4.1 Hotfix 流程
(待填)

### §4.2 版本號規範
(待填:semver / 自訂)

### §4.3 Release Notes
(待填)

### §4.4 PENDING_RESTART 累記卡機制
對齊 ai.factory [memory: feedback_restart_needed_accumulator_card](file:///c%3A/Users/micch/.claude/projects/d--Projects-ai-factory/memory/feedback_restart_needed_accumulator_card.md)

---

## §5 QA 驗證 AC

QA 卡必驗:
- [ ] Serilog 規範 lint 通過(grep 無 `Console.WriteLine`)
- [ ] 無字串拼接 log(grep `Log.\w+\(".*"\s*\+`)
- [ ] 無 PII 露出(grep password / token / credit_card 對應 log 行)
- [ ] log 在 Cloud Logging API 可查詢
- [ ] Alert 觸發鏈端到端驗證

---

## 對齊的 ai.factory memory

- [memory: project_dotnet_gcp_serilog_stdout](file:///c%3A/Users/micch/.claude/projects/d--Projects-ai-factory/memory/project_dotnet_gcp_serilog_stdout.md)
- [memory: project_release_location_by_type](file:///c%3A/Users/micch/.claude/projects/d--Projects-ai-factory/memory/project_release_location_by_type.md)
- [memory: feedback_three_retry_on_error](file:///c%3A/Users/micch/.claude/projects/d--Projects-ai-factory/memory/feedback_three_retry_on_error.md)
- [memory: feedback_comm_observability](file:///c%3A/Users/micch/.claude/projects/d--Projects-ai-factory/memory/feedback_comm_observability.md)

## 參考 skill

- [dotnet-cicd-builder-github-gcp](file:///c%3A/Users/micch/.claude/skills/dotnet-cicd-builder-github-gcp/SKILL.md)
- [dotnet-project-creator](file:///c%3A/Users/micch/.claude/skills/dotnet-project-creator/SKILL.md)
