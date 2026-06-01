# Figma Deliverables — T-eztcomm-20260601-W2-UIUX-9

> 此檔為完整 Figma 區段清冊，作為設計成品物流單。
> 讓下游 PG / QA / AT / admin 可直接點開 Figma 對應區段核對。

**任務 ID**：T-eztcomm-20260601-W2-UIUX-9
**完成時間**：2026-06-02
**負責 Agent**：uiux

---

## Figma 檔案資訊

| 屬性 | 值 |
|------|----|
| **fileKey** | `6XmYJOpiSXab2gtGlmWtks` |
| **檔案名稱** | eztravel.community |
| **pageId** | `88:2` |
| **pageName** | Product Detail |

---

## Variant Set（ComponentSet）

| 屬性 | 值 |
|------|----|
| **元件集名稱** | Product Detail |
| **nodeId** | `88:471` |
| **類型** | COMPONENT_SET |
| **尺寸** | 3000 × 3280 px（2×2 格線，X gap 120px，Y gap 80px）|
| **Figma URL** | https://www.figma.com/design/6XmYJOpiSXab2gtGlmWtks?node-id=88:471 |

---

## 4 Variant 明細

| Variant | Property | nodeId | 位置（Set 內） | 尺寸 | Hero 漸層色 | Figma URL |
|---------|----------|--------|---------------|------|------------|-----------|
| **GroupTour** | `Category=GroupTour` | `88:3` | (0, 0) | 1440×1600 | 綠 #0C9251 → #063050 | https://www.figma.com/design/6XmYJOpiSXab2gtGlmWtks?node-id=88:3 |
| **FreeTour** | `Category=FreeTour` | `88:123` | (1560, 0) | 1440×1600 | 藍 #0075A5 → #004566 | https://www.figma.com/design/6XmYJOpiSXab2gtGlmWtks?node-id=88:123 |
| **Hotel** | `Category=Hotel` | `88:243` | (0, 1680) | 1440×1600 | 紫 #6645AE → #391F6E | https://www.figma.com/design/6XmYJOpiSXab2gtGlmWtks?node-id=88:243 |
| **Ticket** | `Category=Ticket` | `88:355` | (1560, 1680) | 1440×1600 | 橙 #DD6A00 → #994400 | https://www.figma.com/design/6XmYJOpiSXab2gtGlmWtks?node-id=88:355 |

---

## 各 Variant 共用區段結構

差異僅在 Hero 漸層色、麵包屑品類、標題、價格、細節文字。

| 區段 | y | 高度 | 內容摘要 |
|------|---|------|----------|
| **Hero** | 0 | 400px | 麵包屑、產品標題、★×5（4.8/1,234 評價）、起價、立即預訂 + 詢問行程按鈕、產品主圖 |
| **MainContent** | 400 | 500px | 左欄（產品特色 + 細節說明表格）、右欄 BookingCard（日期/人數/預估費用/預訂）|
| **Community_Area** | 900 | 380px | 旅客評價、RatingDistribution 5 bars、2×ReviewCard、FilterBar 5 chips |
| **Recommendation** | 1280 | 220px | 你可能也喜歡 + 4×MiniCard（圖、目的地、綠色起價）|
| **Footer** | 1500 | 100px | 深色背景、Copyright EZTravel 易遊網、客服電話、時段 |

---

## 對應 views_schema.json

```
views.ProductDetail (component_id: "88:471")
  ├── variant: Category=GroupTour  (node_id: "88:3")
  ├── variant: Category=FreeTour   (node_id: "88:123")
  ├── variant: Category=Hotel      (node_id: "88:243")
  └── variant: Category=Ticket     (node_id: "88:355")
```

---

## 視覺自驗結果（8 維度）

| Variant | nodeId | ①比例 | ②密度 | ③層級 | ④對齊 | ⑤樣式 | ⑥容器 | ⑦不重疊 | ⑧文字 | 判定 |
|---------|--------|-------|-------|-------|-------|-------|-------|---------|-------|------|
| GroupTour | 88:3 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **PASS** |
| FreeTour | 88:123 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **PASS** |
| Hotel | 88:243 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **PASS** |
| Ticket | 88:355 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **PASS** |

**全 4 variant 通過。無 [ISSUE] 項目。**
