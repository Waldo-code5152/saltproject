"""
Load and restructure actual R214 inflation data for analysis.

This script handles the specific format where:
- Rows are products
- Columns are months (M200901, M200902, etc.)
- R214 indicator column shows which products are regulated
"""

import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from inflation_analysis import (
    calculate_average_inflation,
    compare_category_statistics,
    perform_unit_root_test,
    perform_cointegration_test,
    estimate_vecm,
    plot_inflation_comparison,
    plot_individual_foods
)


def load_and_restructure_data(file_path):
    """
    Load data from the R214 specific format.

    Expected format:
    - Product name column
    - R214 = 1 column (1 if R214 regulated, 0 otherwise)
    - Month columns: M200901, M200902, etc.
    """
    print(f"Loading data from: {file_path}")

    # Load the raw data
    df_raw = pd.read_excel(file_path)

    print(f"✓ Raw data loaded: {len(df_raw)} products")

    # Identify columns
    product_col = 'Product name'
    r214_col = 'R214 = 1'

    # Get all month columns (starts with M and followed by 6 digits)
    month_cols = [col for col in df_raw.columns if isinstance(col, str) and col.startswith('M') and len(col) == 7]
    month_cols_sorted = sorted(month_cols)

    print(f"✓ Found {len(month_cols_sorted)} month columns from {month_cols_sorted[0]} to {month_cols_sorted[-1]}")

    # Filter to products with valid names and R214 indicator
    df_products = df_raw[[product_col, r214_col] + month_cols_sorted].copy()
    df_products = df_products[df_products[product_col].notna()].copy()

    print(f"✓ Valid products: {len(df_products)}")

    # Separate R214 and non-R214 products
    r214_mask = df_products[r214_col] == 1
    r214_products = df_products[r214_mask]
    non_r214_products = df_products[~r214_mask]

    print(f"✓ R214 products: {len(r214_products)}")
    print(f"✓ Non-R214 products: {len(non_r214_products)}")

    # Restructure to have dates as rows and products as columns
    # First, create date index from month codes
    dates = []
    for month_code in month_cols_sorted:
        # M200901 -> 2009-01
        year = int(month_code[1:5])
        month = int(month_code[5:7])
        dates.append(pd.Timestamp(year=year, month=month, day=1))

    # Create restructured dataframe
    df_restructured = pd.DataFrame(index=dates)
    df_restructured.index.name = 'Date'

    # Add R214 products
    for idx, row in r214_products.iterrows():
        product_name = row[product_col]
        values = row[month_cols_sorted].values
        df_restructured[product_name] = values

    # Add non-R214 products
    for idx, row in non_r214_products.iterrows():
        product_name = row[product_col]
        values = row[month_cols_sorted].values
        df_restructured[product_name] = values

    # Get lists of R214 and non-R214 product names
    r214_food_names = r214_products[product_col].tolist()
    non_r214_food_names = non_r214_products[product_col].tolist()

    print(f"✓ Restructured data shape: {df_restructured.shape}")
    print(f"  - Time periods: {len(df_restructured)}")
    print(f"  - Total products: {len(df_restructured.columns)}")

    return df_restructured, r214_food_names, non_r214_food_names


def main():
    file_path = "data/R214 inflation rates data.xlsx"

    print("="*80)
    print("R214 SALT REGULATION FOODS - INFLATION ANALYSIS")
    print("="*80)
    print()

    # Load and restructure data
    try:
        df, r214_foods, non_r214_foods = load_and_restructure_data(file_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return

    print()
    print("-" * 80)
    print("DATA SUMMARY")
    print("-" * 80)
    print(f"Time period: {df.index[0].strftime('%Y-%m')} to {df.index[-1].strftime('%Y-%m')}")
    print(f"Total months: {len(df)}")
    print(f"R214 regulated products: {len(r214_foods)}")
    print(f"Non-R214 products: {len(non_r214_foods)}")
    print()

    # Show R214 products
    print("-" * 80)
    print(f"R214 REGULATED PRODUCTS ({len(r214_foods)})")
    print("-" * 80)
    for i, product in enumerate(r214_foods, 1):
        print(f"  {i:3d}. {product}")
    print()

    # Show sample non-R214 products
    print("-" * 80)
    print(f"NON-R214 PRODUCTS (showing first 20 of {len(non_r214_foods)})")
    print("-" * 80)
    for i, product in enumerate(non_r214_foods[:20], 1):
        print(f"  {i:3d}. {product}")
    if len(non_r214_foods) > 20:
        print(f"  ... and {len(non_r214_foods) - 20} more")
    print()

    # Calculate averages
    print("-" * 80)
    print("AVERAGE INFLATION RATES")
    print("-" * 80)

    r214_avg = calculate_average_inflation(df, r214_foods)
    non_r214_avg = calculate_average_inflation(df, non_r214_foods)

    print(f"\nR214 Foods:")
    print(f"  - First month ({df.index[0].strftime('%Y-%m')}): {r214_avg.iloc[0]:.2f}%")
    print(f"  - Latest month ({df.index[-1].strftime('%Y-%m')}): {r214_avg.iloc[-1]:.2f}%")
    print(f"  - Average over entire period: {r214_avg.mean():.2f}%")
    print(f"  - Volatility (std dev): {r214_avg.std():.2f}%")
    print(f"  - Minimum: {r214_avg.min():.2f}%")
    print(f"  - Maximum: {r214_avg.max():.2f}%")

    print(f"\nNon-R214 Foods:")
    print(f"  - First month ({df.index[0].strftime('%Y-%m')}): {non_r214_avg.iloc[0]:.2f}%")
    print(f"  - Latest month ({df.index[-1].strftime('%Y-%m')}): {non_r214_avg.iloc[-1]:.2f}%")
    print(f"  - Average over entire period: {non_r214_avg.mean():.2f}%")
    print(f"  - Volatility (std dev): {non_r214_avg.std():.2f}%")
    print(f"  - Minimum: {non_r214_avg.min():.2f}%")
    print(f"  - Maximum: {non_r214_avg.max():.2f}%")
    print()

    # Statistical comparison
    print("-" * 80)
    print("STATISTICAL COMPARISON")
    print("-" * 80)

    stats = compare_category_statistics(df, r214_foods, non_r214_foods)

    diff_mean = stats['R214']['mean'] - stats['Non-R214']['mean']
    diff_median = stats['R214']['median'] - stats['Non-R214']['median']
    diff_std = stats['R214']['std'] - stats['Non-R214']['std']

    print(f"\n{'Metric':<25} {'R214 Foods':>15} {'Non-R214 Foods':>17} {'Difference':>15}")
    print("-" * 80)
    print(f"{'Mean':<25} {stats['R214']['mean']:>14.2f}% {stats['Non-R214']['mean']:>16.2f}% {diff_mean:>14.2f}pp")
    print(f"{'Median':<25} {stats['R214']['median']:>14.2f}% {stats['Non-R214']['median']:>16.2f}% {diff_median:>14.2f}pp")
    print(f"{'Std Deviation':<25} {stats['R214']['std']:>14.2f}% {stats['Non-R214']['std']:>16.2f}% {diff_std:>14.2f}pp")
    print(f"{'Minimum':<25} {stats['R214']['min']:>14.2f}% {stats['Non-R214']['min']:>16.2f}%")
    print(f"{'Maximum':<25} {stats['R214']['max']:>14.2f}% {stats['Non-R214']['max']:>16.2f}%")
    print()

    # Unit root tests
    print("-" * 80)
    print("STATIONARITY TESTS (Augmented Dickey-Fuller)")
    print("-" * 80)

    r214_test = perform_unit_root_test(r214_avg)
    print(f"\nR214 Foods Average:")
    print(f"  - ADF Statistic: {r214_test['adf_statistic']:.4f}")
    print(f"  - P-value: {r214_test['p_value']:.4f}")
    print(f"  - Is Stationary: {r214_test['is_stationary']}")
    if r214_test['is_stationary']:
        print(f"  → Series is STATIONARY (mean-reverting)")
    else:
        print(f"  → Series is NON-STATIONARY (has trend/unit root)")

    non_r214_test = perform_unit_root_test(non_r214_avg)
    print(f"\nNon-R214 Foods Average:")
    print(f"  - ADF Statistic: {non_r214_test['adf_statistic']:.4f}")
    print(f"  - P-value: {non_r214_test['p_value']:.4f}")
    print(f"  - Is Stationary: {non_r214_test['is_stationary']}")
    if non_r214_test['is_stationary']:
        print(f"  → Series is STATIONARY (mean-reverting)")
    else:
        print(f"  → Series is NON-STATIONARY (has trend/unit root)")
    print()

    # Cointegration test
    print("-" * 80)
    print("COINTEGRATION TEST")
    print("-" * 80)

    coint_result = perform_cointegration_test(r214_avg, non_r214_avg)
    print(f"\nTesting if R214 and Non-R214 inflation rates move together:")
    print(f"  - Test Statistic: {coint_result['test_statistic']:.4f}")
    print(f"  - P-value: {coint_result['p_value']:.4f}")
    print(f"  - Are Cointegrated: {coint_result['is_cointegrated']}")

    if coint_result['is_cointegrated']:
        print(f"\n  → COINTEGRATED: Long-run equilibrium relationship detected.")
        print(f"    R214 and non-R214 food inflation move together over time.")
    else:
        print(f"\n  → NOT COINTEGRATED: No long-run relationship.")
        print(f"    R214 foods follow different inflation dynamics.")
    print()

    # VECM
    if len(r214_foods) >= 4:
        print("-" * 80)
        print("VECTOR ERROR CORRECTION MODEL (VECM)")
        print("-" * 80)

        vecm_foods = r214_foods[:min(6, len(r214_foods))]
        print(f"\nEstimating VECM for {len(vecm_foods)} R214 products:")
        for food in vecm_foods:
            print(f"  - {food}")

        try:
            vecm_result = estimate_vecm(df, vecm_foods, k_ar_diff=1)
            print(f"\n✓ Model successfully estimated")
            print(f"  - Number of variables: {len(vecm_foods)}")
            print(f"  - AR lags: {vecm_result['k_ar']}")
            print(f"\nAdjustment coefficients (alpha) - speed of error correction:")
            for i, food in enumerate(vecm_foods):
                print(f"  {food}: {vecm_result['alpha'][i, 0]:.4f}")
        except Exception as e:
            print(f"\nCould not estimate VECM: {e}")
        print()

    # Visualizations
    print("-" * 80)
    print("GENERATING VISUALIZATIONS")
    print("-" * 80)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Reset index for plotting
    df_plot = df.copy()
    df_plot['Date'] = df_plot.index
    df_plot = df_plot.reset_index(drop=True)

    # Comparison plot
    comparison_path = f"{output_dir}/actual_r214_vs_nonr214_comparison.png"
    plot_inflation_comparison(df_plot, r214_foods, non_r214_foods, save_path=comparison_path)
    print(f"✓ Created: {comparison_path}")

    # Individual R214 foods (up to 10)
    if len(r214_foods) > 0:
        r214_plot_foods = r214_foods[:min(10, len(r214_foods))]
        r214_path = f"{output_dir}/actual_r214_individual_trends.png"
        plot_individual_foods(
            df_plot, r214_plot_foods,
            title="R214 Regulated Foods - Inflation Trends (Actual Data)",
            save_path=r214_path
        )
        print(f"✓ Created: {r214_path}")

    # Individual non-R214 foods (up to 10)
    if len(non_r214_foods) > 0:
        non_r214_plot_foods = non_r214_foods[:min(10, len(non_r214_foods))]
        non_r214_path = f"{output_dir}/actual_nonr214_individual_trends.png"
        plot_individual_foods(
            df_plot, non_r214_plot_foods,
            title="Non-R214 Foods - Inflation Trends (Actual Data)",
            save_path=non_r214_path
        )
        print(f"✓ Created: {non_r214_path}")

    print()

    # Key findings
    print("="*80)
    print("KEY FINDINGS")
    print("="*80)

    print(f"\n1. INFLATION DIFFERENTIAL")
    if diff_mean > 0:
        print(f"   R214 foods have {abs(diff_mean):.2f}pp HIGHER average inflation")
    else:
        print(f"   R214 foods have {abs(diff_mean):.2f}pp LOWER average inflation")
    print(f"   R214: {stats['R214']['mean']:.2f}% vs Non-R214: {stats['Non-R214']['mean']:.2f}%")

    print(f"\n2. VOLATILITY")
    if stats['R214']['std'] > stats['Non-R214']['std']:
        print(f"   R214 foods MORE volatile ({stats['R214']['std']:.2f}% vs {stats['Non-R214']['std']:.2f}%)")
    else:
        print(f"   Non-R214 foods MORE volatile ({stats['Non-R214']['std']:.2f}% vs {stats['R214']['std']:.2f}%)")

    print(f"\n3. TIME SERIES PROPERTIES")
    print(f"   R214: {'Stationary' if r214_test['is_stationary'] else 'Non-stationary (trending)'}")
    print(f"   Non-R214: {'Stationary' if non_r214_test['is_stationary'] else 'Non-stationary (trending)'}")

    print(f"\n4. LONG-RUN RELATIONSHIP")
    if coint_result['is_cointegrated']:
        print(f"   COINTEGRATED - R214 regulation hasn't decoupled these foods")
        print(f"   from general food inflation dynamics")
    else:
        print(f"   NOT COINTEGRATED - R214 foods follow different dynamics")

    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nVisualization files saved in: {output_dir}/")
    print(f"  - actual_r214_vs_nonr214_comparison.png")
    print(f"  - actual_r214_individual_trends.png")
    print(f"  - actual_nonr214_individual_trends.png")
    print()


if __name__ == "__main__":
    main()
