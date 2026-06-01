using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Enums;
using EzTravel.Community.Core.Interfaces.Repositories;
using EzTravel.Community.Core.Interfaces.Services;

namespace EzTravel.Community.Web.Services;

public class ProductService : IProductService
{
    private readonly IProductRepository _products;

    public ProductService(IProductRepository products) => _products = products;

    public Task<Product?> GetProductAsync(int id, CancellationToken ct = default)
        => _products.GetByIdAsync(id, ct);

    public Task<IReadOnlyList<Product>> GetProductsByCategoryAsync(ProductCategory category, CancellationToken ct = default)
        => _products.GetByCategoryAsync(category, ct);
}
