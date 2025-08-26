#!/bin/bash
# Author: Leonel Figueiredo de Alencar
# Last update: August 19, 2025

# Find the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# JSON file in the same directory
JSON_FILE="$SCRIPT_DIR/treebanks.json"

# Iterate over repositories from JSON
for repo in $(jq -r '.directories[]' "$JSON_FILE"); do
    if [ -d "$repo" ]; then
        echo "✅ Directory $repo already exists, skipping..."
    else
        echo "⬇️ Cloning $repo..."
        git clone "git@github.com:UniversalDependencies/${repo}.git"
    fi
done
