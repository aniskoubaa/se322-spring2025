#!/bin/bash

# Repository configuration
REPO_NAME="se322-spring2025"
REPO_URL="https://github.com/aniskoubaa/se322-spring2025"
BRANCH="main"
VERSION="1.0.7"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with colors
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    print_warning "Git repository not initialized. Initializing now..."
    git init
    git remote add origin $REPO_URL
    print_info "Git repository initialized and remote added."
fi

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Switch to desired branch if not already on it
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    print_info "Switching to branch $BRANCH..."
    git checkout $BRANCH 2>/dev/null || git checkout -b $BRANCH
fi

# Update version in README if it exists
if [ -f "README.md" ]; then
    print_info "Updating version in README.md..."
    # Only update if version line exists
    if grep -q "Version:" README.md; then
        sed -i '' "s/Version: .*/Version: $VERSION/" README.md
    else
        echo -e "\nVersion: $VERSION" >> README.md
    fi
fi

# Stage all changes
print_info "Staging changes..."
git add .

# Get the current timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Commit changes with version and timestamp
print_info "Committing changes..."
git commit -m "Update repository - Version $VERSION - $TIMESTAMP"

# Pull latest changes from remote
print_info "Pulling latest changes from remote..."
git pull origin $BRANCH

# Push changes to remote
print_info "Pushing changes to remote..."
if git push origin $BRANCH; then
    print_info "Successfully updated repository to version $VERSION"
else
    print_error "Failed to push changes to remote"
    exit 1
fi

# Create version tag
print_info "Creating version tag..."
git tag -a "v$VERSION" -m "Version $VERSION - $TIMESTAMP"
git push origin "v$VERSION"

print_info "Repository update complete!"
print_info "Version: $VERSION"
print_info "Branch: $BRANCH"
print_info "Timestamp: $TIMESTAMP" 