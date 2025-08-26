#!/bin/bash
# Author: Leonel Figueiredo de Alencar
# Last update: August 25, 2025

# Ensure jq is available
if ! command -v jq >/dev/null 2>&1; then
    echo "Error: jq is required but not installed. Please install jq and try again."
    exit 1
fi

# Path to this script’s directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load treebanks from treebanks.json
amerindian=($(jq -r '.amerindian[]' "$SCRIPT_DIR/treebanks.json"))
portuguese=($(jq -r '.portuguese[]' "$SCRIPT_DIR/treebanks.json"))

# Function to display usage message
usage() {
    echo "Usage: $0 [OPTIONS] XML_PATTERN DIMENSION"
    echo "Processes XML files from selected Universal Dependencies treebanks."
    echo ""
    echo "Options:"
    echo "  -p             Process only Portuguese treebanks."
    echo "  -a             Process all treebanks (Portuguese + Amerindian)."
    echo "  -h, --help     Display this help message and exit."
    echo ""
    echo "Arguments:"
    echo "  XML_PATTERN    The XML filename pattern to process (e.g., stats.xml or stats_*.xml)."
    echo "  DIMENSION      The statistical dimension to extract (e.g., sentences, tokens, etc.)."
    echo ""
    echo "If no option is given, the script processes only the Amerindian treebanks by default."
    exit 0
}

# Default to Amerindian treebanks
selected_treebanks=("${amerindian[@]}")

# Handle options
while [[ "$1" == --* || "$1" == -* ]]; do
    case "$1" in
        -p)
            selected_treebanks=("${portuguese[@]}")  # Only Portuguese treebanks
            shift
            ;;
        -a)
            selected_treebanks=("${amerindian[@]}" "${portuguese[@]}")  # All treebanks
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Error: Unknown option '$1'"
            usage
            ;;
    esac
done

# Ensure two arguments are provided
if [ $# -ne 2 ]; then
    echo "Error: Missing arguments."
    usage
fi

xml_pattern="$1"
dimension="$2"

# Iterate over selected treebanks
for dir in "${selected_treebanks[@]}"; do
    if [ -d "$dir" ]; then
        echo "Processing treebank in $dir..."

        # Find and process each XML file matching the pattern
        find "$dir" -maxdepth 1 -name "$xml_pattern" | while read -r file; do
            echo "Processing file $file..."
            # Call Python script with filename and dimension
            ParseStatsXML.py "$file" "$dimension"
        done

        echo "Finished processing treebank in $dir."
        echo "======================================="
    else
        echo "Directory '$dir' not found. Skipping..."
    fi
done
