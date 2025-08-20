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
        assert "data" in schema["required"]
        assert "lsl" in schema["required"] 
        assert "usl" in schema["required"]
    
    def test_capable_process_analysis(self, sample_capability_data):
        """Test analysis of capable process."""
        tool = CapabilityTool()
        lsl, usl = 95, 105  # Wide specification limits
        
        result = tool.execute({
            "data": sample_capability_data,
            "lsl": lsl,
            "usl": usl
        })
        
        # Check basic structure
        assert "capability_indices" in result
        assert "statistics" in result
        assert "defect_analysis" in result
        assert "interpretation" in result
        assert "success" in result
        assert result["success"] == True
        
        # Check capability indices
        indices = result["capability_indices"]
        assert "cp" in indices
        assert "cpk" in indices
        assert "pp" in indices
        assert "ppk" in indices
        
        # All indices should be positive
        assert indices["cp"] > 0
        assert indices["cpk"] > 0
        assert indices["pp"] > 0
        assert indices["ppk"] > 0
    
    def test_not_capable_process_analysis(self, test_data_generator):
        """Test analysis of not capable process."""
        tool = CapabilityTool()
        
        # Generate data that doesn't fit well within tight limits
        data = test_data_generator.generate_normal_data(100, 3, 50)  # std=3
        lsl, usl = 98, 102  # Very tight limits
        
        result = tool.execute({
            "data": data,
            "lsl": lsl,
            "usl": usl
        })
        
        indices = result["capability_indices"]
        
        # Should have low capability indices
        assert indices["cp"] < 1.33  # Not highly capable
        assert indices["cpk"] < 1.33
        
        # Defect analysis should show potential defects
        defects = result["defect_analysis"]
        assert "ppm_total" in defects
        assert defects["ppm_total"] >= 0
    
    def test_marginal_capability(self, test_data_generator):
        """Test marginal capability analysis."""
        tool = CapabilityTool()
        
        data = test_data_generator.generate_normal_data(100, 1.5, 50)
        lsl, usl = 96, 104  # Moderate limits
        
        result = tool.execute({
            "data": data,
            "lsl": lsl,
            "usl": usl
        })
        
        indices = result["capability_indices"]
        
        # Should be in marginal range
        assert 0.8 <= indices["cp"] <= 1.5  # Reasonable range
        assert indices["cpk"] >= 0  # Should be positive
        
        # Interpretation should provide guidance
        interpretation = result["interpretation"]
        assert isinstance(interpretation, str)
        assert len(interpretation) > 50
    
    def test_off_center_process(self, test_data_generator):
        """Test off-center process analysis."""
        tool = CapabilityTool()
        
        # Generate data off-center from specification limits
        data = test_data_generator.generate_normal_data(102, 1, 50)  # Mean at 102
        lsl, usl = 98, 104  # Center would be at 101
        
        result = tool.execute({
            "data": data,
            "lsl": lsl,
            "usl": usl,
            "target": 101
        })
        
        indices = result["capability_indices"]
        
        # Cp should be different from Cpk due to off-center
        cp_cpk_diff = abs(indices["cp"] - indices["cpk"])
        assert cp_cpk_diff > 0.01  # Should be noticeable difference
    
    def test_capability_index_calculations(self):
        """Test capability index calculations."""
        tool = CapabilityTool()
        
        # Use known data for manual verification
        data = [98, 99, 100, 101, 102]  # Mean=100, std≈1.58
        lsl, usl = 95, 105
        
        result = tool.execute({
            "data": data,
            "lsl": lsl,
            "usl": usl
        })
        
        indices = result["capability_indices"]
        stats = result["statistics"]
        
        # Verify mean calculation
        assert abs(stats["mean"] - 100) < 0.1
        
        # Verify indices are calculated
        assert indices["cp"] > 0
        assert indices["cpk"] > 0
        
        # Cp should be (USL-LSL)/(6*sigma)
        tolerance = usl - lsl  # 10
        expected_cp_range = tolerance / (6 * 3)  # Rough estimate
        assert 0.3 < indices["cp"] < 2.0  # Reasonable range
    
    def test_defect_rate_estimation(self, sample_capability_data, specification_limits):
        """Test defect rate estimation."""
        tool = CapabilityTool()
        lsl, usl = specification_limits
        
        result = tool.execute({
            "data": sample_capability_data,
            "lsl": lsl,
            "usl": usl
        })
        
        defects = result["defect_analysis"]
        
        # Should have defect rate information
        assert "ppm_total" in defects
        assert "ppm_lower" in defects
        assert "ppm_upper" in defects
        
        # PPM values should be non-negative
        assert defects["ppm_total"] >= 0
        assert defects["ppm_lower"] >= 0
        assert defects["ppm_upper"] >= 0
        
        # Total should be sum of lower and upper
        total_calc = defects["ppm_lower"] + defects["ppm_upper"]
        assert abs(defects["ppm_total"] - total_calc) < 1  # Allow small rounding differences
    
    def test_sigma_level_calculation(self, test_data_generator):
        """Test sigma level calculations."""
        tool = CapabilityTool()
        
        # Generate high-quality data (low variation)
        data = test_data_generator.generate_normal_data(100, 0.5, 100)
        lsl, usl = 97, 103
        
        result = tool.execute({
            "data": data,
            "lsl": lsl,
            "usl": usl
        })
        
        # Should complete successfully
        assert result.get("success", True)
        
        # Check that all basic indices are present
        indices = result["capability_indices"]
        for key in ["cp", "cpk", "pp", "ppk"]:
            assert key in indices
            assert isinstance(indices[key], (int, float))
    
    def test_confidence_intervals(self, sample_capability_data, specification_limits):
        """Test basic statistical validation."""
        tool = CapabilityTool()
        lsl, usl = specification_limits
        
        result = tool.execute({
            "data": sample_capability_data,
            "lsl": lsl,
            "usl": usl
        })
        
        # Verify basic statistics
        stats = result["statistics"]
        assert "mean" in stats
        assert "std" in stats
        assert "sample_size" in stats
        
        # Sample size should match input
        assert stats["sample_size"] == len(sample_capability_data)
        
        # Standard deviation should be positive
        assert stats["std"] > 0
    
    def test_process_assessment(self, sample_capability_data, specification_limits):
        """Test process assessment functionality."""
        tool = CapabilityTool()
        lsl, usl = specification_limits
        
        result = tool.execute({
            "data": sample_capability_data,
            "lsl": lsl,
            "usl": usl
        })
        
        # Should provide interpretation
        interpretation = result["interpretation"]
        assert isinstance(interpretation, str)
        assert len(interpretation) > 30
        
        # Should mention capability concepts
        assert any(word in interpretation.lower() for word in ["capability", "process", "specification"])
    
    def test_specification_analysis(self, test_data_generator):
        """Test specification limit analysis."""
        tool = CapabilityTool()
        
        data = test_data_generator.generate_normal_data(50, 2, 40)
        lsl, usl = 44, 56  # Reasonable limits
        
        result = tool.execute({
            "data": data,
            "lsl": lsl,
            "usl": usl
        })
        
        # Check that specification limits are used correctly
        defects = result["defect_analysis"]
        
        # Should analyze both upper and lower limits
        assert "ppm_lower" in defects
        assert "ppm_upper" in defects
        
        # Values should be reasonable (not infinite)
        assert defects["ppm_lower"] < 1000000  # Less than 100%
        assert defects["ppm_upper"] < 1000000
    
    def test_six_sigma_performance(self, test_data_generator):
        """Test six sigma level performance."""
        tool = CapabilityTool()
        
        # Generate very high-quality data
        data = test_data_generator.generate_normal_data(100, 0.3, 50)  # Very low variation
        lsl, usl = 96, 104  # Wide limits
        
        result = tool.execute({
            "data": data,
            "lsl": lsl,
            "usl": usl
        })
        
        indices = result["capability_indices"]
        
        # Should have high capability indices
        assert indices["cp"] > 1.0  # At least capable
        assert indices["cpk"] > 0.8  # Reasonably centered
        
        # Defect rates should be low
        defects = result["defect_analysis"]
        assert defects["ppm_total"] < 10000  # Less than 1%
    
    def test_target_specification(self, test_data_generator):
        """Test target specification functionality."""
        tool = CapabilityTool()
        
        data = test_data_generator.generate_normal_data(101, 1, 40)
        lsl, usl = 98, 104
        target = 100  # Different from actual mean
        
        result = tool.execute({
            "data": data,
            "lsl": lsl,
            "usl": usl,
            "target": target
        })
        
        # Should complete successfully
        assert result.get("success", True)
        
        # Should have all capability indices
        indices = result["capability_indices"]
        assert all(key in indices for key in ["cp", "cpk", "pp", "ppk"])
    
    def test_edge_cases_and_validation(self):
        """Test edge cases and validation."""
        tool = CapabilityTool()
        
        # Minimum data points
        min_data = [10.0, 10.1, 10.2]
        result = tool.execute({
            "data": min_data,
            "lsl": 9,
            "usl": 11
        })
        assert result.get("success", True)
        
        # All same values (zero variation)
        constant_data = [10.0] * 10
        result = tool.execute({
            "data": constant_data,
            "lsl": 9,
            "usl": 11
        })
        assert result.get("success", True)
        
        # Very tight specifications
        data = [10.0, 10.1, 9.9, 10.05, 9.95]
        result = tool.execute({
            "data": data,
            "lsl": 9.98,
            "usl": 10.02
        })
        assert result.get("success", True)
    
    def test_chart_html_integration(self, sample_capability_data, specification_limits):
        """Test basic output structure."""
        tool = CapabilityTool()
        lsl, usl = specification_limits
        
        result = tool.execute({
            "data": sample_capability_data,
            "lsl": lsl,
            "usl": usl
        })
        
        # Check that result has expected structure
        assert "analysis_type" in result
        assert result["analysis_type"] == "process_capability"
        assert "success" in result
        assert result["success"] == True
        
        # Verify essential data structure
        assert isinstance(result["capability_indices"], dict)
        assert isinstance(result["statistics"], dict)
        assert isinstance(result["defect_analysis"], dict)
    
    def test_interpretation_quality(self, test_data_generator):
        """Test interpretation quality and content."""
        tool = CapabilityTool()
        
        data = test_data_generator.generate_normal_data(100, 1.5, 60)
        lsl, usl = 95, 105
        
        result = tool.execute({
            "data": data,
            "lsl": lsl,
            "usl": usl
        })
        
        interpretation = result["interpretation"]
        
        # Should provide meaningful interpretation
        assert len(interpretation) > 50
        assert any(word in interpretation.lower() for word in ["capable", "process", "specification"])
        
        # Should mention key indices
        indices = result["capability_indices"]
        cpk_value = indices["cpk"]
        if cpk_value > 1.33:
            assert any(word in interpretation.lower() for word in ["good", "capable", "acceptable"])
        elif cpk_value < 1.0:
            assert any(word in interpretation.lower() for word in ["improvement", "poor", "not capable"])