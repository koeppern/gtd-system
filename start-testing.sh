#!/bin/bash

# GTD Full Stack Testing Script
# Runs all tests for both backend and frontend components

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🧪 GTD Full Stack Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if we're in the correct directory
if [ ! -f "CLAUDE.md" ] || [ ! -d "src" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory.${NC}"
    exit 1
fi

# Function to check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}✅ Virtual environment is active: ${VIRTUAL_ENV}${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Virtual environment not detected${NC}"
        if [ -f ".venv/bin/activate" ]; then
            echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
            source .venv/bin/activate
            return 0
        else
            echo -e "${RED}❌ Virtual environment not found. Please run: python3 -m venv .venv${NC}"
            return 1
        fi
    fi
}

# Function to run ETL tests
run_etl_tests() {
    echo -e "${CYAN}📋 Running ETL Tests${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    
    local test_failed=false
    
    # GTD Projects ETL Tests
    if [ -f "tests/test_etl_projects.py" ]; then
        echo -e "${BLUE}🔧 Testing ETL Projects...${NC}"
        if python3 -m pytest tests/test_etl_projects.py -v; then
            echo -e "${GREEN}✅ ETL Projects tests passed${NC}"
        else
            echo -e "${RED}❌ ETL Projects tests failed${NC}"
            test_failed=true
        fi
        echo ""
    else
        echo -e "${YELLOW}⚠️  ETL Projects tests not found (tests/test_etl_projects.py)${NC}"
    fi
    
    # GTD Tasks ETL Tests
    if [ -f "tests/test_etl_tasks.py" ]; then
        echo -e "${BLUE}📝 Testing ETL Tasks...${NC}"
        if python3 -m pytest tests/test_etl_tasks.py -v; then
            echo -e "${GREEN}✅ ETL Tasks tests passed${NC}"
        else
            echo -e "${RED}❌ ETL Tasks tests failed${NC}"
            test_failed=true
        fi
        echo ""
    else
        echo -e "${YELLOW}⚠️  ETL Tasks tests not found (tests/test_etl_tasks.py)${NC}"
    fi
    
    # All ETL Tests
    if [ -d "tests" ] && [ "$(ls -A tests/*.py 2>/dev/null)" ]; then
        echo -e "${BLUE}🧪 Running all ETL tests...${NC}"
        if python3 -m pytest tests/ -v; then
            echo -e "${GREEN}✅ All ETL tests passed${NC}"
        else
            echo -e "${RED}❌ Some ETL tests failed${NC}"
            test_failed=true
        fi
        echo ""
    fi
    
    if [ "$test_failed" = true ]; then
        return 1
    else
        return 0
    fi
}

# Function to run backend tests
run_backend_tests() {
    echo -e "${CYAN}🔧 Running Backend Tests${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    
    if [ -d "src/backend" ]; then
        cd src/backend
        
        # Check if backend test runner exists
        if [ -f "run_tests.py" ]; then
            echo -e "${BLUE}🚀 Using backend test runner...${NC}"
            if python run_tests.py; then
                echo -e "${GREEN}✅ Backend tests passed${NC}"
                cd ../..
                return 0
            else
                echo -e "${RED}❌ Backend tests failed${NC}"
                cd ../..
                return 1
            fi
        elif [ -d "tests" ]; then
            echo -e "${BLUE}🧪 Running backend pytest...${NC}"
            if python -m pytest tests/ -v; then
                echo -e "${GREEN}✅ Backend tests passed${NC}"
                cd ../..
                return 0
            else
                echo -e "${RED}❌ Backend tests failed${NC}"
                cd ../..
                return 1
            fi
        else
            echo -e "${YELLOW}⚠️  No backend tests found${NC}"
            cd ../..
            return 0
        fi
    else
        echo -e "${YELLOW}⚠️  Backend directory not found (src/backend)${NC}"
        return 0
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    echo -e "${CYAN}🎨 Running Frontend Tests${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    
    if [ -d "src/frontend-prototype" ]; then
        cd src/frontend-prototype
        
        # Check if node_modules exists
        if [ ! -d "node_modules" ]; then
            echo -e "${YELLOW}⚠️  Node modules not found. Installing dependencies...${NC}"
            if ! npm install; then
                echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
                cd ../..
                return 1
            fi
        fi
        
        # Check if test script exists in package.json
        if npm run test --silent 2>/dev/null; then
            echo -e "${GREEN}✅ Frontend tests passed${NC}"
            cd ../..
            return 0
        else
            echo -e "${YELLOW}⚠️  Frontend tests failed or not configured${NC}"
            cd ../..
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Frontend directory not found (src/frontend-prototype)${NC}"
        return 0
    fi
}

# Main execution
main() {
    local overall_success=true
    
    # Check virtual environment
    if ! check_venv; then
        echo -e "${RED}❌ Cannot proceed without virtual environment${NC}"
        exit 1
    fi
    
    echo ""
    
    # Run ETL tests
    if ! run_etl_tests; then
        overall_success=false
    fi
    
    echo ""
    
    # Run backend tests
    if ! run_backend_tests; then
        overall_success=false
    fi
    
    echo ""
    
    # Run frontend tests
    if ! run_frontend_tests; then
        overall_success=false
    fi
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    if [ "$overall_success" = true ]; then
        echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
        echo ""
        echo -e "${GREEN}✅ Test Summary:${NC}"
        echo -e "   ${BLUE}ETL Tests:${NC} Passed"
        echo -e "   ${BLUE}Backend Tests:${NC} Passed"
        echo -e "   ${BLUE}Frontend Tests:${NC} Passed"
        echo ""
        echo -e "${CYAN}💡 Great job! Your codebase is test-ready.${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed!${NC}"
        echo ""
        echo -e "${YELLOW}🔍 Next steps:${NC}"
        echo -e "   1. Review the failed test output above"
        echo -e "   2. Fix any failing tests"
        echo -e "   3. Run ${GREEN}./start-testing.sh${NC} again"
        echo ""
        echo -e "${BLUE}💡 You can also run individual test suites:${NC}"
        echo -e "   - ETL only: ${GREEN}python3 -m pytest tests/ -v${NC}"
        echo -e "   - Backend only: ${GREEN}cd src/backend && python run_tests.py${NC}"
        echo -e "   - Frontend only: ${GREEN}cd src/frontend-prototype && npm test${NC}"
        exit 1
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}⚠️  Tests interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@"