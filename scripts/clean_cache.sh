#!/bin/bash
# Clean VSCode and Python cache files

echo "🧹 Cleaning VSCode and Python cache files..."

# Remove VSCode cache
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✅ Removed .vscode directories"

# Remove Python cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✅ Removed __pycache__ directories"

# Remove pytest cache
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✅ Removed .pytest_cache directories"

# Remove mypy cache
find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✅ Removed .mypy_cache directories"

# Remove coverage files
find . -name ".coverage" -type f -delete 2>/dev/null || true
find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✅ Removed coverage files"

# Remove build artifacts
find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✅ Removed build artifacts"

# Remove temporary files
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true
find . -name "*~" -type f -delete 2>/dev/null || true
echo "✅ Removed temporary files"

echo "🎉 Cache cleanup completed!"
