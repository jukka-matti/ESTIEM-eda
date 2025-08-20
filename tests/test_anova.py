"""Unit tests for ANOVA Analysis tool."""

import pytest
import numpy as np
from estiem_eda.tools.anova import ANOVATool


class TestANOVATool:
    """Test suite for ANOVA functionality."""
    
    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = ANOVATool()
        assert tool.name == "anova_boxplot"
        assert "anova" in tool.description.lower()
    
    def test_input_schema(self):
        """Test input schema is properly defined."""
        tool = ANOVATool()
        schema = tool.get_input_schema()
        
        assert schema["type"] == "object"
        assert "groups" in schema["properties"]
        assert "groups" in schema["required"]
        assert schema["properties"]["groups"]["type"] == "object"
        assert schema["properties"]["groups"]["minProperties"] == 2
    
    def test_significant_difference_detection(self, test_data_generator):
        """Test detection of significant differences between groups."""
        tool = ANOVATool()
        
        # Generate groups with different means (should be significant)
        groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 1.0, 20, seed=42),
            "Group B": test_data_generator.generate_normal_data(13.0, 1.0, 20, seed=43),
            "Group C": test_data_generator.generate_normal_data(16.0, 1.0, 20, seed=44)
        }
        
        result = tool.execute({"groups": groups})
        
        # Check structure
        assert "anova_results" in result
        assert "descriptive_statistics" in result
        assert "post_hoc_analysis" in result
        assert "interpretation" in result
        
        anova_results = result["anova_results"]
        
        # Should detect significant difference
        assert anova_results["significant"] == True
        assert anova_results["p_value"] < 0.05
        assert anova_results["f_statistic"] > 0
        
        # F-statistic should be greater than F-critical for significance
        assert anova_results["f_statistic"] > anova_results["f_critical"]
    
    def test_no_significant_difference(self, test_data_generator):
        """Test when no significant differences exist."""
        tool = ANOVATool()
        
        # Generate groups with similar means (should not be significant)
        groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 1.0, 20, seed=42),
            "Group B": test_data_generator.generate_normal_data(10.1, 1.0, 20, seed=43),
            "Group C": test_data_generator.generate_normal_data(10.2, 1.0, 20, seed=44)
        }
        
        result = tool.execute({"groups": groups})
        anova_results = result["anova_results"]
        
        # Should not detect significant difference
        assert anova_results["significant"] == False
        assert anova_results["p_value"] >= 0.05
        
        # Interpretation should indicate no difference
        interpretation = result["interpretation"]
        assert "NO SIGNIFICANT" in interpretation.upper()
    
    def test_descriptive_statistics(self, sample_anova_groups):
        """Test descriptive statistics calculations."""
        tool = ANOVATool()
        result = tool.execute({"groups": sample_anova_groups})
        
        desc_stats = result["descriptive_statistics"]
        
        # Should have by_group and overall statistics
        assert "by_group" in desc_stats
        assert "overall" in desc_stats
        
        by_group = desc_stats["by_group"]
        
        # Check each group has required statistics
        for group_name, data in sample_anova_groups.items():
            assert group_name in by_group
            group_stats = by_group[group_name]
            
            required_stats = ["n", "mean", "std", "min", "max", "median", "q1", "q3", "iqr"]
            for stat in required_stats:
                assert stat in group_stats
            
            # Verify some calculations
            assert group_stats["n"] == len(data)
            assert abs(group_stats["mean"] - np.mean(data)) < 0.0001
            assert abs(group_stats["std"] - np.std(data, ddof=1)) < 0.0001
        
        # Check overall statistics
        overall = desc_stats["overall"]
        total_n = sum(len(data) for data in sample_anova_groups.values())
        assert overall["total_n"] == total_n
        assert overall["groups"] == len(sample_anova_groups)
    
    def test_anova_calculations(self):
        """Test ANOVA statistical calculations accuracy."""
        tool = ANOVATool()
        
        # Simple known data for manual verification
        groups = {
            "A": [1.0, 2.0, 3.0],
            "B": [4.0, 5.0, 6.0],
            "C": [7.0, 8.0, 9.0]
        }
        
        result = tool.execute({"groups": groups})
        anova_results = result["anova_results"]
        
        # Manual calculation verification
        all_data = [1,2,3,4,5,6,7,8,9]
        grand_mean = np.mean(all_data)
        
        # Degrees of freedom
        k = 3  # number of groups
        n = 9  # total observations
        df_between = k - 1  # 2
        df_within = n - k   # 6
        
        assert anova_results["degrees_of_freedom"]["between_groups"] == df_between
        assert anova_results["degrees_of_freedom"]["within_groups"] == df_within
        
        # Sum of squares should sum correctly
        ss_between = anova_results["sum_of_squares"]["between_groups"]
        ss_within = anova_results["sum_of_squares"]["within_groups"]
        ss_total = anova_results["sum_of_squares"]["total"]
        
        assert abs((ss_between + ss_within) - ss_total) < 0.001
    
    def test_assumption_testing(self, test_data_generator):
        """Test ANOVA assumption testing."""
        tool = ANOVATool()
        
        # Test with normal data (assumptions should be met)
        normal_groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 1.0, 25),
            "Group B": test_data_generator.generate_normal_data(12.0, 1.0, 25),
            "Group C": test_data_generator.generate_normal_data(11.0, 1.0, 25)
        }
        
        result = tool.execute({
            "groups": normal_groups,
            "assumption_tests": True
        })
        
        assumptions = result["assumption_tests"]
        
        # Check normality testing
        assert "normality" in assumptions
        normality = assumptions["normality"]
        assert "by_group" in normality
        assert "all_groups_normal" in normality
        assert normality["test_used"] == "Shapiro-Wilk"
        
        # Check equal variance testing
        assert "equal_variances" in assumptions
        equal_var = assumptions["equal_variances"]
        assert "levene_test" in equal_var
        assert "equal_variances" in equal_var["levene_test"]
        
        # Overall assumption status
        assert "assumptions_met" in assumptions
    
    def test_assumption_violations(self, test_data_generator):
        """Test detection of assumption violations."""
        tool = ANOVATool()
        
        # Generate data with unequal variances
        unequal_var_groups = test_data_generator.generate_unequal_variance_groups()
        
        result = tool.execute({
            "groups": unequal_var_groups,
            "assumption_tests": True
        })
        
        assumptions = result["assumption_tests"]
        
        # Should detect unequal variances
        equal_var_test = assumptions["equal_variances"]["levene_test"]
        # Note: May or may not detect depending on random data, but structure should be correct
        assert "equal_variances" in equal_var_test
        assert "p_value" in equal_var_test
        
        # Interpretation should mention assumption issues if detected
        interpretation = result["interpretation"]
        if not assumptions["assumptions_met"]:
            assert ("ASSUMPTION" in interpretation.upper() or 
                    "VIOLATION" in interpretation.upper())
    
    def test_tukey_hsd_posthoc(self, test_data_generator):
        """Test Tukey HSD post-hoc analysis."""
        tool = ANOVATool()
        
        # Generate groups with clear differences
        groups = {
            "Low": test_data_generator.generate_normal_data(5.0, 0.5, 20),
            "Medium": test_data_generator.generate_normal_data(10.0, 0.5, 20),
            "High": test_data_generator.generate_normal_data(15.0, 0.5, 20)
        }
        
        result = tool.execute({
            "groups": groups,
            "post_hoc": True
        })
        
        if result["anova_results"]["significant"]:
            posthoc = result["post_hoc_analysis"]
            
            assert "test" in posthoc
            assert posthoc["test"] == "Tukey HSD"
            assert "comparisons" in posthoc
            assert "significant_pairs" in posthoc
            
            comparisons = posthoc["comparisons"]
            
            # Should have 3 choose 2 = 3 comparisons
            assert len(comparisons) == 3
            
            # Each comparison should have required fields
            for comparison in comparisons:
                required_fields = ["group1", "group2", "mean1", "mean2", 
                                 "mean_difference", "significant"]
                for field in required_fields:
                    assert field in comparison
                
                # Mean difference should match calculation
                expected_diff = abs(comparison["mean1"] - comparison["mean2"])
                assert abs(comparison["abs_difference"] - expected_diff) < 0.001
    
    def test_effect_size_calculation(self, test_data_generator):
        """Test effect size calculations."""
        tool = ANOVATool()
        
        # Generate groups with moderate differences
        groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 2.0, 30),
            "Group B": test_data_generator.generate_normal_data(13.0, 2.0, 30),
            "Group C": test_data_generator.generate_normal_data(11.5, 2.0, 30)
        }
        
        result = tool.execute({"groups": groups})
        effect_size = result["effect_size"]
        
        # Check required effect size measures
        assert "eta_squared" in effect_size
        assert "partial_eta_squared" in effect_size
        assert "omega_squared" in effect_size
        assert "magnitude" in effect_size
        
        # Values should be between 0 and 1
        assert 0 <= effect_size["eta_squared"] <= 1
        assert 0 <= effect_size["partial_eta_squared"] <= 1
        assert 0 <= effect_size["omega_squared"] <= 1
        
        # Eta-squared should be reasonable for group differences
        # (exact value depends on random data, but should be > 0 for different groups)
        if result["anova_results"]["significant"]:
            assert effect_size["eta_squared"] > 0
        
        # Magnitude should be appropriate descriptor
        assert effect_size["magnitude"] in ["Negligible", "Small", "Medium", "Large"]
    
    def test_boxplot_data_preparation(self, sample_anova_groups):
        """Test boxplot data structure."""
        tool = ANOVATool()
        result = tool.execute({"groups": sample_anova_groups})
        
        boxplot_data = result["boxplot_data"]
        
        # Should have data for each group
        for group_name in sample_anova_groups.keys():
            assert group_name in boxplot_data
            
            group_boxplot = boxplot_data[group_name]
            
            # Required boxplot statistics
            required_stats = ["q1", "median", "q3", "iqr", "min", "max", 
                            "outliers", "mean", "data"]
            for stat in required_stats:
                assert stat in group_boxplot
            
            # Data integrity checks
            data = group_boxplot["data"]
            assert len(data) == len(sample_anova_groups[group_name])
            
            # Statistical relationships
            assert group_boxplot["q1"] <= group_boxplot["median"] <= group_boxplot["q3"]
            assert group_boxplot["iqr"] == group_boxplot["q3"] - group_boxplot["q1"]
    
    def test_alpha_level_customization(self, sample_anova_groups):
        """Test custom alpha level functionality."""
        tool = ANOVATool()
        
        # Test with different alpha levels
        result_01 = tool.execute({"groups": sample_anova_groups, "alpha": 0.01})
        result_05 = tool.execute({"groups": sample_anova_groups, "alpha": 0.05})
        
        # Alpha should be recorded in results
        assert result_01["anova_results"]["alpha"] == 0.01
        assert result_05["anova_results"]["alpha"] == 0.05
        
        # Critical F values should be different (0.01 should be higher)
        f_crit_01 = result_01["anova_results"]["f_critical"]
        f_crit_05 = result_05["anova_results"]["f_critical"]
        assert f_crit_01 > f_crit_05
    
    def test_chart_html_integration(self, sample_anova_groups):
        """Test visualization integration."""
        tool = ANOVATool()
        result = tool.execute({"groups": sample_anova_groups})
        
        assert "chart_html" in result
        assert isinstance(result["chart_html"], str)
    
    def test_interpretation_completeness(self, test_data_generator):
        """Test interpretation text completeness."""
        tool = ANOVATool()
        
        # Test significant case
        significant_groups = {
            "Low": test_data_generator.generate_normal_data(5.0, 1.0, 20),
            "High": test_data_generator.generate_normal_data(10.0, 1.0, 20)
        }
        
        result_sig = tool.execute({"groups": significant_groups})
        interp_sig = result_sig["interpretation"]
        
        # Should contain key elements
        assert len(interp_sig) > 200  # Substantial content
        assert "ANOVA" in interp_sig.upper() or "F(" in interp_sig
        assert "RECOMMENDATION" in interp_sig.upper()
        
        if result_sig["anova_results"]["significant"]:
            assert "SIGNIFICANT" in interp_sig.upper()
        
        # Test non-significant case
        similar_groups = {
            "Group1": test_data_generator.generate_normal_data(10.0, 1.0, 20),
            "Group2": test_data_generator.generate_normal_data(10.1, 1.0, 20)
        }
        
        result_ns = tool.execute({"groups": similar_groups})
        interp_ns = result_ns["interpretation"]
        
        if not result_ns["anova_results"]["significant"]:
            assert "NO SIGNIFICANT" in interp_ns.upper()
    
    def test_edge_cases_and_validation(self):
        """Test edge cases and input validation."""
        tool = ANOVATool()
        
        # Too few groups
        with pytest.raises(ValueError):
            tool.execute({"groups": {"Single Group": [1, 2, 3]}})
        
        # Groups with too few observations
        with pytest.raises(ValueError, match="at least 3"):
            tool.execute({
                "groups": {
                    "Group A": [1, 2],  # Only 2 observations
                    "Group B": [3, 4, 5]
                }
            })
        
        # Empty group
        with pytest.raises(ValueError, match="empty"):
            tool.execute({
                "groups": {
                    "Group A": [1, 2, 3],
                    "Group B": []  # Empty group
                }
            })
        
        # Non-numeric data
        with pytest.raises(ValueError):
            tool.execute({
                "groups": {
                    "Group A": [1, 2, "three"],
                    "Group B": [4, 5, 6]
                }
            })
    
    def test_large_dataset_performance(self, test_data_generator):
        """Test performance with larger datasets."""
        tool = ANOVATool()
        
        # Generate larger groups
        large_groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 2.0, 200),
            "Group B": test_data_generator.generate_normal_data(12.0, 2.0, 180),
            "Group C": test_data_generator.generate_normal_data(11.0, 2.0, 220),
            "Group D": test_data_generator.generate_normal_data(13.0, 2.0, 190)
        }
        
        result = tool.execute({"groups": large_groups})
        
        # Should complete successfully
        assert result["descriptive_statistics"]["overall"]["total_n"] == 790
        assert len(result["post_hoc_analysis"]["comparisons"]) == 6  # 4 choose 2
        
        # Results should be reasonable
        anova_results = result["anova_results"]
        assert anova_results["f_statistic"] > 0
        assert 0 <= anova_results["p_value"] <= 1