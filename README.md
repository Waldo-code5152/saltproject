# Salt Project - R214 Food Inflation Analysis

A Python package for analyzing month-on-month inflation rates of food products, with a focus on comparing R214 salt regulation foods against non-regulated items.

## Overview

This project provides comprehensive tools for:
- Loading and processing inflation rate data from Excel files
- Categorizing food products based on R214 salt regulations
- Statistical analysis including unit root tests and cointegration tests
- VECM (Vector Error Correction Model) estimation
- Visualization of inflation trends
- Comparative analysis between R214 and non-R214 foods

## R214 Regulated Foods

The R214 regulations cover the following food categories:
- Bread products (white bread, brown bread, bread rolls)
- Breakfast cereals (cold cereals, hot cereals/porridge)
- Processed meats (ham, bacon, sausages, boerewors, polony, corned meat, beef mince)
- Spreads (margarine spread, brick margarine)
- Snacks (savoury biscuits, potato crisps, corn/maize chips)
- Instant products (instant noodles, soup powder, stock cubes/powder)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd saltproject

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
saltproject/
├── src/
│   ├── __init__.py
│   └── inflation_analysis.py    # Main analysis module
├── tests/
│   ├── __init__.py
│   └── test_inflation_analysis.py  # Comprehensive test suite
├── data/                         # Place your Excel files here
├── requirements.txt
└── README.md
```

## Usage

### Loading Data

```python
from src.inflation_analysis import load_inflation_data

# Load your inflation data
df = load_inflation_data('data/inflation_rates.xlsx')
```

### Categorizing Foods

```python
from src.inflation_analysis import categorize_foods

# Categorize foods into R214 and non-R214
r214_foods, non_r214_foods = categorize_foods(df)
print(f"Found {len(r214_foods)} R214 foods")
print(f"Found {len(non_r214_foods)} non-R214 foods")
```

### Calculating Average Inflation

```python
from src.inflation_analysis import calculate_average_inflation

# Calculate average inflation for R214 foods
r214_avg = calculate_average_inflation(df, r214_foods)
non_r214_avg = calculate_average_inflation(df, non_r214_foods)
```

### Statistical Analysis

#### Unit Root Tests

```python
from src.inflation_analysis import perform_unit_root_test

# Test for stationarity
result = perform_unit_root_test(r214_avg)
print(f"Is stationary: {result['is_stationary']}")
print(f"ADF Statistic: {result['adf_statistic']:.4f}")
print(f"P-value: {result['p_value']:.4f}")
```

#### Cointegration Tests

```python
from src.inflation_analysis import perform_cointegration_test

# Test for cointegration between R214 and non-R214 foods
result = perform_cointegration_test(r214_avg, non_r214_avg)
print(f"Are cointegrated: {result['is_cointegrated']}")
print(f"P-value: {result['p_value']:.4f}")
```

#### VECM Estimation

```python
from src.inflation_analysis import estimate_vecm

# Estimate VECM for R214 foods
foods_to_model = ['White bread', 'Brown bread', 'Ham', 'Bacon']
result = estimate_vecm(df, foods_to_model, k_ar_diff=1)
print(result['summary'])
```

### Visualization

#### Compare R214 vs Non-R214 Inflation

```python
from src.inflation_analysis import plot_inflation_comparison

# Plot comparison
fig = plot_inflation_comparison(
    df,
    r214_foods,
    non_r214_foods,
    save_path='output/comparison.png'
)
```

#### Plot Individual Foods

```python
from src.inflation_analysis import plot_individual_foods

# Plot specific R214 foods
fig = plot_individual_foods(
    df,
    ['White bread', 'Brown bread', 'Ham', 'Bacon'],
    title="R214 Meat and Bread Products Inflation",
    save_path='output/r214_foods.png'
)
```

### Statistical Comparison

```python
from src.inflation_analysis import compare_category_statistics

# Compare statistics between categories
stats = compare_category_statistics(df, r214_foods, non_r214_foods)

print("R214 Foods Statistics:")
print(f"  Mean: {stats['R214']['mean']:.2f}%")
print(f"  Median: {stats['R214']['median']:.2f}%")
print(f"  Std Dev: {stats['R214']['std']:.2f}%")

print("\nNon-R214 Foods Statistics:")
print(f"  Mean: {stats['Non-R214']['mean']:.2f}%")
print(f"  Median: {stats['Non-R214']['median']:.2f}%")
print(f"  Std Dev: {stats['Non-R214']['std']:.2f}%")
```

## Analysis Workflow

The recommended analysis workflow includes:

1. **Data Loading**: Load month-on-month inflation data from Excel
2. **Categorization**: Separate R214 from non-R214 foods
3. **Visual Exploration**: Plot inflation rates for initial insights
4. **Statistical Testing**:
   - Unit root tests to check for stationarity
   - Cointegration tests to identify long-run relationships
5. **VECM Estimation**: Model relationships with breaks at regulation announcement dates
6. **Interpretation**: Analyze how R214 food inflation relates to overall food inflation

## Running Tests

The project includes comprehensive tests covering all functions:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test class
pytest tests/test_inflation_analysis.py::TestLoadInflationData -v
```

### Test Coverage

The test suite includes:
- **Unit tests** for all individual functions
- **Integration tests** for complete analysis pipelines
- **Edge case tests** for boundary conditions
- **Error handling tests** for invalid inputs

Test categories:
- Data loading and validation
- Food categorization
- Statistical calculations
- Time series tests (unit root, cointegration)
- VECM estimation
- Plotting functions
- Statistical comparisons

## Data Format

Your Excel file should have the following structure:

| Date       | White bread | Brown bread | Milk | ... |
|------------|-------------|-------------|------|-----|
| 2009-01-01 | 2.5         | 2.8         | 3.1  | ... |
| 2009-02-01 | 2.3         | 2.6         | 2.9  | ... |
| ...        | ...         | ...         | ...  | ... |

- First column: Date (will be automatically detected)
- Other columns: Food product names (month-on-month inflation rates)
- Products may have missing values (NaN) for early periods

## Dependencies

- **pandas** (>=2.0.0): Data manipulation and analysis
- **numpy** (>=1.24.0): Numerical computations
- **openpyxl** (>=3.1.0): Excel file handling
- **statsmodels** (>=0.14.0): Statistical tests and models
- **matplotlib** (>=3.7.0): Data visualization
- **pytest** (>=7.4.0): Testing framework

## Functions Reference

### Data Loading
- `load_inflation_data()`: Load data from Excel files

### Categorization
- `categorize_foods()`: Separate R214 from non-R214 foods

### Statistical Calculations
- `calculate_average_inflation()`: Average inflation across foods over time
- `calculate_category_average()`: Overall average for a category
- `compare_category_statistics()`: Compare statistical measures

### Time Series Analysis
- `perform_unit_root_test()`: Augmented Dickey-Fuller test
- `perform_cointegration_test()`: Johansen cointegration test
- `estimate_vecm()`: Vector Error Correction Model estimation

### Visualization
- `plot_inflation_comparison()`: Compare R214 vs non-R214 trends
- `plot_individual_foods()`: Plot individual food inflation rates

## Contributing

When adding new functionality:
1. Write the function with comprehensive docstrings
2. Add corresponding tests in `tests/test_inflation_analysis.py`
3. Update this README with usage examples
4. Ensure all tests pass before committing

## License

[Add your license information here]

## Contact

[Add contact information here]
