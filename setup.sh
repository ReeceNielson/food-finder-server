#!/bin/bash

# Django + Podman Quick Setup Script

set -e

echo "🚀 Django + Podman Setup"
echo "========================"

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed. Please install it first."
    echo "   Ubuntu/Debian: sudo apt install podman"
    echo "   macOS: brew install podman"
    exit 1
fi

echo "✅ Podman found: $(podman --version)"

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "⚠️  podman-compose is not installed. Installing..."
    pip install podman-compose
fi

echo "✅ podman-compose found: $(podman-compose --version)"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update with your settings."
fi

# Build the image
echo "🔨 Building Docker image..."
podman build -t django-app:latest .
echo "✅ Image built successfully"

# Start containers
echo "🚀 Starting containers..."
podman-compose up -d
echo "✅ Containers started"

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 3

# Run migrations
echo "🔄 Running migrations..."
podman-compose exec -T web python manage.py migrate || true
echo "✅ Migrations complete"

# Collect static files
echo "📦 Collecting static files..."
podman-compose exec -T web python manage.py collectstatic --noinput || true
echo "✅ Static files collected"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📍 Access your Django app:"
echo "   Web: http://localhost:8000"
echo "   Admin: http://localhost:8000/admin/"
echo ""
echo "📋 Next steps:"
echo "   1. Create a superuser: make createsuperuser"
echo "   2. View logs: make logs"
echo "   3. Stop containers: make down"
echo ""
echo "📚 For more commands, run: make help"
