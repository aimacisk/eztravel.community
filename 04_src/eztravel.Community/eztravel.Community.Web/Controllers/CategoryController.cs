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
}
