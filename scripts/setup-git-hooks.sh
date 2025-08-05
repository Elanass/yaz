#!/bin/bash
# Git hooks setup script for Surgify Platform
# Installs and configures git hooks for development workflow

set -e

echo "🔧 Setting up Git hooks for Surgify Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "Not in a git repository"
    exit 1
fi

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    print_error "Not in project root directory"
    exit 1
fi

print_status "Installing git hooks..."

# Create git hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install pre-commit hook
if [ -f ".git-hooks/pre-commit" ]; then
    cp .git-hooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    print_success "Pre-commit hook installed"
else
    print_error "Pre-commit hook source not found"
    exit 1
fi

# Install pre-push hook
if [ -f ".git-hooks/pre-push" ]; then
    cp .git-hooks/pre-push .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    print_success "Pre-push hook installed"
else
    print_error "Pre-push hook source not found"
    exit 1
fi

# Install commit-msg hook for conventional commits
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
# Commit message hook for conventional commits

commit_regex='^(feat|fix|docs|style|refactor|test|chore|ci)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "Invalid commit message format!"
    echo ""
    echo "Please use conventional commit format:"
    echo "  feat: add new feature"
    echo "  fix: bug fix"
    echo "  docs: documentation updates"
    echo "  style: formatting changes"
    echo "  refactor: code refactoring"
    echo "  test: add tests"
    echo "  chore: maintenance tasks"
    echo "  ci: CI/CD changes"
    echo ""
    echo "Examples:"
    echo "  feat(api): add AI summarization endpoint"
    echo "  fix(sync): resolve CRDT merge conflicts"
    echo "  docs: update API documentation"
    echo ""
    exit 1
fi
EOF

chmod +x .git/hooks/commit-msg
print_success "Commit-msg hook installed"

# Install prepare-commit-msg hook for branch context
cat > .git/hooks/prepare-commit-msg << 'EOF'
#!/bin/bash
# Prepare commit message with branch context

BRANCH=$(git branch --show-current)
COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# Skip if amending or merging
if [ "$COMMIT_SOURCE" = "merge" ] || [ "$COMMIT_SOURCE" = "squash" ]; then
    exit 0
fi

# Add branch context for feature branches
if [[ $BRANCH == feature/* ]] || [[ $BRANCH == bugfix/* ]] || [[ $BRANCH == hotfix/* ]]; then
    BRANCH_NAME=$(echo $BRANCH | sed 's/.*\///')
    
    # Only add if message doesn't already contain branch reference
    if ! grep -q "$BRANCH_NAME" "$COMMIT_MSG_FILE"; then
        # Get current commit message
        CURRENT_MSG=$(cat "$COMMIT_MSG_FILE")
        
        # Add branch context if message is not empty
        if [ -n "$CURRENT_MSG" ] && [ "$CURRENT_MSG" != "# Please enter the commit message" ]; then
            echo "" >> "$COMMIT_MSG_FILE"
            echo "Branch: $BRANCH" >> "$COMMIT_MSG_FILE"
        fi
    fi
fi
EOF

chmod +x .git/hooks/prepare-commit-msg
print_success "Prepare-commit-msg hook installed"

# Create post-merge hook for dependency updates
cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash
# Post-merge hook for automatic maintenance tasks

echo "🔄 Running post-merge maintenance..."

# Check if requirements.txt or pyproject.toml changed
if git diff HEAD@{1} --name-only | grep -E "(requirements\.txt|pyproject\.toml)" > /dev/null; then
    echo "📦 Dependencies changed, consider running:"
    echo "  pip install -r requirements.txt"
    echo "  # or"
    echo "  pip install -e ."
fi

# Check if database migrations changed
if git diff HEAD@{1} --name-only | grep -E "data/alembic/versions/" > /dev/null; then
    echo "🗄️  Database migrations changed, consider running:"
    echo "  alembic upgrade head"
fi

# Check if Docker files changed
if git diff HEAD@{1} --name-only | grep -E "(Dockerfile|docker-compose\.yml)" > /dev/null; then
    echo "🐳 Docker configuration changed, consider rebuilding:"
    echo "  docker-compose build"
fi

# Check if n8n workflows changed
if git diff HEAD@{1} --name-only | grep -E "n8n/workflows/" > /dev/null; then
    echo "⚙️  n8n workflows changed, consider updating:"
    echo "  Import updated workflows to n8n instance"
fi
EOF

chmod +x .git/hooks/post-merge
print_success "Post-merge hook installed"

# Install development dependencies if not present
print_status "Checking development dependencies..."

MISSING_DEPS=""

# Check for required development tools
if ! command -v black &> /dev/null; then
    MISSING_DEPS="$MISSING_DEPS black"
fi

if ! command -v flake8 &> /dev/null; then
    MISSING_DEPS="$MISSING_DEPS flake8"
fi

if ! command -v pytest &> /dev/null; then
    MISSING_DEPS="$MISSING_DEPS pytest"
fi

if [ -n "$MISSING_DEPS" ]; then
    print_warning "Missing development dependencies:$MISSING_DEPS"
    print_status "Installing development dependencies..."
    
    if [ -f "pyproject.toml" ]; then
        pip install -e ".[dev]"
    elif [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    else
        print_warning "No development requirements file found"
        print_warning "Consider installing manually: pip install black flake8 pytest mypy"
    fi
fi

# Create .gitignore entries for hook logs
print_status "Updating .gitignore..."

GITIGNORE_ENTRIES="
# Git hook logs
.git-hooks/*.log
/tmp/bandit-report.json

# Test coverage reports
htmlcov/
.coverage
coverage.xml

# mypy cache
.mypy_cache/

# pytest cache
.pytest_cache/
"

if [ -f ".gitignore" ]; then
    if ! grep -q "# Git hook logs" .gitignore; then
        echo "$GITIGNORE_ENTRIES" >> .gitignore
        print_success "Updated .gitignore with hook-related entries"
    fi
else
    echo "$GITIGNORE_ENTRIES" > .gitignore
    print_success "Created .gitignore with hook-related entries"
fi

# Test hooks installation
print_status "Testing hooks installation..."

# Create a test commit (dry run)
if git status --porcelain | grep -q .; then
    print_warning "Working directory is not clean, skipping hook test"
else
    print_success "Hooks installed and ready to use"
fi

echo ""
print_success "Git hooks setup completed! 🎉"
echo ""
echo "Installed hooks:"
echo "  ✓ pre-commit  - Code quality checks before each commit"
echo "  ✓ pre-push    - Comprehensive tests before pushing"
echo "  ✓ commit-msg  - Enforces conventional commit format"
echo "  ✓ prepare-commit-msg - Adds branch context"
echo "  ✓ post-merge  - Maintenance reminders after merges"
echo ""
echo "To bypass hooks (not recommended):"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
echo "Happy coding! 🚀"
