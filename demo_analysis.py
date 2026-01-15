"""
Demo analysis script showing the inflation analysis capabilities.
"""

import pandas as pd
import numpy as np
import sys
import os

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

# Create sample data for demonstration
np.random.seed(42)

# Generate 60 months of data (5 years)
dates = pd.date_range('2019-01-01', periods=60, freq='M')

# R214 regulated foods with slightly higher and more volatile inflation
r214_base = 3.5
data = {
    'Date': dates,
    'White bread': np.random.randn(60) * 2.5 + r214_base + np.linspace(0, 2, 60),
    'Brown bread': np.random.randn(60) * 2.3 + r214_base + 0.5 + np.linspace(0, 1.8, 60),
    'Bread rolls': np.random.randn(60) * 2.7 + r214_base + 0.3 + np.linspace(0, 2.2, 60),
    'Savoury biscuits': np.random.randn(60) * 2.0 + r214_base + 0.8 + np.linspace(0, 1.5, 60),
    'Ham': np.random.randn(60) * 3.0 + r214_base + 1.2 + np.linspace(0, 2.5, 60),
    'Bacon': np.random.randn(60) * 3.2 + r214_base + 1.5 + np.linspace(0, 2.8, 60),
    'Sausages (beef, pork, mutton)': np.random.randn(60) * 2.8 + r214_base + 1.0 + np.linspace(0, 2.3, 60),
    'Polony': np.random.randn(60) * 2.5 + r214_base + 0.7 + np.linspace(0, 2.0, 60),
    'Margarine spread': np.random.randn(60) * 2.2 + r214_base + 0.4 + np.linspace(0, 1.7, 60),
    'Potato crisps': np.random.randn(60) * 2.1 + r214_base + 0.9 + np.linspace(0, 1.9, 60),
}

# Non-R214 foods with slightly lower average inflation
non_r214_base = 2.8
data.update({
    'Fresh milk': np.random.randn(60) * 2.0 + non_r214_base + np.linspace(0, 1.5, 60),
    'Cheese': np.random.randn(60) * 2.3 + non_r214_base + 0.8 + np.linspace(0, 1.8, 60),
    'Yoghurt': np.random.randn(60) * 1.8 + non_r214_base + 0.3 + np.linspace(0, 1.2, 60),
    'Eggs': np.random.randn(60) * 2.5 + non_r214_base + 0.5 + np.linspace(0, 2.0, 60),
    'Fresh vegetables': np.random.randn(60) * 3.5 + non_r214_base - 0.2 + np.linspace(0, 1.0, 60),
    'Fresh fruit': np.random.randn(60) * 3.0 + non_r214_base + 0.2 + np.linspace(0, 1.3, 60),
    'Rice': np.random.randn(60) * 1.9 + non_r214_base + 0.4 + np.linspace(0, 1.4, 60),
    'Pasta': np.random.randn(60) * 1.7 + non_r214_base + 0.1 + np.linspace(0, 1.1, 60),
})

df = pd.DataFrame(data)

# Save to Excel for demonstration
excel_path = 'data/sample_inflation_data.xlsx'
df.to_excel(excel_path, index=False)
print(f"✓ Created sample data: {excel_path}")
print(f"  - Time period: {dates[0].strftime('%Y-%m')} to {dates[-1].strftime('%Y-%m')}")
print(f"  - Total products: {len(df.columns) - 1}")
print()

# ============================================================================
# ANALYSIS WORKFLOW
# ============================================================================

print("="*70)
print("INFLATION ANALYSIS: R214 vs NON-R214 FOODS")
print("="*70)
print()

# 1. Categorize foods
print("1. FOOD CATEGORIZATION")
print("-" * 70)
r214_foods, non_r214_foods = categorize_foods(df)
print(f"R214 Regulated Foods ({len(r214_foods)}):")
for food in r214_foods:
    print(f"  • {food}")
print(f"\nNon-R214 Foods ({len(non_r214_foods)}):")
for food in non_r214_foods:
    print(f"  • {food}")
print()

# 2. Calculate averages
print("2. AVERAGE INFLATION RATES")
print("-" * 70)
r214_avg = calculate_average_inflation(df, r214_foods)
non_r214_avg = calculate_average_inflation(df, non_r214_foods)

print(f"R214 Foods:")
print(f"  - Latest month: {r214_avg.iloc[-1]:.2f}%")
print(f"  - Average over period: {r214_avg.mean():.2f}%")
print(f"  - Volatility (std dev): {r214_avg.std():.2f}%")
print()

print(f"Non-R214 Foods:")
print(f"  - Latest month: {non_r214_avg.iloc[-1]:.2f}%")
print(f"  - Average over period: {non_r214_avg.mean():.2f}%")
print(f"  - Volatility (std dev): {non_r214_avg.std():.2f}%")
print()

# 3. Comprehensive statistics
print("3. DETAILED STATISTICAL COMPARISON")
print("-" * 70)
stats = compare_category_statistics(df, r214_foods, non_r214_foods)

print(f"{'Metric':<20} {'R214 Foods':>15} {'Non-R214 Foods':>17}")
print("-" * 70)
print(f"{'Mean':.<20} {stats['R214']['mean']:>14.2f}% {stats['Non-R214']['mean']:>16.2f}%")
print(f"{'Median':.<20} {stats['R214']['median']:>14.2f}% {stats['Non-R214']['median']:>16.2f}%")
print(f"{'Std Deviation':.<20} {stats['R214']['std']:>14.2f}% {stats['Non-R214']['std']:>16.2f}%")
print(f"{'Minimum':.<20} {stats['R214']['min']:>14.2f}% {stats['Non-R214']['min']:>16.2f}%")
print(f"{'Maximum':.<20} {stats['R214']['max']:>14.2f}% {stats['Non-R214']['max']:>16.2f}%")
print()

# 4. Unit root tests
print("4. STATIONARITY TESTS (Augmented Dickey-Fuller)")
print("-" * 70)

r214_test = perform_unit_root_test(r214_avg)
print(f"R214 Foods Average:")
print(f"  - ADF Statistic: {r214_test['adf_statistic']:.4f}")
print(f"  - P-value: {r214_test['p_value']:.4f}")
print(f"  - Is Stationary: {r214_test['is_stationary']}")
print(f"  - Critical Values:")
for level, value in r214_test['critical_values'].items():
    print(f"      {level}: {value:.4f}")
print()

non_r214_test = perform_unit_root_test(non_r214_avg)
print(f"Non-R214 Foods Average:")
print(f"  - ADF Statistic: {non_r214_test['adf_statistic']:.4f}")
print(f"  - P-value: {non_r214_test['p_value']:.4f}")
print(f"  - Is Stationary: {non_r214_test['is_stationary']}")
print(f"  - Critical Values:")
for level, value in non_r214_test['critical_values'].items():
    print(f"      {level}: {value:.4f}")
print()

# 5. Cointegration test
print("5. COINTEGRATION TEST")
print("-" * 70)
coint_result = perform_cointegration_test(r214_avg, non_r214_avg)
print(f"Testing if R214 and Non-R214 inflation rates move together:")
print(f"  - Test Statistic: {coint_result['test_statistic']:.4f}")
print(f"  - P-value: {coint_result['p_value']:.4f}")
print(f"  - Are Cointegrated: {coint_result['is_cointegrated']}")
print()
if coint_result['is_cointegrated']:
    print("  → Result: The series are cointegrated, suggesting a long-run")
    print("    equilibrium relationship between R214 and non-R214 food inflation.")
else:
    print("  → Result: No significant cointegration detected.")
print()

# 6. VECM Estimation
print("6. VECTOR ERROR CORRECTION MODEL (VECM)")
print("-" * 70)
# Select key R214 products for VECM
vecm_foods = ['White bread', 'Brown bread', 'Ham', 'Bacon']
print(f"Estimating VECM for: {', '.join(vecm_foods)}")
print()

try:
    vecm_result = estimate_vecm(df, vecm_foods, k_ar_diff=2)
    print(f"Model successfully estimated:")
    print(f"  - Number of variables: {len(vecm_foods)}")
    print(f"  - AR lags: {vecm_result['k_ar']}")
    print(f"  - Deterministic terms: {vecm_result['deterministic']}")
    print()
    print("Adjustment coefficients (alpha):")
    print(vecm_result['alpha'])
    print()
    print("Cointegration vectors (beta):")
    print(vecm_result['beta'])
    print()
except Exception as e:
    print(f"Note: VECM estimation requires more sophisticated analysis.")
    print(f"Error: {e}")
    print()

# 7. Create visualizations
print("7. VISUALIZATIONS")
print("-" * 70)

# Plot comparison
fig1 = plot_inflation_comparison(
    df, r214_foods, non_r214_foods,
    save_path='data/r214_vs_nonr214_comparison.png'
)
print("✓ Created: data/r214_vs_nonr214_comparison.png")

# Plot individual R214 foods
fig2 = plot_individual_foods(
    df,
    ['White bread', 'Brown bread', 'Ham', 'Bacon', 'Sausages (beef, pork, mutton)'],
    title="Key R214 Regulated Foods - Inflation Trends",
    save_path='data/r214_individual_trends.png'
)
print("✓ Created: data/r214_individual_trends.png")

# Plot individual non-R214 foods
fig3 = plot_individual_foods(
    df,
    ['Fresh milk', 'Cheese', 'Eggs', 'Rice'],
    title="Selected Non-R214 Foods - Inflation Trends",
    save_path='data/nonr214_individual_trends.png'
)
print("✓ Created: data/nonr214_individual_trends.png")
print()

# 8. Key findings summary
print("="*70)
print("KEY FINDINGS SUMMARY")
print("="*70)
print()

diff = stats['R214']['mean'] - stats['Non-R214']['mean']
print(f"1. Average inflation differential: {abs(diff):.2f} percentage points")
if diff > 0:
    print(f"   R214 foods have HIGHER average inflation than non-R214 foods")
else:
    print(f"   R214 foods have LOWER average inflation than non-R214 foods")
print()

print(f"2. Volatility comparison:")
if stats['R214']['std'] > stats['Non-R214']['std']:
    print(f"   R214 foods show MORE volatile inflation (std: {stats['R214']['std']:.2f}% vs {stats['Non-R214']['std']:.2f}%)")
else:
    print(f"   Non-R214 foods show MORE volatile inflation (std: {stats['Non-R214']['std']:.2f}% vs {stats['R214']['std']:.2f}%)")
print()

print(f"3. Stationarity:")
print(f"   R214 series: {'Stationary' if r214_test['is_stationary'] else 'Non-stationary (has trend)'}")
print(f"   Non-R214 series: {'Stationary' if non_r214_test['is_stationary'] else 'Non-stationary (has trend)'}")
print()

print(f"4. Long-run relationship:")
if coint_result['is_cointegrated']:
    print(f"   Evidence of cointegration suggests R214 regulation may not have")
    print(f"   fundamentally decoupled these foods from general food inflation.")
else:
    print(f"   No strong cointegration detected. R214 foods may follow")
    print(f"   different inflation dynamics than non-R214 foods.")
print()

print("="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print()
print("Next steps:")
print("  1. Review the generated plots in the 'data/' directory")
print("  2. Replace sample data with your actual Excel file")
print("  3. Adjust the analysis parameters as needed")
print("  4. Consider adding structural breaks at R214 announcement dates")
