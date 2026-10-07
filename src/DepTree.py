#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# AI tool: ChatGPT 4.0
# Last update: October 7, 2026
import sys
import os
from conllu import parse
from graphviz import Digraph
from PIL import Image
from DisplayPDF import display_pdf_as_image


# Function to generate and display the dependency tree from a CoNLL-U representation
def displayTree(conllu_text='', output_base_name="dependency_tree",display=True, file_format='png', cleanup=True,tokenlist=None):
    sentences=[]
    if conllu_text:
        # Parse the CoNLL-U data using conllu
        sentences = parse(conllu_text)
    elif tokenlist:
        sentences.append(tokenlist)

    # Create a Graphviz Digraph object
    dot = Digraph(comment='Dependency Tree')
    dot.attr('node', shape='ellipse')

    # Function to add nodes and edges to the graph
    def add_edges(token, dot, tokens):
        # Add the node with its form and POS tag
        label = f"{token['form']} ({token['upostag']})"
        dot.node(str(token['id']), label)
        # Handle the root relation (head=0)
        if token['head'] == 0:
            dot.edge('0', str(token['id']), label=token['deprel'])
        elif token['head'] is not None:  # Avoid None heads
            head_token = tokens[token['head'] - 1]
            dot.edge(str(head_token['id']), str(token['id']), label=token['deprel'])

    # Add a node for the root (virtual node with id=0)
    dot.node('0', 'ROOT')

    # Function to delete multiword tokens (MWTs)
    def deleteMWT(sent):
        i = 0
        while i < len(sent):
            if isinstance(sent[i]['id'], tuple):  # Check if the ID is a tuple, indicating MWT
                sent.pop(i)
            else:
                i += 1

    # Iterate over each sentence and add nodes/edges
    for sentence in sentences:
        deleteMWT(sentence)
        for token in sentence:
            add_edges(token, dot, sentence)

    # Save the Graphviz source as a .dot file
    dot_filename = output_base_name + ".dot"
    dot.save(filename=dot_filename)

    # Render the graph as a PNG file
    output_filename = output_base_name + f".{file_format}"
    dot.render(output_base_name, format=file_format, cleanup=cleanup)

    # Display the image using PIL
    if display:
        if file_format == 'png':
            img = Image.open(output_filename)
            img.show()
        elif file_format == 'pdf':
            display_pdf_as_image(output_filename, page_number=0, zoom=1)

    print(f"Dependency tree saved as '{output_filename}' and displayed.")

# Command-line execution
if __name__ == "__main__":
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
        if not input_filename.endswith(".conllu"):
            print("The file must have a .conllu extension.")
            sys.exit(1)

        output_base_name = os.path.splitext(input_filename)[0]

        with open(input_filename, 'r', encoding='utf-8') as f:
            conllu_text = f.read()

        displayTree(conllu_text, output_base_name,display)
    else:
        print("Usage: ./DepTree.py <filename.conllu>")
