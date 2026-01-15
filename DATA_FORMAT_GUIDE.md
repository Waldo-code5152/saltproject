# Data Format Guide

## Expected Excel File Structure

Your Excel file should have the following structure:

### Column Layout

| Date       | White bread | Brown bread | Ham  | Milk | ... (other foods) |
|------------|-------------|-------------|------|------|-------------------|
| 2009-01-01 | 2.5         | 3.1         | 4.2  | 2.8  | ...               |
| 2009-02-01 | 2.7         | 3.3         | 4.5  | 2.9  | ...               |
| 2009-03-01 | 2.4         | 3.0         | 4.1  | 2.7  | ...               |
| ...        | ...         | ...         | ...  | ...  | ...               |

### Requirements

1. **First Column**: Date column (any name is acceptable)
   - Format: Date/DateTime
   - Can be any standard date format Excel recognizes

2. **Other Columns**: Food product inflation rates
   - Column names should match the food product names
   - Values should be month-on-month inflation rates (as percentages)
   - Missing values (NaN) are acceptable for products without data in early periods

3. **Food Names**:
   - Column names should match or be similar to R214 regulated food names (case-insensitive)
   - The script will automatically categorize foods into R214 vs non-R214

### R214 Regulated Foods List

The following foods are recognized as R214 regulated (case-insensitive matching):

**Bread Products:**
- White bread
- Brown bread
- Bread rolls

**Cereals:**
- Cold cereals
- Hot cereals (porridge)

**Instant Products:**
- Instant noodles

**Processed Meats:**
- Ham
- Bacon
- Sausages (beef, pork, mutton)
- Boerewors
- Polony
- Corned meat
- Beef mince - fresh

**Spreads:**
- Margarine spread
- Brick margarine

**Snacks:**
- Savoury biscuits
- Potato crisps
- Corn/Maize chips
- Soup powder
- Stock cubes/powder

### Example File Structure

```
Date         | White bread | Brown bread | Milk  | Cheese | ...
-------------|-------------|-------------|-------|--------|----
2009-01-31   | 2.5         | 3.1         | 2.8   | 3.2    | ...
2009-02-28   | 2.7         | 3.3         | 2.9   | 3.1    | ...
2009-03-31   | 2.4         | 3.0         | 2.7   | 3.4    | ...
```

### Running the Analysis

Once your Excel file is ready:

```bash
# If file is in data/ directory
python run_analysis.py data/your_inflation_data.xlsx

# If file is elsewhere
python run_analysis.py /path/to/your/inflation_data.xlsx
```

### What the Analysis Will Produce

1. **Console Output:**
   - Food categorization (R214 vs non-R214)
   - Statistical summary (means, medians, volatility)
   - Unit root test results (stationarity)
   - Cointegration test results
   - VECM estimation (if applicable)
   - Key findings summary

2. **Visualization Files (in `output/` directory):**
   - `r214_vs_nonr214_comparison.png` - Time series comparison
   - `r214_individual_trends.png` - Individual R214 food trends
   - `nonr214_individual_trends.png` - Individual non-R214 food trends

### Troubleshooting

**"No R214 foods found":**
- Check that your column names match the R214 food list above
- Matching is case-insensitive, so "White Bread", "white bread", "WHITE BREAD" all work
- Ensure there are no extra spaces or special characters

**"Columns not found":**
- Verify column names in your Excel file
- Check for spelling errors
- Make sure the first row contains headers

**"Insufficient observations":**
- Some statistical tests require minimum data points
- VECM requires at least 10 observations

### Need Help?

If you encounter issues:
1. Check the first few rows of your Excel file match the expected format
2. Verify date column is recognized as dates
3. Ensure numeric values are not stored as text
4. Check for any special characters or formatting issues

You can also run the demo analysis to see an example:
```bash
python demo_analysis.py
```
