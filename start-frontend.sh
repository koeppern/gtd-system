#!/bin/bash

# GTD Frontend Startup Script
# This script starts the Next.js frontend development server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting GTD Frontend...${NC}"

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "src/frontend" ]; then
    echo -e "${RED}❌ Error: Frontend directory 'src/frontend' not found.${NC}"
    echo -e "${YELLOW}💡 Available options:${NC}"
    
    # Check for alternative frontend directories
    if [ -d "src/frontend" ]; then
        echo -e "${YELLOW}📁 Found: src/frontend${NC}"
        echo -e "${BLUE}🔄 Using  frontend...${NC}"
        cd src/frontend
    elif [ -d "frontend" ]; then
        echo -e "${YELLOW}📁 Found: frontend${NC}"
        echo -e "${BLUE}🔄 Using frontend directory...${NC}"
        cd frontend
    else
        echo -e "${RED}❌ No frontend directory found. Please create one of:${NC}"
        echo "  - src/frontend"
        echo "  - src/frontend" 
        echo "  - frontend"
        exit 1
    fi
else
    cd src/frontend
fi

# Check if it's a Node.js project
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found. This doesn't appear to be a Node.js project.${NC}"
    echo -e "${YELLOW}💡 Please ensure you're in a valid frontend directory with package.json${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Error: Node.js is not installed.${NC}"
    echo -e "${YELLOW}💡 Please install Node.js from https://nodejs.org/${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Error: npm is not installed.${NC}"
    echo -e "${YELLOW}💡 Please install npm (usually comes with Node.js)${NC}"
    exit 1
fi

# Display Node.js version
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo -e "${BLUE}📦 Node.js version: ${NODE_VERSION}${NC}"
echo -e "${BLUE}📦 npm version: ${NPM_VERSION}${NC}"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
    npm install
fi

# Check if .env.local exists for Next.js
if [ ! -f ".env.local" ] && [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No environment file found. Creating .env.local...${NC}"
    cat > .env.local << EOF
# GTD Frontend Environment Variables
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Development settings
NODE_ENV=development
EOF
    echo -e "${GREEN}✅ Created .env.local with default settings${NC}"
fi

# Detect the frontend framework and start command
if grep -q "next" package.json; then
    echo -e "${GREEN}🔍 Detected Next.js project${NC}"
    START_COMMAND="npm run dev"
elif grep -q "react-scripts" package.json; then
    echo -e "${GREEN}🔍 Detected Create React App project${NC}"
    START_COMMAND="npm start"
elif grep -q "vite" package.json; then
    echo -e "${GREEN}🔍 Detected Vite project${NC}"
    START_COMMAND="npm run dev"
else
    echo -e "${YELLOW}⚠️  Unknown frontend framework. Trying 'npm run dev'...${NC}"
    START_COMMAND="npm run dev"
fi

# Check if backend is running
echo -e "${BLUE}🔌 Checking if backend is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running at http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠️  Backend not detected at http://localhost:8000${NC}"
    echo -e "${YELLOW}💡 Start the backend first with: ./start-backend.sh${NC}"
fi

# Start the frontend development server
echo -e "${GREEN}🌟 Starting frontend development server...${NC}"
echo -e "${BLUE}🌐 Frontend will be available at: http://localhost:3000${NC}"
echo -e "${BLUE}📡 Backend API endpoint: http://localhost:8000/api${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
echo ""

# Function to open browser in Windows
open_browser() {
    local url=$1
    local browser_path="/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    
    if [ -f "$browser_path" ]; then
        echo -e "${GREEN}🌐 Opening $url in Brave browser...${NC}"
        "$browser_path" "$url" &
    else
        echo -e "${YELLOW}⚠️  Brave browser not found at expected location${NC}"
        echo -e "${YELLOW}💡 Please open $url manually in your browser${NC}"
    fi
}

# Start the server in background and wait for it to be ready
echo -e "${BLUE}🚀 Starting server...${NC}"
$START_COMMAND &
SERVER_PID=$!

# Wait for the server to start (check every 2 seconds, max 30 seconds)
echo -e "${BLUE}⏳ Waiting for server to start...${NC}"
for i in {1..15}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is ready!${NC}"
        open_browser "http://localhost:3000"
        break
    fi
    sleep 2
done

# Keep the script running to show server output
wait $SERVER_PID
