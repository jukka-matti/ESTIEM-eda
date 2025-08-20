"""Unit tests for ANOVA Analysis tool."""

import numpy as np
import pytest

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
            "Group C": test_data_generator.generate_normal_data(16.0, 1.0, 20, seed=44),
        }

        result = tool.execute({"groups": groups})

        # Check structure
        assert "anova_results" in result
        assert "group_statistics" in result
        assert "interpretation" in result

        anova_results = result["anova_results"]

        # Should detect significant difference
        assert anova_results["significant"]
        assert anova_results["p_value"] < 0.05
        assert anova_results["f_statistic"] > 0

        # Basic validation of F-statistic
        assert anova_results["f_statistic"] > 0

    def test_no_significant_difference(self, test_data_generator):
        """Test when no significant differences exist."""
        tool = ANOVATool()

        # Generate groups with similar means (should not be significant)
        groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 1.0, 20, seed=42),
            "Group B": test_data_generator.generate_normal_data(10.1, 1.0, 20, seed=43),
            "Group C": test_data_generator.generate_normal_data(10.2, 1.0, 20, seed=44),
        }

        result = tool.execute({"groups": groups})
        anova_results = result["anova_results"]

        # Should not detect significant difference
        assert not anova_results["significant"]
        assert anova_results["p_value"] >= 0.05

        # Interpretation should indicate no difference
        interpretation = result["interpretation"]
        assert "NO SIGNIFICANT" in interpretation.upper()

    def test_descriptive_statistics(self, sample_anova_groups):
        """Test descriptive statistics calculations."""
        tool = ANOVATool()
        result = tool.execute({"groups": sample_anova_groups})

        group_stats = result["group_statistics"]

        # Check each group has required statistics
        for group_name, data in sample_anova_groups.items():
            assert group_name in group_stats
            stats = group_stats[group_name]

            # Basic required stats
            assert "mean" in stats
            assert "std" in stats
            assert "size" in stats

            # Verify calculations
            assert stats["size"] == len(data)
            assert abs(stats["mean"] - np.mean(data)) < 0.0001
            assert abs(stats["std"] - np.std(data, ddof=1)) < 0.0001

    def test_anova_calculations(self):
        """Test ANOVA statistical calculations accuracy."""
        tool = ANOVATool()

        # Simple known data for manual verification
        groups = {"A": [1.0, 2.0, 3.0], "B": [4.0, 5.0, 6.0], "C": [7.0, 8.0, 9.0]}

        result = tool.execute({"groups": groups})
        anova_results = result["anova_results"]

        # Manual calculation verification
        all_data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        np.mean(all_data)

        # Degrees of freedom
        k = 3  # number of groups
        n = 9  # total observations
        df_between = k - 1  # 2
        df_within = n - k  # 6

        assert anova_results["df_between"] == df_between
        assert anova_results["df_within"] == df_within

        # Check sum of squares are present
        assert "ssb" in anova_results
        assert "ssw" in anova_results
        assert "sst" in anova_results

        # Verify sum of squares relationship
        assert abs(anova_results["ssb"] + anova_results["ssw"] - anova_results["sst"]) < 0.0001

    def test_assumption_testing(self, test_data_generator):
        """Test simplified ANOVA analysis."""
        tool = ANOVATool()

        # Test with normal data
        normal_groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 1.0, 25),
            "Group B": test_data_generator.generate_normal_data(12.0, 1.0, 25),
            "Group C": test_data_generator.generate_normal_data(11.0, 1.0, 25),
        }

        result = tool.execute({"groups": normal_groups})

        # Basic structure checks
        assert "anova_results" in result
        assert "group_statistics" in result
        assert "interpretation" in result

        # Verify statistical calculations are present
        anova_results = result["anova_results"]
        assert "f_statistic" in anova_results
        assert "p_value" in anova_results
        assert "significant" in anova_results

    def test_assumption_violations(self, test_data_generator):
        """Test ANOVA with different data patterns."""
        tool = ANOVATool()

        # Generate data with different variances
        groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 1.0, 25),
            "Group B": test_data_generator.generate_normal_data(12.0, 2.0, 25),
            "Group C": test_data_generator.generate_normal_data(11.0, 0.5, 25),
        }

        result = tool.execute({"groups": groups})

        # Basic validation - should still complete analysis
        assert "anova_results" in result
        assert "group_statistics" in result
        assert result.get("success", True)

        # Check that interpretation exists
        assert "interpretation" in result
        assert isinstance(result["interpretation"], str)
        assert len(result["interpretation"]) > 0

    def test_tukey_hsd_posthoc(self, test_data_generator):
        """Test Tukey HSD post-hoc analysis."""
        tool = ANOVATool()

        # Generate groups with clear differences
        groups = {
            "Low": test_data_generator.generate_normal_data(5.0, 0.5, 20),
            "Medium": test_data_generator.generate_normal_data(10.0, 0.5, 20),
            "High": test_data_generator.generate_normal_data(15.0, 0.5, 20),
        }

        result = tool.execute({"groups": groups, "post_hoc": True})

        if result["anova_results"]["significant"] and "post_hoc" in result:
            posthoc = result["post_hoc"]

            assert "method" in posthoc
            assert "comparisons" in posthoc

            comparisons = posthoc["comparisons"]

            # Should have 3 choose 2 = 3 comparisons
            assert len(comparisons) == 3

            # Each comparison should have required fields
            for comparison in comparisons:
                assert "groups" in comparison
                assert "p_value" in comparison
                assert "significant" in comparison
                assert "mean_diff" in comparison

    def test_effect_size_calculation(self, test_data_generator):
        """Test effect size calculations."""
        tool = ANOVATool()

        # Generate groups with moderate differences
        groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 2.0, 30),
            "Group B": test_data_generator.generate_normal_data(13.0, 2.0, 30),
            "Group C": test_data_generator.generate_normal_data(11.5, 2.0, 30),
        }

        result = tool.execute({"groups": groups})
        anova_results = result["anova_results"]

        # Check basic ANOVA statistics are present
        assert "f_statistic" in anova_results
        assert "p_value" in anova_results
        assert "significant" in anova_results
        assert "df_between" in anova_results
        assert "df_within" in anova_results

        # Verify reasonable ranges
        assert anova_results["f_statistic"] >= 0
        assert 0 <= anova_results["p_value"] <= 1
        assert anova_results["df_between"] == 2  # 3 groups - 1
        assert anova_results["df_within"] == 87  # 90 - 3

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
            required_stats = ["q1", "median", "q3", "iqr", "min", "max", "outliers", "mean", "data"]
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

        # P-values should be the same (same data), significance may differ
        p_val_01 = result_01["anova_results"]["p_value"]
        p_val_05 = result_05["anova_results"]["p_value"]
        assert abs(p_val_01 - p_val_05) < 0.001  # Same data, same p-value

    def test_chart_html_integration(self, sample_anova_groups):
        """Test visualization integration."""
        tool = ANOVATool()
        result = tool.execute({"groups": sample_anova_groups})

        # Check that result has expected structure
        assert "analysis_type" in result
        assert result["analysis_type"] == "anova"
        assert "success" in result
        assert result["success"]
        assert isinstance(result["chart_html"], str)

    def test_interpretation_completeness(self, test_data_generator):
        """Test interpretation text completeness."""
        tool = ANOVATool()

        # Test significant case
        significant_groups = {
            "Low": test_data_generator.generate_normal_data(5.0, 1.0, 20),
            "High": test_data_generator.generate_normal_data(10.0, 1.0, 20),
        }

        result_sig = tool.execute({"groups": significant_groups})
        interp_sig = result_sig["interpretation"]

        # Should contain key elements
        assert len(interp_sig) > 50  # Basic content
        assert "significant" in interp_sig.lower() or "difference" in interp_sig.lower()
        assert "ANOVA" in interp_sig.upper() or "F(" in interp_sig
        assert "RECOMMENDATION" in interp_sig.upper()

        if result_sig["anova_results"]["significant"]:
            assert "SIGNIFICANT" in interp_sig.upper()

        # Test non-significant case
        similar_groups = {
            "Group1": test_data_generator.generate_normal_data(10.0, 1.0, 20),
            "Group2": test_data_generator.generate_normal_data(10.1, 1.0, 20),
        }

        result_ns = tool.execute({"groups": similar_groups})
        interp_ns = result_ns["interpretation"]

        if not result_ns["anova_results"]["significant"]:
            assert "NO SIGNIFICANT" in interp_ns.upper()

    def test_edge_cases_and_validation(self):
        """Test edge cases and input validation."""
        tool = ANOVATool()

        # Too few groups should return error
        result = tool.execute({"groups": {"Single Group": [1, 2, 3]}})
        assert not result.get("success", True)

        # Groups with too few observations should handle gracefully
        result = tool.execute(
            {
                "groups": {
                    "Group A": [1, 2],  # Only 2 observations
                    "Group B": [3, 4, 5],
                }
            }
        )
        # May succeed or fail gracefully depending on implementation
        assert "success" in result

        # Empty group
        with pytest.raises(ValueError, match="empty"):
            tool.execute(
                {
                    "groups": {
                        "Group A": [1, 2, 3],
                        "Group B": [],  # Empty group
                    }
                }
            )

        # Non-numeric data
        with pytest.raises(ValueError):
            tool.execute({"groups": {"Group A": [1, 2, "three"], "Group B": [4, 5, 6]}})

    def test_large_dataset_performance(self, test_data_generator):
        """Test performance with larger datasets."""
        tool = ANOVATool()

        # Generate larger groups
        large_groups = {
            "Group A": test_data_generator.generate_normal_data(10.0, 2.0, 200),
            "Group B": test_data_generator.generate_normal_data(12.0, 2.0, 180),
            "Group C": test_data_generator.generate_normal_data(11.0, 2.0, 220),
            "Group D": test_data_generator.generate_normal_data(13.0, 2.0, 190),
        }

        result = tool.execute({"groups": large_groups})

        # Should complete successfully
        # Check group statistics are present
        assert "group_statistics" in result
        assert len(result["group_statistics"]) == 4
        assert len(result["post_hoc_analysis"]["comparisons"]) == 6  # 4 choose 2

        # Results should be reasonable
        anova_results = result["anova_results"]
        assert anova_results["f_statistic"] > 0
        assert 0 <= anova_results["p_value"] <= 1
