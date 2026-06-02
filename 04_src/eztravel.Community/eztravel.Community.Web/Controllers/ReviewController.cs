using EzTravel.Community.Core.Enums;
using EzTravel.Community.Web.Models.ViewModels;
using Microsoft.AspNetCore.Mvc;

namespace EzTravel.Community.Web.Controllers;

/// <summary>
/// MVC controller for the Community Review module UI.
/// Provides a /Review/Submit test page for Playwright visual validation.
/// NOTE: API endpoints live in ReviewsController (ApiController).
/// </summary>
public class ReviewController : Controller
{
    /// <summary>
    /// GET /Review/Submit?productId=1
    /// Returns a full product-detail page with the community module visible.
    /// Used by Playwright visual tests (AC-W6-01 ~ AC-W6-04).
    /// </summary>
    [HttpGet]
    public IActionResult Submit(int productId = 1)
    {
        var vm = new ProductDetailViewModel
        {
            Id            = productId,
            Name          = "北海道 5 日自由行精選",
            Description   = "包含來回機票、四星飯店三連泊、道地溫泉體驗，讓您盡情感受北海道的自然美景與道地美食。",
            Category      = ProductCategory.FreeTour,
            ImageUrl      = "/images/sample-hokkaido.jpg",
            ReviewCount   = 128,
            AverageRating = 4.6,
        };

        return View(vm);
    }
}
