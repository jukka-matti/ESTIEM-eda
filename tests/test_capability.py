"""Unit tests for Process Capability Analysis tool."""

import pytest
import numpy as np
from estiem_eda.tools.capability import CapabilityTool


class TestCapabilityTool:
    """Test suite for Process Capability functionality."""
    
    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = CapabilityTool()
        assert tool.name == "process_capability"
        assert "capability" in tool.description.lower()
    
    def test_input_schema(self):
        """Test input schema is properly defined."""
        tool = CapabilityTool()
        schema = tool.get_input_schema()
        
        assert schema["type"] == "object"
        assert "data" in schema["properties"]
        assert "lsl" in schema["properties"]
        assert "usl" in schema["properties"]
        assert set(schema["required"]) == {"data", "lsl", "usl"}
        
        # Check minimum sample size requirement
        assert schema["properties"]["data"]["minItems"] == 30
    
    def test_capable_process_analysis(self, test_data_generator, specification_limits):
        """Test analysis of a capable process."""
        tool = CapabilityTool()
        
        # Generate capable process data (tight distribution)
        capable_data = test_data_generator.generate_normal_data(10.0, 0.2, 100)
        
        result = tool.execute({
            "data": capable_data,
            "lsl": specification_limits["lsl"],
            "usl": specification_limits["usl"],
            "target": specification_limits["target"]
        })
        
        # Check structure
        assert "capability_indices" in result
        assert "process_statistics" in result
        assert "defect_analysis" in result
        assert "interpretation" in result
        
        indices = result["capability_indices"]
        assert indices["cpk"] > 1.33  # Should be capable
        assert indices["cp"] > 1.33
        assert indices["cpk"] <= indices["cp"]  # Cpk should be <= Cp
        
        # Check interpretation
        interp = result["interpretation"]
        assert "CAPABLE" in interp.upper()
    
    def test_not_capable_process_analysis(self, test_data_generator, specification_limits):
        """Test analysis of a non-capable process."""
        tool = CapabilityTool()
        
        # Generate non-capable process data (wide distribution)
        not_capable_data = test_data_generator.generate_normal_data(10.0, 0.8, 100)
        
        result = tool.execute({
            "data": not_capable_data,
            "lsl": specification_limits["lsl"],
            "usl": specification_limits["usl"]
        })
        
        indices = result["capability_indices"]
        assert indices["cpk"] < 1.0  # Should not be capable
        
        interp = result["interpretation"]
        assert "NOT CAPABLE" in interp.upper()
    
    def test_marginal_capability(self, test_data_generator, specification_limits):
        """Test analysis of marginally capable process."""
        tool = CapabilityTool()
        
        # Generate marginally capable data
        marginal_data = test_data_generator.generate_normal_data(10.0, 0.4, 100)
        
        result = tool.execute({
            "data": marginal_data,
            "lsl": specification_limits["lsl"],
            "usl": specification_limits["usl"]
        })
        
        indices = result["capability_indices"]
        # Should be marginally capable (1.0 <= Cpk < 1.33)
        assert 1.0 <= indices["cpk"] < 1.33
        
        interp = result["interpretation"]
        assert "MARGINAL" in interp.upper() or "MARGINALLY" in interp.upper()
    
    def test_off_center_process(self, test_data_generator, specification_limits):
        """Test process that is off-center (good Cp, poor Cpk)."""
        tool = CapabilityTool()
        
        # Generate off-center data (shifted mean, tight distribution)
        off_center_data = test_data_generator.generate_normal_data(9.5, 0.25, 100)
        
        result = tool.execute({
            "data": off_center_data,
            "lsl": specification_limits["lsl"],
            "usl": specification_limits["usl"],
            "target": specification_limits["target"]
        })
        
        indices = result["capability_indices"]
        
        # Cp should be good (variation acceptable)
        assert indices["cp"] > 1.0
        
        # Cpk should be worse than Cp (centering issue)
        assert indices["cpk"] < indices["cp"]
        
        # Should detect centering issue
        interp = result["interpretation"]
        assert ("CENTERING" in interp.upper() or 
                "OFF-TARGET" in interp.upper() or
                "SHIFT" in interp.upper())
    
    def test_capability_index_calculations(self):
        """Test accuracy of capability index calculations."""
        tool = CapabilityTool()
        
        # Known data for manual verification
        data = [10.0] * 50 + [10.1] * 25 + [9.9] * 25  # Mean=10.0, very low variation
        
        result = tool.execute({
            "data": data,
            "lsl": 9.0,
            "usl": 11.0,
            "target": 10.0
        })
        
        indices = result["capability_indices"]
        stats = result["process_statistics"]
        
        # Manual calculations
        mean = stats["mean"]
        std = stats["standard_deviation"]
        
        expected_cp = (11.0 - 9.0) / (6 * std)
        expected_cpu = (11.0 - mean) / (3 * std)
        expected_cpl = (mean - 9.0) / (3 * std)
        expected_cpk = min(expected_cpu, expected_cpl)
        
        # Verify calculations
        assert abs(indices["cp"] - expected_cp) < 0.001
        assert abs(indices["cpu"] - expected_cpu) < 0.001
        assert abs(indices["cpl"] - expected_cpl) < 0.001
        assert abs(indices["cpk"] - expected_cpk) < 0.001
    
    def test_defect_rate_estimation(self, test_data_generator):
        """Test PPM defect rate calculations."""
        tool = CapabilityTool()
        
        # Generate data with known properties
        data = test_data_generator.generate_normal_data(10.0, 0.5, 100)
        
        result = tool.execute({
            "data": data,
            "lsl": 8.5,  # 3 sigma below mean
            "usl": 11.5  # 3 sigma above mean
        })
        
        defect_analysis = result["defect_analysis"]
        
        # For 3-sigma process, expect very low defect rates
        assert defect_analysis["ppm_total"] < 10000  # Less than 1%
        assert defect_analysis["yield_percentage"] > 90
        
        # PPM components should sum to total
        expected_total = defect_analysis["ppm_below_lsl"] + defect_analysis["ppm_above_usl"]
        assert abs(defect_analysis["ppm_total"] - expected_total) < 0.1
    
    def test_sigma_level_calculation(self):
        """Test sigma level conversion from PPM."""
        tool = CapabilityTool()
        
        # Test different capability scenarios
        test_cases = [
            (0.2, 6.0),      # Excellent
            (0.5, 5.0),      # Very good  
            (10, 5.0),       # Good
            (100, 4.0),      # Acceptable
            (1000, 4.0),     # Marginal
            (10000, 3.0)     # Poor
        ]
        
        for i, (std_dev, expected_min_sigma) in enumerate(test_cases):
            data = tool._generate_normal_data = lambda: [10.0] * 100  # Mock data
            
            # Calculate sigma level indirectly through tool
            ppm = (1 - 0.9973) * 1e6 if std_dev == 0.2 else (std_dev / 10.0) * 1e6
            sigma_level = tool._calculate_sigma_level(ppm)
            
            assert sigma_level >= expected_min_sigma - 1.0  # Allow some tolerance
    
    def test_confidence_intervals(self, test_data_generator):
        """Test confidence interval calculations."""
        tool = CapabilityTool()
        
        data = test_data_generator.generate_normal_data(10.0, 0.3, 100)
        
        result = tool.execute({
            "data": data,
            "lsl": 9.0,
            "usl": 11.0,
            "confidence_level": 0.95
        })
        
        ci = result["confidence_intervals"]
        
        assert "cp_interval" in ci
        assert "cpk_interval" in ci
        assert ci["confidence_level"] == 0.95
        
        # Intervals should be reasonable
        cp_lower, cp_upper = ci["cp_interval"]
        cpk_lower, cpk_upper = ci["cpk_interval"]
        
        assert cp_lower < cp_upper
        assert cpk_lower < cpk_upper
        assert cp_lower > 0
        assert cpk_lower >= 0  # Cpk can be 0
    
    def test_process_assessment(self, test_data_generator):
        """Test process assessment logic."""
        tool = CapabilityTool()
        
        # Test excellent capability
        excellent_data = test_data_generator.generate_normal_data(10.0, 0.15, 100)
        result = tool.execute({
            "data": excellent_data,
            "lsl": 9.0,
            "usl": 11.0
        })
        
        assessment = result["process_assessment"]
        assert assessment["capability_class"] in ["Excellent", "Capable"]
        assert assessment["ready_for_production"] == True
        
        # Test not capable
        poor_data = test_data_generator.generate_normal_data(10.0, 1.0, 100)
        result_poor = tool.execute({
            "data": poor_data,
            "lsl": 9.0,
            "usl": 11.0
        })
        
        assessment_poor = result_poor["process_assessment"]
        assert assessment_poor["capability_class"] == "Not Capable"
        assert assessment_poor["ready_for_production"] == False
    
    def test_specification_analysis(self, test_data_generator):
        """Test specification analysis with actual vs predicted defects."""
        tool = CapabilityTool()
        
        # Generate data that may have some actual defects
        data = test_data_generator.generate_normal_data(10.0, 0.6, 200)
        
        result = tool.execute({
            "data": data,
            "lsl": 8.5,
            "usl": 11.5
        })
        
        spec_analysis = result["specification_analysis"]
        
        # Check actual defects
        assert "actual_defects" in spec_analysis
        actual = spec_analysis["actual_defects"]
        assert actual["total_samples"] == 200
        assert (actual["below_lsl"] + actual["above_usl"] + 
                actual["within_spec"]) == actual["total_samples"]
        
        # Yield should be reasonable
        assert 0 <= spec_analysis["actual_yield"] <= 100
    
    def test_six_sigma_performance(self, test_data_generator):
        """Test Six Sigma performance identification."""
        tool = CapabilityTool()
        
        # Generate Six Sigma level data (Cpk >= 1.5)
        six_sigma_data = test_data_generator.generate_normal_data(10.0, 0.18, 100)
        
        result = tool.execute({
            "data": six_sigma_data,
            "lsl": 9.0,
            "usl": 11.0
        })
        
        assessment = result["process_assessment"]
        defects = result["defect_analysis"]
        
        # Should meet Six Sigma standards
        if result["capability_indices"]["cpk"] >= 1.5:
            assert assessment["meets_six_sigma"] == True
            assert defects["ppm_total"] <= 3.4  # Six Sigma standard
    
    def test_target_specification(self):
        """Test with and without target specification."""
        tool = CapabilityTool()
        data = [10.0] * 100
        
        # Without target - should use midpoint
        result_no_target = tool.execute({
            "data": data,
            "lsl": 9.0,
            "usl": 11.0
        })
        
        # With target
        result_with_target = tool.execute({
            "data": data,
            "lsl": 9.0,
            "usl": 11.0,
            "target": 10.5
        })
        
        # Target should be different
        stats_no_target = result_no_target["process_statistics"]
        stats_with_target = result_with_target["process_statistics"]
        
        assert stats_no_target["target"] == 10.0  # Midpoint
        assert stats_with_target["target"] == 10.5
    
    def test_edge_cases_and_validation(self):
        """Test edge cases and input validation."""
        tool = CapabilityTool()
        
        # Insufficient sample size
        with pytest.raises(ValueError, match="at least 30"):
            tool.execute({
                "data": [10.0] * 20,
                "lsl": 9.0,
                "usl": 11.0
            })
        
        # Invalid specification limits
        with pytest.raises(ValueError, match="greater than"):
            tool.execute({
                "data": [10.0] * 50,
                "lsl": 11.0,  # LSL > USL
                "usl": 9.0
            })
        
        # Target outside specifications
        with pytest.raises(ValueError, match="between"):
            tool.execute({
                "data": [10.0] * 50,
                "lsl": 9.0,
                "usl": 11.0,
                "target": 12.0  # Outside specs
            })
        
        # Missing required parameters
        with pytest.raises(ValueError, match="required"):
            tool.execute({"data": [10.0] * 50})  # Missing LSL, USL
    
    def test_chart_html_integration(self, sample_capability_data):
        """Test visualization integration."""
        tool = CapabilityTool()
        
        result = tool.execute({
            "data": sample_capability_data,
            "lsl": 9.0,
            "usl": 11.0
        })
        
        assert "chart_html" in result
        assert isinstance(result["chart_html"], str)
    
    def test_interpretation_quality(self, test_data_generator):
        """Test quality and completeness of interpretation text."""
        tool = CapabilityTool()
        
        scenarios = test_data_generator.generate_capability_scenarios()
        
        for scenario_name, data in scenarios.items():
            result = tool.execute({
                "data": data,
                "lsl": 9.0,
                "usl": 11.0,
                "target": 10.0
            })
            
            interpretation = result["interpretation"]
            
            # Should contain key elements
            assert len(interpretation) > 100  # Substantial content
            assert ("CAPABILITY" in interpretation.upper() or 
                    "CAPABLE" in interpretation.upper())
            assert "RECOMMENDATIONS" in interpretation.upper()
            
            # Should match scenario
            cpk = result["capability_indices"]["cpk"]
            if cpk >= 1.33:
                assert "CAPABLE" in interpretation.upper()
            elif cpk < 1.0:
                assert "NOT CAPABLE" in interpretation.upper()
            else:
                assert "MARGINAL" in interpretation.upper()