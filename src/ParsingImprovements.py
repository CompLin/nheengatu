#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: December 10, 2025

import matplotlib.pyplot as plt
from scipy.stats import wilcoxon

# LAS results from the two experiments
# exp1: baseline (Alencar 2024), exp2: improved parser

# Leonel Figueiredo de Alencar. 2024. A Universal Dependencies Treebank for Nheengatu. 
# In Proceedings of the 16th International Conference on Computational Processing of Portuguese - Vol. 2, pages 37–54, Santiago de Compostela, Galicia/Spain. Association for Computational Lingustics.
# https://aclanthology.org/2024.propor-2.8/

# Each list contains LAS scores for 10 folds
exp1 = [83.23, 82.35, 80.16, 82.65, 81.72, 80.8, 81.52, 83.1, 81.49, 80.93]
exp2 = [84.38, 85.57, 82.79, 82.42, 82.77, 83.55, 85.22, 85.22, 84.05, 83.66]

# Compute paired improvements
improvements = [b - a for a, b in zip(exp1, exp2)]

# Wilcoxon test
statistic, p_value = wilcoxon(exp1, exp2)
print("Wilcoxon statistic:", statistic)
print("Two-tailed p-value:", p_value)

# X-axis values for folds 1..10
folds = list(range(1, 11))

# Plot improvements
plt.figure(figsize=(8,5))
plt.plot(folds, improvements, marker='o')
plt.axhline(0, linestyle='--', linewidth=1)   # reference line at zero
plt.xlabel('Fold')
plt.ylabel('LAS improvement (exp2 − exp1)')
plt.title('LAS Improvements per Fold')
plt.xticks(folds)  # ensure labels are 1..10
plt.tight_layout()
plt.show()
