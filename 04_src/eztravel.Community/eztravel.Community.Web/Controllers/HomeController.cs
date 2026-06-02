using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using eztravel.Community.Web.Models;
using EzTravel.Community.Web.Services;

namespace EzTravel.Community.Web.Controllers;

public class HomeController : Controller
{
    private readonly ILogger<HomeController> _logger;
    private readonly IPageDataLoader _loader;

    public HomeController(ILogger<HomeController> logger, IPageDataLoader loader)
    {
        _logger = logger;
        _loader = loader;
    }

    public IActionResult Index()
    {
        var model = _loader.Load("homepage");
        return View(model);
    }

    public IActionResult Privacy() => View();

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    [Route("Home/Error/{statusCode:int?}")]
    [Route("Home/Error")]
    public IActionResult Error(int? statusCode = null)
    {
        if (statusCode.HasValue)
            ViewData["StatusCode"] = statusCode.Value;
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
