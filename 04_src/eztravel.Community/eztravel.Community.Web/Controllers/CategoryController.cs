using EzTravel.Community.Web.Services;
using Microsoft.AspNetCore.Mvc;

namespace EzTravel.Community.Web.Controllers;

[Route("category")]
public class CategoryController : Controller
{
    private readonly IPageDataLoader _loader;

    public CategoryController(IPageDataLoader loader)
    {
        _loader = loader;
    }

    [HttpGet("{slug}")]
    public IActionResult Show(string slug)
    {
        var model = _loader.Load(slug);
        if (model is null) return NotFound();
        return View(model);
    }

    [HttpGet("flight")]
    public IActionResult Flight()
    {
        var model = _loader.Load("flight");
        if (model is null) return NotFound();
        return View(model);
    }

    [HttpGet("hotel")]
    public IActionResult Hotel()
    {
        var model = _loader.Load("hotel");
        if (model is null) return NotFound();
        return View(model);
    }

    // T-eztcomm-20260602-W6PG-CAT-GROUPTOUR: 團體分類頁獨立 route
    // 需要明確 route 因為 class-level [Route("category")] 取代 conventional routing
    [Route("Category/GroupTour")]
    [HttpGet]
    public IActionResult GroupTour()
    {
        var model = _loader.Load("grouptour");
        if (model is null) return NotFound();
        return View("GroupTour", model);
    }

    [HttpGet("freetour")]
    public IActionResult FreeTour()
    {
        var model = _loader.Load("freetour");
        if (model is null) return NotFound();
        return View(model);
    }

    // T-eztcomm-20260602-W6PG-CAT-TICKET: 票券分類頁獨立 route (W4-REBUILD)
    // 明確 route 對齊 GroupTour 模式：class-level [Route("category")] 覆蓋 conventional routing
    [Route("Category/Ticket")]
    [HttpGet]
    public IActionResult Ticket()
    {
        var model = _loader.Load("ticket");
        if (model is null) return NotFound();
        return View("Ticket", model);
    }
}
