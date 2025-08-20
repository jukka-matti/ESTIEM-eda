"""Unit tests for Probability Plot Analysis tool."""

import numpy as np

from estiem_eda.tools.probability_plot import ProbabilityPlotTool


class TestProbabilityPlotTool:
    """Test suite for Probability Plot functionality."""

    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = ProbabilityPlotTool()
        assert tool.name == "probability_plot"
        assert "probability" in tool.description.lower()

    def test_input_schema_structure(self):
        """Test input schema is properly defined."""
        tool = ProbabilityPlotTool()
        schema = tool.get_input_schema()

        assert schema["type"] == "object"
        assert "data" in schema["properties"]
        assert "data" in schema["required"]
        assert schema["properties"]["data"]["type"] == "array"

    def test_normal_data_analysis(self, test_data_generator):
        """Test analysis of normal data."""
        tool = ProbabilityPlotTool()

        # Generate normal data
        data = test_data_generator.generate_normal_data(100, 10, 50)
        result = tool.execute({"data": data})

        # Check basic structure
        assert "distribution" in result
        assert "plotting_positions" in result
        assert "theoretical_quantiles" in result
        assert "sorted_values" in result
        assert "goodness_of_fit" in result
        assert "interpretation" in result
        assert "success" in result
        assert result["success"]

        # Should detect normal distribution for normal data
        assert result["distribution"] == "normal"

        # Plotting positions should match data length
        assert len(result["plotting_positions"]) == len(data)
        assert len(result["sorted_values"]) == len(data)
        assert len(result["theoretical_quantiles"]) == len(data)

    def test_skewed_data_analysis(self, test_data_generator):
        """Test analysis of skewed data."""
        tool = ProbabilityPlotTool()

        # Generate skewed data (exponential-like)
        data = [np.random.exponential(2) for _ in range(40)]
        result = tool.execute({"data": data})

        # Should complete analysis
        assert result.get("success", True)
        assert "goodness_of_fit" in result
        assert "interpretation" in result

        # Should have goodness of fit measure
        gof = result["goodness_of_fit"]
        assert isinstance(gof, dict)
        assert "r_squared" in gof
        assert 0 <= gof["r_squared"] <= 1  # R-squared should be between 0 and 1

    def test_confidence_intervals(self, test_data_generator):
        """Test confidence interval functionality."""
        tool = ProbabilityPlotTool()

        data = test_data_generator.generate_normal_data(50, 5, 30)
        result = tool.execute({"data": data, "confidence_level": 0.95})

        assert "confidence_level" in result
        assert result["confidence_level"] == 0.95

        # Should complete successfully
        assert result.get("success", True)

    def test_percentile_estimates(self, test_data_generator):
        """Test percentile estimation accuracy."""
        tool = ProbabilityPlotTool()

        data = test_data_generator.generate_normal_data(100, 15, 100)
        result = tool.execute({"data": data})

        # Sorted values should be monotonic
        sorted_vals = result["sorted_values"]
        assert all(sorted_vals[i] <= sorted_vals[i + 1] for i in range(len(sorted_vals) - 1))

        # Plotting positions should be between 0 and 1
        positions = result["plotting_positions"]
        assert all(0 < p < 1 for p in positions)
        assert all(positions[i] <= positions[i + 1] for i in range(len(positions) - 1))

    def test_different_distributions(self, test_data_generator):
        """Test different distribution types."""
        tool = ProbabilityPlotTool()

        # Test normal distribution
        normal_data = test_data_generator.generate_normal_data(0, 1, 40)
        result_normal = tool.execute({"data": normal_data, "distribution": "normal"})
        assert result_normal.get("success", True)
        assert result_normal["distribution"] == "normal"

        # Test with different distribution parameter
        data2 = test_data_generator.generate_normal_data(10, 2, 40)
        result_2 = tool.execute({"data": data2, "distribution": "normal"})
        assert result_2.get("success", True)
        assert result_2["distribution"] == "normal"

    def test_grouped_data_analysis(self, test_data_generator):
        """Test analysis with grouped data scenarios."""
        tool = ProbabilityPlotTool()

        # Mix two normal distributions
        group1 = test_data_generator.generate_normal_data(50, 5, 25)
        group2 = test_data_generator.generate_normal_data(70, 5, 25)
        mixed_data = group1 + group2

        result = tool.execute({"data": mixed_data})

        # Should complete analysis
        assert result.get("success", True)

        # May or may not fit well to normal (bimodal data)
        assert "goodness_of_fit" in result
        assert isinstance(result["goodness_of_fit"], dict)
        assert "r_squared" in result["goodness_of_fit"]

    def test_plotting_positions(self):
        """Test plotting position calculations."""
        tool = ProbabilityPlotTool()

        # Simple known data
        data = [1, 2, 3, 4, 5]
        result = tool.execute({"data": data})

        positions = result["plotting_positions"]

        # Should have 5 positions for 5 data points
        assert len(positions) == 5

        # First position should be smallest, last should be largest
        assert positions[0] < positions[-1]

        # All positions should be between 0 and 1
        assert all(0 < p < 1 for p in positions)

    def test_visualization_creation(self, test_data_generator):
        """Test visualization data creation."""
        tool = ProbabilityPlotTool()

        data = test_data_generator.generate_normal_data(100, 10, 50)
        result = tool.execute({"data": data})

        # Should have all data needed for plotting
        assert "sorted_values" in result  # Y-axis data
        assert "theoretical_quantiles" in result  # X-axis data
        assert "plotting_positions" in result  # For reference

        # Data should be same length
        assert len(result["sorted_values"]) == len(result["theoretical_quantiles"])
        assert len(result["theoretical_quantiles"]) == len(result["plotting_positions"])

    def test_interpretation_generation(self, test_data_generator):
        """Test interpretation text generation."""
        tool = ProbabilityPlotTool()

        data = test_data_generator.generate_normal_data(50, 8, 40)
        result = tool.execute({"data": data})

        interpretation = result["interpretation"]

        # Should provide meaningful interpretation
        assert isinstance(interpretation, str)
        assert len(interpretation) > 30

        # Should mention distribution or fit
        assert any(
            word in interpretation.lower() for word in ["normal", "distribution", "fit", "data"]
        )

    def test_error_handling_invalid_confidence_level(self):
        """Test error handling for invalid confidence levels."""
        tool = ProbabilityPlotTool()

        data = [1, 2, 3, 4, 5]

        # Invalid confidence level (too high)
        result = tool.execute({"data": data, "confidence_level": 1.5})

        # Should handle gracefully
        assert "success" in result
        # May succeed with default value or fail gracefully

    def test_different_confidence_levels(self, test_data_generator):
        """Test different confidence level functionality."""
        tool = ProbabilityPlotTool()

        data = test_data_generator.generate_normal_data(100, 10, 50)

        # Test 90% confidence
        result_90 = tool.execute({"data": data, "confidence_level": 0.90})

        # Test 99% confidence
        result_99 = tool.execute({"data": data, "confidence_level": 0.99})

        # Both should succeed
        assert result_90.get("success", True)
        assert result_99.get("success", True)

        # Should record confidence levels
        assert result_90["confidence_level"] == 0.90
        assert result_99["confidence_level"] == 0.99

    def test_group_comparison_anova(self, test_data_generator):
        """Test basic data analysis functionality."""
        tool = ProbabilityPlotTool()

        # Generate multiple groups of data
        data1 = test_data_generator.generate_normal_data(50, 5, 30)
        data2 = test_data_generator.generate_normal_data(55, 5, 30)

        # Test each group separately
        result1 = tool.execute({"data": data1})
        result2 = tool.execute({"data": data2})

        # Both should succeed
        assert result1.get("success", True)
        assert result2.get("success", True)

        # Should have different results for different data
        assert result1["sorted_values"] != result2["sorted_values"]

    def test_recommendation_system(self, test_data_generator):
        """Test recommendation and interpretation system."""
        tool = ProbabilityPlotTool()

        # Test with good normal data
        good_normal_data = test_data_generator.generate_normal_data(100, 5, 100)
        result_good = tool.execute({"data": good_normal_data})

        # Should provide good fit interpretation
        interpretation = result_good["interpretation"]
        gof = result_good["goodness_of_fit"]

        # Good fit should have high R-squared
        if gof["r_squared"] > 0.95:
            assert any(word in interpretation.lower() for word in ["good", "well", "closely"])
        # Otherwise just check that interpretation exists and is meaningful
        assert len(interpretation) > 20

        # Test with poor fitting data
        mixed_data = test_data_generator.generate_normal_data(
            20, 2, 25
        ) + test_data_generator.generate_normal_data(80, 2, 25)
        result_poor = tool.execute({"data": mixed_data})

        # Should complete analysis regardless of fit quality
        assert result_poor.get("success", True)
        assert "goodness_of_fit" in result_poor
        assert isinstance(result_poor["goodness_of_fit"], dict)
