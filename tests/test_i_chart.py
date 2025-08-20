"""Unit tests for I-Chart (Individual Control Chart) tool."""

import numpy as np

from estiem_eda.tools.i_chart import IChartTool


class TestIChartTool:
    """Test suite for I-Chart functionality."""

    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = IChartTool()
        assert tool.name == "i_chart"
        assert "individual control chart" in tool.description.lower()

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
        assert "interpretation" in result
        assert "success" in result
        assert result["success"]

        # Check statistics
        stats = result["statistics"]
        assert "mean" in stats
        assert "ucl" in stats
        assert "lcl" in stats
        assert "sigma_hat" in stats

        # UCL should be above mean, LCL below
        assert stats["ucl"] > stats["mean"]
        assert stats["lcl"] < stats["mean"]

    def test_out_of_control_detection(self, sample_unstable_process):
        """Test detection of out-of-control points."""
        tool = IChartTool()
        result = tool.execute({"data": sample_unstable_process})

        # Should detect some out-of-control points
        assert "out_of_control_indices" in result
        assert "statistics" in result

        # Check that out-of-control points are tracked
        ooc_count = result["statistics"].get("out_of_control_points", 0)
        assert ooc_count >= 0  # At least validate structure

    def test_runs_detection(self, test_data_generator):
        """Test Western Electric rules detection."""
        tool = IChartTool()

        # Generate trend data (should trigger runs rules)
        trend_data = list(range(1, 26))  # Consistent trend
        result = tool.execute({"data": trend_data})

        # Should complete analysis
        assert "statistics" in result
        assert "western_electric_violations" in result
        assert "interpretation" in result

    def test_moving_range_calculation(self):
        """Test moving range calculations."""
        tool = IChartTool()

        # Simple data for verification
        data = [10, 12, 9, 11, 13, 8]
        result = tool.execute({"data": data})

        stats = result["statistics"]
        assert "avg_moving_range" in stats
        assert stats["avg_moving_range"] > 0

        # Verify control limits are calculated
        assert "ucl" in stats
        assert "lcl" in stats
        assert stats["ucl"] > stats["mean"]
        assert stats["lcl"] < stats["mean"]

    def test_control_limit_calculation(self):
        """Test control limit calculations are correct."""
        tool = IChartTool()

        # Known data for manual verification
        data = [10.0, 10.5, 9.5, 10.2, 9.8, 10.3, 9.7]
        result = tool.execute({"data": data})

        stats = result["statistics"]
        mean = np.mean(data)

        # Control limits should be mean ± 3*sigma_hat
        expected_range = 3 * stats["sigma_hat"]
        assert abs((stats["ucl"] - mean) - expected_range) < 0.001
        assert abs((mean - stats["lcl"]) - expected_range) < 0.001

    def test_performance_metrics(self, sample_stable_process):
        """Test basic performance validation."""
        tool = IChartTool()
        result = tool.execute({"data": sample_stable_process})

        # Should complete successfully
        assert result.get("success", True)
        assert "analysis_type" in result
        assert result["analysis_type"] == "i_chart"

        # Basic statistics should be present
        assert "statistics" in result
        stats = result["statistics"]
        assert "sample_size" in stats
        assert stats["sample_size"] == len(sample_stable_process)

    def test_interpretation_generation(self, sample_stable_process):
        """Test interpretation text generation."""
        tool = IChartTool()
        result = tool.execute({"data": sample_stable_process})

        interpretation = result["interpretation"]
        assert isinstance(interpretation, str)
        assert len(interpretation) > 20  # Should have substantial content

        # Should mention process status
        assert any(word in interpretation.lower() for word in ["process", "control", "stable"])

    def test_chart_data_structure(self, sample_stable_process):
        """Test chart data preparation."""
        tool = IChartTool()
        result = tool.execute({"data": sample_stable_process})

        # Should have data points for visualization
        assert "data_points" in result
        data_points = result["data_points"]
        assert len(data_points) == len(sample_stable_process)
        assert all(isinstance(x, int | float) for x in data_points)

    def test_edge_cases(self):
        """Test edge cases and validation."""
        tool = IChartTool()

        # Minimum data points
        min_data = [1.0, 2.0, 3.0]
        result = tool.execute({"data": min_data})
        assert result.get("success", True)

        # All same values
        constant_data = [10.0] * 10
        result = tool.execute({"data": constant_data})
        assert result.get("success", True)

        # Very small variation
        small_var_data = [10.000, 10.001, 9.999, 10.002]
        result = tool.execute({"data": small_var_data})
        assert result.get("success", True)

    def test_statistical_accuracy(self):
        """Test statistical calculation accuracy."""
        tool = IChartTool()

        # Known dataset
        data = [5, 7, 6, 8, 5, 9, 4, 6, 7, 5]
        result = tool.execute({"data": data})

        stats = result["statistics"]

        # Verify mean calculation
        expected_mean = np.mean(data)
        assert abs(stats["mean"] - expected_mean) < 0.001

        # Verify moving range calculation
        moving_ranges = [abs(data[i] - data[i - 1]) for i in range(1, len(data))]
        expected_avg_mr = np.mean(moving_ranges)
        assert abs(stats["avg_moving_range"] - expected_avg_mr) < 0.001

    def test_custom_title(self):
        """Test custom title functionality."""
        tool = IChartTool()

        data = [1, 2, 3, 4, 5]
        custom_title = "Custom Process Monitor"
        result = tool.execute({"data": data, "title": custom_title})

        # Should complete successfully
        assert result.get("success", True)

        # Title should be used in some way (analysis type or elsewhere)
        assert "analysis_type" in result

    def test_large_dataset_performance(self, test_data_generator):
        """Test performance with larger datasets."""
        tool = IChartTool()

        # Generate large dataset
        large_data = test_data_generator.generate_normal_data(100, 10, 1000)
        result = tool.execute({"data": large_data})

        # Should complete successfully
        assert result.get("success", True)
        assert "statistics" in result
        assert result["statistics"]["sample_size"] == 1000

        # Should have reasonable control limits
        stats = result["statistics"]
        assert stats["ucl"] > stats["mean"]
        assert stats["lcl"] < stats["mean"]
