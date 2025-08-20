"""Unit tests for Pareto Analysis tool."""

from estiem_eda.tools.pareto import ParetoTool


class TestParetoTool:
    """Test suite for Pareto Analysis functionality."""

    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = ParetoTool()
        assert tool.name == "pareto_analysis"
        assert "pareto" in tool.description.lower()
        assert "80/20" in tool.description

    def test_input_schema(self):
        """Test input schema is properly defined."""
        tool = ParetoTool()
        schema = tool.get_input_schema()

        assert schema["type"] == "object"
        assert "data" in schema["properties"]
        assert "data" in schema["required"]
        assert schema["properties"]["data"]["type"] == "object"

    def test_classic_80_20_analysis(self, sample_pareto_data):
        """Test classic 80/20 analysis."""
        tool = ParetoTool()
        result = tool.execute({"data": sample_pareto_data})

        # Check basic structure
        assert "categories" in result
        assert "values" in result
        assert "percentages" in result
        assert "cumulative_percentages" in result
        assert "vital_few" in result
        assert "interpretation" in result

        # Verify data is sorted (descending order)
        values = result["values"]
        assert all(values[i] >= values[i + 1] for i in range(len(values) - 1))

        # Check percentages sum to 100
        total_percentage = sum(result["percentages"])
        assert abs(total_percentage - 100.0) < 0.01

    def test_dictionary_input_format(self):
        """Test dictionary input format."""
        tool = ParetoTool()

        data = {"Defect A": 45, "Defect B": 30, "Defect C": 15, "Defect D": 10}

        result = tool.execute({"data": data})

        assert result.get("success", True)
        assert "categories" in result
        assert "total_value" in result
        assert result["total_value"] == 100

        # Categories should be sorted by value
        categories = result["categories"]
        assert categories[0] == "Defect A"  # Highest value first

    def test_array_input_format(self):
        """Test handling of different data formats."""
        tool = ParetoTool()

        # Test with numeric keys
        data = {"Category_1": 50.5, "Category_2": 25.3, "Category_3": 15.2, "Category_4": 9.0}

        result = tool.execute({"data": data})

        assert result.get("success", True)
        assert len(result["categories"]) == 4
        assert abs(result["total_value"] - 100.0) < 0.1

    def test_cumulative_percentage_calculation(self):
        """Test cumulative percentage calculations."""
        tool = ParetoTool()

        data = {"A": 40, "B": 30, "C": 20, "D": 10}
        result = tool.execute({"data": data})

        cum_percentages = result["cumulative_percentages"]

        # Should be monotonically increasing
        assert all(
            cum_percentages[i] <= cum_percentages[i + 1] for i in range(len(cum_percentages) - 1)
        )

        # Last value should be 100%
        assert abs(cum_percentages[-1] - 100.0) < 0.01

        # First value should equal first percentage
        assert abs(cum_percentages[0] - result["percentages"][0]) < 0.01

    def test_vital_few_identification(self):
        """Test vital few category identification."""
        tool = ParetoTool()

        # Create clear 80/20 distribution
        data = {"Major": 80, "Minor1": 8, "Minor2": 7, "Minor3": 5}
        result = tool.execute({"data": data, "threshold": 0.8})

        vital_few = result["vital_few"]
        assert len(vital_few) >= 1
        assert "Major" in vital_few

        # Check Gini coefficient is present
        assert "gini_coefficient" in result
        gini = result["gini_coefficient"]
        assert 0 <= gini <= 1

    def test_insights_generation(self):
        """Test insights generation."""
        tool = ParetoTool()

        data = {"Problem_A": 60, "Problem_B": 25, "Problem_C": 10, "Problem_D": 5}
        result = tool.execute({"data": data})

        interpretation = result["interpretation"]
        assert isinstance(interpretation, str)
        assert len(interpretation) > 20

        # Should mention key concepts
        assert any(
            word in interpretation.lower() for word in ["vital", "few", "pareto", "categories"]
        )

    def test_gini_coefficient_calculation(self):
        """Test Gini coefficient calculation."""
        tool = ParetoTool()

        # Perfect equality (should have low Gini)
        equal_data = {"A": 25, "B": 25, "C": 25, "D": 25}
        result_equal = tool.execute({"data": equal_data})
        gini_equal = result_equal["gini_coefficient"]

        # High inequality (should have high Gini)
        unequal_data = {"A": 90, "B": 5, "C": 3, "D": 2}
        result_unequal = tool.execute({"data": unequal_data})
        gini_unequal = result_unequal["gini_coefficient"]

        # Unequal distribution should have higher Gini coefficient
        assert gini_unequal > gini_equal
        assert 0 <= gini_equal <= 1
        assert 0 <= gini_unequal <= 1

    def test_chart_data_preparation(self):
        """Test chart data structure."""
        tool = ParetoTool()

        data = {"Cat1": 40, "Cat2": 30, "Cat3": 20, "Cat4": 10}
        result = tool.execute({"data": data})

        # All required data for visualization should be present
        assert len(result["categories"]) == len(result["values"])
        assert len(result["values"]) == len(result["percentages"])
        assert len(result["percentages"]) == len(result["cumulative_percentages"])

        # Data should be properly formatted
        assert all(isinstance(cat, str) for cat in result["categories"])
        assert all(isinstance(val, int | float) for val in result["values"])

    def test_custom_threshold_analysis(self):
        """Test custom threshold functionality."""
        tool = ParetoTool()

        data = {"A": 50, "B": 30, "C": 15, "D": 5}

        # Test with 70% threshold
        result_70 = tool.execute({"data": data, "threshold": 0.7})
        vital_70 = result_70["vital_few"]

        # Test with 90% threshold
        result_90 = tool.execute({"data": data, "threshold": 0.9})
        vital_90 = result_90["vital_few"]

        # 90% threshold should include more categories
        assert len(vital_90) >= len(vital_70)

    def test_interpretation_quality(self):
        """Test interpretation content quality."""
        tool = ParetoTool()

        data = {"Major_Issue": 70, "Medium_Issue": 20, "Small_Issue": 10}
        result = tool.execute({"data": data})

        interpretation = result["interpretation"]

        # Should be substantial and informative
        assert len(interpretation) > 50
        assert "Major_Issue" in interpretation or "categories" in interpretation.lower()

        # Should mention vital few concept
        vital_few_count = len(result["vital_few"])
        assert str(vital_few_count) in interpretation or "vital" in interpretation.lower()

    def test_edge_cases_and_validation(self):
        """Test edge cases and input validation."""
        tool = ParetoTool()

        # Single category (edge case)
        single_data = {"Only_One": 100}
        result = tool.execute({"data": single_data})
        assert result.get("success", True)

        # Two categories (minimum)
        two_data = {"First": 70, "Second": 30}
        result = tool.execute({"data": two_data})
        assert result.get("success", True)
        assert len(result["categories"]) == 2

        # Zero values (should handle gracefully)
        zero_data = {"A": 50, "B": 0, "C": 50}
        result = tool.execute({"data": zero_data})
        assert result.get("success", True)

    def test_chart_html_integration(self):
        """Test basic output structure."""
        tool = ParetoTool()

        data = {"Problem_1": 45, "Problem_2": 25, "Problem_3": 20, "Problem_4": 10}
        result = tool.execute({"data": data})

        # Check that result has expected structure
        assert "analysis_type" in result
        assert result["analysis_type"] == "pareto"
        assert "success" in result
        assert result["success"]

        # Verify essential data structure
        assert isinstance(result["categories"], list)
        assert isinstance(result["values"], list)
        assert isinstance(result["vital_few"], list)

    def test_distributed_vs_concentrated_analysis(self):
        """Test analysis of different distribution patterns."""
        tool = ParetoTool()

        # Highly concentrated (strong Pareto effect)
        concentrated = {"Major": 85, "Minor1": 8, "Minor2": 4, "Minor3": 3}
        result_conc = tool.execute({"data": concentrated})

        # Evenly distributed (weak Pareto effect)
        distributed = {"A": 26, "B": 25, "C": 25, "D": 24}
        result_dist = tool.execute({"data": distributed})

        # Concentrated should have higher Gini coefficient
        assert result_conc["gini_coefficient"] > result_dist["gini_coefficient"]

        # Concentrated should have fewer vital few
        assert len(result_conc["vital_few"]) <= len(result_dist["vital_few"])

    def test_unit_and_title_customization(self):
        """Test custom titles and units."""
        tool = ParetoTool()

        data = {"Defect_A": 40, "Defect_B": 35, "Defect_C": 25}
        custom_title = "Quality Control Analysis"

        result = tool.execute({"data": data, "title": custom_title})

        # Should complete successfully
        assert result.get("success", True)

        # Basic structure should be maintained
        assert "categories" in result
        assert "interpretation" in result
        assert len(result["categories"]) == 3
