#!/bin/bash

# Deployment script for Web Scraper Chat Agent
# Usage: ./deploy.sh [local|production]

set -e

ENV=${1:-local}

echo "Deploying in $ENV mode..."

if [ "$ENV" = "production" ]; then
    echo "Using production configuration (nginx.prod.conf with SSL)"
    
    # Check if SSL certificates exist
    if [ ! -f "/etc/letsencrypt/live/demo.feirto.com/fullchain.pem" ]; then
        echo "WARNING: SSL certificates not found!"
        echo "Run the following to obtain certificates:"
        echo ""
        echo "sudo certbot certonly --webroot \\"
        echo "  -w /var/www/certbot \\"
        echo "  -d demo.feirto.com \\"
        echo "  --email your-email@example.com \\"
        echo "  --agree-tos"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    docker compose down 2>/dev/null || true
    docker compose -f docker-compose.prod.yml up -d --build
    
    echo "Production deployment complete"
    echo "Access at: https://demo.feirto.com"
    
elif [ "$ENV" = "local" ]; then
    echo "Using local configuration (nginx.conf without SSL)"
    
    docker compose -f docker-compose.prod.yml down 2>/dev/null || true
    docker compose up -d --build
    
    echo "Local deployment complete"
    echo "Access at: http://localhost"
    
else
    echo "Invalid environment: $ENV"
    echo "Usage: ./deploy.sh [local|production]"
    exit 1
fi

echo ""
echo "Service Status:"
docker ps --filter "name=web_scraper" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "View logs:"
if [ "$ENV" = "production" ]; then
    echo "  docker compose -f docker-compose.prod.yml logs -f"
else
    echo "  docker compose logs -f"
fi
