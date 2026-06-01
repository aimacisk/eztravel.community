# eztravel.community — data/ 目錄 JSON Schema 規範

> **Owner**: BA agent (T-eztcomm-20260601-W1-BA-1)
> **Version**: 1.0.0
> **建立日期**: 2026-06-01 (TST)
> **對應 Wish**: W-eztcomm-20260601-REBUILD
> **下游**: PG (W1-PG-1~7)、UIUX (W2)、AQ (W1-AQ-1)

---

## §1 目錄結構

```
projects/eztravel.community/data/
├── homepage/
│   ├── homepage.json
│   ├── homepage_screenshot.png
│   └── images/
├── 機票/
│   ├── 機票.json
│   ├── 機票_screenshot.png
│   └── images/
├── 旅館/
│   ├── 旅館.json
│   ├── 旅館_screenshot.png
│   └── images/
├── 團體/
│   ├── 團體.json
│   ├── 團體_screenshot.png
│   └── images/
├── 自由行/
│   ├── 自由行.json
│   ├── 自由行_screenshot.png
│   └── images/
├── 票券/
│   ├── 票券.json
│   ├── 票券_screenshot.png
│   └── images/
└── 景點/
    ├── 景點.json
    ├── 景點_screenshot.png
    └── images/
```

**命名規則**：JSON 檔名 = 資料夾名稱（中文），截圖檔名 = `{資料夾名稱}_screenshot.png`。

---

## §2 JSON 頂層結構（所有頁面共用）

```json
{
  "page": "string",
  "scraped_at": "ISO 8601 UTC string",
  "url": "string (完整 URL)",
  "sections": [
    {
      "id": "string (snake_case anchor id)",
      "type": "string (section 類型，見 §3)",
      "title": "string | null (選填，section 標題文字)",
      "items": []
    }
  ]
}
```

### 欄位規格

| 欄位 | 型別 | 必填 | 規則 |
|------|------|------|------|
| `page` | string | ✅ | 對應 7 個資料夾名稱之一（`homepage` / `機票` / `旅館` / `團體` / `自由行` / `票券` / `景點`） |
| `scraped_at` | string | ✅ | ISO 8601 UTC，格式 `YYYY-MM-DDTHH:mm:ss.sssZ` |
| `url` | string | ✅ | 爬取頁面的完整 URL |
| `sections` | array | ✅ | 至少 1 個元素；依頁面由上至下順序排列 |
| `sections[].id` | string | ✅ | snake_case，全頁唯一，見 §4 |
| `sections[].type` | string | ✅ | 限定值，見 §3 |
| `sections[].title` | string\|null | ❌ | 若畫面有明顯標題文字則填入，否則 null |
| `sections[].items` | array | ✅ | 空陣列 `[]` 可接受（若 section 無可列舉項目） |

---

## §3 Section Type 列舉值

| type 值 | 描述 | 常見出現頁面 |
|---------|------|------------|
| `hero_banner` | 輪播大圖 banner（首圖區） | homepage, all |
| `category_nav` | 分類導覽按鈕列（快速跳轉各分類） | homepage |
| `search_bar` | 搜尋輸入框區域 | 機票, 旅館, 團體, 自由行 |
| `promo_section` | 促銷活動卡片區 | all |
| `product_list` | 商品卡片列表（可購買項目） | all |
| `featured_items` | 編輯精選／熱銷推薦 | all |
| `destination_grid` | 目的地圖片格狀導覽 | 機票, 旅館, 團體, 自由行, 景點 |
| `quick_links` | 快速連結按鈕列 | homepage, 票券 |
| `theme_section` | 主題旅遊分類（如：溫泉旅遊、親子旅遊） | 旅館, 景點 |
| `footer_links` | 頁腳連結區 | all |
| `ad_banner` | 廣告橫幅（非主要內容） | all |

> **PG 注意**：若頁面出現上表未定義的區塊，以 `type: "other"` 記錄，並在 `title` 欄位加以描述。

---

## §4 Anchor ID 命名規則與各頁預設清單

### 規則

- **格式**：snake_case，全小寫，底線分隔
- **唯一性**：同一 JSON 檔內不重複
- **命名原則**：`{功能描述}` 或 `{位置}_{功能描述}`，反映畫面實際區塊意義

### 各頁預設 Anchor ID（非強制，以實際抓取為準）

#### homepage（首頁）

| anchor id | 對應區塊 |
|-----------|---------|
| `hero_banner` | 首頁大圖輪播 |
| `category_nav` | 主要分類導覽（機票/旅館/團體...） |
| `hot_deals` | 熱門促銷活動 |
| `featured_products` | 精選商品推薦 |
| `destination_picks` | 熱門目的地 |
| `campaign_banner` | 活動廣告橫幅 |
| `quick_links` | 快速服務連結 |

#### 機票

| anchor id | 對應區塊 |
|-----------|---------|
| `search_bar` | 機票搜尋框（出發地/目的地/日期） |
| `promo_fares` | 特惠票價促銷 |
| `hot_routes` | 熱門航線 |
| `airline_section` | 航空公司專區 |
| `visa_info` | 簽證資訊連結 |

#### 旅館

| anchor id | 對應區塊 |
|-----------|---------|
| `search_bar` | 住宿搜尋框（地點/日期/人數） |
| `featured_hotels` | 精選飯店推薦 |
| `destination_grid` | 熱門住宿目的地 |
| `theme_section` | 主題住宿（溫泉/親子/海景） |
| `promo_section` | 限時優惠 |

#### 團體

| anchor id | 對應區塊 |
|-----------|---------|
| `search_bar` | 行程搜尋（目的地/出發地/日期） |
| `hero_banner` | 團體旅遊主視覺 |
| `destination_grid` | 熱門目的地格狀導覽 |
| `featured_tours` | 精選行程推薦 |
| `promo_section` | 限時優惠行程 |

#### 自由行

| anchor id | 對應區塊 |
|-----------|---------|
| `search_bar` | 機加酒搜尋框 |
| `hero_banner` | 自由行主視覺 |
| `hot_packages` | 熱銷機加酒套裝 |
| `destination_grid` | 熱門目的地 |
| `airline_section` | 航空公司專區 |

#### 票券

| anchor id | 對應區塊 |
|-----------|---------|
| `hero_banner` | 票券主視覺 |
| `category_nav` | 票券分類（門票/餐券/交通/一日遊） |
| `hot_tickets` | 熱銷票券 |
| `promo_section` | 限時優惠票券 |
| `theme_section` | 主題活動票券 |

#### 景點

| anchor id | 對應區塊 |
|-----------|---------|
| `hero_banner` | 景點主視覺 |
| `search_bar` | 景點/行程搜尋 |
| `featured_items` | 精選景點推薦 |
| `destination_grid` | 熱門景點目的地 |
| `theme_section` | 主題景點分類 |
| `quick_links` | 相關服務快速連結 |

---

## §5 items 元素結構

每個 `items` 陣列的元素為物件，所有欄位均**選填**，由 PG 依實際抓取到的內容填入。

```json
{
  "text": "string | null",
  "image_url": "string | null",
  "link_url": "string | null",
  "price": "string | null",
  "badge": "string | null",
  "description": "string | null"
}
```

### items 欄位說明

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `text` | string\|null | 主要文字（標題/名稱/按鈕文字） | `"日本東京 5 天 4 夜"` |
| `image_url` | string\|null | 圖片 URL（相對路徑或絕對 URL） | `"images/homepage_banner_01.jpg"` |
| `link_url` | string\|null | 點擊後跳轉的連結 URL | `"https://vacation.eztravel.com.tw/trip/123"` |
| `price` | string\|null | 價格文字（保留原始格式含單位） | `"TWD 25,900 起"` |
| `badge` | string\|null | 標籤/角標文字 | `"限時特價"`, `"熱銷中"`, `"最後幾席"` |
| `description` | string\|null | 補充說明文字 | `"含來回機票+4星飯店3晚"` |

> **AC-items-01**（AQ 驗收）：GIVEN 一個 item，WHEN 檢查其欄位，THEN 所有欄位值若非 null 則必須為非空字串。
> **AC-items-02**（AQ 驗收）：GIVEN 一個 item，WHEN 欄位值為空，THEN 必須記錄為 JSON `null`，禁用空字串 `""`。

---

## §6 圖檔命名規範

### 命名格式

```
{category}_{type}_{index}.{ext}
```

### 欄位定義

| 欄位 | 規則 | 合法值範例 |
|------|------|----------|
| `category` | 資料夾名稱的英文/拼音表示 | `homepage`, `flight`, `hotel`, `group`, `freetour`, `ticket`, `attraction` |
| `type` | 圖片所屬 section type（對應 §3） | `banner`, `promo`, `product`, `destination`, `nav_icon`, `theme` |
| `index` | 零補位兩位數字，從 `01` 開始 | `01`, `02`, ..., `99` |
| `ext` | 原始格式 | `jpg`, `png`, `webp` |

### Category 對應表

| 資料夾名稱 | category 值 |
|-----------|------------|
| homepage | `homepage` |
| 機票 | `flight` |
| 旅館 | `hotel` |
| 團體 | `group` |
| 自由行 | `freetour` |
| 票券 | `ticket` |
| 景點 | `attraction` |

### 範例

| 圖檔路徑 | 說明 |
|---------|------|
| `data/homepage/images/homepage_banner_01.jpg` | 首頁第 1 張輪播 banner |
| `data/homepage/images/homepage_banner_02.jpg` | 首頁第 2 張輪播 banner |
| `data/homepage/images/homepage_nav_icon_01.png` | 首頁分類導覽第 1 個圖示 |
| `data/機票/images/flight_promo_01.jpg` | 機票頁第 1 張促銷圖 |
| `data/旅館/images/hotel_destination_01.jpg` | 旅館頁第 1 個目的地圖 |
| `data/景點/images/attraction_theme_01.jpg` | 景點頁第 1 個主題圖 |

> **AC-naming-01**（AQ 驗收）：GIVEN `images/` 目錄下所有圖檔，WHEN 以正規表達式 `^(homepage|flight|hotel|group|freetour|ticket|attraction)_\w+_\d{2}\.(jpg|png|webp)$` 驗證，THEN 全部符合命名規範。

---

## §7 各頁完整 JSON 範例

### 7.1 homepage.json 節錄

```json
{
  "page": "homepage",
  "scraped_at": "2026-06-01T08:00:00.000Z",
  "url": "https://www.eztravel.com.tw/",
  "sections": [
    {
      "id": "hero_banner",
      "type": "hero_banner",
      "title": null,
      "items": [
        {
          "text": "夏日限定！東南亞機加酒特賣",
          "image_url": "images/homepage_banner_01.jpg",
          "link_url": "https://packages.eztravel.com.tw/",
          "price": null,
          "badge": "限時特賣",
          "description": null
        }
      ]
    },
    {
      "id": "category_nav",
      "type": "category_nav",
      "title": null,
      "items": [
        {
          "text": "搜機票",
          "image_url": "images/homepage_nav_icon_01.png",
          "link_url": "https://flight.eztravel.com.tw/",
          "price": null,
          "badge": null,
          "description": null
        },
        {
          "text": "找住宿",
          "image_url": "images/homepage_nav_icon_02.png",
          "link_url": "https://hotel.eztravel.com.tw/",
          "price": null,
          "badge": null,
          "description": null
        }
      ]
    },
    {
      "id": "featured_products",
      "type": "featured_items",
      "title": "熱銷行程推薦",
      "items": [
        {
          "text": "日本東京 5 天 4 夜",
          "image_url": "images/homepage_product_01.jpg",
          "link_url": "https://vacation.eztravel.com.tw/trip/12345",
          "price": "TWD 25,900 起",
          "badge": "熱銷",
          "description": "含來回機票+4星飯店3晚"
        }
      ]
    }
  ]
}
```

### 7.2 機票.json 節錄

```json
{
  "page": "機票",
  "scraped_at": "2026-06-01T08:05:00.000Z",
  "url": "https://flight.eztravel.com.tw/",
  "sections": [
    {
      "id": "search_bar",
      "type": "search_bar",
      "title": null,
      "items": [
        {
          "text": "出發地",
          "image_url": null,
          "link_url": null,
          "price": null,
          "badge": null,
          "description": "搜尋框佔位文字：請選擇出發城市"
        }
      ]
    },
    {
      "id": "hot_routes",
      "type": "product_list",
      "title": "熱門航線",
      "items": [
        {
          "text": "台北 → 東京 (NRT)",
          "image_url": "images/flight_promo_01.jpg",
          "link_url": "https://flight.eztravel.com.tw/tpe-nrt",
          "price": "TWD 8,900 起",
          "badge": "特價",
          "description": null
        }
      ]
    }
  ]
}
```

---

## §8 驗收標準（AC）

| AC | 驗收條件 | 驗證方式 |
|----|---------|---------|
| AC-schema-01 | GIVEN `data/{category}/{category}.json`，WHEN 以 `page`/`scraped_at`/`url`/`sections` 4 個頂層欄位驗證，THEN 全部存在且型別正確 | AQ 讀 JSON + Python 型別檢查 |
| AC-schema-02 | GIVEN `sections` 陣列每個元素，WHEN 驗證 `id`/`type`/`items` 欄位，THEN 全部存在；`title` 存在（可 null） | AQ 程式驗證 |
| AC-schema-03 | GIVEN `sections[].id`，WHEN 與同一 JSON 檔內所有 id 對比，THEN 無重複 | AQ 程式驗證 |
| AC-schema-04 | GIVEN `sections[].type`，WHEN 對照 §3 type 列舉，THEN 值為列舉值之一或 `"other"` | AQ 程式驗證 |
| AC-schema-05 | GIVEN `items[]` 每個元素，WHEN 檢查值，THEN 非 null 欄位為非空字串（即不含 `""` 空字串） | AQ 程式驗證 |
| AC-schema-06 | GIVEN 7 個 JSON 檔，WHEN 計數，THEN 全部 7 個存在：`homepage.json` / `機票.json` / `旅館.json` / `團體.json` / `自由行.json` / `票券.json` / `景點.json` | AQ Glob 驗證 |
| AC-schema-07 | GIVEN `data/{category}/images/` 目錄，WHEN 以命名規則 `^{category}_{type}_{dd}.{ext}$` 驗證，THEN 全部符合 §6 規範 | AQ 正規表達式批次驗證 |
| AC-schema-08 | GIVEN 每個 JSON 中 `items[].image_url` 非 null 值，WHEN 對應到 `images/` 目錄，THEN 檔案物理存在 | AQ 程式驗證 |

---

## §9 合規性與注意事項

1. **著作權**：`images/` 內圖片為從 eztravel.com.tw 爬取的公開展示圖片，僅用於學習/展示目的，不得用於商業用途。
2. **robots.txt**：爬取前應確認 `https://www.eztravel.com.tw/robots.txt` 的 Disallow 規則，爬取速率控制在 1 req/3s 以上間隔。
3. **個人資料**：若頁面出現使用者評論或個人資料，不得納入 `items`。
4. **動態內容**：所有商品價格、促銷內容依爬取當時快照為準，非即時資料，不作為商業報價依據。
