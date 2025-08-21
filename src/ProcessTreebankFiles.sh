#!/bin/bash
# Author: Leonel Figueiredo de Alencar
# Last update: May 27, 2025


# List of Amerindian treebanks
directories=(
    "UD_Akuntsu-TuDeT"
    "UD_Apurina-UFPA"
    "UD_Bororo-BDT"
    "UD_Guajajara-TuDeT"
    "UD_Guarani-OldTuDeT"
    "UD_Highland_Puebla_Nahuatl-ITML"
    "UD_Kaapor-TuDeT"
    "UD_Karo-TuDeT"
    "UD_Kiche-IU"
    "UD_Madi-Jarawara"
    "UD_Makurap-TuDeT"
    "UD_Mbya_Guarani-Dooley"
    "UD_Mbya_Guarani-Thomas"
    "UD_Munduruku-TuDeT"
    "UD_Nheengatu-CompLin"
    "UD_Paumari-TueCL"
    "UD_Teko-TuDeT"
    "UD_Tupinamba-TuDeT"
    "UD_Western_Sierra_Puebla_Nahuatl-ITML"
    "UD_Xavante-XDT"
    "UD_Yupik-SLI",
    "UD_Gwichin-TueCL"
    "UD_Ika-ChibErgIS"
    "UD_Pesh-ChibErgIS"
    "UD_Bokota-ChibErgIS"
)

# List of Portuguese treebanks
portuguese=(
    "UD_Portuguese-Bosque"
    "UD_Portuguese-CINTIL"
    "UD_Portuguese-DANTEStocks"
    "UD_Portuguese-GSD"
    "UD_Portuguese-PetroGold"
    "UD_Portuguese-Porttinari"
    "UD_Portuguese-PUD"
)

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
selected_treebanks=("${directories[@]}")

# Handle options
while [[ "$1" == --* || "$1" == -* ]]; do
    case "$1" in
        -p)
            selected_treebanks=("${portuguese[@]}")  # Only Portuguese treebanks
            shift
            ;;
        -a)
            selected_treebanks=("${directories[@]}" "${portuguese[@]}")  # All treebanks
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


