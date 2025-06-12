#!/bin/bash

# GTD Full Stack Development Startup Script - WSL Terminal Version
# This script opens two new WSL terminals - one for backend and one for frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 Starting GTD Full Stack Development Environment in separate terminals...${NC}"
echo ""

# Check if we're in the correct directory
if [ ! -f "start-backend.sh" ] || [ ! -f "start-frontend.sh" ]; then
    echo -e "${RED}❌ Error: Startup scripts not found. Please run this from the project root directory.${NC}"
    exit 1
fi

# Get the current working directory
PROJECT_DIR=$(pwd)

# Check if we're running in WSL
if ! grep -q Microsoft /proc/version; then
    echo -e "${YELLOW}⚠️  Warning: This script is designed for WSL. Running in compatibility mode...${NC}"
fi

# Function to start backend in new terminal
start_backend_terminal() {
    echo -e "${BLUE}🔧 Opening new terminal for Backend Server...${NC}"
    
    # Create a temporary script to run in the new terminal
    cat > /tmp/gtd-backend-starter.sh << EOF
#!/bin/bash
cd "$PROJECT_DIR"
echo -e "\033[0;35m🔧 GTD Backend Terminal\033[0m"
echo -e "\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "\033[0;33m💡 Starting backend server... This may take a moment.\033[0m"
./start-backend.sh
echo ""
echo -e "\033[0;31m🛑 Backend server stopped. Press Enter to close this terminal.\033[0m"
read
EOF
    chmod +x /tmp/gtd-backend-starter.sh
    
    # Try different methods to open new terminal
    if command -v wt.exe &> /dev/null; then
        # Windows Terminal is available - try to open in new window
        wt.exe --window new --title "GTD Backend" wsl.exe bash /tmp/gtd-backend-starter.sh &
        BACKEND_OPENED=true
    elif command -v cmd.exe &> /dev/null; then
        # Fallback to cmd.exe with new window
        cmd.exe /c start "GTD Backend" wsl.exe bash /tmp/gtd-backend-starter.sh &
        BACKEND_OPENED=true
    else
        echo -e "${YELLOW}⚠️  Could not open new terminal window. Starting in background...${NC}"
        ./start-backend.sh &
        BACKEND_OPENED=false
    fi
}

# Function to start frontend in new terminal
start_frontend_terminal() {
    echo -e "${BLUE}🎨 Opening new terminal for Frontend Server...${NC}"
    
    # Create a temporary script to run in the new terminal
    cat > /tmp/gtd-frontend-starter.sh << EOF
#!/bin/bash
cd "$PROJECT_DIR"
echo -e "\033[0;35m🎨 GTD Frontend Terminal\033[0m"
echo -e "\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "\033[0;33m💡 Waiting for backend to start (5 seconds)...\033[0m"
sleep 5
echo -e "\033[0;33m💡 Starting frontend server... This may take a moment.\033[0m"
./start-frontend.sh
echo ""
echo -e "\033[0;31m🛑 Frontend server stopped. Press Enter to close this terminal.\033[0m"
read
EOF
    chmod +x /tmp/gtd-frontend-starter.sh
    
    # Try different methods to open new terminal
    if command -v wt.exe &> /dev/null; then
        # Windows Terminal is available - try to open in new window
        wt.exe --window new --title "GTD Frontend" wsl.exe bash /tmp/gtd-frontend-starter.sh &
        FRONTEND_OPENED=true
    elif command -v cmd.exe &> /dev/null; then
        # Fallback to cmd.exe with new window
        cmd.exe /c start "GTD Frontend" wsl.exe bash /tmp/gtd-frontend-starter.sh &
        FRONTEND_OPENED=true
    else
        echo -e "${YELLOW}⚠️  Could not open new terminal window. Starting in background...${NC}"
        sleep 5 && ./start-frontend.sh &
        FRONTEND_OPENED=false
    fi
}

# Start both terminals
start_backend_terminal
sleep 2  # Small delay between terminal launches
start_frontend_terminal

# Show success message
echo ""
if [[ "${BACKEND_OPENED:-false}" == "true" && "${FRONTEND_OPENED:-false}" == "true" ]]; then
    echo -e "${PURPLE}🎉 GTD Development Environment terminals launched!${NC}"
    echo ""
    echo -e "${GREEN}📱 Two new terminal windows should have opened:${NC}"
    echo -e "   ${BLUE}1. Backend Terminal${NC} - FastAPI server"
    echo -e "   ${BLUE}2. Frontend Terminal${NC} - Next.js/React server"
elif [[ "${BACKEND_OPENED:-false}" == "true" || "${FRONTEND_OPENED:-false}" == "true" ]]; then
    echo -e "${YELLOW}⚠️  Partial success - some terminals opened, others running in background${NC}"
else
    echo -e "${YELLOW}⚠️  Running in background mode - no separate terminals opened${NC}"
fi

echo ""
echo -e "${GREEN}🌐 Access points (once servers start):${NC}"
echo -e "   ${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "   ${BLUE}Backend API:${NC} http://localhost:8000/api"
echo -e "   ${BLUE}API Docs:${NC} http://localhost:8000/api/docs"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   - Each service runs in its own terminal window"
echo -e "   - Backend starts immediately, frontend waits 5 seconds"
echo -e "   - You can close each terminal individually with Ctrl+C"
echo -e "   - Check each terminal for service-specific logs and errors"
echo ""
if [[ "${BACKEND_OPENED:-false}" != "true" || "${FRONTEND_OPENED:-false}" != "true" ]]; then
    echo -e "${BLUE}🔍 If terminals didn't open automatically:${NC}"
    echo -e "   - Run ${GREEN}./start-backend.sh${NC} in one terminal"
    echo -e "   - Run ${GREEN}./start-frontend.sh${NC} in another terminal"
    echo ""
fi

# Clean up temporary files after a delay
(sleep 10 && rm -f /tmp/gtd-backend-starter.sh /tmp/gtd-frontend-starter.sh) &