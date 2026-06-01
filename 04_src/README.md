# 04_src — 原始碼與單元測試

> **Owner**: PG agent
> **Phase**: IMPLEMENTATION
> 由 PG agent 撰寫,PM 代為提交。**編譯必須通過才能交付**(自帶修復迴圈)。

## 結構規劃 (eztravel.community rebuild 2026-06-01)

```
04_src/
└── eztravel.Community/
    ├── eztravel.Community.sln
    ├── eztravel.Community.Web/              # ASP.NET Core MVC + Razor 主專案
    │   ├── Controllers/
    │   ├── Views/
    │   ├── wwwroot/
    │   └── Program.cs                       # Serilog stdout JSON
    ├── eztravel.Community.Core/             # Domain entities + interfaces
    ├── eztravel.Community.Infrastructure/   # EF Core + Npgsql + Identity
    └── eztravel.Community.Tests/            # xUnit + WebApplicationFactory
```

## 殘留清理 (2026-06-01)

`04_src/eztravel.Community.Api/` 為舊版殘留空殼,Windows file lock 暫無法刪除。
新版 .NET solution 將建於 `04_src/eztravel.Community/`,與舊空殼平行存在。
待 Windows 釋放 lock 後 (重啟系統或 antimalware 掃描完成) 由 admin 補刪。

## 約束

- 變更 API spec → 需透過 PM 退回 AT,**PG 不得擅改**
- 變更業務規則 → 需透過 PM 退回 BA,**PG 不得擅改**
- 每次提交必含對應 unit test
- 不寫 WHAT 註解(命名表達);只在 WHY 非顯而易見時寫
