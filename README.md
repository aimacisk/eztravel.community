# eztravel.community

> EZTravel Community — 旅遊社群網站(rebuild 2026-06-01)
>
> 還原 eztravel 首頁與第一層連結內容,商品頁加入 Google Maps 風格社群評論模組,
> 部署於 GCP Cloud Run + Cloud SQL PostgreSQL,以 commit message 含 `[release]` 觸發 CI/CD。

## 技術棧

- **後端 / 前端**: ASP.NET Core MVC + Razor (.NET 8 LTS)
- **資料庫**: PostgreSQL (本機 docker / 雲端 Cloud SQL Unix socket)
- **ORM**: EF Core + Npgsql
- **認證**: ASP.NET Identity (email/password)
- **Logging**: Serilog → stdout JSON (GCP Cloud Logging)
- **CI/CD**: GitHub Actions(commit message 含 `[release]` 觸發)
- **雲端**: GCP Cloud Run + Cloud SQL + Artifact Registry
- **region**: asia-east1

## 5 Waves 規劃

| Wave | 主軸 | 主要 agent |
|------|------|----------|
| W0 | 清除舊資產 + GitHub repo 建立 | admin |
| W1 | 爬 eztravel 首頁 + 第一層 6 分類頁 → `data/` | BA, PG, AQ |
| W2 | Figma `eztravel.community design` 設計 | UIUX |
| W3 | Google Maps 風格社群留言模組設計 | BA, UIUX |
| W4 | .NET MVC 實作 (首頁/分類/商品/Community) | AT, PG, AQ |
| W5 | GCP 部署 + CI/CD | AT, PG, admin |

完整 spec 見 `../../docs/superpowers/specs/2026-06-01-eztravel-community-rebuild-design.md`。

## 目錄分區

| 目錄 | 負責 | 內容 |
|------|------|------|
| `.agent_system/` | PM | task_board.json + cards/ + events/ |
| `01_requirements/` | BA | features / rules / sitemap / community_spec |
| `02_design/` | UIUX | figma_deliverables / style_tokens |
| `03_architecture/` | AT | solution_layout / data_model / devops / auth |
| `data/` | PG (W1) | 爬蟲產出:首頁+6 分類頁 json + 截圖 + 圖片 |
| `04_src/` | PG | .NET solution (`eztravel.Community/`) |
| `05_tests/` | AQ | test cases / bug reports / E2E |
| `06_wiki/` | 全員 | 知識歸檔 |
| `.github/workflows/` | PG (W5) | release.yml |
| `Dockerfile` | PG (W5) | .NET 8 multi-stage build |
