"""Unit tests for Pareto Analysis tool."""

import pytest
from estiem_eda.tools.pareto import ParetoTool


class TestParetoTool:
    """Test suite for Pareto Analysis functionality."""
    
    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = ParetoTool()
        assert tool.name == "pareto_analysis"
        assert "pareto" in tool.description.lower()
        assert "80/20" in tool.description or "vital few" in tool.description.lower()
    
    def test_input_schema(self):
        """Test input schema is properly defined."""
        tool = ParetoTool()
        schema = tool.get_input_schema()
        
        assert schema["type"] == "object"
        assert "data" in schema["properties"]
        assert "data" in schema["required"]
        
        # Should accept either dictionary or array format
        data_schema = schema["properties"]["data"]
        assert "oneOf" in data_schema
        assert len(data_schema["oneOf"]) == 2
    
    def test_classic_80_20_analysis(self, sample_pareto_data):
        """Test analysis that follows classic 80/20 rule."""
        tool = ParetoTool()
        result = tool.execute({"data": sample_pareto_data})
        
        # Check structure
        assert "summary" in result
        assert "vital_few" in result
        assert "interpretation" in result
        assert "sorted_data" in result
        
        summary = result["summary"]
        vital_few = result["vital_few"]
        
        # Should identify vital few
        assert vital_few["count"] < summary["total_categories"]
        assert vital_few["percentage"] >= 70  # Should capture majority of impact
        
        # Vital few should be small portion of categories
        vital_few_ratio = vital_few["count"] / summary["total_categories"]
        assert vital_few_ratio <= 0.5  # Less than 50% of categories
    
    def test_dictionary_input_format(self):
        """Test dictionary input format."""
        tool = ParetoTool()
        
        data_dict = {
            "Issue A": 100,
            "Issue B": 80,
            "Issue C": 60,
            "Issue D": 30,
            "Issue E": 15
        }
        
        result = tool.execute({"data": data_dict})
        
        # Should sort by value descending
        sorted_data = result["sorted_data"]
        assert sorted_data[0]["category"] == "Issue A"
        assert sorted_data[0]["value"] == 100
        assert sorted_data[-1]["category"] == "Issue E"
        assert sorted_data[-1]["value"] == 15
        
        # Check ranking
        for i, item in enumerate(sorted_data):
            assert item["rank"] == i + 1
    
    def test_array_input_format(self):
        """Test array input format."""
        tool = ParetoTool()
        
        data_array = [
            {"category": "Problem X", "value": 50},
            {"category": "Problem Y", "value": 30},
            {"category": "Problem Z", "value": 20}
        ]
        
        result = tool.execute({"data": data_array})
        
        sorted_data = result["sorted_data"]
        assert sorted_data[0]["category"] == "Problem X"
        assert sorted_data[1]["category"] == "Problem Y"
        assert sorted_data[2]["category"] == "Problem Z"
    
    def test_cumulative_percentage_calculation(self):
        """Test cumulative percentage calculations."""
        tool = ParetoTool()
        
        # Simple data for exact verification
        data = {
            "A": 40,  # 40% of total (100)
            "B": 30,  # 30% of total
            "C": 20,  # 20% of total
            "D": 10   # 10% of total
        }
        
        result = tool.execute({"data": data})
        sorted_data = result["sorted_data"]
        
        # Verify cumulative percentages
        assert abs(sorted_data[0]["cumulative_percentage"] - 40.0) < 0.01
        assert abs(sorted_data[1]["cumulative_percentage"] - 70.0) < 0.01
        assert abs(sorted_data[2]["cumulative_percentage"] - 90.0) < 0.01
        assert abs(sorted_data[3]["cumulative_percentage"] - 100.0) < 0.01
        
        # Individual percentages should sum to 100
        total_pct = sum(item["percentage"] for item in sorted_data)
        assert abs(total_pct - 100.0) < 0.01
    
    def test_vital_few_identification(self):
        """Test vital few identification at different thresholds."""
        tool = ParetoTool()
        
        data = {
            "Major": 50,    # 50%
            "Medium": 25,   # 25% (cumulative 75%)
            "Small": 15,    # 15% (cumulative 90%)
            "Tiny": 10      # 10% (cumulative 100%)
        }
        
        # Test 80% threshold
        result_80 = tool.execute({"data": data, "threshold": 80})
        vital_few_80 = result_80["vital_few"]
        
        # Should identify first 2 categories (75% < 80%, but next jumps to 90%)
        assert vital_few_80["count"] == 2
        assert "Major" in vital_few_80["categories"]
        assert "Medium" in vital_few_80["categories"]
        
        # Test 90% threshold
        result_90 = tool.execute({"data": data, "threshold": 90})
        vital_few_90 = result_90["vital_few"]
        
        # Should identify first 3 categories
        assert vital_few_90["count"] == 3
    
    def test_insights_generation(self):
        """Test insights and analysis generation."""
        tool = ParetoTool()
        
        data = {
            "Top Issue": 60,
            "Second Issue": 25,
            "Third Issue": 10,
            "Fourth Issue": 3,
            "Fifth Issue": 2
        }
        
        result = tool.execute({"data": data})
        insights = result["insights"]
        
        # Should have key insights
        assert "pareto_ratio" in insights
        assert "concentration" in insights
        assert "top_contributor" in insights
        
        # Top contributor should be identified correctly
        top = insights["top_contributor"]
        assert top["category"] == "Top Issue"
        assert top["value"] == 60
        assert top["percentage"] == 60.0  # 60/100
        
        # Pareto ratio should be reasonable
        assert "/" in insights["pareto_ratio"]
        assert insights["pareto_percentage"].endswith("%")
    
    def test_gini_coefficient_calculation(self):
        """Test inequality measurement with Gini coefficient."""
        tool = ParetoTool()
        
        # Perfectly equal distribution
        equal_data = {"A": 25, "B": 25, "C": 25, "D": 25}
        result_equal = tool.execute({"data": equal_data})
        
        # Highly unequal distribution
        unequal_data = {"A": 90, "B": 5, "C": 3, "D": 2}
        result_unequal = tool.execute({"data": unequal_data})
        
        # Get Gini coefficients (if calculated)
        insights_equal = result_equal["insights"]
        insights_unequal = result_unequal["insights"]
        
        if "inequality" in insights_equal and "inequality" in insights_unequal:
            gini_equal = insights_equal["inequality"]["gini_coefficient"]
            gini_unequal = insights_unequal["inequality"]["gini_coefficient"]
            
            # Unequal should have higher Gini coefficient
            assert gini_unequal > gini_equal
            assert 0 <= gini_equal <= 1
            assert 0 <= gini_unequal <= 1
    
    def test_chart_data_preparation(self):
        """Test chart data structure for visualization."""
        tool = ParetoTool()
        
        data = {"Issue A": 100, "Issue B": 75, "Issue C": 25}
        result = tool.execute({
            "data": data,
            "title": "Problem Analysis",
            "unit": "incidents"
        })
        
        chart_data = result["chart_data"]
        
        # Required chart elements
        assert chart_data["title"] == "Problem Analysis"
        assert chart_data["unit"] == "incidents"
        assert chart_data["chart_type"] == "pareto"
        
        # Data arrays should match sorted order
        assert chart_data["categories"] == ["Issue A", "Issue B", "Issue C"]
        assert chart_data["values"] == [100, 75, 25]
        
        # Cumulative percentages should be correct
        expected_cum_pct = [50.0, 87.5, 100.0]  # 100/200, 175/200, 200/200
        for i, expected in enumerate(expected_cum_pct):
            assert abs(chart_data["cumulative_percentages"][i] - expected) < 0.1
        
        # Colors should be provided
        assert "colors" in chart_data
        assert len(chart_data["colors"]) == len(chart_data["categories"])
    
    def test_custom_threshold_analysis(self):
        """Test analysis with custom thresholds."""
        tool = ParetoTool()
        
        data = {"A": 50, "B": 30, "C": 15, "D": 5}
        
        # Test different thresholds
        thresholds = [70, 80, 90, 95]
        
        for threshold in thresholds:
            result = tool.execute({"data": data, "threshold": threshold})
            
            vital_few = result["vital_few"]
            summary = result["summary"]
            
            # Threshold should be recorded
            assert summary["threshold_used"] == threshold
            
            # Vital few percentage should be close to or exceed threshold
            # (unless no single category reaches it)
            if vital_few["count"] > 0:
                assert vital_few["percentage"] >= threshold or vital_few["count"] == len(data)
    
    def test_interpretation_quality(self):
        """Test interpretation text quality and completeness."""
        tool = ParetoTool()
        
        # Classic 80/20 scenario
        classic_data = {
            "Major Problem": 60,
            "Significant Issue": 20,
            "Minor Issue": 12,
            "Small Problem": 5,
            "Tiny Issue": 3
        }
        
        result = tool.execute({"data": classic_data})
        interpretation = result["interpretation"]
        
        # Should be comprehensive
        assert len(interpretation) > 300  # Substantial content
        
        # Key elements should be present
        assert "PARETO" in interpretation.upper()
        assert "VITAL FEW" in interpretation.upper()
        assert "RECOMMENDATION" in interpretation.upper()
        assert "80" in interpretation or "PRINCIPLE" in interpretation.upper()
        
        # Should identify top contributors
        assert "Major Problem" in interpretation
        
        # Should provide actionable recommendations
        assert "FOCUS" in interpretation.upper() or "PRIORITIZE" in interpretation.upper()
    
    def test_edge_cases_and_validation(self):
        """Test edge cases and input validation."""
        tool = ParetoTool()
        
        # Empty data
        with pytest.raises(ValueError):
            tool.execute({"data": {}})
        
        # Single category
        with pytest.raises(ValueError, match="at least 2"):
            tool.execute({"data": {"Only One": 100}})
        
        # Negative values
        with pytest.raises(ValueError, match="non-negative"):
            tool.execute({"data": {"A": 100, "B": -50}})
        
        # All zero values
        with pytest.raises(ValueError, match="positive"):
            tool.execute({"data": {"A": 0, "B": 0, "C": 0}})
        
        # Duplicate categories in array format
        with pytest.raises(ValueError, match="unique"):
            tool.execute({"data": [
                {"category": "A", "value": 100},
                {"category": "A", "value": 50}  # Duplicate
            ]})
        
        # Invalid array format
        with pytest.raises(ValueError, match="category.*value"):
            tool.execute({"data": [
                {"name": "A", "count": 100}  # Wrong field names
            ]})
        
        # Invalid threshold
        with pytest.raises(ValueError):
            tool.execute({"data": {"A": 100, "B": 50}, "threshold": 150})  # > 100%
    
    def test_chart_html_integration(self, sample_pareto_data):
        """Test visualization integration."""
        tool = ParetoTool()
        result = tool.execute({"data": sample_pareto_data})
        
        assert "chart_html" in result
        assert isinstance(result["chart_html"], str)
    
    def test_distributed_vs_concentrated_analysis(self):
        """Test analysis of distributed vs concentrated impact."""
        tool = ParetoTool()
        
        # Concentrated impact (classic Pareto)
        concentrated = {
            "Major": 70,
            "Medium": 15,
            "Small1": 5,
            "Small2": 5,
            "Small3": 5
        }
        
        # Distributed impact (more even)
        distributed = {
            "Issue1": 25,
            "Issue2": 20,
            "Issue3": 18,
            "Issue4": 17,
            "Issue5": 20
        }
        
        result_conc = tool.execute({"data": concentrated})
        result_dist = tool.execute({"data": distributed})
        
        # Concentrated should have fewer vital few
        vital_few_conc = result_conc["vital_few"]
        vital_few_dist = result_dist["vital_few"]
        
        # Concentrated should achieve 80% with fewer categories
        conc_ratio = vital_few_conc["count"] / len(concentrated)
        dist_ratio = vital_few_dist["count"] / len(distributed)
        
        assert conc_ratio <= dist_ratio
        
        # Interpretations should reflect different strategies
        interp_conc = result_conc["interpretation"]
        interp_dist = result_dist["interpretation"]
        
        if vital_few_conc["percentage"] >= 80:
            assert "FOCUS" in interp_conc.upper()
        
        if vital_few_dist["percentage"] < 70:
            assert ("BROAD" in interp_dist.upper() or 
                    "DISTRIBUTED" in interp_dist.upper())
    
    def test_unit_and_title_customization(self):
        """Test customization of units and titles."""
        tool = ParetoTool()
        
        data = {"Defect A": 50, "Defect B": 30, "Defect C": 20}
        
        result = tool.execute({
            "data": data,
            "title": "Quality Issues Analysis",
            "unit": "defects"
        })
        
        # Check customization is preserved
        summary = result["summary"]
        chart_data = result["chart_data"]
        
        assert summary["unit"] == "defects"
        assert chart_data["title"] == "Quality Issues Analysis"
        assert chart_data["unit"] == "defects"
        
        # Should appear in interpretation
        interpretation = result["interpretation"]
        # Title might be referenced in interpretation
        # Unit should definitely appear in summary statistics