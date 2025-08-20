"""Unit tests for I-Chart (Individual Control Chart) tool."""

import pytest
import numpy as np
from estiem_eda.tools.i_chart import IChartTool


class TestIChartTool:
    """Test suite for I-Chart functionality."""
    
    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = IChartTool()
        assert tool.name == "i_chart"
        assert "Individual control chart" in tool.description.lower()
    
    def test_input_schema(self):
        """Test input schema is properly defined."""
        tool = IChartTool()
        schema = tool.get_input_schema()
        
        assert schema["type"] == "object"
        assert "data" in schema["properties"]
        assert "data" in schema["required"]
        assert schema["properties"]["data"]["type"] == "array"
    
    def test_stable_process_analysis(self, sample_stable_process):
        """Test analysis of stable process data."""
        tool = IChartTool()
        result = tool.execute({"data": sample_stable_process})
        
        # Check basic structure
        assert "statistics" in result
        assert "control_analysis" in result
        assert "pattern_analysis" in result
        assert "interpretation" in result
        
        # Check statistics
        stats = result["statistics"]
        assert "mean" in stats
        assert "ucl" in stats
        assert "lcl" in stats
        assert "sigma_estimate" in stats
        
        # UCL should be above mean, LCL below
        assert stats["ucl"] > stats["mean"]
        assert stats["lcl"] < stats["mean"]
        
        # Control limits should be symmetric around mean
        assert abs((stats["ucl"] - stats["mean"]) - (stats["mean"] - stats["lcl"])) < 0.001
    
    def test_unstable_process_detection(self, sample_unstable_process):
        """Test detection of out-of-control points."""
        tool = IChartTool()
        result = tool.execute({"data": sample_unstable_process})
        
        control_analysis = result["control_analysis"]
        
        # Should detect out-of-control points
        assert control_analysis["out_of_control_points"] > 0
        assert len(control_analysis["ooc_indices"]) > 0
        assert len(control_analysis["ooc_values"]) > 0
        
        # Percentage calculation
        total_points = len(sample_unstable_process)
        expected_percentage = (control_analysis["out_of_control_points"] / total_points) * 100
        assert abs(control_analysis["percentage_ooc"] - expected_percentage) < 0.01
    
    def test_runs_detection(self):
        """Test runs detection (Western Electric Rule)."""
        tool = IChartTool()
        
        # Create data with a run of 8 consecutive points above mean
        data = [10.0] * 5 + [10.5] * 8 + [10.0] * 5
        result = tool.execute({"data": data})
        
        runs_test = result["pattern_analysis"]["runs_test"]
        assert runs_test["runs_violation"] == True
        assert runs_test["max_consecutive_total"] >= 7
    
    def test_moving_range_calculation(self):
        """Test moving range calculation for sigma estimation."""
        tool = IChartTool()
        
        # Simple data with known moving ranges
        data = [10.0, 11.0, 9.0, 12.0, 8.0]
        result = tool.execute({"data": data})
        
        stats = result["statistics"]
        
        # Moving ranges should be: |11-10|, |9-11|, |12-9|, |8-12| = 1, 2, 3, 4
        # Average moving range = (1+2+3+4)/4 = 2.5
        expected_avg_mr = 2.5
        assert abs(stats["moving_range_average"] - expected_avg_mr) < 0.001
        
        # Sigma estimate = avg_mr / d2 = 2.5 / 1.128 ≈ 2.216
        expected_sigma = expected_avg_mr / 1.128
        assert abs(stats["sigma_estimate"] - expected_sigma) < 0.001
    
    def test_pattern_detection(self):
        """Test additional pattern detection beyond runs."""
        tool = IChartTool()
        
        # Create data with increasing trend
        data = list(range(1, 15))  # Strictly increasing
        result = tool.execute({"data": data})
        
        patterns = result["pattern_analysis"]["other_patterns"]
        
        # Should detect increasing trend
        trend_patterns = [p for p in patterns if "trend" in p["type"]]
        assert len(trend_patterns) > 0
    
    def test_control_limit_calculation(self):
        """Test control limit calculations with different sigma multipliers."""
        tool = IChartTool()
        data = [10.0, 10.5, 9.5, 10.2, 9.8] * 10  # Stable pattern
        
        # Test 3-sigma limits (default)
        result_3s = tool.execute({"data": data, "sigma_limits": 3})
        stats_3s = result_3s["statistics"]
        
        # Test 2-sigma limits
        result_2s = tool.execute({"data": data, "sigma_limits": 2})
        stats_2s = result_2s["statistics"]
        
        # 3-sigma limits should be wider than 2-sigma limits
        ucl_diff_3s = stats_3s["ucl"] - stats_3s["mean"]
        ucl_diff_2s = stats_2s["ucl"] - stats_2s["mean"]
        assert ucl_diff_3s > ucl_diff_2s
        
        # Ratio should be approximately 3/2 = 1.5
        ratio = ucl_diff_3s / ucl_diff_2s
        assert abs(ratio - 1.5) < 0.1
    
    def test_performance_metrics(self):
        """Test process performance metric calculations."""
        tool = IChartTool()
        data = list(np.random.normal(10, 1, 50))
        
        result = tool.execute({"data": data})
        performance = result["performance_metrics"]
        
        assert "process_spread_6sigma" in performance
        assert "control_limit_width" in performance
        assert "stability_percentage" in performance
        assert "points_within_limits" in performance
        
        # Stability percentage should be between 0 and 100
        assert 0 <= performance["stability_percentage"] <= 100
        
        # Points within limits + total should equal sample size
        assert performance["points_within_limits"] <= performance["total_points"]
    
    def test_interpretation_generation(self, sample_stable_process, sample_unstable_process):
        """Test interpretation text generation."""
        tool = IChartTool()
        
        # Stable process should indicate control
        stable_result = tool.execute({"data": sample_stable_process})
        stable_interp = stable_result["interpretation"]
        assert "IN CONTROL" in stable_interp.upper() or "STATISTICAL CONTROL" in stable_interp.upper()
        
        # Unstable process should indicate out of control
        unstable_result = tool.execute({"data": sample_unstable_process})
        unstable_interp = unstable_result["interpretation"]
        assert "OUT OF CONTROL" in unstable_interp.upper() or "SPECIAL CAUSE" in unstable_interp.upper()
    
    def test_chart_data_structure(self, sample_stable_process):
        """Test chart data is properly formatted."""
        tool = IChartTool()
        result = tool.execute({"data": sample_stable_process})
        
        chart_data = result["chart_data"]
        assert "title" in chart_data
        assert "data_points" in chart_data
        assert "center_line" in chart_data
        assert "upper_control_limit" in chart_data
        assert "lower_control_limit" in chart_data
        assert "sample_numbers" in chart_data
        
        # Data integrity checks
        assert len(chart_data["data_points"]) == len(sample_stable_process)
        assert len(chart_data["sample_numbers"]) == len(sample_stable_process)
        assert chart_data["sample_numbers"] == list(range(1, len(sample_stable_process) + 1))
    
    def test_visualization_integration(self, sample_stable_process):
        """Test visualization integration."""
        tool = IChartTool()
        result = tool.execute({"data": sample_stable_process})
        
        # Should have chart_html in result
        assert "chart_html" in result
        chart_html = result["chart_html"]
        
        # Should either be HTML string or error message
        assert isinstance(chart_html, str)
        if "error" not in chart_html.lower():
            # If not error, should contain HTML
            assert "html" in chart_html.lower() or "div" in chart_html.lower()
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        tool = IChartTool()
        
        # Empty data
        with pytest.raises(ValueError, match="empty"):
            tool.execute({"data": []})
        
        # Single data point
        with pytest.raises(ValueError, match="at least 2"):
            tool.execute({"data": [10.0]})
        
        # Non-numeric data should be caught by validation
        with pytest.raises(ValueError):
            tool.execute({"data": [1, 2, "three", 4]})
        
        # Missing required parameter
        with pytest.raises(ValueError, match="required"):
            tool.execute({})
    
    def test_statistical_accuracy(self):
        """Test statistical calculations for accuracy."""
        tool = IChartTool()
        
        # Known data with exact calculations
        data = [10.0, 12.0, 8.0, 11.0, 9.0]
        result = tool.execute({"data": data})
        stats = result["statistics"]
        
        # Manual calculations
        expected_mean = np.mean(data)
        moving_ranges = [abs(data[i] - data[i-1]) for i in range(1, len(data))]
        expected_avg_mr = np.mean(moving_ranges)
        expected_sigma = expected_avg_mr / 1.128
        expected_ucl = expected_mean + 3 * expected_sigma
        expected_lcl = expected_mean - 3 * expected_sigma
        
        # Verify calculations
        assert abs(stats["mean"] - expected_mean) < 0.0001
        assert abs(stats["moving_range_average"] - expected_avg_mr) < 0.0001
        assert abs(stats["sigma_estimate"] - expected_sigma) < 0.0001
        assert abs(stats["ucl"] - expected_ucl) < 0.0001
        assert abs(stats["lcl"] - expected_lcl) < 0.0001
    
    def test_custom_title(self):
        """Test custom title functionality."""
        tool = IChartTool()
        custom_title = "Process Temperature Control Chart"
        
        result = tool.execute({
            "data": [10, 11, 9, 12, 8],
            "title": custom_title
        })
        
        assert result["chart_data"]["title"] == custom_title
    
    def test_large_dataset_performance(self):
        """Test performance with larger datasets."""
        tool = IChartTool()
        
        # Generate larger dataset
        np.random.seed(42)
        large_data = np.random.normal(100, 5, 1000).tolist()
        
        result = tool.execute({"data": large_data})
        
        # Should complete successfully
        assert result["statistics"]["sample_size"] == 1000
        assert len(result["chart_data"]["data_points"]) == 1000
        
        # Results should be reasonable
        stats = result["statistics"]
        assert 90 < stats["mean"] < 110  # Should be around 100
        assert stats["ucl"] > stats["mean"] > stats["lcl"]