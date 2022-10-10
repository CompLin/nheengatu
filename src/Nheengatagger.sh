#! /bin/bash

# This script applies the Nheengatagger.py Python module to a list
# of files in the data/corpus/navarro-2016 folder.

# Usage example:
# Nheengatagger.sh [et]*[0-9][0-9].txt

# Author: Leonel Figueiredo de Alencar
# Date May 31, 2022

for i in "$@"
do

set $(echo "$i" | awk 'BEGIN {FS= "."} { print $1}')

Nheengatagger.py "$i" > "$1"-pos.txt
done
