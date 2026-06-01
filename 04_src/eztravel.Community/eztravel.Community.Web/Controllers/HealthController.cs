using Microsoft.AspNetCore.Mvc;

namespace EzTravel.Community.Web.Controllers;

[ApiController]
[Route("[controller]")]
public class HealthController : ControllerBase
{
    [HttpGet]
    public IActionResult Get() => Ok("OK");
}
