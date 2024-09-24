#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: September 24, 2024
import numpy as np
from scipy.stats import ttest_rel

# LAS values for both experiments
las_experiment_1 = [81.52, 80.14, 81.59, 84.6, 81.92, 82.06, 80.31, 82.11, 82.83, 80.92]
las_experiment_2 = [83.2, 84.02, 82.75, 82.17, 81.01, 82.37, 81.7, 81.46, 83.93, 81.89]

# Run a paired t-test
t_stat, p_value = ttest_rel(las_experiment_1, las_experiment_2)

print(f"t_stat, p_value: {t_stat, p_value}")
