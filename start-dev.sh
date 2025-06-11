#!/bin/bash

# GTD Full Stack Development Startup Script
# This script starts both backend and frontend in parallel

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 Starting GTD Full Stack Development Environment...${NC}"
echo ""

# Check if we're in the correct directory
if [ ! -f "start-backend.sh" ] || [ ! -f "start-frontend.sh" ]; then
    echo -e "${RED}❌ Error: Startup scripts not found. Please run this from the project root directory.${NC}"
    exit 1
fi

# Function to handle cleanup on script exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down development servers...${NC}"
    # Kill all background jobs
    jobs -p | xargs -r kill
    exit 0
}

# Set up trap to handle Ctrl+C
trap cleanup SIGINT

# Start backend in background
echo -e "${BLUE}🔧 Starting Backend Server...${NC}"
./start-backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Backend started successfully${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

# Start frontend in background
echo -e "${BLUE}🎨 Starting Frontend Server...${NC}"
./start-frontend.sh &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Frontend started successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may have failed to start${NC}"
fi

echo ""
echo -e "${PURPLE}🎉 GTD Development Environment is running!${NC}"
echo -e "${GREEN}🌐 Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}🔧 Backend API: http://localhost:8000/api${NC}"
echo -e "${GREEN}📖 API Docs: http://localhost:8000/api/docs${NC}"
echo ""
echo -e "${YELLOW}💡 Press Ctrl+C to stop both servers${NC}"
echo -e "${YELLOW}💡 Backend logs: Check terminal output above${NC}"
echo -e "${YELLOW}💡 Frontend logs: Check terminal output above${NC}"

# Wait for background processes
wait