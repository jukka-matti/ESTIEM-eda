"""Unified Process Analysis Tool combining I-Chart, Capability, and Probability Plot.

This module provides a comprehensive process analysis workflow that combines
three related statistical analyses for a single measurement variable:
1. I-Chart for process stability assessment
2. Capability analysis for specification compliance
3. Probability plot for distribution assessment
"""

from typing import Any

import numpy as np

from ..core.calculations import calculate_process_capability, calculate_i_chart, calculate_probability_plot
from .simplified_base import SimplifiedMCPTool


class ProcessAnalysisTool(SimplifiedMCPTool):
    """Unified Process Analysis combining stability, capability, and distribution analysis.

    This tool provides a comprehensive Six Sigma process analysis workflow:
    - Process stability assessment using I-Chart
    - Process capability analysis (when specification limits provided)
    - Distribution analysis using probability plots

    All analyses are performed on the same selected measurement variable.
    """

    def __init__(self):
        """Initialize the Process Analysis tool."""
        super().__init__(
            name="process_analysis",
            description="Comprehensive process analysis combining stability, capability, and distribution assessment",
        )

    def get_input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for tool inputs."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Array of measurement values for comprehensive process analysis",
                    "minItems": 10,
                    "maxItems": 10000,
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the analysis",
                    "default": "Process Analysis",
                },
                "specification_limits": {
                    "type": "object",
                    "properties": {
                        "lsl": {"type": "number", "description": "Lower specification limit"},
                        "usl": {"type": "number", "description": "Upper specification limit"},
                        "target": {
                            "type": "number",
                            "description": "Target value (optional, defaults to midpoint of LSL/USL)",
                        },
                    },
                    "description": "Specification limits for capability analysis",
                    "anyOf": [
                        {"required": ["lsl", "usl"]},
                        {"required": ["lsl"]},
                        {"required": ["usl"]},
                    ],
                },
                "distribution": {
                    "type": "string",
                    "enum": ["normal", "lognormal", "exponential", "weibull"],
                    "description": "Distribution type for probability plot analysis",
                    "default": "normal",
                },
                "confidence_level": {
                    "type": "number",
                    "minimum": 0.8,
                    "maximum": 0.99,
                    "description": "Confidence level for statistical tests",
                    "default": 0.95,
                },
            },
            "required": ["data"],
        }

    def analyze(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Perform comprehensive process analysis.

        Args:
            arguments: Validated input parameters

        Returns:
            Combined analysis results from all three methods
        """
        # Extract validated data
        values = np.array(arguments["data"])
        title = arguments.get("title", "Process Analysis")
        spec_limits = arguments.get("specification_limits", {})
        distribution = arguments.get("distribution", "normal")
        confidence_level = arguments.get("confidence_level", 0.95)

        # Initialize results structure
        results = {
            "process_summary": {
                "sample_size": len(values),
                "measurement_range": {
                    "minimum": float(np.min(values)),
                    "maximum": float(np.max(values)),
                    "mean": float(np.mean(values)),
                    "std_dev": float(np.std(values, ddof=1)),
                },
            }
        }

        # 1. Stability Analysis (I-Chart)
        try:
            stability_results = calculate_i_chart(values, f"{title} - Stability Assessment")
            results["stability_analysis"] = {
                "type": "i_chart",
                "statistics": self.format_statistics(stability_results.get("statistics", {})),
                "out_of_control_indices": stability_results.get("out_of_control_indices", []),
                "control_status": "in_control"
                if len(stability_results.get("out_of_control_indices", [])) == 0
                else "out_of_control",
            }
        except Exception as e:
            self.logger.error(f"Stability analysis failed: {e}")
            results["stability_analysis"] = {
                "type": "i_chart",
                "error": str(e),
                "control_status": "unknown",
            }

        # 2. Capability Analysis (if specification limits provided)
        if spec_limits:
            try:
                capability_results = calculate_process_capability(
                    values, spec_limits.get("lsl"), spec_limits.get("usl"), spec_limits.get("target")
                )
                results["capability_analysis"] = {
                    "type": "capability",
                    "statistics": self.format_statistics(capability_results.get("statistics", {})),
                    "capability_indices": self.format_statistics(
                        capability_results.get("capability_indices", {})
                    ),
                    "defect_analysis": self.format_statistics(
                        capability_results.get("defect_analysis", {})
                    ),
                    "specification_limits": spec_limits,
                }
            except Exception as e:
                self.logger.error(f"Capability analysis failed: {e}")
                results["capability_analysis"] = {
                    "type": "capability",
                    "error": str(e),
                    "specification_limits": spec_limits,
                }
        else:
            results["capability_analysis"] = {
                "type": "capability",
                "note": "Specification limits not provided - capability analysis skipped",
                "recommendation": "Provide LSL and/or USL for capability assessment",
            }

        # 3. Distribution Analysis (Probability Plot)
        try:
            distribution_results = calculate_probability_plot(
                values, distribution, confidence_level
            )
            results["distribution_analysis"] = {
                "type": "probability_plot",
                "distribution": distribution,
                "statistics": self.format_statistics(distribution_results.get("statistics", {})),
                "goodness_of_fit": self.format_statistics(
                    distribution_results.get("goodness_of_fit", {})
                ),
                "theoretical_quantiles": distribution_results.get("theoretical_quantiles", []),
                "sorted_values": distribution_results.get("sorted_values", []),
            }
        except Exception as e:
            self.logger.error(f"Distribution analysis failed: {e}")
            results["distribution_analysis"] = {
                "type": "probability_plot",
                "distribution": distribution,
                "error": str(e),
            }

        # Create comprehensive interpretation
        results["interpretation"] = self.create_comprehensive_interpretation(results)

        # Add overall assessment
        results["overall_assessment"] = self.create_overall_assessment(results)

        return results

    def create_comprehensive_interpretation(self, results: dict[str, Any]) -> str:
        """Create comprehensive interpretation combining all analyses.

        Args:
            results: Complete analysis results

        Returns:
            Comprehensive interpretation string
        """
        interpretations = []

        # Process summary
        summary = results.get("process_summary", {})
        sample_size = summary.get("sample_size", 0)
        mean_val = summary.get("measurement_range", {}).get("mean", 0)

        interpretations.append(
            f"Process analysis of {sample_size} measurements with mean value {mean_val:.4f}."
        )

        # Stability assessment
        stability = results.get("stability_analysis", {})
        control_status = stability.get("control_status", "unknown")
        if control_status == "in_control":
            interpretations.append(
                "Process appears statistically stable with no out-of-control points detected."
            )
        elif control_status == "out_of_control":
            ooc_count = len(stability.get("out_of_control_indices", []))
            interpretations.append(
                f"Process shows instability with {ooc_count} out-of-control points requiring investigation."
            )

        # Capability assessment
        capability = results.get("capability_analysis", {})
        if "capability_indices" in capability:
            indices = capability["capability_indices"]
            cpk = indices.get("cpk", 0)
            if cpk >= 1.33:
                interpretations.append(
                    f"Process is capable (Cpk = {cpk:.3f}) and meets specification requirements."
                )
            elif cpk >= 1.0:
                interpretations.append(
                    f"Process has marginal capability (Cpk = {cpk:.3f}) and may need improvement."
                )
            else:
                interpretations.append(
                    f"Process is not capable (Cpk = {cpk:.3f}) and requires significant improvement."
                )
        elif "note" in capability:
            interpretations.append(
                "Capability analysis requires specification limits for assessment."
            )

        # Distribution assessment
        distribution = results.get("distribution_analysis", {})
        if "goodness_of_fit" in distribution:
            gof = distribution["goodness_of_fit"]
            dist_type = distribution.get("distribution", "normal")
            p_value = gof.get("p_value", 0)
            if p_value > 0.05:
                interpretations.append(
                    f"Data follows {dist_type} distribution (p-value = {p_value:.4f})."
                )
            else:
                interpretations.append(
                    f"Data does not follow {dist_type} distribution (p-value = {p_value:.4f})."
                )

        return " ".join(interpretations)

    def create_overall_assessment(self, results: dict[str, Any]) -> dict[str, Any]:
        """Create overall process assessment with recommendations.

        Args:
            results: Complete analysis results

        Returns:
            Overall assessment with status and recommendations
        """
        assessment = {
            "stability_status": "unknown",
            "capability_status": "unknown",
            "distribution_status": "unknown",
            "overall_status": "needs_review",
            "recommendations": [],
        }

        # Assess stability
        stability = results.get("stability_analysis", {})
        control_status = stability.get("control_status", "unknown")
        assessment["stability_status"] = control_status

        if control_status == "out_of_control":
            assessment["recommendations"].append(
                "Investigate and eliminate sources of special cause variation"
            )

        # Assess capability
        capability = results.get("capability_analysis", {})
        if "capability_indices" in capability:
            cpk = capability["capability_indices"].get("cpk", 0)
            if cpk >= 1.33:
                assessment["capability_status"] = "capable"
            elif cpk >= 1.0:
                assessment["capability_status"] = "marginal"
                assessment["recommendations"].append(
                    "Improve process capability through variation reduction"
                )
            else:
                assessment["capability_status"] = "not_capable"
                assessment["recommendations"].append(
                    "Significant process improvement required to meet specifications"
                )

        # Assess distribution
        distribution = results.get("distribution_analysis", {})
        if "goodness_of_fit" in distribution:
            p_value = distribution["goodness_of_fit"].get("p_value", 0)
            if p_value > 0.05:
                assessment["distribution_status"] = "fits_assumed"
            else:
                assessment["distribution_status"] = "does_not_fit"
                assessment["recommendations"].append(
                    "Consider alternative distribution or data transformation"
                )

        # Overall status determination
        if (
            assessment["stability_status"] == "in_control"
            and assessment["capability_status"] == "capable"
            and assessment["distribution_status"] == "fits_assumed"
        ):
            assessment["overall_status"] = "excellent"
        elif assessment["stability_status"] == "in_control" and assessment["capability_status"] in [
            "capable",
            "marginal",
        ]:
            assessment["overall_status"] = "good"
        elif assessment["stability_status"] == "in_control":
            assessment["overall_status"] = "stable_but_needs_improvement"
        else:
            assessment["overall_status"] = "needs_significant_improvement"

        # Add general recommendations if none specific
        if not assessment["recommendations"]:
            if assessment["overall_status"] == "excellent":
                assessment["recommendations"].append("Continue monitoring with control charts")
            else:
                assessment["recommendations"].append("Implement systematic improvement methodology")

        return assessment
