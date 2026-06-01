# Multi-stage build for ASP.NET Core 8 MVC — eztravel.Community
# Target: GCP Cloud Run (linux/amd64)

ARG TARGETPLATFORM=linux/amd64

# ============================================================
# Stage 1: Build
# ============================================================
FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj first for layer cache
COPY 04_src/eztravel.Community/eztravel.Community.sln ./
COPY 04_src/eztravel.Community/eztravel.Community.Web/eztravel.Community.Web.csproj eztravel.Community.Web/
COPY 04_src/eztravel.Community/eztravel.Community.Core/eztravel.Community.Core.csproj eztravel.Community.Core/
COPY 04_src/eztravel.Community/eztravel.Community.Infrastructure/eztravel.Community.Infrastructure.csproj eztravel.Community.Infrastructure/
COPY 04_src/eztravel.Community/eztravel.Community.Tests/eztravel.Community.Tests.csproj eztravel.Community.Tests/

RUN dotnet restore eztravel.Community.Web/eztravel.Community.Web.csproj

# Copy full source
COPY 04_src/eztravel.Community/ ./

RUN dotnet publish eztravel.Community.Web/eztravel.Community.Web.csproj \
    -c Release \
    -o /app/publish \
    --no-restore \
    /p:UseAppHost=false

# ============================================================
# Stage 2: Runtime
# ============================================================
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Install wget for HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/*

# Copy published artifacts
COPY --from=build /app/publish .

# Copy data/ folder into wwwroot so static images and JSON are served
COPY data/ ./wwwroot/data/

# Cloud Run defaults
ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "eztravel.Community.Web.dll"]
