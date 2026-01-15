"""
Salt Project - R214 Food Inflation Analysis

This package provides tools for analyzing inflation rates of food products,
with a focus on comparing R214-regulated items against non-regulated items.
"""

from .inflation_analysis import (
    load_inflation_data,
    categorize_foods,
    calculate_average_inflation,
    calculate_category_average,
    perform_unit_root_test,
    perform_cointegration_test,
    estimate_vecm,
    plot_inflation_comparison,
    plot_individual_foods,
    compare_category_statistics,
    R214_FOODS
)

__version__ = '0.1.0'
__all__ = [
    'load_inflation_data',
    'categorize_foods',
    'calculate_average_inflation',
    'calculate_category_average',
    'perform_unit_root_test',
    'perform_cointegration_test',
    'estimate_vecm',
    'plot_inflation_comparison',
    'plot_individual_foods',
    'compare_category_statistics',
    'R214_FOODS'
]
