#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: February 11, 2025

import sys
import xml.etree.ElementTree as ET

def parse_xml(filename, dimension, tag_name=None):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    dimensions = {
        "sentences": "./size/total/sentences",
        "tokens": "./size/total/tokens",
        "words": "./size/total/words",
        "fused": "./size/total/fused",
        "lemmas": "./lemmas",
        "forms": "./forms",
        "fusions": "./fusions",
        "tags": "./tags",
        "feats": "./feats",
        "deps": "./deps"
    }
    
    if dimension not in dimensions:
        print("Invalid dimension")
        return None
    
    element_path = dimensions[dimension]
    
    if dimension in ["sentences", "tokens", "words", "fused"]:
        return int(root.find(element_path).text)
    elif dimension in ["lemmas", "forms", "fusions"]:
        element = root.find(element_path)
        return int(element.get("unique"))
    elif dimension == "tags":
        if tag_name:
            tag_element = root.find(element_path + '/tag[@name="' + tag_name + '"]')
            if tag_element is not None:
                return int(tag_element.text)
            else:
                print("Tag not found")
                return None
        else:
            element = root.find(element_path)
            return int(element.get("unique"))
    elif dimension == "feats":
        element = root.find(element_path)
        return int(element.get("unique"))
    elif dimension == "deps":
        element = root.find(element_path)
        return int(element.get("unique"))
    else:
        print("Invalid dimension")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python ParseStatsXML.py filename dimension [tag_name]")
    else:
        filename = sys.argv[1]
        dimension = sys.argv[2]
        tag_name = sys.argv[3] if len(sys.argv) == 4 else None
        result = parse_xml(filename, dimension, tag_name)
        if result is not None:
            print(result)



