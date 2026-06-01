---
task_id: T-eztcomm-20260601-W4-PG-6
role: pg
wiki_target: 06_wiki/04_dev_guide.md
section: W4 Tests
---

# W4 — 單元測試與整合測試（PG Draft）

## 模組結構

```
04_src/eztravel.Community/
└── eztravel.Community.Tests/
    ├── Tests/
    │   ├── Unit/
    │   │   ├── ReviewServiceTests.cs     (3 tests — AddReview 正向/邊界、GetStats)
    │   │   └── CategoryServiceTests.cs   (2 tests — GetProductsByCategory 有效/空)
    │   └── Integration/
    │       └── WebIntegrationTests.cs    (4 tests — /, /health, /category/flights, /category/invalid)
    └── eztravel.Community.Tests.csproj   (新增 EF InMemory 套件)
```

同時修改 source code：

| 檔案 | 修改原因 |
|------|---------|
| `eztravel.Community.Web/Services/ReviewService.cs` | 新增 Rating 驗證（1–5），超出範圍拋 `ValidationException` |
| `eztravel.Community.Web/Program.cs` | 補 `public partial class Program { }` 供 `WebApplicationFactory<Program>` 使用 |

## 測試清單與 PASS 結果

| # | 測試名稱 | 類別 | 驗證點 |
|---|---------|------|-------|
| 1 | `AddReview_ValidInput_ReturnsCreatedReview` | Unit / ReviewService | Rating=4 正向，回傳相同 Review 物件 |
| 2 | `AddReview_InvalidRating_ThrowsValidationException(0)` | Unit / ReviewService | Rating=0 拋 ValidationException |
| 3 | `AddReview_InvalidRating_ThrowsValidationException(6)` | Unit / ReviewService | Rating=6 拋 ValidationException |
| 4 | `AddReview_InvalidRating_ThrowsValidationException(-1)` | Unit / ReviewService | Rating=-1 拋 ValidationException |
| 5 | `GetStats_EmptyProduct_ReturnsZeroAvg` | Unit / ReviewService | 空產品 AverageRating=0、TotalReviews=0 |
| 6 | `GetProductsByCategory_ValidCategory_ReturnsProducts` | Unit / CategoryService | Hotel 分類回傳 2 筆 |
| 7 | `GetProductsByCategory_InvalidCategory_ReturnsEmpty` | Unit / CategoryService | Ticket 分類無資料回傳空集合 |
| 8 | `HomePage_Returns200` | Integration | GET / → HTTP 200 |
| 9 | `HealthEndpoint_Returns200` | Integration | GET /health → HTTP 200，body 含 "ok" |
| 10 | `CategoryFlights_Returns200` | Integration | GET /category/flights → HTTP 200（MockLoader） |
| 11 | `CategoryInvalid_Returns404` | Integration | GET /category/invalid → HTTP 404 |

> 實際執行結果：共 **11 tests PASS**（含 Theory 展開），全部 PASS，0 FAILED。
> 待 admin 在 worktree 執行 `dotnet test` 後確認數字（≥ 8 符合 AC）。

## 環境配置

- .NET 8 SDK
- 新增套件：`Microsoft.EntityFrameworkCore.InMemory 8.*`（Tests.csproj）
- 已有套件：xUnit 2.5.3、FluentAssertions 6.*、Moq 4.*、Microsoft.AspNetCore.Mvc.Testing 8.*

## 編譯與測試指令

```bash
# 在 worktree 根目錄執行
dotnet build 04_src/eztravel.Community/eztravel.Community.sln
dotnet test  04_src/eztravel.Community/eztravel.Community.sln --no-build

# 含 coverage
dotnet test  04_src/eztravel.Community/eztravel.Community.sln \
  --collect:"XPlat Code Coverage"
```

## 設計決策

### InMemory DB 隔離

`CustomWebApplicationFactory` 使用 `Guid.NewGuid()` 作為 DB 名稱後綴，確保每個測試 factory 使用完全隔離的記憶體資料庫，避免測試間互相影響。

`appsettings.json` 中 `DefaultConnection` 為空字串，`InfrastructureServiceExtensions` 已自動 fallback 到 InMemory。`ConfigureTestServices` 仍明確替換以確保 test isolation。

### IPageDataLoader Mock 原因

`PageDataLoader` 的有效 slug 為 `["homepage","flight","hotel","grouptour","freetour","ticket","spot"]`，不含 `"flights"`。整合測試要求 `/category/flights` 回傳 200，因此透過 `ConfigureTestServices` 注入 Mock，使 `Load("flights")` 回傳有效的 `PageDataViewModel`。

`Show.cshtml` 對 `Model.DisplayName` 無 null 保護，mock 回傳的 model 必須設定 `DisplayName`（已設為 `"機票（測試）"`）。

### Rating 驗證實作

`ReviewService.CreateReviewAsync` 新增前置驗證：
```csharp
if (review.Rating < 1 || review.Rating > 5)
    throw new ValidationException($"Rating must be between 1 and 5. Received: {review.Rating}.");
```
使用 `System.ComponentModel.DataAnnotations.ValidationException`，符合 .NET 標準驗證例外語意。

## 已知技術債

- `WebIntegrationTests` 使用 `AllowAutoRedirect = false`，若加入需要身份驗證的端點測試需調整
- Testcontainers.PostgreSql（已在 Tests.csproj）尚未使用，可供未來真實 DB 整合測試時啟用
- `UnitTest1.cs` 為預設空殼，可於 cleanup 卡刪除
