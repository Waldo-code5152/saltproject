"""
Comprehensive tests for the inflation_analysis module.

Tests cover all functions with various edge cases, error conditions,
and normal operation scenarios.
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
from unittest.mock import patch, MagicMock
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from inflation_analysis import (
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


# Fixtures
@pytest.fixture
def sample_inflation_data():
    """Create sample inflation data for testing."""
    dates = pd.date_range('2020-01-01', periods=24, freq='M')
    data = {
        'Date': dates,
        'White bread': np.random.randn(24) * 2 + 3,
        'Brown bread': np.random.randn(24) * 2 + 3.5,
        'Milk': np.random.randn(24) * 1.5 + 2.5,
        'Cheese': np.random.randn(24) * 2 + 4,
        'Ham': np.random.randn(24) * 2.5 + 3,
        'Bacon': np.random.randn(24) * 2.5 + 3.2
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_time_series():
    """Create sample time series for statistical tests."""
    np.random.seed(42)
    # Stationary series
    stationary = np.random.randn(100)
    # Non-stationary series (random walk)
    non_stationary = np.cumsum(np.random.randn(100))
    return stationary, non_stationary


@pytest.fixture
def temp_excel_file(sample_inflation_data):
    """Create a temporary Excel file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        sample_inflation_data.to_excel(tmp.name, index=False)
        yield tmp.name
    os.unlink(tmp.name)


# Tests for load_inflation_data
class TestLoadInflationData:
    """Tests for load_inflation_data function."""

    def test_load_valid_file(self, temp_excel_file):
        """Test loading a valid Excel file."""
        df = load_inflation_data(temp_excel_file)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'Date' in df.columns or df.columns[0] == 'Date'

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Data file not found"):
            load_inflation_data('/nonexistent/path/file.xlsx')

    def test_load_with_sheet_name(self, temp_excel_file):
        """Test loading with specific sheet name."""
        df = load_inflation_data(temp_excel_file, sheet_name=0)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_empty_dataframe_raises_error(self):
        """Test that empty data raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            pd.DataFrame().to_excel(tmp.name, index=False)
            with pytest.raises(ValueError, match="empty"):
                load_inflation_data(tmp.name)
            os.unlink(tmp.name)


# Tests for categorize_foods
class TestCategorizeFoods:
    """Tests for categorize_foods function."""

    def test_categorize_with_r214_foods(self, sample_inflation_data):
        """Test categorization with R214 foods present."""
        r214, non_r214 = categorize_foods(sample_inflation_data)

        assert 'White bread' in r214
        assert 'Brown bread' in r214
        assert 'Ham' in r214
        assert 'Bacon' in r214
        assert 'Milk' in non_r214
        assert 'Cheese' in non_r214

    def test_categorize_case_insensitive(self):
        """Test that categorization is case-insensitive."""
        df = pd.DataFrame({
            'Date': pd.date_range('2020-01-01', periods=5, freq='M'),
            'WHITE BREAD': [1, 2, 3, 4, 5],
            'white bread': [1, 2, 3, 4, 5],
            'White Bread': [1, 2, 3, 4, 5]
        })
        r214, non_r214 = categorize_foods(df)

        assert len(r214) == 3
        assert len(non_r214) == 0

    def test_categorize_with_custom_list(self, sample_inflation_data):
        """Test categorization with custom R214 list."""
        custom_r214 = ['Milk', 'Cheese']
        r214, non_r214 = categorize_foods(sample_inflation_data, custom_r214)

        assert 'Milk' in r214
        assert 'Cheese' in r214
        assert 'White bread' in non_r214

    def test_categorize_excludes_date_column(self, sample_inflation_data):
        """Test that Date column is not included in categorization."""
        r214, non_r214 = categorize_foods(sample_inflation_data)

        assert 'Date' not in r214
        assert 'Date' not in non_r214

    def test_categorize_empty_dataframe(self):
        """Test categorization with empty dataframe."""
        df = pd.DataFrame()
        r214, non_r214 = categorize_foods(df)

        assert len(r214) == 0
        assert len(non_r214) == 0


# Tests for calculate_average_inflation
class TestCalculateAverageInflation:
    """Tests for calculate_average_inflation function."""

    def test_calculate_average_basic(self, sample_inflation_data):
        """Test basic average calculation."""
        foods = ['White bread', 'Brown bread']
        avg = calculate_average_inflation(sample_inflation_data, foods)

        assert isinstance(avg, pd.Series)
        assert len(avg) == len(sample_inflation_data)

    def test_calculate_average_single_food(self, sample_inflation_data):
        """Test average with single food."""
        foods = ['White bread']
        avg = calculate_average_inflation(sample_inflation_data, foods)

        assert isinstance(avg, pd.Series)
        np.testing.assert_array_almost_equal(
            avg.values,
            sample_inflation_data['White bread'].values
        )

    def test_calculate_average_with_nan(self):
        """Test average calculation with NaN values."""
        df = pd.DataFrame({
            'Food1': [1, 2, np.nan, 4],
            'Food2': [2, np.nan, 4, 5]
        })
        avg = calculate_average_inflation(df, ['Food1', 'Food2'])

        assert not np.isnan(avg[0])  # Should average [1, 2]
        assert not np.isnan(avg[1])  # Should handle NaN
        assert len(avg) == 4

    def test_calculate_average_empty_list_raises_error(self, sample_inflation_data):
        """Test that empty food list raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            calculate_average_inflation(sample_inflation_data, [])

    def test_calculate_average_missing_columns_raises_error(self, sample_inflation_data):
        """Test that missing columns raise ValueError."""
        with pytest.raises(ValueError, match="not found"):
            calculate_average_inflation(sample_inflation_data, ['NonexistentFood'])

    def test_calculate_average_all_foods(self, sample_inflation_data):
        """Test average across all food columns."""
        foods = ['White bread', 'Brown bread', 'Milk', 'Cheese', 'Ham', 'Bacon']
        avg = calculate_average_inflation(sample_inflation_data, foods)

        assert len(avg) == len(sample_inflation_data)
        # Check that average is within reasonable range
        assert avg.mean() > 0


# Tests for calculate_category_average
class TestCalculateCategoryAverage:
    """Tests for calculate_category_average function."""

    def test_calculate_category_average_basic(self, sample_inflation_data):
        """Test basic category average calculation."""
        foods = ['White bread', 'Brown bread']
        avg = calculate_category_average(sample_inflation_data, foods)

        assert isinstance(avg, (float, np.floating))
        assert not np.isnan(avg)

    def test_calculate_category_average_empty_list(self, sample_inflation_data):
        """Test category average with empty list returns NaN."""
        avg = calculate_category_average(sample_inflation_data, [])
        assert np.isnan(avg)

    def test_calculate_category_average_missing_columns(self, sample_inflation_data):
        """Test category average with all missing columns returns NaN."""
        avg = calculate_category_average(sample_inflation_data, ['NonexistentFood'])
        assert np.isnan(avg)

    def test_calculate_category_average_partial_missing(self, sample_inflation_data):
        """Test category average with some missing columns."""
        avg = calculate_category_average(
            sample_inflation_data,
            ['White bread', 'NonexistentFood']
        )
        assert not np.isnan(avg)


# Tests for perform_unit_root_test
class TestPerformUnitRootTest:
    """Tests for perform_unit_root_test function."""

    def test_unit_root_stationary_series(self, sample_time_series):
        """Test unit root test on stationary series."""
        stationary, _ = sample_time_series
        series = pd.Series(stationary)
        result = perform_unit_root_test(series)

        assert 'adf_statistic' in result
        assert 'p_value' in result
        assert 'is_stationary' in result
        assert 'critical_values' in result
        assert isinstance(result['is_stationary'], bool)

    def test_unit_root_nonstationary_series(self, sample_time_series):
        """Test unit root test on non-stationary series."""
        _, non_stationary = sample_time_series
        series = pd.Series(non_stationary)
        result = perform_unit_root_test(series)

        assert 'adf_statistic' in result
        assert 'p_value' in result
        assert isinstance(result['p_value'], float)

    def test_unit_root_with_nan_values(self):
        """Test unit root test handles NaN values."""
        series = pd.Series([1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10])
        result = perform_unit_root_test(series)

        assert 'adf_statistic' in result
        assert not np.isnan(result['adf_statistic'])

    def test_unit_root_too_short_series_raises_error(self):
        """Test that too short series raises ValueError."""
        series = pd.Series([1, 2])
        with pytest.raises(ValueError, match="too short"):
            perform_unit_root_test(series)

    def test_unit_root_custom_significance_level(self, sample_time_series):
        """Test unit root test with custom significance level."""
        stationary, _ = sample_time_series
        series = pd.Series(stationary)
        result = perform_unit_root_test(series, significance_level=0.01)

        assert 'is_stationary' in result
        assert isinstance(result['is_stationary'], bool)

    def test_unit_root_all_nan_raises_error(self):
        """Test that all NaN series raises ValueError."""
        series = pd.Series([np.nan, np.nan, np.nan, np.nan])
        with pytest.raises(ValueError, match="too short"):
            perform_unit_root_test(series)


# Tests for perform_cointegration_test
class TestPerformCointegrationTest:
    """Tests for perform_cointegration_test function."""

    def test_cointegration_basic(self):
        """Test basic cointegration test."""
        np.random.seed(42)
        # Create cointegrated series
        series1 = pd.Series(np.cumsum(np.random.randn(100)))
        series2 = series1 + np.random.randn(100) * 0.5

        result = perform_cointegration_test(series1, series2)

        assert 'test_statistic' in result
        assert 'p_value' in result
        assert 'is_cointegrated' in result
        assert 'critical_values' in result
        assert isinstance(result['is_cointegrated'], bool)

    def test_cointegration_with_nan(self):
        """Test cointegration test with NaN values."""
        series1 = pd.Series([1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10])
        series2 = pd.Series([2, 3, 4, np.nan, 6, 7, 8, 9, 10, 11])

        result = perform_cointegration_test(series1, series2)

        assert 'test_statistic' in result
        assert not np.isnan(result['test_statistic'])

    def test_cointegration_too_short_raises_error(self):
        """Test that too short series raises ValueError."""
        series1 = pd.Series([1, 2])
        series2 = pd.Series([2, 3])

        with pytest.raises(ValueError, match="too short"):
            perform_cointegration_test(series1, series2)

    def test_cointegration_custom_significance(self):
        """Test cointegration with custom significance level."""
        np.random.seed(42)
        series1 = pd.Series(np.cumsum(np.random.randn(50)))
        series2 = pd.Series(np.cumsum(np.random.randn(50)))

        result = perform_cointegration_test(series1, series2, significance_level=0.01)

        assert 'is_cointegrated' in result
        assert isinstance(result['is_cointegrated'], bool)

    def test_cointegration_unequal_length_handled(self):
        """Test that series of unequal length are handled."""
        series1 = pd.Series(np.random.randn(100))
        series2 = pd.Series(np.random.randn(50))

        # Should work by aligning
        result = perform_cointegration_test(series1, series2)
        assert 'test_statistic' in result


# Tests for estimate_vecm
class TestEstimateVECM:
    """Tests for estimate_vecm function."""

    def test_vecm_basic(self, sample_inflation_data):
        """Test basic VECM estimation."""
        foods = ['White bread', 'Brown bread']
        result = estimate_vecm(sample_inflation_data, foods)

        assert 'model' in result
        assert 'summary' in result
        assert 'alpha' in result
        assert 'beta' in result
        assert isinstance(result['summary'], str)

    def test_vecm_with_more_variables(self, sample_inflation_data):
        """Test VECM with multiple variables."""
        foods = ['White bread', 'Brown bread', 'Ham']
        result = estimate_vecm(sample_inflation_data, foods)

        assert 'model' in result
        assert result['alpha'] is not None
        assert result['beta'] is not None

    def test_vecm_single_variable_raises_error(self, sample_inflation_data):
        """Test that single variable raises ValueError."""
        with pytest.raises(ValueError, match="at least 2 variables"):
            estimate_vecm(sample_inflation_data, ['White bread'])

    def test_vecm_empty_list_raises_error(self, sample_inflation_data):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="at least 2 variables"):
            estimate_vecm(sample_inflation_data, [])

    def test_vecm_missing_columns_raises_error(self, sample_inflation_data):
        """Test that missing columns raise ValueError."""
        with pytest.raises(ValueError, match="not found"):
            estimate_vecm(sample_inflation_data, ['Food1', 'Food2'])

    def test_vecm_insufficient_observations_raises_error(self):
        """Test that insufficient observations raise ValueError."""
        df = pd.DataFrame({
            'Food1': [1, 2, 3],
            'Food2': [2, 3, 4]
        })
        with pytest.raises(ValueError, match="Insufficient observations"):
            estimate_vecm(df, ['Food1', 'Food2'])

    def test_vecm_custom_parameters(self, sample_inflation_data):
        """Test VECM with custom parameters."""
        foods = ['White bread', 'Brown bread']
        result = estimate_vecm(
            sample_inflation_data,
            foods,
            deterministic='co',
            k_ar_diff=2
        )

        assert result['deterministic'] == 'co'
        # k_ar is k_ar_diff + 1 in VECM
        assert result['k_ar'] == 3

    def test_vecm_with_nan_values(self):
        """Test VECM handles NaN values by dropping them."""
        np.random.seed(42)
        # Create more varied data to avoid singular matrix
        df = pd.DataFrame({
            'Food1': [1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10, 11, 12] + list(np.random.randn(10) + 10),
            'Food2': [2, 3, 4, np.nan, 6, 7, 8, 9, 10, 11, 12, 13] + list(np.random.randn(10) + 11)
        })
        result = estimate_vecm(df, ['Food1', 'Food2'])

        assert 'model' in result


# Tests for plot_inflation_comparison
class TestPlotInflationComparison:
    """Tests for plot_inflation_comparison function."""

    def test_plot_comparison_basic(self, sample_inflation_data):
        """Test basic inflation comparison plot."""
        r214_foods = ['White bread', 'Brown bread', 'Ham']
        non_r214_foods = ['Milk', 'Cheese']

        fig = plot_inflation_comparison(
            sample_inflation_data,
            r214_foods,
            non_r214_foods
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_comparison_with_save(self, sample_inflation_data):
        """Test plot with save path."""
        r214_foods = ['White bread', 'Brown bread']
        non_r214_foods = ['Milk', 'Cheese']

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            fig = plot_inflation_comparison(
                sample_inflation_data,
                r214_foods,
                non_r214_foods,
                save_path=tmp.name
            )

            assert os.path.exists(tmp.name)
            plt.close(fig)
            os.unlink(tmp.name)

    def test_plot_comparison_with_date_index(self):
        """Test plot with date as index instead of column."""
        dates = pd.date_range('2020-01-01', periods=12, freq='M')
        df = pd.DataFrame({
            'Food1': np.random.randn(12),
            'Food2': np.random.randn(12),
            'Food3': np.random.randn(12)
        }, index=dates)

        fig = plot_inflation_comparison(df, ['Food1'], ['Food2'])

        assert isinstance(fig, plt.Figure)
        plt.close(fig)


# Tests for plot_individual_foods
class TestPlotIndividualFoods:
    """Tests for plot_individual_foods function."""

    def test_plot_individual_basic(self, sample_inflation_data):
        """Test basic individual foods plot."""
        foods = ['White bread', 'Brown bread', 'Ham']

        fig = plot_individual_foods(sample_inflation_data, foods)

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_individual_empty_list_raises_error(self, sample_inflation_data):
        """Test that empty food list raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            plot_individual_foods(sample_inflation_data, [])

    def test_plot_individual_with_custom_title(self, sample_inflation_data):
        """Test plot with custom title."""
        foods = ['White bread', 'Brown bread']

        fig = plot_individual_foods(
            sample_inflation_data,
            foods,
            title="Custom Title"
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_individual_with_save(self, sample_inflation_data):
        """Test individual plot with save path."""
        foods = ['White bread', 'Milk']

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            fig = plot_individual_foods(
                sample_inflation_data,
                foods,
                save_path=tmp.name
            )

            assert os.path.exists(tmp.name)
            plt.close(fig)
            os.unlink(tmp.name)

    def test_plot_individual_missing_foods_handled(self, sample_inflation_data):
        """Test that missing foods are skipped gracefully."""
        foods = ['White bread', 'NonexistentFood', 'Brown bread']

        fig = plot_individual_foods(sample_inflation_data, foods)

        assert isinstance(fig, plt.Figure)
        plt.close(fig)


# Tests for compare_category_statistics
class TestCompareCategoryStatistics:
    """Tests for compare_category_statistics function."""

    def test_compare_statistics_basic(self, sample_inflation_data):
        """Test basic category statistics comparison."""
        r214_foods = ['White bread', 'Brown bread', 'Ham']
        non_r214_foods = ['Milk', 'Cheese']

        stats = compare_category_statistics(
            sample_inflation_data,
            r214_foods,
            non_r214_foods
        )

        assert 'R214' in stats
        assert 'Non-R214' in stats
        assert 'mean' in stats['R214']
        assert 'median' in stats['R214']
        assert 'std' in stats['R214']
        assert 'min' in stats['R214']
        assert 'max' in stats['R214']

    def test_compare_statistics_values(self, sample_inflation_data):
        """Test that statistics are calculated correctly."""
        r214_foods = ['White bread', 'Brown bread']
        non_r214_foods = ['Milk', 'Cheese']

        stats = compare_category_statistics(
            sample_inflation_data,
            r214_foods,
            non_r214_foods
        )

        # Check that all statistics are numeric
        for category in ['R214', 'Non-R214']:
            for stat in ['mean', 'median', 'std', 'min', 'max']:
                assert isinstance(stats[category][stat], (float, np.floating))
                assert not np.isnan(stats[category][stat])

    def test_compare_statistics_min_max_ordering(self, sample_inflation_data):
        """Test that min is less than max."""
        r214_foods = ['White bread', 'Brown bread']
        non_r214_foods = ['Milk', 'Cheese']

        stats = compare_category_statistics(
            sample_inflation_data,
            r214_foods,
            non_r214_foods
        )

        assert stats['R214']['min'] <= stats['R214']['max']
        assert stats['Non-R214']['min'] <= stats['Non-R214']['max']

    def test_compare_statistics_std_non_negative(self, sample_inflation_data):
        """Test that standard deviation is non-negative."""
        r214_foods = ['White bread', 'Brown bread']
        non_r214_foods = ['Milk', 'Cheese']

        stats = compare_category_statistics(
            sample_inflation_data,
            r214_foods,
            non_r214_foods
        )

        assert stats['R214']['std'] >= 0
        assert stats['Non-R214']['std'] >= 0


# Integration tests
class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_full_analysis_pipeline(self, sample_inflation_data):
        """Test complete analysis pipeline."""
        # Categorize foods
        r214_foods, non_r214_foods = categorize_foods(sample_inflation_data)

        assert len(r214_foods) > 0
        assert len(non_r214_foods) > 0

        # Calculate averages
        r214_avg = calculate_average_inflation(sample_inflation_data, r214_foods)
        non_r214_avg = calculate_average_inflation(sample_inflation_data, non_r214_foods)

        assert len(r214_avg) == len(sample_inflation_data)
        assert len(non_r214_avg) == len(sample_inflation_data)

        # Compare statistics
        stats = compare_category_statistics(
            sample_inflation_data,
            r214_foods,
            non_r214_foods
        )

        assert 'R214' in stats
        assert 'Non-R214' in stats

        # Perform unit root test on averages
        r214_test = perform_unit_root_test(r214_avg)
        non_r214_test = perform_unit_root_test(non_r214_avg)

        assert 'adf_statistic' in r214_test
        assert 'adf_statistic' in non_r214_test

        # Test cointegration
        coint_result = perform_cointegration_test(r214_avg, non_r214_avg)

        assert 'is_cointegrated' in coint_result

    def test_r214_foods_constant_available(self):
        """Test that R214_FOODS constant is properly defined."""
        assert isinstance(R214_FOODS, list)
        assert len(R214_FOODS) > 0
        assert 'White bread' in R214_FOODS
        assert 'Brown bread' in R214_FOODS


# Edge case tests
class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_single_observation_dataframe(self):
        """Test handling of dataframe with single observation."""
        df = pd.DataFrame({
            'Date': ['2020-01-01'],
            'Food1': [5.0],
            'Food2': [3.0]
        })

        avg = calculate_average_inflation(df, ['Food1', 'Food2'])
        assert len(avg) == 1
        assert avg[0] == 4.0

    def test_all_nan_column(self):
        """Test handling of column with all NaN values."""
        df = pd.DataFrame({
            'Food1': [np.nan, np.nan, np.nan],
            'Food2': [1, 2, 3]
        })

        avg = calculate_average_inflation(df, ['Food1', 'Food2'])
        # Should average to Food2 values when Food1 is all NaN
        assert not np.isnan(avg[0])

    def test_very_large_dataframe(self):
        """Test with large dataframe."""
        n = 10000
        df = pd.DataFrame({
            'Food1': np.random.randn(n),
            'Food2': np.random.randn(n),
            'Food3': np.random.randn(n)
        })

        avg = calculate_average_inflation(df, ['Food1', 'Food2', 'Food3'])
        assert len(avg) == n

    def test_extreme_values(self):
        """Test with extreme inflation values."""
        df = pd.DataFrame({
            'Food1': [1000, -1000, 500, -500],
            'Food2': [2000, -2000, 1000, -1000]
        })

        avg = calculate_average_inflation(df, ['Food1', 'Food2'])
        assert len(avg) == 4
        assert not any(np.isnan(avg))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
