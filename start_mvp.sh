#!/bin/bash

echo "🚀 Starting Real-time Marketing Analytics MVP"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker compose down

# Start all services
echo "🔧 Starting services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker compose ps

# Wait a bit more for Flink to be ready
echo "⏳ Waiting for Flink to be ready..."
sleep 20

# Show logs
echo "📋 Recent logs:"
docker compose logs --tail=20

echo ""
echo "✅ MVP is starting up!"
echo ""
echo "🌐 Access points:"
echo "   Dashboard: http://localhost:8503"
echo "   Kafka:     localhost:9092"
echo ""
echo "📊 Monitor logs:"
echo "   docker compose logs -f producer"
echo "   docker compose logs -f flink-job"
echo "   docker compose logs -f dashboard"
echo ""
echo "🛑 To stop: docker compose down"
