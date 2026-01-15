"""
Run inflation analysis on your actual data file.

Usage:
    python run_analysis.py <path_to_excel_file>

Example:
    python run_analysis.py data/my_inflation_data.xlsx
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from inflation_analysis import (
    load_inflation_data,
    categorize_foods,
    calculate_average_inflation,
    compare_category_statistics,
    perform_unit_root_test,
    perform_cointegration_test,
    estimate_vecm,
    plot_inflation_comparison,
    plot_individual_foods
)


def main():
    if len(sys.argv) < 2:
        print("Error: Please provide the path to your Excel file")
        print("Usage: python run_analysis.py <path_to_excel_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    print("="*80)
    print("R214 SALT REGULATION FOODS - INFLATION ANALYSIS")
    print("="*80)
    print()
    print(f"Loading data from: {file_path}")
    print()

    # Load data
    try:
        df = load_inflation_data(file_path)
        print(f"✓ Data loaded successfully")
        print(f"  - Time period: {df['Date'].min()} to {df['Date'].max()}")
        print(f"  - Total observations: {len(df)}")
        print(f"  - Total products: {len(df.columns) - 1}")
        print()
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    # Show first few rows
    print("First 5 rows of data:")
    print(df.head().to_string())
    print()

    # Categorize foods
    print("-" * 80)
    print("FOOD CATEGORIZATION")
    print("-" * 80)
    r214_foods, non_r214_foods = categorize_foods(df)

    print(f"\nR214 Regulated Foods ({len(r214_foods)}):")
    for i, food in enumerate(r214_foods, 1):
        print(f"  {i:2d}. {food}")

    print(f"\nNon-R214 Foods ({len(non_r214_foods)}):")
    for i, food in enumerate(non_r214_foods, 1):
        print(f"  {i:2d}. {food}")
    print()

    if len(r214_foods) == 0:
        print("WARNING: No R214 foods found in the data!")
        print("Please check that your column names match the R214 food list.")
        print("\nExpected R214 foods include:")
        from inflation_analysis import R214_FOODS
        for food in R214_FOODS[:10]:
            print(f"  - {food}")
        print("  ... and more")
        sys.exit(1)

    if len(non_r214_foods) == 0:
        print("WARNING: No non-R214 foods found in the data!")
        sys.exit(1)

    # Calculate averages
    print("-" * 80)
    print("AVERAGE INFLATION RATES")
    print("-" * 80)
    r214_avg = calculate_average_inflation(df, r214_foods)
    non_r214_avg = calculate_average_inflation(df, non_r214_foods)

    print(f"\nR214 Foods:")
    print(f"  - First month: {r214_avg.iloc[0]:.2f}%")
    print(f"  - Latest month: {r214_avg.iloc[-1]:.2f}%")
    print(f"  - Average over entire period: {r214_avg.mean():.2f}%")
    print(f"  - Volatility (std dev): {r214_avg.std():.2f}%")
    print(f"  - Minimum: {r214_avg.min():.2f}%")
    print(f"  - Maximum: {r214_avg.max():.2f}%")

    print(f"\nNon-R214 Foods:")
    print(f"  - First month: {non_r214_avg.iloc[0]:.2f}%")
    print(f"  - Latest month: {non_r214_avg.iloc[-1]:.2f}%")
    print(f"  - Average over entire period: {non_r214_avg.mean():.2f}%")
    print(f"  - Volatility (std dev): {non_r214_avg.std():.2f}%")
    print(f"  - Minimum: {non_r214_avg.min():.2f}%")
    print(f"  - Maximum: {non_r214_avg.max():.2f}%")
    print()

    # Detailed statistics comparison
    print("-" * 80)
    print("STATISTICAL COMPARISON")
    print("-" * 80)
    stats = compare_category_statistics(df, r214_foods, non_r214_foods)

    print(f"\n{'Metric':<25} {'R214 Foods':>15} {'Non-R214 Foods':>17} {'Difference':>15}")
    print("-" * 80)
    diff_mean = stats['R214']['mean'] - stats['Non-R214']['mean']
    diff_median = stats['R214']['median'] - stats['Non-R214']['median']
    diff_std = stats['R214']['std'] - stats['Non-R214']['std']

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
        print(f"  → Series is STATIONARY (no unit root)")
    else:
        print(f"  → Series is NON-STATIONARY (has unit root/trend)")

    non_r214_test = perform_unit_root_test(non_r214_avg)
    print(f"\nNon-R214 Foods Average:")
    print(f"  - ADF Statistic: {non_r214_test['adf_statistic']:.4f}")
    print(f"  - P-value: {non_r214_test['p_value']:.4f}")
    print(f"  - Is Stationary: {non_r214_test['is_stationary']}")
    if non_r214_test['is_stationary']:
        print(f"  → Series is STATIONARY (no unit root)")
    else:
        print(f"  → Series is NON-STATIONARY (has unit root/trend)")
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
        print(f"\n  → COINTEGRATED: The series share a long-run equilibrium relationship.")
        print(f"    This suggests R214 and non-R214 food inflation move together over time.")
    else:
        print(f"\n  → NOT COINTEGRATED: No long-run relationship detected.")
        print(f"    R214 foods may follow different inflation dynamics.")
    print()

    # VECM (if enough R214 foods)
    if len(r214_foods) >= 4:
        print("-" * 80)
        print("VECTOR ERROR CORRECTION MODEL (VECM)")
        print("-" * 80)

        # Select up to 5 R214 foods for VECM
        vecm_foods = r214_foods[:min(5, len(r214_foods))]
        print(f"\nEstimating VECM for {len(vecm_foods)} R214 foods:")
        for food in vecm_foods:
            print(f"  - {food}")

        try:
            vecm_result = estimate_vecm(df, vecm_foods, k_ar_diff=1)
            print(f"\n✓ Model successfully estimated")
            print(f"  - Number of variables: {len(vecm_foods)}")
            print(f"  - AR lags: {vecm_result['k_ar']}")
            print(f"  - Deterministic terms: {vecm_result['deterministic']}")
            print(f"\nAdjustment coefficients (alpha) - first column:")
            print(vecm_result['alpha'][:, 0])
            print(f"\nCointegration vector (beta) - first column:")
            print(vecm_result['beta'][:, 0])
        except Exception as e:
            print(f"\nNote: Could not estimate VECM - {e}")
        print()

    # Create visualizations
    print("-" * 80)
    print("GENERATING VISUALIZATIONS")
    print("-" * 80)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Comparison plot
    comparison_path = f"{output_dir}/r214_vs_nonr214_comparison.png"
    plot_inflation_comparison(df, r214_foods, non_r214_foods, save_path=comparison_path)
    print(f"✓ Created: {comparison_path}")

    # Individual R214 foods (up to 8)
    r214_plot_foods = r214_foods[:min(8, len(r214_foods))]
    r214_path = f"{output_dir}/r214_individual_trends.png"
    plot_individual_foods(
        df, r214_plot_foods,
        title="R214 Regulated Foods - Inflation Trends",
        save_path=r214_path
    )
    print(f"✓ Created: {r214_path}")

    # Individual non-R214 foods (up to 8)
    if len(non_r214_foods) > 0:
        non_r214_plot_foods = non_r214_foods[:min(8, len(non_r214_foods))]
        non_r214_path = f"{output_dir}/nonr214_individual_trends.png"
        plot_individual_foods(
            df, non_r214_plot_foods,
            title="Non-R214 Foods - Inflation Trends",
            save_path=non_r214_path
        )
        print(f"✓ Created: {non_r214_path}")

    print()

    # Summary
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
        print(f"   R214 foods are MORE volatile ({stats['R214']['std']:.2f}% vs {stats['Non-R214']['std']:.2f}%)")
    else:
        print(f"   Non-R214 foods are MORE volatile ({stats['Non-R214']['std']:.2f}% vs {stats['R214']['std']:.2f}%)")

    print(f"\n3. STATIONARITY")
    print(f"   R214: {'Stationary' if r214_test['is_stationary'] else 'Non-stationary (trending)'}")
    print(f"   Non-R214: {'Stationary' if non_r214_test['is_stationary'] else 'Non-stationary (trending)'}")

    print(f"\n4. LONG-RUN RELATIONSHIP")
    if coint_result['is_cointegrated']:
        print(f"   Series are COINTEGRATED - they move together in the long run")
    else:
        print(f"   Series are NOT COINTEGRATED - they follow different dynamics")

    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nVisualization files saved in: {output_dir}/")
    print()


if __name__ == "__main__":
    main()
