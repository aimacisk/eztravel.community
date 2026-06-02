using Microsoft.AspNetCore.Mvc;

namespace EzTravel.Community.Web.Controllers;

/// <summary>
/// 自訂錯誤頁 Controller（T-eztcomm-20260602-R8）
/// 由 UseStatusCodePagesWithReExecute("/Error/{0}") 呼叫，攔截 4xx/5xx 狀態碼。
/// </summary>
[Route("Error/{statusCode:int}")]
public class ErrorController : Controller
{
    [HttpGet]
    public IActionResult Index(int statusCode)
    {
        ViewData["StatusCode"] = statusCode;
        return View("Error"); // → Views/Shared/Error.cshtml
    }
}
