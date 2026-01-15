"""
Inflation Analysis Module for R214 Salt Regulation Foods

This module provides functions to analyze month-on-month inflation rates
for food products, comparing R214-regulated items against non-R214 items.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, coint
from statsmodels.tsa.vector_ar.vecm import VECM
import warnings

# R214 regulated food products
R214_FOODS = [
    "White bread",
    "Brown bread",
    "Bread rolls",
    "Savoury biscuits",
    "Cold cereals",
    "Hot cereals (porridge)",
    "Instant noodles",
    "Ham",
    "Bacon",
    "Sausages (beef, pork, mutton)",
    "Boerewors",
    "Polony",
    "Corned meat",
    "Margarine spread",
    "Brick margarine",
    "Potato crisps",
    "Corn/Maize chips",
    "Soup powder",
    "Stock cubes/powder",
    "Beef mince - fresh"
]


def load_inflation_data(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    Load inflation rate data from Excel file.

    Args:
        file_path: Path to the Excel file containing inflation data
        sheet_name: Name of the sheet to load (optional)

    Returns:
        DataFrame with inflation rates, indexed by date

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the data format is invalid
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found at: {file_path}")

    # Handle case where multiple sheets return a dict
    if isinstance(df, dict):
        # If no sheet specified and multiple sheets exist, use first sheet
        df = df[list(df.keys())[0]]

    if df.empty:
        raise ValueError("Loaded data is empty")

    # Assume first column is date
    if 'date' not in df.columns.str.lower():
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)

    return df


def categorize_foods(df: pd.DataFrame, r214_list: Optional[List[str]] = None) -> Tuple[List[str], List[str]]:
    """
    Categorize food products into R214 and non-R214 categories.

    Args:
        df: DataFrame containing food product columns
        r214_list: List of R214 regulated foods (uses default if None)

    Returns:
        Tuple of (r214_foods, non_r214_foods) found in the dataframe
    """
    if r214_list is None:
        r214_list = R214_FOODS

    # Normalize for case-insensitive matching
    r214_normalized = [food.lower().strip() for food in r214_list]

    food_columns = [col for col in df.columns if col.lower() != 'date']

    r214_found = []
    non_r214_found = []

    for col in food_columns:
        col_normalized = col.lower().strip()
        if col_normalized in r214_normalized:
            r214_found.append(col)
        else:
            non_r214_found.append(col)

    return r214_found, non_r214_found


def calculate_average_inflation(df: pd.DataFrame, food_list: List[str]) -> pd.Series:
    """
    Calculate average inflation rate across specified foods.

    Args:
        df: DataFrame with inflation rates
        food_list: List of food column names to average

    Returns:
        Series with average inflation rates over time

    Raises:
        ValueError: If food_list is empty or columns don't exist
    """
    if not food_list:
        raise ValueError("food_list cannot be empty")

    missing_cols = [food for food in food_list if food not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in dataframe: {missing_cols}")

    return df[food_list].mean(axis=1, skipna=True)


def calculate_category_average(df: pd.DataFrame, food_list: List[str]) -> float:
    """
    Calculate overall average inflation rate for a category.

    Args:
        df: DataFrame with inflation rates
        food_list: List of food column names

    Returns:
        Single average value across all foods and time periods
    """
    if not food_list:
        return np.nan

    available_foods = [food for food in food_list if food in df.columns]
    if not available_foods:
        return np.nan

    return df[available_foods].mean().mean()


def perform_unit_root_test(series: pd.Series, significance_level: float = 0.05) -> Dict[str, any]:
    """
    Perform Augmented Dickey-Fuller unit root test on a time series.

    Args:
        series: Time series data to test
        significance_level: Significance level for the test (default 0.05)

    Returns:
        Dictionary containing test results:
            - adf_statistic: The test statistic
            - p_value: The p-value
            - is_stationary: Boolean indicating if series is stationary
            - critical_values: Dictionary of critical values
            - used_lag: Number of lags used
    """
    # Remove NaN values
    clean_series = series.dropna()

    if len(clean_series) < 3:
        raise ValueError("Series too short for unit root test (minimum 3 observations)")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = adfuller(clean_series, autolag='AIC')

    return {
        'adf_statistic': result[0],
        'p_value': result[1],
        'is_stationary': bool(result[1] < significance_level),
        'critical_values': result[4],
        'used_lag': result[2],
        'n_obs': result[3]
    }


def perform_cointegration_test(series1: pd.Series, series2: pd.Series,
                               significance_level: float = 0.05) -> Dict[str, any]:
    """
    Perform Johansen cointegration test between two time series.

    Args:
        series1: First time series
        series2: Second time series
        significance_level: Significance level for the test

    Returns:
        Dictionary containing test results:
            - test_statistic: The test statistic
            - p_value: The p-value
            - is_cointegrated: Boolean indicating if series are cointegrated
            - critical_value: Critical value at given significance level
    """
    # Align series and remove NaN
    combined = pd.concat([series1, series2], axis=1).dropna()

    if len(combined) < 3:
        raise ValueError("Series too short for cointegration test (minimum 3 observations)")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = coint(combined.iloc[:, 0], combined.iloc[:, 1])

    return {
        'test_statistic': result[0],
        'p_value': result[1],
        'is_cointegrated': bool(result[1] < significance_level),
        'critical_values': result[2]
    }


def estimate_vecm(df: pd.DataFrame, food_list: List[str],
                  deterministic: str = 'ci', k_ar_diff: int = 1) -> Dict[str, any]:
    """
    Estimate Vector Error Correction Model (VECM).

    Args:
        df: DataFrame with inflation rates
        food_list: List of food columns to include in the model
        deterministic: Deterministic term ('n', 'co', 'ci', 'lo', 'li')
        k_ar_diff: Number of lagged differences

    Returns:
        Dictionary containing VECM results:
            - model: Fitted VECM model
            - summary: Model summary string
            - alpha: Adjustment coefficients
            - beta: Cointegration vectors

    Raises:
        ValueError: If insufficient data or invalid parameters
    """
    if len(food_list) < 2:
        raise ValueError("VECM requires at least 2 variables")

    missing_cols = [food for food in food_list if food not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found: {missing_cols}")

    # Prepare data
    data = df[food_list].dropna()

    if len(data) < 10:
        raise ValueError("Insufficient observations for VECM (minimum 10)")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = VECM(data, k_ar_diff=k_ar_diff, deterministic=deterministic)
        fitted_model = model.fit()

    return {
        'model': fitted_model,
        'summary': str(fitted_model.summary()),
        'alpha': fitted_model.alpha,
        'beta': fitted_model.beta,
        'k_ar': fitted_model.k_ar,
        'deterministic': deterministic
    }


def plot_inflation_comparison(df: pd.DataFrame, r214_foods: List[str],
                              non_r214_foods: List[str],
                              save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot comparison of average R214 vs non-R214 food inflation rates.

    Args:
        df: DataFrame with inflation rates
        r214_foods: List of R214 food columns
        non_r214_foods: List of non-R214 food columns
        save_path: Path to save the plot (optional)

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Calculate averages
    r214_avg = calculate_average_inflation(df, r214_foods)
    non_r214_avg = calculate_average_inflation(df, non_r214_foods)

    # Assume first column or index is date
    if 'Date' in df.columns:
        x_axis = pd.to_datetime(df['Date'])
    else:
        x_axis = df.index

    # Plot
    ax.plot(x_axis, r214_avg, label='R214 Foods', linewidth=2, color='#E74C3C')
    ax.plot(x_axis, non_r214_avg, label='Non-R214 Foods', linewidth=2, color='#3498DB')

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Average Inflation Rate (%)', fontsize=12)
    ax.set_title('Inflation Rates: R214 vs Non-R214 Foods', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_individual_foods(df: pd.DataFrame, food_list: List[str],
                         title: str = "Individual Food Inflation Rates",
                         save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot individual inflation rate trends for specified foods.

    Args:
        df: DataFrame with inflation rates
        food_list: List of food columns to plot
        title: Plot title
        save_path: Path to save the plot (optional)

    Returns:
        matplotlib Figure object
    """
    if not food_list:
        raise ValueError("food_list cannot be empty")

    fig, ax = plt.subplots(figsize=(14, 8))

    # Assume first column or index is date
    if 'Date' in df.columns:
        x_axis = pd.to_datetime(df['Date'])
    else:
        x_axis = df.index

    for food in food_list:
        if food in df.columns:
            ax.plot(x_axis, df[food], label=food, linewidth=1.5, alpha=0.7)

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Inflation Rate (%)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def compare_category_statistics(df: pd.DataFrame, r214_foods: List[str],
                                non_r214_foods: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Compare statistical measures between R214 and non-R214 food categories.

    Args:
        df: DataFrame with inflation rates
        r214_foods: List of R214 food columns
        non_r214_foods: List of non-R214 food columns

    Returns:
        Dictionary with statistics for each category:
            - mean: Average inflation rate
            - median: Median inflation rate
            - std: Standard deviation
            - min: Minimum inflation rate
            - max: Maximum inflation rate
    """
    r214_avg = calculate_average_inflation(df, r214_foods)
    non_r214_avg = calculate_average_inflation(df, non_r214_foods)

    return {
        'R214': {
            'mean': r214_avg.mean(),
            'median': r214_avg.median(),
            'std': r214_avg.std(),
            'min': r214_avg.min(),
            'max': r214_avg.max()
        },
        'Non-R214': {
            'mean': non_r214_avg.mean(),
            'median': non_r214_avg.median(),
            'std': non_r214_avg.std(),
            'min': non_r214_avg.min(),
            'max': non_r214_avg.max()
        }
    }
