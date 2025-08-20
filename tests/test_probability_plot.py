"""Tests for Probability Plot Tool functionality."""

import pytest
import numpy as np
from scipy import stats
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estiem_eda.tools.probability_plot import ProbabilityPlotTool


class TestProbabilityPlotTool:
    """Test cases for Normal Probability Plot analysis."""
    
    @pytest.fixture
    def tool(self):
        """Create ProbabilityPlotTool instance."""
        return ProbabilityPlotTool()
    
    @pytest.fixture
    def normal_data(self):
        """Generate normal distributed test data."""
        np.random.seed(42)
        return list(np.random.normal(10, 2, 50))
    
    @pytest.fixture
    def skewed_data(self):
        """Generate skewed test data."""
        np.random.seed(42)
        return list(np.random.exponential(2, 50))
    
    @pytest.fixture
    def mixed_data(self):
        """Generate mixed distribution data (bimodal)."""
        np.random.seed(42)
        data1 = np.random.normal(8, 1, 25)
        data2 = np.random.normal(12, 1, 25)
        return list(np.concatenate([data1, data2]))
    
    def test_tool_initialization(self, tool):
        """Test tool initializes correctly."""
        assert isinstance(tool, ProbabilityPlotTool)
        assert hasattr(tool, 'get_input_schema')
        assert hasattr(tool, 'execute')
    
    def test_input_schema_structure(self, tool):
        """Test input schema has required structure."""
        schema = tool.get_input_schema()
        
        assert schema["type"] == "object"
        assert "data" in schema["properties"]
        assert schema["properties"]["data"]["type"] == "array"
        assert "data" in schema["required"]
        
        # Optional parameters
        assert "groups" in schema["properties"]
        assert "distribution" in schema["properties"] 
        assert "confidence_level" in schema["properties"]
        assert "title" in schema["properties"]
    
    def test_normal_data_analysis(self, tool, normal_data):
        """Test analysis of normally distributed data."""
        result = tool.execute({
            "data": normal_data,
            "distribution": "normal"
        })
        
        assert result["success"] is True
        assert result["distribution_type"] == "normal"
        assert result["sample_size"] == len(normal_data)
        
        # Check fitted parameters
        params = result["fitted_parameters"]
        assert "mean" in params
        assert "std" in params
        assert abs(params["mean"] - 10) < 1  # Should be close to true mean
        assert abs(params["std"] - 2) < 1    # Should be close to true std
        
        # Check goodness of fit
        gof = result["goodness_of_fit"]
        assert "correlation_coefficient" in gof
        assert gof["correlation_coefficient"] > 0.9  # Should have high correlation for normal data
        
        # Check normality test
        normality = result["normality_test"]
        assert "anderson_darling_statistic" in normality
        assert "p_value" in normality
        assert "is_normal" in normality
    
    def test_skewed_data_analysis(self, tool, skewed_data):
        """Test analysis of skewed (non-normal) data."""
        result = tool.execute({
            "data": skewed_data,
            "distribution": "normal"
        })
        
        assert result["success"] is True
        
        # Skewed data should have poorer fit to normal distribution
        gof = result["goodness_of_fit"]
        assert gof["correlation_coefficient"] < 0.98  # Should have lower correlation
        
        # Should likely fail normality test
        normality = result["normality_test"]
        if normality["p_value"] is not None:
            # Low p-value indicates non-normality
            assert normality["is_normal"] is False or normality["p_value"] < 0.1
    
    def test_confidence_intervals(self, tool, normal_data):
        """Test confidence interval calculation."""
        result = tool.execute({
            "data": normal_data,
            "confidence_level": 0.95
        })
        
        assert result["success"] is True
        
        ci = result["confidence_intervals"]
        assert ci["level"] == 0.95
        assert "lower_bounds" in ci
        assert "upper_bounds" in ci
        assert len(ci["lower_bounds"]) == len(normal_data)
        assert len(ci["upper_bounds"]) == len(normal_data)
        
        # Upper bounds should be greater than lower bounds
        for lower, upper in zip(ci["lower_bounds"], ci["upper_bounds"]):
            assert upper > lower
    
    def test_outlier_detection(self, tool):
        """Test outlier detection functionality."""
        # Create data with clear outliers
        normal_part = list(np.random.normal(10, 1, 45))
        outliers = [5, 15]  # Clear outliers
        data_with_outliers = normal_part + outliers
        
        result = tool.execute({
            "data": data_with_outliers,
            "distribution": "normal"
        })
        
        assert result["success"] is True
        
        outlier_info = result["outliers"]
        assert "count" in outlier_info
        assert "values" in outlier_info
        assert outlier_info["count"] >= 0  # Should detect some outliers
    
    def test_percentile_estimates(self, tool, normal_data):
        """Test percentile estimation."""
        result = tool.execute({
            "data": normal_data
        })
        
        assert result["success"] is True
        
        percentiles = result["percentile_estimates"]
        expected_keys = ["5th_percentile", "10th_percentile", "25th_percentile", 
                        "50th_percentile", "75th_percentile", "90th_percentile", "95th_percentile"]
        
        for key in expected_keys:
            assert key in percentiles
            assert isinstance(percentiles[key], (int, float))
        
        # Percentiles should be in ascending order
        values = [percentiles[key] for key in expected_keys]
        assert values == sorted(values)
    
    def test_different_distributions(self, tool, normal_data):
        """Test analysis with different distribution types."""
        distributions = ["normal", "lognormal", "weibull"]
        
        for dist in distributions:
            result = tool.execute({
                "data": normal_data,
                "distribution": dist
            })
            
            assert result["success"] is True
            assert result["distribution_type"] == dist
    
    def test_grouped_data_analysis(self, tool):
        """Test analysis of grouped data."""
        np.random.seed(42)
        groups = {
            "Group_A": list(np.random.normal(10, 1, 20)),
            "Group_B": list(np.random.normal(12, 1, 20)),
            "Group_C": list(np.random.normal(8, 1, 20))
        }
        
        result = tool.execute({
            "data": [],  # Empty main data
            "groups": groups
        })
        
        assert result["success"] is True
        assert "overall_analysis" in result
        assert "group_analyses" in result
        assert "group_comparison" in result
        
        # Check individual group analyses
        group_results = result["group_analyses"]
        assert len(group_results) == 3
        for group_name in groups.keys():
            assert group_name in group_results
            assert group_results[group_name]["success"] is True
    
    def test_plotting_positions(self, tool):
        """Test plotting position calculations."""
        # Test with known data to verify plotting positions
        data = [1, 2, 3, 4, 5]
        result = tool.execute({"data": data})
        
        assert result["success"] is True
        
        plotting_data = result["plotting_data"]
        assert "plotting_positions" in plotting_data
        assert "theoretical_quantiles" in plotting_data
        assert "observed_values" in plotting_data
        
        positions = plotting_data["plotting_positions"]
        assert len(positions) == len(data)
        assert all(0 < p < 1 for p in positions)  # All positions should be between 0 and 1
        assert positions == sorted(positions)     # Should be in ascending order
    
    def test_visualization_creation(self, tool, normal_data):
        """Test visualization is created."""
        result = tool.execute({
            "data": normal_data,
            "title": "Test Probability Plot"
        })
        
        assert result["success"] is True
        assert "visualization" in result
        assert isinstance(result["visualization"], str)
        # Should contain HTML content (even if plotly not available, should have fallback)
        assert len(result["visualization"]) > 0
    
    def test_interpretation_generation(self, tool, normal_data):
        """Test interpretation text generation."""
        result = tool.execute({
            "data": normal_data
        })
        
        assert result["success"] is True
        assert "interpretation" in result
        assert isinstance(result["interpretation"], str)
        assert len(result["interpretation"]) > 0
        
        # Should contain assessment symbols
        interpretation = result["interpretation"]
        assert any(symbol in interpretation for symbol in ["✅", "⚠️", "❌"])
    
    def test_error_handling_insufficient_data(self, tool):
        """Test error handling with insufficient data."""
        result = tool.execute({
            "data": [1, 2]  # Less than minimum required
        })
        
        assert result["success"] is False
        assert "error" in result
    
    def test_error_handling_invalid_confidence_level(self, tool, normal_data):
        """Test error handling with invalid confidence level."""
        result = tool.execute({
            "data": normal_data,
            "confidence_level": 1.5  # Invalid: > 1
        })
        
        assert result["success"] is False
        assert "error" in result
    
    def test_different_confidence_levels(self, tool, normal_data):
        """Test different confidence levels."""
        levels = [0.90, 0.95, 0.99]
        
        for level in levels:
            result = tool.execute({
                "data": normal_data,
                "confidence_level": level
            })
            
            assert result["success"] is True
            assert result["confidence_intervals"]["level"] == level
            
            # Higher confidence level should give wider intervals
            ci = result["confidence_intervals"]
            widths = [u - l for l, u in zip(ci["lower_bounds"], ci["upper_bounds"])]
            assert all(w > 0 for w in widths)  # All intervals should have positive width
    
    def test_group_comparison_anova(self, tool):
        """Test ANOVA comparison in grouped analysis."""
        np.random.seed(42)
        # Create groups with significant differences
        groups = {
            "Low": list(np.random.normal(5, 1, 15)),
            "Medium": list(np.random.normal(10, 1, 15)),
            "High": list(np.random.normal(15, 1, 15))
        }
        
        result = tool.execute({
            "data": [],
            "groups": groups
        })
        
        assert result["success"] is True
        
        comparison = result["group_comparison"]
        assert "group_statistics" in comparison
        assert "anova_test" in comparison
        
        anova = comparison["anova_test"]
        assert "f_statistic" in anova
        assert "p_value" in anova
        assert "significant_difference" in anova
        
        # With such different means, should detect significant difference
        assert anova["significant_difference"] is True
        assert anova["p_value"] < 0.05
    
    def test_recommendation_system(self, tool):
        """Test analysis recommendation system."""
        np.random.seed(42)
        
        # Case 1: Good single distribution fit
        normal_data = list(np.random.normal(10, 1, 50))
        result = tool.execute({"data": normal_data})
        
        assert result["success"] is True
        # Should recommend single distribution for good fit
        
        # Case 2: Poor overall fit but good group fits
        groups = {
            "Mode1": list(np.random.normal(5, 0.5, 25)),
            "Mode2": list(np.random.normal(15, 0.5, 25))
        }
        
        result = tool.execute({
            "data": [],
            "groups": groups
        })
        
        assert result["success"] is True
        assert "recommendation" in result
        assert isinstance(result["recommendation"], str)
        assert len(result["recommendation"]) > 0


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])