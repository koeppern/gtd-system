#!/bin/bash

# GTD Claude Code mit automatischem Worktree Management
# Erstellt einen neuen Worktree, startet Claude Code und merged bei Beendigung

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAIN_BRANCH="main"
WORKTREE_PREFIX="claude-work"
WORKTREE_DIR="../gtd-worktrees"

echo -e "${BLUE}🤖 GTD Claude Code Worktree Manager${NC}"
echo -e "${BLUE}====================================${NC}"

# Ensure we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Get current directory name for worktree naming
REPO_NAME=$(basename "$(pwd)")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
WORKTREE_NAME="${WORKTREE_PREFIX}_${TIMESTAMP}"
WORKTREE_PATH="${WORKTREE_DIR}/${WORKTREE_NAME}"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🔄 Claude Code beendet - starte Worktree Cleanup...${NC}"
    
    # Change back to worktree directory if we're not there
    cd "${WORKTREE_PATH}" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Bereits außerhalb des Worktrees${NC}"
        return
    }
    
    # Check if there are any changes to commit
    if ! git diff --quiet || ! git diff --quiet --staged || [[ -n $(git ls-files --others --exclude-standard) ]]; then
        echo -e "${YELLOW}📝 Uncommitted changes detected - committing...${NC}"
        
        # Add all changes
        git add .
        
        # Create commit with timestamp
        git commit -m "chore: auto-commit from Claude Code session ${TIMESTAMP}

🤖 Generated with Claude Code Worktree Manager
Session ended: $(date)

Co-Authored-By: Claude <noreply@anthropic.com>" || {
            echo -e "${YELLOW}⚠️  Nothing to commit${NC}"
        }
    fi
    
    # Get the current branch name
    CURRENT_BRANCH=$(git branch --show-current)
    
    # Switch back to main repository
    cd - > /dev/null
    
    echo -e "${BLUE}🔄 Merging changes to ${MAIN_BRANCH}...${NC}"
    
    # Ensure we're on main branch
    git checkout "${MAIN_BRANCH}" 2>/dev/null || {
        echo -e "${RED}❌ Could not switch to ${MAIN_BRANCH}${NC}"
        exit 1
    }
    
    # Pull latest changes
    git pull origin "${MAIN_BRANCH}" || {
        echo -e "${YELLOW}⚠️  Could not pull latest changes${NC}"
    }
    
    # Merge the worktree branch
    if git merge --no-ff "${CURRENT_BRANCH}" -m "feat: merge Claude Code session ${TIMESTAMP}

🤖 Merged from worktree: ${WORKTREE_NAME}
Session completed: $(date)

Co-Authored-By: Claude <noreply@anthropic.com>"; then
        echo -e "${GREEN}✅ Successfully merged changes${NC}"
        
        # Delete the temporary branch
        git branch -d "${CURRENT_BRANCH}" 2>/dev/null || {
            echo -e "${YELLOW}⚠️  Could not delete branch ${CURRENT_BRANCH}${NC}"
        }
    else
        echo -e "${RED}❌ Merge failed - manual intervention required${NC}"
        echo -e "${YELLOW}💡 Worktree preserved at: ${WORKTREE_PATH}${NC}"
        echo -e "${YELLOW}💡 Branch: ${CURRENT_BRANCH}${NC}"
        exit 1
    fi
    
    # Remove the worktree
    echo -e "${BLUE}🗑️  Removing worktree...${NC}"
    git worktree remove "${WORKTREE_PATH}" --force || {
        echo -e "${YELLOW}⚠️  Could not remove worktree automatically${NC}"
        echo -e "${YELLOW}💡 Please remove manually: rm -rf \"${WORKTREE_PATH}\"${NC}"
    }
    
    # Clean up worktree directory if empty
    rmdir "${WORKTREE_DIR}" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Worktree cleanup completed!${NC}"
    echo -e "${BLUE}📁 Back in main repository: $(pwd)${NC}"
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM EXIT

# Create worktree directory if it doesn't exist
mkdir -p "${WORKTREE_DIR}"

# Create new worktree
echo -e "${BLUE}🌿 Creating new worktree: ${WORKTREE_NAME}${NC}"
git worktree add "${WORKTREE_PATH}" -b "${WORKTREE_NAME}" "${MAIN_BRANCH}" || {
    echo -e "${RED}❌ Failed to create worktree${NC}"
    exit 1
}

echo -e "${GREEN}✅ Worktree created at: ${WORKTREE_PATH}${NC}"

# Change to worktree directory
cd "${WORKTREE_PATH}"
echo -e "${BLUE}📁 Working in: $(pwd)${NC}"

# Verify we're in the right place
if [[ ! -f "CLAUDE.md" ]]; then
    echo -e "${YELLOW}⚠️  CLAUDE.md not found - might not be in correct directory${NC}"
fi

echo -e "${BLUE}🚀 Starting Claude Code in worktree...${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to end session and auto-merge changes${NC}"
echo ""

# Add MCP servers
echo -e "${BLUE}🔌 Adding MCP servers...${NC}"
claude mcp add github /home/jkoeppern/mcp_servers/github-mcp-wrapper.sh
claude mcp add digitalocean /home/jkoeppern/mcp_servers/digitalocean-mcp-wrapper.sh
claude mcp add supabase /home/jkoeppern/mcp_servers/supabase-mcp-wrapper.sh
claude mcp add vercel /home/jkoeppern/mcp_servers/vercel-mcp-wrapper.sh

# Start Claude Code
claude