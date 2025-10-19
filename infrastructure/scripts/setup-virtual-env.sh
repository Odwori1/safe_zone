#!/bin/bash

echo "🔧 Setting up Safe Zone Virtual Environment"
echo "==========================================="

# Check if we're in the right directory
if [ ! -f "backend/package.json" ]; then
    echo "❌ Error: Must run from safe_zone root directory"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2)
MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1)

if [ $MAJOR_VERSION -lt 18 ]; then
    echo "❌ Error: Node.js 18 or higher required. Current: $NODE_VERSION"
    exit 1
fi

echo "✅ Node.js version: $NODE_VERSION"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Installing..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
fi

# Start PostgreSQL service
sudo service postgresql start

# Setup PostgreSQL database and user
echo "🗄️  Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE safe_zone;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER safe_zone_user WITH PASSWORD 'safe_zone_password_2024';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE safe_zone TO safe_zone_user;" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER safe_zone_user CREATEDB;" 2>/dev/null || true

echo "✅ PostgreSQL database configured"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
npm install

if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed"
else
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p uploads

# Set proper permissions
chmod 755 logs/
chmod 755 uploads/

cd ..

echo ""
echo "🎉 Virtual environment setup completed!"
echo ""
echo "To start the development server:"
echo "  cd backend && npm run dev"
echo ""
echo "To test the setup:"
echo "  curl http://localhost:3000/health"
echo ""
