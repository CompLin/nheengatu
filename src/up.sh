#!/bin/sh
# Update the Yauti lexicon JSON glossary

echo "Compiling glossary from source file..."
python3 -c 'import BuildDictionary; BuildDictionary.main()'
echo "Glossary successfully updated."
