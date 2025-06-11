#!/bin/bash

# GTD Backend Startup Script
# This script starts the FastAPI backend server with Supabase integration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting GTD Backend...${NC}"

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating .venv...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if requirements are installed
echo -e "${BLUE}📋 Checking dependencies...${NC}"
if ! python -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found in project root.${NC}"
    echo -e "${YELLOW}💡 Please create a .env file with your Supabase credentials:${NC}"
    echo "SUPABASE_URL=https://your-project.supabase.co"
    echo "SUPABASE_SERVICE_ROLE_KEY=your-service-role-key"
    echo "DEFAULT_USER_ID=00000000-0000-0000-0000-000000000001"
    exit 1
fi

# Navigate to backend directory
cd src/backend

# Check if backend .env exists and has Supabase config
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: Backend .env file not found.${NC}"
    echo -e "${YELLOW}💡 Please ensure src/backend/.env exists with Supabase configuration.${NC}"
    exit 1
fi

# Test database connection
echo -e "${BLUE}🔌 Testing database connection...${NC}"
if python3 -c "
from app.config import get_settings
from app.database import async_session_maker
import asyncio

async def test_connection():
    try:
        async with async_session_maker() as session:
            from sqlalchemy import text
            result = await session.execute(text('SELECT 1'))
            return result.scalar() == 1
    except Exception as e:
        print(f'Connection error: {e}')
        return False

result = asyncio.run(test_connection())
exit(0 if result else 1)
" 2>/dev/null; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${YELLOW}⚠️  Database connection failed, but starting server anyway...${NC}"
fi

# Start the server
echo -e "${GREEN}🌟 Starting FastAPI server on http://localhost:8000${NC}"
echo -e "${BLUE}📖 API Documentation: http://localhost:8000/api/docs${NC}"
echo -e "${BLUE}🔄 Alternative docs: http://localhost:8000/api/redoc${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
echo ""

# Run the server with auto-reload in development
python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir app \
    --log-level info