# Deployment script for Web Scraper Chat Agent
# Usage: .\deploy.ps1 [local|production]

param(
    [Parameter(Position=0)]
    [ValidateSet("local", "production")]
    [string]$Environment = "local"
)

Write-Host "Deploying in $Environment mode..." -ForegroundColor Cyan

if ($Environment -eq "production") {
    Write-Host "Using production configuration (nginx.prod.conf with SSL)" -ForegroundColor Yellow
    Write-Host "Note: SSL certificates should be configured on your production server"
    
    docker compose down 2>$null
    docker compose -f docker-compose.prod.yml up -d --build
    
    Write-Host "`nProduction deployment complete" -ForegroundColor Green
    Write-Host "Access at: https://demo.feirto.com"
    
} else {
    Write-Host "Using local configuration (nginx.conf without SSL)" -ForegroundColor Yellow
    
    docker compose -f docker-compose.prod.yml down 2>$null
    docker compose up -d --build
    
    Write-Host "`nLocal deployment complete" -ForegroundColor Green
    Write-Host "Access at: http://localhost"
}

Write-Host "`nService Status:"
docker ps --filter "name=web_scraper" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`nView logs:"
if ($Environment -eq "production") {
    Write-Host "  docker compose -f docker-compose.prod.yml logs -f"
} else {
    Write-Host "  docker compose logs -f"
}
