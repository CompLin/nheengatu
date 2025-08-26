#!/bin/bash
# Author: Leonel Figueiredo de Alencar
# Last update: August 25, 2025
#
# Clone Universal Dependencies treebanks defined in treebanks.json.
# - Default: Amerindian treebanks
# -p: Portuguese treebanks
# -a: All treebanks

# Ensure jq is installed
if ! command -v jq >/dev/null 2>&1; then
    echo "Error: jq is required but not installed. Please install jq and try again."
    exit 1
fi

# Find the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# JSON file in the same directory
JSON_FILE="$SCRIPT_DIR/treebanks.json"

# Default: Amerindian treebanks
selected_treebanks=$(jq -r '.amerindian[]' "$JSON_FILE")

# Parse options
while [[ "$1" == -* ]]; do
    case "$1" in
        -p)
            selected_treebanks=$(jq -r '.portuguese[]' "$JSON_FILE")
            shift
            ;;
        -a)
            selected_treebanks=$(jq -r '.amerindian[], .portuguese[]' "$JSON_FILE")
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-p | -a]"
            echo "Clone Universal Dependencies treebanks defined in treebanks.json"
            echo ""
            echo "Options:"
            echo "  -p    Clone only Portuguese treebanks"
            echo "  -a    Clone all treebanks (Amerindian + Portuguese)"
            echo "  -h    Show this help message"
            exit 0
            ;;
        *)
            echo "Error: Unknown option '$1'"
            exit 1
            ;;
    esac
done

# Iterate over selected repositories
for repo in $selected_treebanks; do
    if [ -d "$repo" ]; then
        echo "✅ Directory $repo already exists, skipping..."
    else
        echo "⬇️ Cloning $repo..."
        git clone "git@github.com:UniversalDependencies/${repo}.git"
    fi
done
