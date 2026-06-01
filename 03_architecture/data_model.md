# Data Model — eztravel.Community EF Core 設計

> **文件版本**：v1.0
> **建立日期**：2026-06-01 (TST)
> **負責人**：AT agent（T-eztcomm-20260601-W4-AT-1）
> **對應任務**：W4-AT-1 架構文件（三份之二）
> **上游規格**：community_spec.md（W3-BA-1）/ data_schema.md（W1-BA-1）
> **狀態**：APPROVED — W4-PG-1（entity + migration）的單一規格依據

---

## §1 資料模型關係圖（ER Diagram）

```
┌─────────────────────┐       ┌───────────────────────────────┐
│  ApplicationUser    │       │           Product             │
│─────────────────────│       │───────────────────────────────│
│ Id (string, PK)     │       │ Id (Guid, PK)                 │
│ DisplayName         │       │ Category (ProductCategory)    │
│ AvatarUrl (nullable)│       │ Title                         │
│ Email               │       │ Description                   │
│ ... (Identity cols) │       │ ImageUrl (nullable)           │
└──────────┬──────────┘       │ Price (decimal)               │
           │                  │ Location (nullable)           │
           │ 1:N              │ CreatedAt                     │
           ▼                  └────────────────┬──────────────┘
┌──────────────────────────────────────┐       │ 1:N
│              Review                 │◄──────┘
│──────────────────────────────────────│
│ Id (Guid, PK)                        │
│ ProductId (Guid, FK→Product.Id)      │
│ UserId (string, FK→ApplicationUser)  │
│ Rating (short, 1–5)                  │
│ Text (string)                        │
│ Photos (string[], JSON column)       │
│ HelpfulCount (int)                   │
│ ParentReviewId (Guid?, self-ref FK)  │
│ IsDeleted (bool)                     │
│ CreatedAt (DateTimeOffset)           │
│ UpdatedAt (DateTimeOffset)           │
└──────────────┬───────────────────────┘
               │ 1:N
               ▼
┌──────────────────────────────────────┐
│           ReviewLike                 │
│──────────────────────────────────────│
│ Id (Guid, PK)                        │
│ ReviewId (Guid, FK→Review.Id)        │
│ UserId (string, FK→ApplicationUser)  │
│ CreatedAt (DateTimeOffset)           │
│ [UNIQUE] (ReviewId, UserId)          │
└──────────────────────────────────────┘
```

---

## §2 Entity 詳細設計

### 2.1 `ApplicationUser`（擴充 IdentityUser）

```csharp
// EzTravel.Community.Core.Entities.ApplicationUser
public class ApplicationUser : IdentityUser
{
    /// <summary>評論卡片顯示名稱，不可為 null；預設取 Email prefix。</summary>
    [Required]
    [MaxLength(50)]
    public string DisplayName { get; set; } = string.Empty;

    /// <summary>頭像 URL；null 時前端顯示 Gravatar 或文字頭像。</summary>
    [MaxLength(500)]
    public string? AvatarUrl { get; set; }
}
```

**DB Table**：`asp_net_users`（由 ASP.NET Identity 管理；Npgsql snake_case convention）

**新增欄位映射**：

| C# Property | DB Column | 型別 | 約束 |
|-------------|----------|------|------|
| `DisplayName` | `display_name` | `varchar(50)` | `NOT NULL` |
| `AvatarUrl` | `avatar_url` | `varchar(500)` | `NULL` 允許 |

---

### 2.2 `Product`（旅遊商品）

```csharp
// EzTravel.Community.Core.Entities.Product
public class Product
{
    public Guid Id { get; set; }

    [Required]
    public ProductCategory Category { get; set; }

    [Required]
    [MaxLength(200)]
    public string Title { get; set; } = string.Empty;

    [MaxLength(2000)]
    public string? Description { get; set; }

    [MaxLength(500)]
    public string? ImageUrl { get; set; }

    /// <summary>顯示用價格文字，保留原始格式，如 "TWD 25,900 起"。</summary>
    [MaxLength(100)]
    public string? Price { get; set; }

    [MaxLength(200)]
    public string? Location { get; set; }

    public DateTimeOffset CreatedAt { get; set; }

    // Navigation
    public ICollection<Review> Reviews { get; set; } = [];
}
```

**ProductCategory 列舉**：

```csharp
// EzTravel.Community.Core.Enums.ProductCategory
public enum ProductCategory
{
    GroupTour  = 1,   // 團體旅遊
    FreeTour   = 2,   // 自由行
    Hotel      = 3,   // 旅館
    Ticket     = 4    // 票券
}
```

**DB Table**：`products`

| C# Property | DB Column | 型別 | 約束 |
|-------------|----------|------|------|
| `Id` | `id` | `uuid` | `PRIMARY KEY, DEFAULT gen_random_uuid()` |
| `Category` | `category` | `integer` | `NOT NULL` |
| `Title` | `title` | `varchar(200)` | `NOT NULL` |
| `Description` | `description` | `text` | `NULL` |
| `ImageUrl` | `image_url` | `varchar(500)` | `NULL` |
| `Price` | `price` | `varchar(100)` | `NULL` |
| `Location` | `location` | `varchar(200)` | `NULL` |
| `CreatedAt` | `created_at` | `timestamptz` | `NOT NULL` |

---

### 2.3 `Review`（評論主體）

```csharp
// EzTravel.Community.Core.Entities.Review
public class Review
{
    public Guid Id { get; set; }

    // FK
    public Guid ProductId { get; set; }
    public Product Product { get; set; } = null!;

    [Required]
    public string UserId { get; set; } = string.Empty;
    public ApplicationUser User { get; set; } = null!;

    /// <summary>1–5 星；DB 有 CHECK 約束。</summary>
    public short Rating { get; set; }

    /// <summary>評論正文；10 ≤ len(Text.Trim()) ≤ 2000（Service 層強制）。</summary>
    [Required]
    [MaxLength(2000)]
    public string Text { get; set; } = string.Empty;

    /// <summary>
    /// 圖片相對路徑陣列，最多 6 張。
    /// EF Core 以 JSON column 儲存於 PostgreSQL。
    /// 格式：["/uploads/{guid}.{ext}"]
    /// </summary>
    public string[] Photos { get; set; } = [];

    /// <summary>累計讚數，由 Service 層維護，禁 Client 直接寫入。</summary>
    public int HelpfulCount { get; set; }

    /// <summary>樓主回應指向父評論；null 表示一般評論。</summary>
    public Guid? ParentReviewId { get; set; }
    public Review? ParentReview { get; set; }

    /// <summary>soft delete 旗標。</summary>
    public bool IsDeleted { get; set; }

    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset UpdatedAt { get; set; }

    // Navigation
    public ICollection<ReviewLike> Likes { get; set; } = [];
    public ICollection<Review> Replies { get; set; } = [];   // 樓主回應（最多 1 筆）
}
```

**DB Table**：`reviews`

| C# Property | DB Column | 型別 | 約束 |
|-------------|----------|------|------|
| `Id` | `id` | `uuid` | `PK, DEFAULT gen_random_uuid()` |
| `ProductId` | `product_id` | `uuid` | `NOT NULL, FK→products(id)` |
| `UserId` | `user_id` | `text` | `NOT NULL, FK→asp_net_users(id)` |
| `Rating` | `rating` | `smallint` | `NOT NULL, CHECK (rating BETWEEN 1 AND 5)` |
| `Text` | `text` | `text` | `NOT NULL` |
| `Photos` | `photos` | `jsonb` | `NOT NULL, DEFAULT '[]'` |
| `HelpfulCount` | `helpful_count` | `integer` | `NOT NULL, DEFAULT 0` |
| `ParentReviewId` | `parent_review_id` | `uuid` | `NULL, FK→reviews(id)` |
| `IsDeleted` | `is_deleted` | `boolean` | `NOT NULL, DEFAULT false` |
| `CreatedAt` | `created_at` | `timestamptz` | `NOT NULL` |
| `UpdatedAt` | `updated_at` | `timestamptz` | `NOT NULL` |

**索引清單**：

```sql
-- 商品評論列表主要查詢索引
CREATE INDEX ix_reviews_product_id_is_deleted
    ON reviews (product_id, is_deleted)
    WHERE is_deleted = false;

-- 使用者自己的評論（Rate limit 查詢）
CREATE INDEX ix_reviews_user_id_product_id_created_at
    ON reviews (user_id, product_id, created_at DESC)
    WHERE is_deleted = false;

-- 樓主回應查詢
CREATE INDEX ix_reviews_parent_review_id
    ON reviews (parent_review_id)
    WHERE parent_review_id IS NOT NULL;
```

---

### 2.4 `ReviewLike`（按讚記錄）

```csharp
// EzTravel.Community.Core.Entities.ReviewLike
public class ReviewLike
{
    public Guid Id { get; set; }

    public Guid ReviewId { get; set; }
    public Review Review { get; set; } = null!;

    [Required]
    public string UserId { get; set; } = string.Empty;
    public ApplicationUser User { get; set; } = null!;

    public DateTimeOffset CreatedAt { get; set; }
}
```

**DB Table**：`review_likes`

| C# Property | DB Column | 型別 | 約束 |
|-------------|----------|------|------|
| `Id` | `id` | `uuid` | `PK` |
| `ReviewId` | `review_id` | `uuid` | `NOT NULL, FK→reviews(id) ON DELETE CASCADE` |
| `UserId` | `user_id` | `text` | `NOT NULL, FK→asp_net_users(id)` |
| `CreatedAt` | `created_at` | `timestamptz` | `NOT NULL` |

**唯一約束**（防重複按讚）：

```sql
ALTER TABLE review_likes
    ADD CONSTRAINT uq_review_likes_review_user
    UNIQUE (review_id, user_id);
```

---

## §3 EF Core Configuration（`IEntityTypeConfiguration<T>`）

### 3.1 `ReviewConfiguration`

```csharp
// EzTravel.Community.Infrastructure.Data.Configurations.ReviewConfiguration
public class ReviewConfiguration : IEntityTypeConfiguration<Review>
{
    public void Configure(EntityTypeBuilder<Review> builder)
    {
        builder.HasKey(r => r.Id);
        builder.Property(r => r.Id).HasDefaultValueSql("gen_random_uuid()");

        // Rating CHECK constraint
        builder.ToTable(t => t.HasCheckConstraint(
            "ck_reviews_rating",
            "rating BETWEEN 1 AND 5"));

        // Photos → JSONB column
        builder.Property(r => r.Photos)
               .HasColumnType("jsonb")
               .HasDefaultValueSql("'[]'::jsonb");

        // FK: Product
        builder.HasOne(r => r.Product)
               .WithMany(p => p.Reviews)
               .HasForeignKey(r => r.ProductId)
               .OnDelete(DeleteBehavior.Restrict);

        // FK: User
        builder.HasOne(r => r.User)
               .WithMany()
               .HasForeignKey(r => r.UserId)
               .OnDelete(DeleteBehavior.Restrict);

        // Self-reference: ParentReview（樓主回應）
        builder.HasOne(r => r.ParentReview)
               .WithMany(r => r.Replies)
               .HasForeignKey(r => r.ParentReviewId)
               .OnDelete(DeleteBehavior.Restrict);

        // Indexes
        builder.HasIndex(r => new { r.ProductId, r.IsDeleted });
        builder.HasIndex(r => new { r.UserId, r.ProductId, r.CreatedAt });
        builder.HasIndex(r => r.ParentReviewId);
    }
}
```

### 3.2 `ReviewLikeConfiguration`

```csharp
public class ReviewLikeConfiguration : IEntityTypeConfiguration<ReviewLike>
{
    public void Configure(EntityTypeBuilder<ReviewLike> builder)
    {
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).HasDefaultValueSql("gen_random_uuid()");

        // UNIQUE (review_id, user_id)
        builder.HasIndex(l => new { l.ReviewId, l.UserId }).IsUnique();

        // FK: Review（CASCADE DELETE — Review 刪除時 Like 一起刪）
        builder.HasOne(l => l.Review)
               .WithMany(r => r.Likes)
               .HasForeignKey(l => l.ReviewId)
               .OnDelete(DeleteBehavior.Cascade);

        // FK: User
        builder.HasOne(l => l.User)
               .WithMany()
               .HasForeignKey(l => l.UserId)
               .OnDelete(DeleteBehavior.Restrict);
    }
}
```

### 3.3 `AppDbContext`

```csharp
// EzTravel.Community.Infrastructure.Data.AppDbContext
public class AppDbContext : IdentityDbContext<ApplicationUser>
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Product> Products => Set<Product>();
    public DbSet<Review> Reviews => Set<Review>();
    public DbSet<ReviewLike> ReviewLikes => Set<ReviewLike>();

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder); // Identity 表的 snake_case 由 Npgsql 處理

        builder.ApplyConfiguration(new ProductConfiguration());
        builder.ApplyConfiguration(new ReviewConfiguration());
        builder.ApplyConfiguration(new ReviewLikeConfiguration());

        // 全域使用 snake_case（Npgsql Convention）
        builder.UseSnakeCaseNamingConvention();
    }
}
```

---

## §4 Migration 命名規範

| Migration 名稱 | 包含內容 | 觸發時機 |
|--------------|---------|---------|
| `Initial` | 所有 ASP.NET Identity 表（`asp_net_users` / `asp_net_roles` / `asp_net_user_roles` 等）+ `ApplicationUser` 擴充欄位 | W4-PG-1 初始建立 |
| `AddCommunity` | `products` 表 + `reviews` 表（含 CHECK / INDEX）+ `review_likes` 表（含 UNIQUE） | W4-PG-1 同批 |
| `SeedProducts` | 種子資料插入（詳見 §5） | W4-PG-3 商品頁完工後 |

**Migration 執行指令**：

```bash
# 建立 Migration
dotnet ef migrations add Initial \
  --project eztravel.Community.Infrastructure \
  --startup-project eztravel.Community.Web

# 套用至 DB（啟動時也會自動執行，見 Program.cs）
dotnet ef database update \
  --project eztravel.Community.Infrastructure \
  --startup-project eztravel.Community.Web
```

---

## §5 種子資料策略

### 5.1 策略原則

- **種子商品**（Product）：從 `data/{category}/*.json` 的 `sections[].items` 中取 sample，每類商品各取最多 3 筆，建立假商品記錄供前端展示。
- **Identity 種子**：Migration 中不直接插入使用者密碼（安全考量）；改在 `Program.cs` 啟動時以 `UserManager.CreateAsync` 建立預設管理員帳號（僅在 Development 環境）。
- **ReviewLike / Review**：不預置；由使用者操作產生。

### 5.2 `SeedProducts` Migration 實作方式

```csharp
// Migration: SeedProducts
public partial class SeedProducts : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // 從嵌入資源或相對路徑讀取 data/團體/團體.json
        // 取前 3 筆 product_list 類型 items 建立 Product 記錄
        // 每筆 Product.Id 固定 Guid（冪等，重跑 migration 不重複插入）

        migrationBuilder.Sql("""
            INSERT INTO products (id, category, title, description, image_url, price, location, created_at)
            VALUES
              ('11111111-0000-0000-0000-000000000001', 1, '日本東京 5 天 4 夜精選', '含來回機票+4星飯店3晚', '/images/group/group_product_01.jpg', 'TWD 25,900 起', '東京', NOW()),
              ('11111111-0000-0000-0000-000000000002', 2, '東京自由行 5 日', '機加酒套裝，彈性行程', '/images/freetour/freetour_product_01.jpg', 'TWD 18,500 起', '東京', NOW()),
              ('11111111-0000-0000-0000-000000000003', 3, '東京新宿王子大飯店', '市中心交通便利，商務旅客首選', '/images/hotel/hotel_product_01.jpg', 'TWD 3,200 /晚起', '東京新宿', NOW()),
              ('11111111-0000-0000-0000-000000000004', 4, '迪士尼樂園一日券', '含入場券，可加購 Skip the Line', '/images/ticket/ticket_product_01.jpg', 'TWD 2,800 起', '東京千葉', NOW())
            ON CONFLICT (id) DO NOTHING;
        """);
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("""
            DELETE FROM products
            WHERE id IN (
              '11111111-0000-0000-0000-000000000001',
              '11111111-0000-0000-0000-000000000002',
              '11111111-0000-0000-0000-000000000003',
              '11111111-0000-0000-0000-000000000004'
            );
        """);
    }
}
```

---

## §6 聚合快取設計（IMemoryCache）

### 6.1 快取 Key 格式

```
review_summary:{product_id}
```

例如：`review_summary:11111111-0000-0000-0000-000000000001`

### 6.2 快取更新觸發時機

| 觸發事件 | 對應 Endpoint | Service 動作 |
|---------|-------------|-------------|
| 新增評論 | `POST /api/products/{id}/reviews` | `_cache.Remove($"review_summary:{productId}")` 後重算寫入 |
| 修改評論（rating 改變） | `PATCH /api/reviews/{id}` | 同上 |
| 刪除評論（soft delete） | `DELETE /api/reviews/{id}` | 同上 |

**TTL**：5 分鐘（`TimeSpan.FromMinutes(5)`）— 作為兜底防止極罕見 race condition 殘留舊值。

### 6.3 `ReviewSummary` DTO（快取內容）

```csharp
// EzTravel.Community.Core.Models.ReviewSummary
public record ReviewSummary(
    Guid ProductId,
    decimal AverageRating,
    int TotalReviews,
    int PhotosReviews,
    int Star5Count, decimal Star5Pct,
    int Star4Count, decimal Star4Pct,
    int Star3Count, decimal Star3Pct,
    int Star2Count, decimal Star2Pct,
    int Star1Count, decimal Star1Pct
);
```

### 6.4 聚合查詢（LINQ / EF Core）

```csharp
// ReviewService.ComputeSummaryAsync(Guid productId)
var baseQuery = _context.Reviews
    .Where(r => r.ProductId == productId
             && !r.IsDeleted
             && r.ParentReviewId == null);

var totalReviews  = await baseQuery.CountAsync();
var avgRating     = totalReviews > 0
    ? Math.Round(await baseQuery.AverageAsync(r => (decimal)r.Rating), 1)
    : 0m;
var photosReviews = await baseQuery.CountAsync(r => r.Photos.Length > 0);

var distribution  = await baseQuery
    .GroupBy(r => r.Rating)
    .Select(g => new { Rating = g.Key, Count = g.Count() })
    .ToListAsync();
```

---

## §7 PostgreSQL 連線字串設計總覽

| 環境 | 連線方式 | 連線字串格式 |
|------|---------|------------|
| Development（本機） | TCP → Docker PostgreSQL | `Host=localhost;Port=5432;Database=eztcomm_dev;Username=postgres;Password=devpassword` |
| Production（GCP） | Unix socket → Cloud SQL | `Host=/cloudsql/{PROJECT}:{REGION}:{INSTANCE};Database=eztcomm_prod;Username=eztcomm_app;Password={SECRET}` |
| CI/CD（GitHub Actions） | Testcontainers（自動化測試）| Testcontainers 自動配置，不需手動設定 |

---

## §8 Repository 介面規範

### 8.1 `IReviewRepository`

```csharp
// EzTravel.Community.Core.Interfaces.Repositories.IReviewRepository
public interface IReviewRepository
{
    Task<Review?> GetByIdAsync(Guid id, CancellationToken ct = default);

    /// <summary>分頁查詢評論（含過濾、排序；不含 soft-deleted；不含樓主回應）。</summary>
    Task<ReviewListResult> GetPagedAsync(ReviewListQuery query, CancellationToken ct = default);

    /// <summary>取得指定評論的所有樓主回應（最多 1 筆，API 保證）。</summary>
    Task<IReadOnlyList<Review>> GetRepliesAsync(Guid parentReviewId, CancellationToken ct = default);

    Task<Review> CreateAsync(Review review, CancellationToken ct = default);
    Task UpdateAsync(Review review, CancellationToken ct = default);

    /// <summary>Soft delete — 只改 is_deleted = true。</summary>
    Task SoftDeleteAsync(Guid id, CancellationToken ct = default);

    /// <summary>Rate limit 查詢 — 24 小時內同 user 對同 product 的評論數（不含樓主回應）。</summary>
    Task<int> CountRecentAsync(string userId, Guid productId, TimeSpan window, CancellationToken ct = default);
}
```

### 8.2 `IReviewLikeRepository`

```csharp
public interface IReviewLikeRepository
{
    Task<ReviewLike?> GetAsync(Guid reviewId, string userId, CancellationToken ct = default);
    Task<ReviewLike> CreateAsync(ReviewLike like, CancellationToken ct = default);
    Task DeleteAsync(Guid reviewId, string userId, CancellationToken ct = default);
}
```

---

## §9 驗收條件（對應卡片 verification）

| 條件 | 驗證方式 |
|------|---------|
| 本文件行數 ≥ 150 | `wc -l data_model.md` |
| 含 ApplicationUser entity | grep 驗證 |
| 含 Product entity | grep 驗證 |
| 含 Review entity（含 Photos JSONB） | grep 驗證 |
| 含 ReviewLike entity（含 UNIQUE 約束） | grep 驗證 |
| Migration 命名清單存在 | 人工驗核 §4 |
| 快取 key 格式明確定義 | 人工驗核 §6.1 |

---

*文件結束。如 community_spec.md 規格與本文件有矛盾，以 community_spec.md 為準，請向 AT 提出 REWORK。*
