#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: December 5, 2024

import re
import numpy as np
import glob
import os

# Directory where your result files are located
#MYDIR="/home/leonel/Dropbox/nheengatu/pibic/test01/"
RESULTS_DIR = ''

def extract_las_values(data):
    """
    Extracts LAS values from the provided data string.
    
    Args:
        data (str): Multi-line string containing LAS results.
    
    Returns:
        list: A list of LAS values as floats.
    """
    # Regular expression to find LAS values
    las_matches = re.findall(r'LAS:\s([\d\.]+)%', data)
    
    # Convert matched strings to floats
    las_values = [float(value) for value in las_matches]
    
    return las_values

def calculate_statistics(values):
    """
    Calculates mean and standard deviation of a list of numbers.
    
    Args:
        values (list): List of numerical values.
    
    Returns:
        tuple: Mean and standard deviation rounded to two decimals.
    """
    mean = np.mean(values)
    std_dev = np.std(values, ddof=1)  # Using sample standard deviation
    
    return round(mean, 2), round(std_dev, 2)

def main():
    try:
        # Pattern to match all relevant files
        pattern = os.path.join(RESULTS_DIR, "gold-tok-tags-*.txt")
        
        # Find all files matching the pattern
        files = glob.glob(pattern)
        
        if not files:
            print("No files found matching the pattern.")
            return
        # Sort numerically by file index: 1,2,3,...,10
        files.sort(key=lambda f: int(re.search(r'(\d+)', os.path.basename(f)).group(1)))
        las_values = []
        
        for file_path in files:
            print(f"Processing file: {file_path}")
            with open(file_path, 'r') as file:
                data = file.read()
                las_values.extend(extract_las_values(data))
        
        if not las_values:
            print("No LAS values found in the data.")
            return
        
        # Calculate statistics
        mean, std_dev = calculate_statistics(las_values)
        
        # Print results
        print(f"LAS Values: {las_values}")
        print(f"Mean LAS: {mean}%")
        print(f"Standard Deviation of LAS: {std_dev}%")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
