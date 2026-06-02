# Eztravel.Community — DevOps 規劃 (devops.md)

> **Owner**: AT agent  
> **Phase**: ARCHITECTURE  
> 由 AT 撰寫，涵蓋 DevOps 4 子塊（原始碼控管 / 自動佈署 / 錯誤回報 / 修復發布）。  
> **更新日期**: 2026-06-01  
> **對應設計規格**: docs/superpowers/specs/2026-06-01-eztravel-community-rebuild-design.md §2.2~2.3, §5

---

## §0 部署目標宣告

本專案部署目標為 **GCP Cloud Run + Cloud SQL PostgreSQL**，採雙環境策略：

| 環境 | 目標 | 描述 |
|------|------|------|
| **開發環境** | Docker Compose (本機) | ai.factory 開發環境，啟動本機 PostgreSQL 容器 |
| **生產環境** | GCP Cloud Run + Cloud SQL | 雲端運行環境，完整託管資料庫與應用容器 |

---

## §0.X 基底專案實作 Checklist (2026-05-26 使用者明定 — 階段 A 必跑 + 階段 B 已授權)

對齊 [memory: project_at_implements_baseline_project](../../memory/project_at_implements_baseline_project.md)

### 階段 A — 必跑 (專案起始強制) ✅

- [x] 基底專案 `04_src/` 含 csproj / Program.cs / Dockerfile / docker-compose.yml / launchSettings.json
- [x] 預留分層空殼 (Controllers / Services / Repositories) **不含業務功能**
- [x] 可運行驗收 — ai.factory 開發環境: `dotnet run` 或 `docker compose up` 不報錯
- [x] 可運行驗收 — 需佈署環境: 本機 IIS / Docker / systemd 啟動成功
- [x] 含配套 1: **原始碼控管** — git init + `.gitignore` + branch 策略 + worktree 配置
- [x] 含配套 2: **佈署環境** — Dockerfile / docker-compose 本機可跑
- [x] 含配套 3: **Log 規劃** — Serilog + Console sink + Severity 分級 (對齊 §3)
- [x] 含配套 4: **代理設定** — `../global_registry.json` `reverse_proxy` 欄位註冊, apphost YARP routing 可代理

### 階段 B — 已授權 (關鍵字「佈署雲端」/「上雲」/「Cloud Run」) ✅

- [x] 兼容 ai.factory + 雲端的 Dockerfile (同份 image 雙環境可跑)
- [x] `appsettings.Production.json` 雲端環境配置 (Cloud SQL Unix socket)
- [x] Serilog 雙 sink — 本機 Console (純文字) + 雲端 Console (JSON stdout-first)
- [x] 雲端 endpoint 連線驗證 (Cloud Run URL `/health` 200)
- [x] 對齊 [memory: project_dotnet_gcp_serilog_stdout](../../memory/project_dotnet_gcp_serilog_stdout.md)

---

## §1 原始碼控管 (Source Control)

### §1.1 Git Repository 結構

```
projects/eztravel.community/
├── 04_src/                              # 應用層原始碼 repo
│   ├── .git/                            # 獨立 git repo (GitHub remote)
│   ├── .gitignore                       # 標準 .NET ignore rules
│   ├── eztravel.Community.sln           # Visual Studio Solution
│   ├── eztravel.Community.Web/          # ASP.NET MVC 主專案
│   ├── eztravel.Community.Core/         # Business entities + Interfaces
│   ├── eztravel.Community.Infrastructure/ # EF Core DbContext + Repositories
│   ├── eztravel.Community.Tests/        # xUnit 單元測試 + 整合測試
│   ├── Dockerfile                       # Multi-stage build for linux/amd64
│   ├── docker-compose.yml               # 本機開發環境
│   ├── .github/workflows/               # GitHub Actions
│   │   └── release.yml                  # [release] commit trigger
│   ├── appsettings.json                 # 預設設定
│   ├── appsettings.Development.json     # 本機開發環境
│   └── appsettings.Production.json      # 雲端生產環境
├── .gitignore                           # 根層 .gitignore
└── (其他架構、資料、設計檔案)
```

### §1.2 Branch 策略

採 **Trunk-based** 工作流，搭配 ai.factory Worktree 紀律：

| Branch | 用途 | 部署目標 |
|--------|------|---------|
| `main` | 主幹，永遠 production-ready | Cloud Run prod (自動部署) |
| `feat/{tid}` | 功能分支，worktree 隔離開發 | 無 (本機驗證) |
| `dev` | (預留) 開發分支 | (預留) Cloud Run dev |

**Commit 規範**:
- 日常開發: `{ComponentName}: {Description}` (e.g., `ReviewController: add reply feature`)
- 發布提交: `[release] {Message}` (e.g., `[release] Community Module v1.0`) — 此類 commit 觸發 GitHub Actions CI/CD

### §1.3 Worktree 配置

對齊 ai.factory [memory: project_pg_worktree_discipline](../../memory/project_pg_worktree_discipline.md):

```bash
# PG 進場
cd projects/eztravel.community
git worktree add ".worktrees/{task_id}" --track origin/main

# 在 worktree 內開發
cd ".worktrees/{task_id}/04_src"
git checkout -b "feat/{task_id}"
# ... dotnet run, develop, test ...
git add . && git commit -m "..."

# 完工後（由 dispatch 執行）
cd projects/eztravel.community
git -C ".worktrees/{task_id}/04_src" rebase main
git -C ".worktrees/{task_id}/04_src" checkout main
git -C ".worktrees/{task_id}/04_src" merge --ff-only feat/{task_id}
git worktree remove ".worktrees/{task_id}"
```

### §1.4 .gitignore 必含規則

```
# .NET
bin/
obj/
*.dll
*.exe
*.pdb
*.nupkg
*.user
*.suo

# IDE
.vs/
.vscode/
*.code-workspace

# 環境
appsettings.Local.json
.env
.env.local

# 臨時
*.tmp
node_modules/
```

---

## §2 自動佈署 (Auto Deployment)

### §2.1 部署流程架構

```
┌─────────────────────────────────────────────────────────┐
│  開發者 push [release] commit 到 GitHub (main branch)   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │ GitHub Actions Workflow  │
         │ (.github/workflows/release.yml)
         └──────────────────────────┘
                     │
      ┌──────────────┬──────────────┐
      │              │              │
      ▼              ▼              ▼
   Build        Unit Test      Build Image
   dotnet       xUnit          docker build
      │              │              │
      └──────────────┴──────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │  Push to Artifact        │
         │  Registry (GCP)          │
         └──────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │  Deploy to Cloud Run     │
         │  + Schema Migration      │
         └──────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │  Smoke Test              │
         │  GET /health → 200       │
         └──────────────────────────┘
```

### §2.2 CI/CD Pipeline 階段

**Trigger 條件**:
```yaml
on:
  push:
    branches: [main]
    # 檢測 commit message 是否含 [release]
```

**Pipeline 階段**:

| 階段 | 動作 | 時長 |
|------|------|------|
| **Checkout** | 取得原始碼 | ~ 5s |
| **Setup .NET** | 安裝 .NET 8 SDK | ~ 30s |
| **Restore** | 還原 NuGet 套件 | ~ 20s |
| **Build** | `dotnet build -c Release` | ~ 60s |
| **Unit Tests** | `dotnet test` (xUnit) | ~ 40s |
| **Docker Build** | 多階段編譯，linux/amd64 | ~ 90s |
| **Push Image** | 推到 Artifact Registry | ~ 20s |
| **Migrate DB** | Cloud SQL schema init | ~ 30s |
| **Deploy** | `gcloud run deploy ...` | ~ 60s |
| **Smoke Test** | GET `/health` | ~ 10s |

**總預估時間**: ~ 365 秒 (6 分鐘)

### §2.3 環境變數與 Secret 注入

GitHub Actions Secrets (由 admin 負責初始化):

```yaml
env:
  GCP_PROJECT_ID: eztcomm-prod-1780402352
  GCP_REGION: asia-east1
  ARTIFACT_REGISTRY_HOST: asia-east1-docker.pkg.dev
  ARTIFACT_REGISTRY_REPO: eztravel-community
  CLOUD_RUN_SERVICE: eztravel-community
  CLOUD_SQL_INSTANCE: projects/eztcomm-prod-1780402352/instances/eztcomm-db
  CLOUD_SQL_CONNECTION_NAME: eztcomm-prod-1780402352:asia-east1:eztcomm-db

secrets:
  GCP_SA_KEY:                  # Service Account JSON 金鑰 (base64)
  DB_PASSWORD:                 # Cloud SQL postgres 密碼
  ASPNETCORE_ENVIRONMENT:      # Production
```

### §2.4 Image Registry 與版本管理

**Artifact Registry 設定**:
- **Host**: `asia-east1-docker.pkg.dev`
- **Project**: `eztcomm-prod-1780402352`
- **Repository**: `eztravel-community`
- **Image Tag**: `{GITHUB_SHA:8}` (前 8 位 commit hash)
- **完整 URI**: `asia-east1-docker.pkg.dev/eztcomm-prod-1780402352/eztravel-community/app:{hash}`

**版本策略**: 
- 每次 `[release]` commit 自動推送新 image
- Cloud Run revision 自動部署最新 image
- 歷史 revision 保留 5 個，超過自動刪除

---

## §3 錯誤回報與可觀測性 (Observability)

### §3.1 Log Stack 選型

**本機開發**:
```csharp
new Serilog.Formatting.Json.JsonFormatter()
// 純文字主控台輸出，供開發者讀取
```

**GCP 生產**:
```csharp
new Serilog.Formatting.Compact.RenderedCompactJsonFormatter()
// stdout JSON 寫至 GCP Cloud Logging，自動聚合與索引
```

### §3.2 .NET on GCP 強制紀律 — Serilog + stdout JSON

**必要 NuGet 套件** (需在 `eztravel.Community.Web.csproj` 已安裝):
- `Serilog.AspNetCore` 
- `Serilog.Formatting.Compact`
- `Serilog.Enrichers.Environment`
- `Serilog.Enrichers.Span`

**Program.cs 必要配置**:
```csharp
using Serilog;
using Serilog.Enrichers.Span;

var builder = WebApplication.CreateBuilder(args);

// Serilog 配置
builder.Host.UseSerilog((ctx, services, lc) => lc
    .ReadFrom.Configuration(ctx.Configuration)
    .Enrich.FromLogContext()
    .Enrich.WithEnvironmentName()
    .Enrich.WithSpan()
    .MinimumLevel.Information()  // Production 關閉 Debug/Trace
    .WriteTo.Console(new Serilog.Formatting.Compact.RenderedCompactJsonFormatter()));

var app = builder.Build();
app.Run();
```

**appsettings.Production.json 配置**:
```json
{
  "Serilog": {
    "MinimumLevel": "Information",
    "Enrich": ["FromLogContext", "WithEnvironmentName", "WithSpan"],
    "WriteTo": [
      {
        "Name": "Console",
        "Args": {
          "formatter": "Serilog.Formatting.Compact.RenderedCompactJsonFormatter"
        }
      }
    ]
  }
}
```

**Cloud Run 環境變數**:
```bash
ASPNETCORE_ENVIRONMENT=Production
ASPNETCORE_FORWARDEDHEADERS_ENABLED=true
```

### §3.3 Serilog Severity 分級規範 (PG 開發紀律)

| Serilog Level | Cloud Logging Level | 業務情境 | 範例 |
|---------------|-------------------|---------|------|
| **Verbose** | DEBUG | 方法進出、追蹤 (僅 dev) | `Log.Verbose("enter {Method}", nameof(GetProduct))` |
| **Debug** | DEBUG | 變數內容、SQL 語句 | `Log.Debug("SQL params: {Params}", params)` |
| **Information** | INFO | 業務事件（登入、建立、修改） | `Log.Information("user {UserId} logged in", uid)` |
| **Warning** | WARNING | 可恢復異常 (retry 成功後) | `Log.Warning(ex, "retry {N}/{Max} succeeded", n, max)` |
| **Error** | ERROR | 業務邏輯失敗 | `Log.Error(ex, "failed to save {Entity} id={Id}", "Review", id)` |
| **Fatal** | CRITICAL | 服務不可用、無法連線 | `Log.Fatal(ex, "cannot connect to {Service}", "CloudSQL")` |

### §3.4 PG 開發強制紀律 (寫入 PG 卡 AC)

**所有** Service / Controller / Repository 開發時必須遵守：

1. **禁止 `Console.WriteLine()`** — 一律使用 `Serilog.Log.{Level}`
2. **必須 Structured Log** — 用 `{Placeholder}` 占位符，不可字串拼接
3. **必須對應 Severity** — 見 §3.3 表，Severity 對應業務語意
4. **必須帶 Trace ID** — `LogContext.PushProperty("RequestId", correlationId)`
5. **必須過濾 PII** — 不 log 密碼 / 驗證碼 / token / 信用卡號
6. **例外處理 Retry-aware** — 區分可重試異常 (Warning) vs 終局異常 (Error)

**正確範例**:
```csharp
public async Task CreateReview(CreateReviewDto dto)
{
    var correlationId = HttpContext.TraceIdentifier;
    using (LogContext.PushProperty("RequestId", correlationId))
    {
        try
        {
            Log.Information("creating review for {ProductId} user={UserId}", 
                dto.ProductId, dto.UserId);
            var review = await _service.CreateReviewAsync(dto);
            Log.Information("review created {ReviewId}", review.Id);
        }
        catch (InvalidOperationException ex) when (ex.Message.Contains("duplicate"))
        {
            Log.Warning(ex, "duplicate review attempt for {ProductId}", dto.ProductId);
            throw;
        }
        catch (Exception ex)
        {
            Log.Error(ex, "unexpected failure creating review {ProductId} {@Dto}", 
                dto.ProductId, dto);
            throw;
        }
    }
}
```

**錯誤範例** ❌:
```csharp
Console.WriteLine("Creating review for " + dto.ProductId);  // ❌ Console
Log.Information("creating review for " + dto.ProductId);     // ❌ 字串拼接
Log.Information("user {User} pwd {Password}", user, pwd);   // ❌ PII 露出
```

### §3.5 GCP Cloud Logging 查詢能力

**優點**: REST API + gRPC + .NET SDK + Logs Query Language (LQL)

**查詢範例** (LQL):
```sql
resource.type="cloud_run_revision"
resource.labels.service_name="eztravel-community"
jsonPayload.Level="Error"
timestamp>="2026-06-01T00:00:00Z"
```

**.NET SDK 查詢** (PG 在本機 debug 時):
```csharp
using Google.Cloud.Logging.V2;
var client = new LoggingServiceV2Client();
var filter = @"resource.type=cloud_run_revision AND 
              resource.labels.service_name=eztravel-community AND
              severity>=ERROR";
var entries = client.ListLogEntries(
    new[] { $"projects/{projectId}" }, 
    filter).ToList();
```

### §3.6 主動通知管道分級

| Severity | 通知管道 | 目的 |
|---------|---------|------|
| DEBUG / INFO | 無 (僅 log) | 開發參考 |
| WARNING | 無 (可選手動檢閱) | 系統自恢復 |
| ERROR | TG + Slack #alerts | 需人工介入，日常時段 |
| CRITICAL / FATAL | TG + Email + PagerDuty | 24/7 oncall，立即處理 |

*(本階段預留，W5-ADMIN-3 階段實施)*

### §3.7 成本控制

- **MinimumLevel**: Production 設 `Information`，關閉 Trace/Debug
- **Log Exclusion**: 過濾 `/health` 無用 access log
- **Retention**: 預設 30 天內免費，超過 90 天自動刪除

---

## §4 修復發布 (Fix Release)

### §4.1 [release] Commit 觸發機制

**Commit Message 規格**:
```
[release] {Service Name} v{SemVer} — {Brief Description}

例:
[release] Eztravel Community v0.1.0 — Initial Community Module release

例:
[release] Fix review comment encoding issue
```

**GitHub Actions 檢測邏輯**:
```yaml
- name: Check for [release] in commit
  id: check_release
  run: |
    if [[ "${{ github.event.head_commit.message }}" =~ \[release\] ]]; then
      echo "release_detected=true" >> $GITHUB_OUTPUT
    fi

- name: Deploy to Cloud Run (conditional)
  if: steps.check_release.outputs.release_detected == 'true'
  run: gcloud run deploy ...
```

### §4.2 版本號規範

採 **Semantic Versioning** (SemVer):
- **MAJOR**: API breaking change (e.g., Review entity 刪除欄位)
- **MINOR**: 新功能向後相容 (e.g., 新增 ReviewLike 功能)
- **PATCH**: Bug fix (e.g., 修正評論編碼問題)

**版本標籤** (Git tag):
```bash
# 發布前由 PG 建立 tag
git tag -a v0.1.0 -m "Initial Community Module release"
git push origin v0.1.0
```

### §4.3 Release Notes

每次 `[release]` commit 需在對應 PR 或 commit message 下方添加簡述，範例:

```
## v0.1.0 - Community Module Initial Release

### Features
- ✨ Review CRUD (Create, Read, Update, Delete)
- ⭐ Rating 1-5 星等支援
- 📸 Review 內嵌照片上傳 (最多 5 張)
- 🔄 Review helpful vote (讚計數)
- 💬 樓主回應 nested comment

### Bug Fixes
- 🐛 Fix Unicode encoding in review text
- 🐛 Fix image upload timeout for large files

### Performance
- ⚡ Add index on Review.ProductId + CreatedAt
- ⚡ Cache rating distribution query (TTL 1 min)
```

### §4.4 PENDING_RESTART 累記卡機制

對齊 ai.factory [memory: feedback_restart_needed_accumulator_card](../../memory/feedback_restart_needed_accumulator_card.md)

**系統維護卡**: `T-eztcomm-MAINT-PENDING-RESTART`

此卡用於累記所有「代碼已提交但服務未重啟就不視為生效」的項目，包括：
- 新 endpoint 增加
- Database schema migration
- 環境變數更改
- Serilog 配置異動

---

## §5 GCP 環境初始化 (Admin Responsibility)

### §5.1 GCP Project 配置

```bash
# 1. 建立 GCP Project
gcloud projects create eztcomm-prod-1780402352 \
  --name="Eztravel Community Production"

# 2. 設定預設 project
gcloud config set project eztcomm-prod-1780402352

# 3. 啟用必要 API
gcloud services enable \
  compute.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  container.googleapis.com \
  cloudresourcemanager.googleapis.com
```

### §5.2 Cloud SQL 實例建立

```bash
# 1. 建立 Cloud SQL 實例
gcloud sql instances create eztcomm-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-east1 \
  --availability-type=zonal \
  --backup-start-time=02:00 \
  --enable-bin-log=false \
  --storage-auto-increase \
  --storage-auto-increase-limit=50

# 2. 建立初始資料庫
gcloud sql databases create eztravel_community \
  --instance=eztcomm-db \
  --charset=UTF8

# 3. 建立 postgres 使用者 (如未自動建立)
gcloud sql users create postgres \
  --instance=eztcomm-db \
  --password=$(openssl rand -base64 16)

# 4. 獲取 Connection Name (用於應用層)
gcloud sql instances describe eztcomm-db \
  --format='value(connectionName)'
# 輸出: eztcomm-prod-1780402352:asia-east1:eztcomm-db
```

### §5.3 Artifact Registry 建立

```bash
# 1. 建立 Docker registry repository
gcloud artifacts repositories create eztravel-community \
  --repository-format=docker \
  --location=asia-east1 \
  --description="Eztravel Community .NET images"

# 2. 設定 Docker auth
gcloud auth configure-docker asia-east1-docker.pkg.dev
```

### §5.4 Service Account 與 IAM

```bash
# 1. 建立 Service Account (用於 GitHub Actions)
gcloud iam service-accounts create github-actions-deployer \
  --display-name="GitHub Actions CI/CD Deployer"

# 2. 授予必要角色
gcloud projects add-iam-policy-binding eztcomm-prod-1780402352 \
  --member=serviceAccount:github-actions-deployer@eztcomm-prod-1780402352.iam.gserviceaccount.com \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding eztcomm-prod-1780402352 \
  --member=serviceAccount:github-actions-deployer@eztcomm-prod-1780402352.iam.gserviceaccount.com \
  --role=roles/artifactregistry.writer

gcloud projects add-iam-policy-binding eztcomm-prod-1780402352 \
  --member=serviceAccount:github-actions-deployer@eztcomm-prod-1780402352.iam.gserviceaccount.com \
  --role=roles/cloudsql.client

# 3. 生成 JSON 金鑰 (供 GitHub Actions 使用)
gcloud iam service-accounts keys create gh-actions-key.json \
  --iam-account=github-actions-deployer@eztcomm-prod-1780402352.iam.gserviceaccount.com

# 4. 將金鑰 base64 編碼並存入 GitHub Secrets
cat gh-actions-key.json | base64 -w 0 > gh-actions-key-b64.txt
# 複製內容到 GitHub Secrets 環境變數 GCP_SA_KEY
```

### §5.5 Cloud Secret Manager 註冊

```bash
# 1. 建立 Secret: Database 密碼
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create db-password \
  --data-file=-

# 2. 建立 Secret: ASP.NET ASPNETCORE_ENVIRONMENT
echo -n "Production" | \
  gcloud secrets create aspnetcore-environment \
  --data-file=-

# 3. 授予 Cloud Run service account 讀權限
gcloud secrets add-iam-policy-binding db-password \
  --member=serviceAccount:eztravel-community@eztcomm-prod-1780402352.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding aspnetcore-environment \
  --member=serviceAccount:eztravel-community@eztcomm-prod-1780402352.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

---

## §6 Cloud Run Service 部署

### §6.1 Service 建立與配置

```bash
# 初次部署 (GitHub Actions 中自動執行)
gcloud run deploy eztravel-community \
  --image=asia-east1-docker.pkg.dev/eztcomm-prod-1780402352/eztravel-community/app:$(git rev-parse --short HEAD) \
  --platform managed \
  --region asia-east1 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60s \
  --min-instances 0 \
  --max-instances 100 \
  --allow-unauthenticated \
  --set-env-vars=ASPNETCORE_ENVIRONMENT=Production,ASPNETCORE_FORWARDEDHEADERS_ENABLED=true \
  --set-secrets=DB_PASSWORD=db-password:latest \
  --add-cloudsql-instances=eztcomm-prod-1780402352:asia-east1:eztcomm-db \
  --service-account=eztravel-community@eztcomm-prod-1780402352.iam.gserviceaccount.com \
  --no-gen2 \
  --port 8080
```

### §6.2 Cloud Run 環境變數注入

**appsettings.Production.json 中讀取的環境變數**:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=/cloudsql/eztcomm-prod-1780402352:asia-east1:eztcomm-db;Database=eztravel_community;User Id=postgres;Password=${DB_PASSWORD};"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning"
    }
  }
}
```

**Program.cs 中注入機制**:
```csharp
var connStr = configuration.GetConnectionString("DefaultConnection");
// Cloud SQL Unix socket 自動透過 --add-cloudsql-instances 參數設置
// 應用層直接使用 Npgsql 連線字串
services.AddDbContext<ApplicationDbContext>(opts =>
    opts.UseNpgsql(connStr));
```

### §6.3 Health Check Endpoint

**必須實作 `/health` endpoint** (供 Cloud Run liveness probe):

```csharp
app.MapGet("/health", async (IApplicationDbContext db) =>
{
    try
    {
        await db.Database.ExecuteSqlAsync($"SELECT 1;");
        return Results.Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
    }
    catch (Exception ex)
    {
        Log.Error(ex, "health check failed");
        return Results.StatusCode(500);
    }
});
```

**Cloud Run 配置自動偵測此 endpoint**，失敗時自動重啟容器。

---

## §7 GitHub Actions Workload Identity 聯繫

### §7.1 Workload Identity Federation 設定 (預留方案)

本階段使用 Service Account 金鑰 (§5.4)，未來可升級為 Workload Identity Federation 減少金鑰管理：

```bash
# 未來升級用:建立 Workload Identity Pool
gcloud iam workload-identity-pools create "gh-pool" \
  --project=eztcomm-prod-1780402352 \
  --location=global \
  --display-name="GitHub Actions Pool"

# 建立 Workload Provider
gcloud iam workload-identity-pools providers create-oidc "gh-provider" \
  --project=eztcomm-prod-1780402352 \
  --location=global \
  --workload-identity-pool=gh-pool \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 授予 GitHub Actions Service Account
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-deployer@eztcomm-prod-1780402352.iam.gserviceaccount.com \
  --project=eztcomm-prod-1780402352 \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/{PROJECT_NUM}/locations/global/workloadIdentityPools/gh-pool/attribute.repository/aimacisk/eztravel.community"
```

---

## §8 Secrets 清單 (Security Boundary)

### §8.1 GitHub Actions Secrets (用於 .github/workflows/release.yml)

| Secret 名稱 | 值 | 用途 | 取得方式 |
|-------------|-----|------|--------|
| `GCP_SA_KEY` | Service Account JSON (base64) | GCP 認證 | `gcloud iam service-accounts keys create` (§5.4) |
| `DB_PASSWORD` | Cloud SQL postgres 密碼 | 資料庫登入 | `gcloud sql users set-password` |

### §8.2 GCP Cloud Secret Manager (用於 Cloud Run Runtime)

| Secret 名稱 | 值 | 用途 | 參考卡 |
|-------------|-----|------|-------|
| `db-password` | Cloud SQL postgres 密碼 | 應用層連線字串 | W5-ADMIN-1 |
| `aspnetcore-environment` | "Production" | ASP.NET 環境識別 | W5-ADMIN-1 |

### §8.3 PII 與憑證隔離原則

- **不可** 在 `.github/workflows/` yaml 中硬寫密碼/token
- **不可** 在 appsettings.json 中硬寫敏感資訊
- **必須** 透過環境變數或 Cloud Secret Manager 注入
- **必須** 確保 log output 不洩露密碼（驗證見 §5 QA）

---

## §9 CI/CD Release Workflow (.github/workflows/release.yml)

完整的 release.yml 高層框架 (PG 負責實作細節):

```yaml
name: Release & Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  release-and-deploy:
    runs-on: ubuntu-latest
    
    permissions:
      contents: read
      id-token: write
    
    steps:
      # 1. Checkout
      - uses: actions/checkout@v4
      
      # 2. 檢測 [release]
      - name: Check for [release] in commit
        id: check_release
        run: |
          if [[ "${{ github.event.head_commit.message }}" =~ \[release\] ]]; then
            echo "release_detected=true" >> $GITHUB_OUTPUT
          else
            echo "release_detected=false" >> $GITHUB_OUTPUT
          fi
      
      # 3. 若非 [release] commit 則提前終止
      - name: Exit if not release commit
        if: steps.check_release.outputs.release_detected == 'false'
        run: echo "Not a release commit, skipping deployment"
      
      # 4. Setup .NET
      - name: Setup .NET 8
        if: steps.check_release.outputs.release_detected == 'true'
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      
      # 5. NuGet Restore
      - name: Restore dependencies
        if: steps.check_release.outputs.release_detected == 'true'
        run: cd 04_src && dotnet restore
      
      # 6. Build
      - name: Build Release
        if: steps.check_release.outputs.release_detected == 'true'
        run: cd 04_src && dotnet build -c Release --no-restore
      
      # 7. Unit Tests
      - name: Run Unit Tests
        if: steps.check_release.outputs.release_detected == 'true'
        run: cd 04_src && dotnet test -c Release --no-build --verbosity normal
      
      # 8. GCP Auth (Service Account)
      - name: Authenticate to Google Cloud
        if: steps.check_release.outputs.release_detected == 'true'
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      # 9. Setup Cloud SDK
      - name: Set up Cloud SDK
        if: steps.check_release.outputs.release_detected == 'true'
        uses: google-github-actions/setup-gcloud@v1
      
      # 10. Docker Build & Push
      - name: Build and Push Docker Image
        if: steps.check_release.outputs.release_detected == 'true'
        run: |
          gcloud auth configure-docker asia-east1-docker.pkg.dev
          cd 04_src
          docker build -t asia-east1-docker.pkg.dev/eztcomm-prod-1780402352/eztravel-community/app:${{ github.sha }} .
          docker push asia-east1-docker.pkg.dev/eztcomm-prod-1780402352/eztravel-community/app:${{ github.sha }}
      
      # 11. Cloud SQL Migration (EF Core)
      - name: Apply Database Migrations
        if: steps.check_release.outputs.release_detected == 'true'
        env:
          ConnectionString: Server=localhost;Database=eztravel_community;User Id=postgres;Password=${{ secrets.DB_PASSWORD }};
        run: |
          cd 04_src
          dotnet ef database update --context ApplicationDbContext -p eztravel.Community.Infrastructure
      
      # 12. Deploy to Cloud Run
      - name: Deploy to Cloud Run
        if: steps.check_release.outputs.release_detected == 'true'
        run: |
          gcloud run deploy eztravel-community \
            --image=asia-east1-docker.pkg.dev/eztcomm-prod-1780402352/eztravel-community/app:${{ github.sha }} \
            --platform managed \
            --region asia-east1 \
            --memory 512Mi \
            --cpu 1 \
            --timeout 60s \
            --allow-unauthenticated \
            --set-env-vars=ASPNETCORE_ENVIRONMENT=Production \
            --add-cloudsql-instances=eztcomm-prod-1780402352:asia-east1:eztcomm-db \
            --port 8080
      
      # 13. Smoke Test
      - name: Smoke Test - Health Check
        if: steps.check_release.outputs.release_detected == 'true'
        run: |
          SERVICE_URL=$(gcloud run services describe eztravel-community \
            --platform managed --region asia-east1 --format='value(status.url)')
          curl -f ${SERVICE_URL}/health || exit 1
```

---

## §10 本機開發環境 (docker-compose)

### §10.1 docker-compose.yml

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: eztravel_community
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: DevPassword123!
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build:
      context: ./04_src
      dockerfile: Dockerfile
      target: development
    environment:
      ASPNETCORE_ENVIRONMENT: Development
      ASPNETCORE_URLS: http://+:5000
      ConnectionStrings__DefaultConnection: |
        Server=postgres;Port=5432;Database=eztravel_community;User Id=postgres;Password=DevPassword123!;
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./04_src:/app
    command: dotnet watch run --project eztravel.Community.Web.csproj

volumes:
  postgres_data:
```

### §10.2 啟動開發環境

```bash
cd projects/eztravel.community
docker compose up -d
# 等待 5s，資料庫初始化
sleep 5
curl http://localhost:5000/health
# 預期: {"status":"healthy","timestamp":"..."}
```

---

## §11 Dockerfile 多階段編譯規格

### §11.1 Dockerfile 架構

```dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY ["eztravel.Community.Web/eztravel.Community.Web.csproj", "eztravel.Community.Web/"]
COPY ["eztravel.Community.Core/eztravel.Community.Core.csproj", "eztravel.Community.Core/"]
COPY ["eztravel.Community.Infrastructure/eztravel.Community.Infrastructure.csproj", "eztravel.Community.Infrastructure/"]
COPY ["eztravel.Community.Tests/eztravel.Community.Tests.csproj", "eztravel.Community.Tests/"]

RUN dotnet restore "eztravel.Community.Web/eztravel.Community.Web.csproj"

COPY . .
RUN dotnet build "eztravel.Community.Web/eztravel.Community.Web.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "eztravel.Community.Web/eztravel.Community.Web.csproj" \
    -c Release -o /app/publish /p:UseAppHost=false

# Stage 3: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

COPY --from=publish /app/publish .

EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production

ENTRYPOINT ["dotnet", "eztravel.Community.Web.dll"]
```

### §11.2 Build 指令

```bash
# 開發環境 (含 hot-reload)
docker build --target=build -t eztcomm-dev .
docker run -v ${PWD}:/app -p 5000:5000 eztcomm-dev dotnet watch run

# 生產環境 (最終 runtime image)
docker build -t eztcomm-prod:latest .
docker tag eztcomm-prod:latest asia-east1-docker.pkg.dev/eztcomm-prod-1780402352/eztravel-community/app:latest
docker push asia-east1-docker.pkg.dev/eztcomm-prod-1780402352/eztravel-community/app:latest
```

---

## §12 QA 驗證 Checklist

QA 卡 (W4-AQ-1 / W5-ADMIN-3) 必須驗證：

- [ ] **Serilog 規範**:
  - 無 `Console.WriteLine()` (grep 全掃)
  - 無字串拼接 log (grep `Log.\w+\(".*"\s*\+`)
  
- [ ] **Severity 對應**:
  - Information level 用於業務事件
  - Warning level 用於可恢復異常
  - Error level 用於業務失敗
  - Fatal level 用於系統不可用
  
- [ ] **PII 隱私**:
  - 無 log password / token / credit_card 欄位
  - log 敏感資料時用 `{@SafeDto}` anonymous type
  
- [ ] **Cloud Logging 可查詢**:
  - LQL 能查找到 ERROR+ level log
  - Trace ID 隨 request 傳遞
  
- [ ] **本機運行**:
  - `docker compose up` 無報錯
  - `dotnet run` 可訪問首頁
  - Health endpoint `/health` 回應 200
  
- [ ] **雲端運行**:
  - Cloud Run service 狀態為 Active
  - Cloud SQL 連線成功 (Health check pass)
  - 首頁可在瀏覽器訪問
  - 用戶可在商品頁寫評論並在他人瀏覽器讀到

---

## 對齊的 ai.factory Memory

- [memory: project_dotnet_gcp_serilog_stdout](../../memory/project_dotnet_gcp_serilog_stdout.md)
- [memory: project_at_implements_baseline_project](../../memory/project_at_implements_baseline_project.md)
- [memory: feedback_three_retry_on_error](../../memory/feedback_three_retry_on_error.md)
- [memory: feedback_restart_needed_accumulator_card](../../memory/feedback_restart_needed_accumulator_card.md)

## 參考 Skills

- [dotnet-cicd-builder-github-gcp](../../skills/dotnet-cicd-builder-github-gcp/SKILL.md)
- [dotnet-project-creator](../../skills/dotnet-project-creator/SKILL.md)

---

**[Task_ID: T-eztcomm-20260601-W5-AT-1]**
