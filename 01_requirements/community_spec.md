# Community 社群留言與星等模組 — 需求規格

> **文件版本**：v1.0
> **建立日期**：2026-06-01 (TST)
> **負責人**：BA agent
> **對應任務卡**：T-eztcomm-20260601-W3-BA-1
> **對應許願卡**：W-eztcomm-20260601-REBUILD
> **狀態**：APPROVED（作為 W3-UIUX 設計與 W4-PG-4 實作的單一 source of truth）

---

## §0 文件導覽

| 章節 | 主題 | 主要讀者 |
|------|------|---------|
| §1 | 功能總覽與設計原則 | PM、UIUX、PG |
| §2 | 評論欄位定義（Review entity） | AT、PG |
| §3 | 權限矩陣（RBAC） | AT、PG |
| §4 | 星等聚合規則 | PG（Service 層）、AT（DB 設計） |
| §5 | 防濫用規則 | PG（Validation 層） |
| §6 | UX 互動規約 | UIUX、PG（Razor/JS 層） |
| §7 | API Endpoint 草案 | AT、PG |

**縮寫對照**：
- `MVP 假設` — 此處規格為最小可行版本假設，後續迭代可調整。
- `AC-xxx` — 對應 W-eztcomm-20260601-REBUILD 許願卡的驗收標準。
- `soft delete` — 邏輯刪除，`is_deleted = true`，資料不從 DB 移除。

---

## §1 功能總覽與設計原則

### 1.1 功能定位

Community 模組賦予 eztravel.community 網站**真實使用者社群互動能力**，讓旅客可以：
1. 對旅遊商品（團體旅、自由行、旅館、票券）撰寫心得評論。
2. 給予 1–5 星評分，反映整體滿意度。
3. 為他人評論按「讚」（Helpful）。
4. 上傳旅遊照片作為附件。
5. 依星數、有無照片、排序方式篩選評論。
6. 商品擁有者（樓主）可在自己商品的評論下發表官方回應。

### 1.2 設計風格融合原則

| 面向 | Google Maps 評論風格（借鑑） | eztravel 調整方向 |
|------|--------------------------|----------------|
| 星等視覺 | 黃色五星、半星支援 | 配合 eztravel 主色系（橘/藍），保留黃色五星 |
| 評論卡片 | 頭像 + 名字 + 星等 + 時間 + 文字 + 照片 grid | 同上，加「旅遊類別 badge」於頭像右下角 |
| 評分分布 | 5 條橫向長條圖 + 平均分 + 總則數 | 同上 |
| 篩選列 | 標籤型 filter chips | 改為標準 Dropdown/Tab，符合 eztravel 慣例風格 |
| 樓主回應 | 灰底縮排 nested | 保留，底色改用 eztravel 淺藍 (#E8F0FE 等同 Google Maps 灰底之功能角色) |

### 1.3 5 個 Atomic Primitives（對應 W3-UIUX）

| Primitive | 職責 | 對應 AC |
|-----------|------|--------|
| `StarRating` | 互動式星等選取（ComposerModeMode）& 唯讀顯示（ReadOnlyMode） | AC-4 |
| `RatingDistribution` | 5 條長條圖 + 總平均 + 總則數 | AC-4 |
| `ReviewCard` | 單筆評論顯示（頭像/名字/星等/時間/文字/照片/讚/樓主回應 nested） | AC-4 |
| `FilterBar` | 篩選標籤（全部/5星/4星/3星↓/有照片/最新/最相關） | AC-4 |
| `ReviewComposer` | 星等 picker + textarea + 照片上傳 + 送出按鈕 | AC-4、AC-5 |

---

## §2 評論欄位定義（Review Entity）

### 2.1 欄位清單

| 欄位名稱 | 型別 | 必填性 | 說明 | 驗收條件 |
|---------|------|-------|------|---------|
| `id` | `Guid` | 自動 | 主鍵，server 端產生 | `NOT NULL`，DB 預設 `gen_random_uuid()` |
| `product_id` | `Guid` | 必填 | FK → `Products.Id` | `NOT NULL`；外鍵約束，Product 不存在則 `404` |
| `user_id` | `string` | 必填 | FK → `AspNetUsers.Id` | `NOT NULL`；外鍵約束，未登入則 `401` |
| `rating` | `smallint` | 必填 | 1–5 整數星等 | `CHECK (rating BETWEEN 1 AND 5)`；超出範圍 `400` |
| `text` | `text` | 必填 | 評論正文 | 字數：10 ≤ len(text) ≤ 2000（Server-side 強制，詳 §5） |
| `photos` | `text[]`（JSON column） | 選填 | 圖片相對路徑陣列，最多 6 張 | 空值允許；超過 6 張 → `400`；每張路徑格式 `/uploads/{guid}.{ext}` |
| `parent_review_id` | `Guid?` | 選填 | 樓主回應用，指向父評論 `id` | 允許 `NULL`；若有值則父評論須屬同一 `product_id`，否則 `400` |
| `helpful_count` | `int` | 自動 | 累計讚數，`ReviewLike` 聚合 | Server 端維護，不接受 client 直接寫入 |
| `is_deleted` | `boolean` | 自動 | soft delete 標記 | 預設 `false`；刪除操作只設 `true`，不物理刪除 |
| `created_at` | `timestamptz` | 自動 | 建立時間（UTC） | Server 端 `DateTime.UtcNow` |
| `updated_at` | `timestamptz` | 自動 | 最後更新時間（UTC） | 每次 PATCH 更新；建立時與 `created_at` 相同 |

### 2.2 `ReviewLike` Entity

`ReviewLike` 記錄「誰對哪篇評論按了讚」，用於計算 `helpful_count` 與防止重複按讚。

| 欄位名稱 | 型別 | 說明 |
|---------|------|------|
| `id` | `Guid` | 主鍵 |
| `review_id` | `Guid` | FK → `Reviews.Id`，`CASCADE DELETE` |
| `user_id` | `string` | FK → `AspNetUsers.Id` |
| `created_at` | `timestamptz` | 按讚時間 |

**唯一約束**：`UNIQUE (review_id, user_id)` — 同一使用者對同一評論只能按一次讚。

### 2.3 `ApplicationUser` 延伸欄位（Identity 擴充）

| 欄位名稱 | 型別 | 說明 |
|---------|------|------|
| `DisplayName` | `string` | 顯示名稱，用於評論卡片頭像旁 |
| `AvatarUrl` | `string?` | 頭像 URL；`NULL` 則顯示預設 Gravatar 或文字頭像 |

### 2.4 資料模型關係圖（文字 FSM）

```
Product (1) ──────────── (*) Review
  │                           │
  │                     ┌─────┴──────┐
  │                     │            │
  │                ReviewLike     Review (parent_review_id，nullable，自回參)
  │              (user_id FK)
  │
ApplicationUser (*) ─── (*) Review (user_id FK)
ApplicationUser (*) ─── (*) ReviewLike (user_id FK)
```

---

## §3 權限矩陣（RBAC）

### 3.1 角色定義

| 角色識別碼 | 對應 Identity Role | 取得條件 |
|-----------|------------------|---------|
| `Guest` | 無（未登入） | 任何未登入訪客 |
| `Member` | （無 Role，即 Identity 預設使用者） | 完成 email + password 註冊後 |
| `Owner` | `Owner`（MVP 假設：後台人工設定） | 對應商品的擁有者，由管理員授予 |
| `Admin` | `Admin` | 系統管理員，MVP 預留角色不實作後台 UI |

### 3.2 操作權限矩陣

| 操作 | Guest | Member（他人） | Member（自己） | Owner（自己商品） | Admin |
|------|-------|--------------|--------------|----------------|-------|
| 讀取評論列表 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 讀取單筆評論 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 新增評論 | ❌（401） | ✅ | ✅ | ✅ | ✅ |
| 編輯評論 | ❌（401） | ❌（403） | ✅（時限內） | ❌（403） | ✅ |
| 刪除評論（soft delete） | ❌（401） | ❌（403） | ✅ | ❌（403） | ✅ |
| 按讚評論 | ❌（401） | ✅ | ❌（不能讚自己，400） | ✅ | ✅ |
| 新增樓主回應 | ❌（401） | ❌（403） | ❌（403） | ✅（限自己商品） | ✅ |
| 隱藏評論 | ❌ | ❌ | ❌ | ❌ | ✅（MVP 預留，不實作 UI） |

### 3.3 編輯時限規則

**GIVEN** Member 於 `created_at` + 24 小時內
**WHEN** 送出 PATCH `/api/reviews/{id}`
**THEN** 允許更新 `text`、`rating`、`photos`

**GIVEN** 超過 24 小時
**WHEN** 送出 PATCH `/api/reviews/{id}`
**THEN** 回傳 `403 Forbidden`，body 含 `{ "error": "edit_window_expired" }`

### 3.4 樓主回應約束規則（FSM）

```
狀態：review.parent_review_id

[NULL] ──（Owner 對此評論發表回應）──► [有值：指向父評論 id]

約束（不可違反）：
1. parent_review_id 指向的父評論必須屬同一 product_id
2. parent_review_id 指向的父評論不能也是樓主回應（禁止多層 nested）
   → 若 parent.parent_review_id != NULL，拒絕 → 400 { "error": "nested_reply_not_allowed" }
3. 每篇父評論只能有一條樓主回應
   → 若同 product/user(Owner) 已有同 parent_review_id 的回應，拒絕 → 409 { "error": "owner_reply_exists" }
```

---

## §4 星等聚合規則

### 4.1 商品星等聚合公式

**GIVEN** 商品 `product_id` 的所有未刪除評論
**WHEN** 取得商品評論摘要
**THEN** 計算以下 4 個指標：

| 指標 | 計算公式 | 型別 | 精度說明 |
|------|---------|------|---------|
| `average_rating` | `AVG(rating) WHERE is_deleted = false AND parent_review_id IS NULL` | `decimal(3,1)` | 四捨五入至小數點第一位，如 `4.3` |
| `total_reviews` | `COUNT(*) WHERE is_deleted = false AND parent_review_id IS NULL` | `int` | 不含樓主回應 |
| `photos_reviews` | `COUNT(*) WHERE is_deleted = false AND parent_review_id IS NULL AND array_length(photos, 1) > 0` | `int` | 有照片的評論數 |
| `rating_distribution` | 見 §4.2 | `object` | 5 個 bucket |

### 4.2 星等分布（5 條長條圖）

| 欄位 | 說明 | 計算 |
|------|------|------|
| `star5_count` | 5 星評論數 | `COUNT(*) WHERE rating = 5 AND is_deleted = false AND parent_review_id IS NULL` |
| `star4_count` | 4 星評論數 | `COUNT(*) WHERE rating = 4 AND ...` |
| `star3_count` | 3 星評論數 | `COUNT(*) WHERE rating = 3 AND ...` |
| `star2_count` | 2 星評論數 | `COUNT(*) WHERE rating = 2 AND ...` |
| `star1_count` | 1 星評論數 | `COUNT(*) WHERE rating = 1 AND ...` |
| `star{n}_pct` | 各星佔比（UI 用，長條圖寬度百分比） | `star{n}_count / total_reviews * 100`（若 total = 0 則全 0） |

### 4.3 快取策略

**原則**：MVP 不使用排程（cron）更新，而是在 **Service 層事件驅動即時重算**。

```
事件觸發條件                           觸發動作
────────────────────────────────────────────────────────
POST   /api/products/{id}/reviews     → 重算 product_id 聚合並寫入快取
PATCH  /api/reviews/{id}（rating 變動）→ 重算對應 product_id 聚合
DELETE /api/reviews/{id}              → 重算對應 product_id 聚合
```

**MVP 假設**：快取實作使用 `IMemoryCache`（in-process），key = `review_summary:{product_id}`，TTL = 5 分鐘（作為兜底，防止極罕見的 race condition 殘留舊值）。

**後續升級路徑**（非 MVP 範圍）：引入 Redis Distributed Cache，key 設計不變，支援多節點 Cloud Run。

### 4.4 聚合回應 JSON 結構

```json
{
  "product_id": "{{guid}}",
  "average_rating": 4.3,
  "total_reviews": 128,
  "photos_reviews": 42,
  "rating_distribution": {
    "star5_count": 64,   "star5_pct": 50.0,
    "star4_count": 32,   "star4_pct": 25.0,
    "star3_count": 16,   "star3_pct": 12.5,
    "star2_count":  8,   "star2_pct":  6.25,
    "star1_count":  8,   "star1_pct":  6.25
  }
}
```

---

## §5 防濫用規則

### 5.1 評論發布頻率限制（Rate Limit）

| 規則 ID | 條件 | 約束 | 違反回應 |
|--------|------|------|---------|
| RL-1 | 同 `user_id` 對同 `product_id` 在 24 小時滾動窗口內 | 最多新增 **1 則**評論（PATCH 修改不計入） | `429 Too Many Requests`，body 含 `{ "error": "rate_limit_exceeded", "retry_after_seconds": {{剩餘秒數}} }` |
| RL-2 | 樓主回應（`parent_review_id IS NOT NULL`）同 Owner 對同一父評論 | 最多 **1 則**（見 §3.4 約束 3） | `409 Conflict`，body 含 `{ "error": "owner_reply_exists" }` |

**實作位置**：Service 層（`ReviewService.CreateAsync`），查詢 DB 而非 in-memory，確保多節點正確性。

### 5.2 字數驗證

| 規則 ID | 對象 | 約束 | 實作層次 |
|--------|------|------|---------|
| LEN-1 | `text`（評論正文） | `10 ≤ len(text.Trim()) ≤ 2000` | **Server-side 強制**（FluentValidation or DataAnnotations） |
| LEN-2 | `text` Client-side | 即時字數提示（ReviewComposer 下方顯示 `{n}/2000`） | Client-side UX，不影響 Server 驗證 |
| LEN-3 | 超出字數上限 | `400 Bad Request`，body 含 `{ "error": "text_too_long", "max": 2000 }` | Server |
| LEN-4 | 低於字數下限 | `400 Bad Request`，body 含 `{ "error": "text_too_short", "min": 10 }` | Server |

### 5.3 照片上傳規則

| 規則 ID | 約束 | 違反回應 |
|--------|------|---------|
| IMG-1 | 每則評論最多 **6 張**照片 | `400`，`{ "error": "too_many_photos", "max": 6 }` |
| IMG-2 | 每張檔案大小 **≤ 5 MB** | `400`，`{ "error": "photo_too_large", "max_bytes": 5242880 }` |
| IMG-3 | 允許格式：`image/jpeg`、`image/png`、`image/webp` | `415 Unsupported Media Type`，`{ "error": "unsupported_photo_format" }` |
| IMG-4 | 儲存路徑（MVP）：`wwwroot/uploads/{guid}.{ext}` | 不使用 GCS（MVP 假設）；Cloud Run 重啟後 wwwroot 靜態，須注意 Cloud Run 無狀態特性（後續升級用 GCS） |
| IMG-5 | 刪除評論（soft delete）後，對應照片**不**主動刪除 | 孤立檔案由後續維護任務清理（非 MVP 範圍） |

### 5.4 XSS 防護與輸入清理

| 規則 ID | 規則內容 | 實作方式 |
|--------|---------|---------|
| XSS-1 | `text` 欄位儲存前須 **strip 所有 HTML tags**，只保留純文字與 `\n` 換行符 | Service 層呼叫 `HtmlSanitizer` 或自訂 regex 清除 `<[^>]*>` |
| XSS-2 | `text` 顯示時 Razor 預設 HTML encode（`@Model.Text`），不允許 `@Html.Raw` | PG 強制紀律，Code Review 關注點 |
| XSS-3 | `DisplayName` 欄位同樣 HTML encode 顯示 | 同上 |
| XSS-4 | 照片 URL 不允許 `javascript:` scheme | Server 驗證：`Uri.TryCreate` + `scheme == "https" or "/uploads/"` |

---

## §6 UX 互動規約

### 6.1 ReviewComposer 提交流程

**GIVEN** 已登入 Member，在商品頁 ReviewComposer 填寫星等 + 正文後按「送出」
**WHEN** POST `/api/products/{id}/reviews` 回傳 `201 Created`
**THEN**：
1. 評論列表頂端**即時插入**新評論卡片（不重整頁面）。
2. ReviewComposer 清空（星等重置、textarea 清空、預覽圖移除）。
3. 聚合統計（`RatingDistribution`、平均分、總則數）**即時更新**（重新 fetch `/api/products/{id}/reviews/summary`）。

**WHEN** 回傳 `400` 或 `429`
**THEN**：在 ComposerMode 中顯示對應錯誤訊息，不清空已輸入內容。

### 6.2 樓主回應顯示規則

```
ReviewCard（父評論）
└── [顯示樓主回應 nested]
    ├── 底色：eztravel 淺藍（MVP 假設：#EBF3FD）
    ├── 左側縱線：2px solid #1A73E8（Google Maps 樓主顏色對應 eztravel 主色）
    ├── 頭像旁顯示 "官方回應" badge
    └── 文字格式：同一般 ReviewCard，但不顯示星等、不顯示按讚
```

**GIVEN** 評論無樓主回應
**THEN** 不顯示樓主回應區塊（不留空白）。

**GIVEN** 評論有樓主回應
**THEN** 評論卡片尾端縮排顯示官方回應區塊（非獨立卡，屬同一 `ReviewCard` 元件的子節點）。

### 6.3 按讚（Helpful）互動規則

**GIVEN** Member 點擊「讚」按鈕
**WHEN** 動作送出至 POST `/api/reviews/{id}/like`
**THEN** 前端採 **Optimistic Update**：
1. 立即將讚數 +1，按鈕改為「已讚」狀態。
2. 背景 fetch 完成後，若成功 `201`，維持狀態。
3. 若 API 回傳 `400`（不能讚自己）或 `409`（已讚）或網路失敗，**Rollback**：讚數回復原值，按鈕回到未讚狀態，顯示 tooltip 說明原因。

**GIVEN** Member 再次點擊「已讚」按鈕（取消讚）
**THEN** DELETE `/api/reviews/{id}/like`，Optimistic Update 同上（讚數 -1，失敗 rollback）。

### 6.4 FilterBar 篩選規約

**規則**：所有篩選條件對應 URL query string，使畫面可**分享與書籤**。

| 篩選維度 | Query Param | 允許值 | 預設值 |
|---------|-------------|-------|-------|
| 星等篩選 | `stars` | `5`、`4`、`3`、`2`、`1`、`low`（3 星以下） | 未指定（全部） |
| 有照片 | `hasPhoto` | `1`（有）、`0`（無） | 未指定（全部） |
| 排序 | `sort` | `newest`、`most_helpful`、`most_relevant` | `most_relevant` |
| 分頁 | `page` | 正整數，從 `1` 開始 | `1` |

**規則**：切換 FilterBar 時 `page` 重置為 `1`。

**規則**：`most_relevant` 排序 = `helpful_count DESC, created_at DESC`（MVP 假設；後續可加入 ML 相關性）。

**規則**：`most_helpful` 排序 = `helpful_count DESC, created_at DESC`（與 `most_relevant` 目前相同，保留未來差異化空間）。

### 6.5 分頁規則

| 規則 ID | 內容 |
|--------|------|
| PAGE-1 | 每頁顯示 **10 則**評論（MVP 假設；不含樓主回應，樓主回應跟隨父評論一起返回） |
| PAGE-2 | API 回應含 `total_count` 與 `has_next_page`，前端根據此渲染「載入更多」按鈕 |
| PAGE-3 | 樓主回應（`parent_review_id IS NOT NULL`）**不佔用分頁計數**，由 API 附加在父評論的 `replies` 陣列 |

### 6.6 未登入狀態導引

**GIVEN** Guest 點擊「撰寫評論」或「按讚」
**WHEN** 動作觸發
**THEN** 顯示對話框或跳轉至登入頁（`/Account/Login?returnUrl={current_url}`）；不送出 API request。

---

## §7 API Endpoint 草案（供 W4-AT-1 採用）

> **重要**：此為 BA 視角的業務邏輯草案，最終 API spec（OpenAPI / Swagger）由 AT 產出，AT 有責任對齊本文件的業務規則。命名規則、HTTP 狀態碼、request/response schema 以 AT `03_architecture/` 為準。

### 7.1 評論讀取

```
GET /api/products/{product_id}/reviews
```

**Query Params**（對應 §6.4 FilterBar）：

| 參數 | 型別 | 說明 |
|------|------|------|
| `stars` | `int?` | 篩選特定星數（1–5）；`low` = stars ≤ 3（MVP 簡化：low 不支援，只支援單一整數） |
| `hasPhoto` | `bool?` | `true` 只顯示有照片評論 |
| `sort` | `string?` | `newest` / `most_helpful` / `most_relevant`（預設 `most_relevant`） |
| `page` | `int?` | 頁碼，預設 `1` |
| `pageSize` | `int?` | MVP 固定 `10`（不開放 client 修改） |

**Response 200 OK**：

```json
{
  "product_id": "{{guid}}",
  "total_count": 128,
  "page": 1,
  "page_size": 10,
  "has_next_page": true,
  "items": [
    {
      "id": "{{guid}}",
      "user": { "id": "{{guid}}", "display_name": "旅遊達人 Wang", "avatar_url": "/uploads/avatar.jpg" },
      "rating": 5,
      "text": "超棒的旅遊體驗！...",
      "photos": ["/uploads/abc.jpg", "/uploads/def.jpg"],
      "helpful_count": 12,
      "created_at": "2026-05-20T10:00:00Z",
      "updated_at": "2026-05-20T10:00:00Z",
      "can_edit": false,
      "can_delete": false,
      "current_user_liked": false,
      "replies": [
        {
          "id": "{{guid}}",
          "user": { "id": "{{guid}}", "display_name": "eztravel 官方", "avatar_url": "/uploads/eztravel-logo.png" },
          "text": "感謝您的支持！我們持續為您服務。",
          "created_at": "2026-05-21T08:00:00Z",
          "is_owner_reply": true
        }
      ]
    }
  ]
}
```

**說明**：
- `can_edit`、`can_delete` 由 Server 端依當前使用者身份計算（Server-side 業務規則，非 client 自決）。
- `current_user_liked` 由 Server 查 `ReviewLike` 表計算。
- `replies` 只含直接樓主回應，最多 1 筆（見 §3.4 約束 2）。

---

### 7.2 評論聚合摘要

```
GET /api/products/{product_id}/reviews/summary
```

**Response 200 OK**：見 §4.4 聚合回應 JSON 結構。

---

### 7.3 新增評論

```
POST /api/products/{product_id}/reviews
```

**Request Body**：

```json
{
  "rating": 5,
  "text": "這次出遊非常順利，導遊專業...",
  "photos": ["/uploads/temp_abc.jpg"]
}
```

**業務規則（依序驗證）**：
1. 未登入 → `401`
2. `product_id` 不存在 → `404`
3. `rating` 不在 1–5 範圍 → `400`
4. `text` 字數 < 10 或 > 2000 → `400`
5. `photos` 張數 > 6 → `400`
6. 24 小時內已有評論（RL-1）→ `429`

**Response 201 Created**：回傳完整評論物件（格式同 `items[0]`）。

---

### 7.4 修改評論

```
PATCH /api/reviews/{review_id}
```

**Request Body**（所有欄位選填，只傳要改的）：

```json
{
  "rating": 4,
  "text": "修改後的評論...",
  "photos": ["/uploads/new_photo.jpg"]
}
```

**業務規則**：
1. 未登入 → `401`
2. 非評論擁有者（且非 Admin）→ `403`
3. 超過 24 小時時限 → `403`，`{ "error": "edit_window_expired" }`
4. 欄位驗證同新增規則

**Response 200 OK**：回傳更新後完整評論物件。

---

### 7.5 刪除評論（soft delete）

```
DELETE /api/reviews/{review_id}
```

**業務規則**：
1. 未登入 → `401`
2. 非評論擁有者且非 Admin → `403`
3. 設 `is_deleted = true`；不物理刪除。
4. 對應 `helpful_count` 聚合於下次計算時自動扣除（is_deleted 過濾）。

**Response 204 No Content**

---

### 7.6 按讚 / 取消讚

**按讚**：

```
POST /api/reviews/{review_id}/like
```

**業務規則**：
1. 未登入 → `401`
2. 對自己的評論按讚 → `400`，`{ "error": "cannot_like_own_review" }`
3. 已按讚 → `409`，`{ "error": "already_liked" }`
4. 寫入 `ReviewLike`，更新 `Review.helpful_count += 1`（Service 層觸發）

**Response 201 Created**

**取消讚**：

```
DELETE /api/reviews/{review_id}/like
```

**業務規則**：
1. 未登入 → `401`
2. 未按過讚 → `404`，`{ "error": "like_not_found" }`
3. 刪除 `ReviewLike`，更新 `Review.helpful_count -= 1`

**Response 204 No Content**

---

### 7.7 新增樓主回應

```
POST /api/reviews/{parent_review_id}/reply
```

**業務規則**：
1. 未登入 → `401`
2. 呼叫者非 Owner Role 或非此商品 Owner → `403`
3. `parent_review_id` 指向的評論本身已是樓主回應（多層 nested 禁止）→ `400`
4. 已有樓主回應存在 → `409`
5. Server 自動設 `parent_review_id = {parent_review_id}`、`user_id = current_user`、`rating = NULL`（樓主回應不含星等）

**Request Body**：

```json
{
  "text": "感謝您寶貴的意見！我們會持續改善..."
}
```

**Response 201 Created**：回傳樓主回應物件。

---

## §8 驗收標準（Acceptance Criteria）

| AC ID | 驗收項目 | 驗證方法 | 對應 AC |
|-------|---------|---------|--------|
| AC-BA-1 | `community_spec.md` 存在於 `01_requirements/`，行數 ≥ 300 | `wc -l community_spec.md` | AC-4 |
| AC-BA-2 | 7 個主要章節（`## §1` ~ `## §7`）全部存在 | `grep -E '^## §' community_spec.md \| wc -l` ≥ 7 | AC-4 |
| AC-BA-3 | §2 欄位清單中 `rating` 有 `CHECK (rating BETWEEN 1 AND 5)` 約束描述 | grep 驗證 | AC-5 |
| AC-BA-4 | §3 權限矩陣涵蓋 4 個角色（Guest/Member/Owner/Admin） | grep 驗證 | AC-5 |
| AC-BA-5 | §5 防濫用規則明確標示 RL-1（24 小時 rate limit）、LEN-1（字數上下限）、XSS-1 | grep 驗證 | AC-5 |
| AC-BA-6 | §7 含 6 個以上 API endpoint（GET reviews / summary / POST review / PATCH / DELETE / like） | 人工驗核 | AC-5、AC-6 |

---

## §9 下游交接提示

### 9.1 UIUX（W3-UIUX-*）

- 5 個 Atomic Primitives 定義於 §1.3，每個 Primitive 有互動狀態。
- `StarRating` 需支援兩種 Mode：`interactive`（ReviewComposer）與 `readonly`（ReviewCard）。
- `FilterBar` 篩選條件詳見 §6.4，URL query string 格式固定。
- 樓主回應視覺規格見 §6.2（底色、左側縱線、badge）。
- 照片顯示建議：grid 2×3，點擊展開 lightbox（MVP 可先用 `<a href>` 新視窗，不強制 lightbox）。

### 9.2 AT（W4-AT-1，`data_model.md`）

- `Review` entity 欄位定義見 §2.1，AT 需對齊命名（PascalCase 轉 snake_case 依 EF Core convention）。
- `ReviewLike` 唯一約束 `UNIQUE (review_id, user_id)` 需在 migration 中明確建立（不只靠 EF FK）。
- `ApplicationUser` 需加 `DisplayName` + `AvatarUrl` 欄位（§2.3）。
- 聚合快取使用 `IMemoryCache`，key 格式 `review_summary:{product_id}`（§4.3）。
- API endpoint route 草案見 §7，AT 確認後定案於 OpenAPI spec。

### 9.3 PG（W4-PG-4，Community feature 實作）

- 授權邏輯優先使用 `[Authorize]` 屬性 + Policy 組合，避免在 Controller 大量 if/else。
- 編輯時限（24 小時）於 `ReviewService.PatchAsync` 中實作，不在 Controller。
- Rate limit（RL-1）於 `ReviewService.CreateAsync` 中 DB 查詢實作，不用 in-memory。
- XSS strip 於 `ReviewService.SanitizeText` 私有方法集中處理，所有文字寫入前必過此方法。
- 圖片儲存路徑 `wwwroot/uploads/{guid}.{ext}` — 注意 Cloud Run 無狀態，此為 MVP 限制（詳 §5.3 IMG-4）。

---

*文件結束。如有需求矛盾或 MVP 假設需要調整，請依 §7 API 草案向 BA 提出 REWORK 卡，說明矛盾點與建議修正方向。*
