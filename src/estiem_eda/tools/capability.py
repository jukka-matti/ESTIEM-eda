"""Process Capability Analysis (Cp and Cpk) for Six Sigma quality assessment.

This module calculates process capability indices to assess whether a process
can consistently produce products within specification limits.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, Optional
from .base import BaseTool

try:
    from ..utils.visualization import create_capability_histogram
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class CapabilityTool(BaseTool):
    """Process capability analysis tool for Cp and Cpk calculations.
    
    Analyzes process capability using short-term variation (Cp, Cpk only).
    Does not include long-term performance indices (Pp, Ppk) per requirements.
    """
    
    def __init__(self):
        """Initialize the Process Capability tool."""
        self.name = "process_capability"
        self.description = "Calculate process capability indices Cp and Cpk with defect rate estimation"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for capability analysis inputs.
        
        Returns:
            JSON schema defining required specification limits and data.
        """
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Process measurements for capability analysis",
                    "minItems": 30
                },
                "lsl": {
                    "type": "number",
                    "description": "Lower Specification Limit"
                },
                "usl": {
                    "type": "number",
                    "description": "Upper Specification Limit"
                },
                "target": {
                    "type": "number",
                    "description": "Target value (nominal). If not provided, uses midpoint of LSL and USL"
                },
                "confidence_level": {
                    "type": "number",
                    "default": 0.95,
                    "minimum": 0.80,
                    "maximum": 0.99,
                    "description": "Confidence level for capability indices (0.95 = 95%)"
                }
            },
            "required": ["data", "lsl", "usl"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate process capability indices and performance metrics.
        
        Args:
            params: Dictionary with 'data', 'lsl', 'usl', and optional parameters.
            
        Returns:
            Dictionary containing capability indices, performance metrics, and interpretation.
            
        Raises:
            ValueError: If specification limits are invalid or data is insufficient.
        """
        # Validate inputs
        self.validate_inputs(params, ["data", "lsl", "usl"])
        
        data_list = params["data"]
        self.validate_data_array(data_list, min_length=30)
        
        data = np.array(data_list, dtype=float)
        lsl = float(params["lsl"])
        usl = float(params["usl"])
        target = params.get("target")
        confidence_level = params.get("confidence_level", 0.95)
        
        # Validate specification limits
        if usl <= lsl:
            raise ValueError("Upper Specification Limit must be greater than Lower Specification Limit")
        
        # Set target if not provided
        if target is None:
            target = (lsl + usl) / 2
        else:
            target = float(target)
            if not (lsl <= target <= usl):
                raise ValueError("Target must be between LSL and USL")
        
        # Calculate basic statistics
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)  # Sample standard deviation
        
        # Capability indices
        cp = (usl - lsl) / (6 * std)
        cpu = (usl - mean) / (3 * std)
        cpl = (mean - lsl) / (3 * std)
        cpk = min(cpu, cpl)
        
        # Centering metrics
        ca = (mean - target) / ((usl - lsl) / 2)  # Capability accuracy
        centering_index = abs(mean - target) / (usl - lsl)
        
        # Defect rate estimation (assuming normal distribution)
        z_upper = (usl - mean) / std
        z_lower = (mean - lsl) / std
        
        prob_above_usl = 1 - stats.norm.cdf(z_upper)
        prob_below_lsl = stats.norm.cdf(z_lower)
        total_defect_rate = prob_above_usl + prob_below_lsl
        
        # Convert to PPM (parts per million)
        ppm_above = prob_above_usl * 1e6
        ppm_below = prob_below_lsl * 1e6
        ppm_total = total_defect_rate * 1e6
        
        # Sigma level calculation
        sigma_level = self._calculate_sigma_level(ppm_total)
        
        # Confidence intervals (approximate)
        confidence_intervals = self._calculate_confidence_intervals(
            data, cp, cpk, confidence_level
        )
        
        # Process assessment
        assessment = self._assess_capability(cp, cpk, ca, centering_index)
        
        # Specification analysis
        spec_analysis = self._analyze_specifications(data, lsl, usl, target)
        
        # Create visualization
        chart_html = None
        if VISUALIZATION_AVAILABLE:
            try:
                chart_html = create_capability_histogram(
                    data=data,
                    lsl=lsl,
                    usl=usl,
                    target=target,
                    mean=mean,
                    std=std,
                    title="Process Capability Analysis"
                )
            except Exception as e:
                chart_html = f"Visualization error: {str(e)}"
        else:
            chart_html = "Visualization not available - install plotly>=5.0.0"
        
        return {
            "capability_indices": {
                "cp": float(cp),
                "cpk": float(cpk),
                "cpu": float(cpu),
                "cpl": float(cpl),
                "ca": float(ca)
            },
            "process_statistics": {
                "sample_size": n,
                "mean": float(mean),
                "standard_deviation": float(std),
                "target": target,
                "centering_index": float(centering_index)
            },
            "specification_limits": {
                "lsl": lsl,
                "usl": usl,
                "specification_width": float(usl - lsl),
                "process_spread": float(6 * std),
                "margin_lower": float(mean - lsl),
                "margin_upper": float(usl - mean)
            },
            "defect_analysis": {
                "total_defect_rate": float(total_defect_rate),
                "ppm_below_lsl": float(ppm_below),
                "ppm_above_usl": float(ppm_above),
                "ppm_total": float(ppm_total),
                "yield_percentage": float((1 - total_defect_rate) * 100),
                "sigma_level": float(sigma_level)
            },
            "confidence_intervals": confidence_intervals,
            "process_assessment": assessment,
            "specification_analysis": spec_analysis,
            "interpretation": self._generate_interpretation(cp, cpk, ppm_total, assessment),
            "chart_html": chart_html
        }
    
    def _calculate_sigma_level(self, ppm: float) -> float:
        """Convert PPM defects to approximate sigma level.
        
        Args:
            ppm: Parts per million defects.
            
        Returns:
            Approximate sigma level.
        """
        if ppm <= 0.001:
            return 6.5  # Theoretical maximum
        elif ppm <= 3.4:
            return 6.0
        elif ppm <= 23:
            return 5.5
        elif ppm <= 233:
            return 5.0
        elif ppm <= 1350:
            return 4.5
        elif ppm <= 6210:
            return 4.0
        elif ppm <= 22750:
            return 3.5
        elif ppm <= 66807:
            return 3.0
        elif ppm <= 158655:
            return 2.5
        else:
            return 2.0
    
    def _calculate_confidence_intervals(self, data: np.ndarray, cp: float, 
                                      cpk: float, confidence: float) -> Dict[str, Any]:
        """Calculate approximate confidence intervals for capability indices.
        
        Args:
            data: Process data.
            cp: Cp value.
            cpk: Cpk value.
            confidence: Confidence level (e.g., 0.95 for 95%).
            
        Returns:
            Dictionary with confidence intervals.
        """
        n = len(data)
        alpha = 1 - confidence
        
        # Chi-square critical values for Cp
        chi2_lower = stats.chi2.ppf(alpha/2, n-1)
        chi2_upper = stats.chi2.ppf(1-alpha/2, n-1)
        
        # Approximate confidence intervals
        cp_lower = cp * np.sqrt((n-1)/chi2_upper)
        cp_upper = cp * np.sqrt((n-1)/chi2_lower)
        
        # Cpk intervals (approximate)
        cpk_margin = 1.96 * np.sqrt(1/(9*n) + cpk**2/(2*(n-1)))  # Approximate for 95%
        cpk_lower = max(0, cpk - cpk_margin)
        cpk_upper = cpk + cpk_margin
        
        return {
            "confidence_level": confidence,
            "cp_interval": [float(cp_lower), float(cp_upper)],
            "cpk_interval": [float(cpk_lower), float(cpk_upper)]
        }
    
    def _assess_capability(self, cp: float, cpk: float, ca: float, 
                          centering: float) -> Dict[str, Any]:
        """Assess overall process capability and provide recommendations.
        
        Args:
            cp: Process capability index.
            cpk: Process capability index (accounts for centering).
            ca: Capability accuracy index.
            centering: Centering index.
            
        Returns:
            Process assessment with recommendations.
        """
        # Capability classification
        if cpk >= 1.67:
            capability_class = "Excellent"
            capability_color = "green"
        elif cpk >= 1.33:
            capability_class = "Capable"
            capability_color = "green"
        elif cpk >= 1.00:
            capability_class = "Marginally Capable"
            capability_color = "yellow"
        else:
            capability_class = "Not Capable"
            capability_color = "red"
        
        # Centering assessment
        if abs(ca) <= 0.1:
            centering_status = "Well Centered"
        elif abs(ca) <= 0.2:
            centering_status = "Moderately Off-Center"
        else:
            centering_status = "Poorly Centered"
        
        # Primary improvement opportunities
        improvements = []
        if cp >= 1.33 and cpk < 1.33:
            improvements.append("Improve process centering (reduce mean shift)")
        if cp < 1.33:
            improvements.append("Reduce process variation")
        if abs(ca) > 0.1:
            improvements.append("Center process closer to target")
        
        return {
            "capability_class": capability_class,
            "capability_color": capability_color,
            "centering_status": centering_status,
            "improvement_opportunities": improvements,
            "meets_six_sigma": cpk >= 1.5,
            "ready_for_production": cpk >= 1.33
        }
    
    def _analyze_specifications(self, data: np.ndarray, lsl: float, 
                              usl: float, target: float) -> Dict[str, Any]:
        """Analyze how well data fits within specifications.
        
        Args:
            data: Process measurements.
            lsl: Lower specification limit.
            usl: Upper specification limit.
            target: Target value.
            
        Returns:
            Specification analysis results.
        """
        # Count defects in actual data
        below_lsl = np.sum(data < lsl)
        above_usl = np.sum(data > usl)
        within_spec = len(data) - below_lsl - above_usl
        
        # Data distribution relative to specs
        data_min = np.min(data)
        data_max = np.max(data)
        data_mean = np.mean(data)
        
        return {
            "actual_defects": {
                "below_lsl": int(below_lsl),
                "above_usl": int(above_usl),
                "within_spec": int(within_spec),
                "total_samples": len(data)
            },
            "actual_yield": float(within_spec / len(data) * 100),
            "data_vs_specs": {
                "data_min": float(data_min),
                "data_max": float(data_max),
                "data_range": float(data_max - data_min),
                "spec_range": float(usl - lsl),
                "utilization": float((data_max - data_min) / (usl - lsl) * 100)
            },
            "centering_metrics": {
                "mean_vs_target": float(data_mean - target),
                "mean_position": float((data_mean - lsl) / (usl - lsl) * 100)
            }
        }
    
    def _generate_interpretation(self, cp: float, cpk: float, ppm: float, 
                               assessment: Dict[str, Any]) -> str:
        """Generate comprehensive interpretation of capability analysis.
        
        Args:
            cp: Process capability.
            cpk: Process capability with centering.
            ppm: Parts per million defects.
            assessment: Process assessment results.
            
        Returns:
            Human-readable interpretation.
        """
        lines = []
        
        # Header with overall assessment
        status_emoji = {"Excellent": "🎯", "Capable": "✅", 
                       "Marginally Capable": "⚠️", "Not Capable": "❌"}
        emoji = status_emoji.get(assessment["capability_class"], "📊")
        
        lines.append(f"{emoji} PROCESS CAPABILITY: {assessment['capability_class'].upper()}")
        lines.append(f"Cpk = {cpk:.3f} | Expected defects: {ppm:.0f} PPM")
        
        # Detailed analysis
        lines.append("\n📊 CAPABILITY ANALYSIS:")
        
        if cpk >= 1.33:
            lines.append(f"✅ Process is capable (Cpk ≥ 1.33)")
            if assessment["meets_six_sigma"]:
                lines.append("🎯 Meets Six Sigma standards (Cpk ≥ 1.5)")
        elif cpk >= 1.0:
            lines.append(f"⚠️  Process is marginally capable (1.0 ≤ Cpk < 1.33)")
            lines.append("   Additional process improvements recommended")
        else:
            lines.append(f"❌ Process is not capable (Cpk < 1.0)")
            lines.append("   Significant improvements required before production")
        
        # Cp vs Cpk analysis
        if cp >= 1.33 and cpk < 1.33:
            lines.append(f"\n🎯 CENTERING ISSUE DETECTED:")
            lines.append(f"   Cp ({cp:.3f}) > Cpk ({cpk:.3f}) indicates poor centering")
            lines.append(f"   Process variation is acceptable, but mean is off-target")
        elif cp < 1.33:
            lines.append(f"\n📈 VARIATION REDUCTION NEEDED:")
            lines.append(f"   Both Cp ({cp:.3f}) and Cpk ({cpk:.3f}) below 1.33")
            lines.append(f"   Primary focus should be reducing process variation")
        
        # Recommendations
        lines.append(f"\n📋 RECOMMENDATIONS:")
        
        if not assessment["improvement_opportunities"]:
            lines.append("1. Maintain current process controls")
            lines.append("2. Continue routine monitoring")
            lines.append("3. Document best practices")
        else:
            for i, improvement in enumerate(assessment["improvement_opportunities"], 1):
                lines.append(f"{i}. {improvement}")
        
        # Six Sigma context
        if ppm <= 3.4:
            lines.append(f"\n🏆 SIX SIGMA PERFORMANCE: World-class quality level")
        elif ppm <= 233:
            lines.append(f"\n🌟 FIVE SIGMA PERFORMANCE: Excellent quality level")
        elif ppm <= 6210:
            lines.append(f"\n⭐ FOUR SIGMA PERFORMANCE: Good quality level")
        else:
            lines.append(f"\n📈 IMPROVEMENT OPPORTUNITY: Focus on systematic variation reduction")
        
        return "\n".join(lines)