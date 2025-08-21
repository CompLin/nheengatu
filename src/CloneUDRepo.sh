#!/bin/bash
# Author: Leonel Figueiredo de Alencar
# Last update: August 19, 2025

# List of UD repositories for Amerindian languages
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
    "UD_Yupik-SLI"
    "UD_Gwichin-TueCL"
    "UD_Ika-ChibErgIS"
    "UD_Pesh-ChibErgIS"
    "UD_Bokota-ChibErgIS"
)

# Iterate through each repository
for repo in "${directories[@]}"; do
    if [ -d "$repo" ]; then
        echo "✅ Directory $repo already exists, skipping..."
    else
        echo "⬇️ Cloning $repo..."
        git clone "git@github.com:UniversalDependencies/${repo}.git"
    fi
done
