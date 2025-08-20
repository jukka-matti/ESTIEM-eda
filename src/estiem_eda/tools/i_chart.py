"""Individual Control Chart (I-Chart) implementation for process monitoring.

This module provides statistical process control using Individual control charts,
including control limits calculation, out-of-control point detection, and runs analysis.
"""

import numpy as np
from typing import Dict, Any, List
from .base import BaseTool

try:
    from ..utils.visualization import create_control_chart
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class IChartTool(BaseTool):
    """Individual Control Chart for process monitoring.
    
    Creates control charts for individual measurements with:
    - Center line (process mean)
    - Upper and Lower Control Limits (UCL, LCL)
    - Out-of-control point detection
    - Runs test for pattern detection
    """
    
    def __init__(self):
        """Initialize the I-Chart tool."""
        self.name = "i_chart"
        self.description = "Create Individual control chart for process monitoring with control limits and pattern detection"
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for I-Chart inputs.
        
        Returns:
            JSON schema defining required and optional parameters.
        """
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Array of individual measurements for analysis",
                    "minItems": 2
                },
                "sigma_limits": {
                    "type": "number",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 6,
                    "description": "Number of sigma for control limits (typically 3)"
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the control chart"
                }
            },
            "required": ["data"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate control chart statistics and create analysis.
        
        Args:
            params: Dictionary containing 'data' array and optional parameters.
            
        Returns:
            Dictionary containing statistics, analysis results, and interpretation.
            
        Raises:
            ValueError: If input data is invalid or insufficient.
        """
        # Validate inputs
        self.validate_inputs(params, ["data"])
        
        data_list = params["data"]
        self.validate_data_array(data_list, min_length=2)
        
        data = np.array(data_list, dtype=float)
        sigma_limits = params.get("sigma_limits", 3)
        title = params.get("title", "Individual Control Chart")
        
        # Calculate basic statistics
        mean = np.mean(data)
        n_points = len(data)
        
        # Calculate moving range for sigma estimation
        moving_range = np.abs(np.diff(data))
        avg_moving_range = np.mean(moving_range)
        
        # Sigma estimation using d2 constant for n=2 (consecutive pairs)
        d2 = 1.128  # constant for subgroup size n=2
        sigma_est = avg_moving_range / d2
        
        # Control limits
        ucl = mean + sigma_limits * sigma_est
        lcl = mean - sigma_limits * sigma_est
        
        # Detect out-of-control points
        ooc_indices = np.where((data > ucl) | (data < lcl))[0].tolist()
        ooc_values = data[ooc_indices].tolist() if ooc_indices else []
        
        # Check for runs (Western Electric Rule 1: 7+ consecutive points on one side)
        runs_analysis = self._detect_runs(data, mean)
        
        # Additional pattern detection
        patterns = self._detect_patterns(data, mean, sigma_est)
        
        # Calculate process performance metrics
        performance = self._calculate_performance(data, ucl, lcl, mean, sigma_est)
        
        # Generate interpretation
        interpretation = self._interpret_results(ooc_indices, runs_analysis, patterns, performance)
        
        # Create visualization
        chart_html = None
        if VISUALIZATION_AVAILABLE:
            try:
                chart_html = create_control_chart(
                    data=data,
                    center_line=mean,
                    ucl=ucl,
                    lcl=lcl,
                    ooc_indices=ooc_indices,
                    title=title
                )
            except Exception as e:
                chart_html = f"Visualization error: {str(e)}"
        else:
            chart_html = "Visualization not available - install plotly>=5.0.0"
        
        return {
            "statistics": {
                "sample_size": n_points,
                "mean": float(mean),
                "ucl": float(ucl),
                "lcl": float(lcl),
                "sigma_estimate": float(sigma_est),
                "moving_range_average": float(avg_moving_range),
                "sigma_limits": sigma_limits
            },
            "control_analysis": {
                "out_of_control_points": len(ooc_indices),
                "ooc_indices": ooc_indices,
                "ooc_values": ooc_values,
                "percentage_ooc": round(len(ooc_indices) / n_points * 100, 2)
            },
            "pattern_analysis": {
                "runs_test": runs_analysis,
                "other_patterns": patterns
            },
            "performance_metrics": performance,
            "interpretation": interpretation,
            "chart_data": {
                "title": title,
                "data_points": data.tolist(),
                "center_line": float(mean),
                "upper_control_limit": float(ucl),
                "lower_control_limit": float(lcl),
                "sample_numbers": list(range(1, n_points + 1))
            },
            "chart_html": chart_html
        }
    
    def _detect_runs(self, data: np.ndarray, center: float) -> Dict[str, Any]:
        """Detect runs above or below center line.
        
        Western Electric Rule: 7+ consecutive points on same side of center line.
        
        Args:
            data: Array of measurements.
            center: Center line value (mean).
            
        Returns:
            Dictionary with runs analysis results.
        """
        above = data > center
        
        # Find longest consecutive run
        max_run_above = 0
        max_run_below = 0
        current_run = 1
        
        for i in range(1, len(above)):
            if above[i] == above[i-1]:
                current_run += 1
            else:
                if above[i-1]:
                    max_run_above = max(max_run_above, current_run)
                else:
                    max_run_below = max(max_run_below, current_run)
                current_run = 1
        
        # Check final run
        if above[-1]:
            max_run_above = max(max_run_above, current_run)
        else:
            max_run_below = max(max_run_below, current_run)
        
        max_run = max(max_run_above, max_run_below)
        has_violation = max_run >= 7
        
        return {
            "max_consecutive_above": max_run_above,
            "max_consecutive_below": max_run_below,
            "max_consecutive_total": max_run,
            "runs_violation": has_violation,
            "threshold": 7,
            "rule": "Western Electric Rule: 7+ consecutive points on one side"
        }
    
    def _detect_patterns(self, data: np.ndarray, mean: float, sigma: float) -> List[Dict[str, Any]]:
        """Detect additional control chart patterns.
        
        Args:
            data: Array of measurements.
            mean: Process mean.
            sigma: Process sigma estimate.
            
        Returns:
            List of detected patterns.
        """
        patterns = []
        
        # Pattern 1: 2 of 3 consecutive points beyond 2-sigma
        two_sigma_upper = mean + 2 * sigma
        two_sigma_lower = mean - 2 * sigma
        
        beyond_2sigma = (data > two_sigma_upper) | (data < two_sigma_lower)
        
        for i in range(len(data) - 2):
            if np.sum(beyond_2sigma[i:i+3]) >= 2:
                patterns.append({
                    "type": "2_of_3_beyond_2sigma",
                    "description": "2 of 3 consecutive points beyond 2-sigma limits",
                    "start_index": i,
                    "severity": "moderate"
                })
        
        # Pattern 2: Increasing or decreasing trend (6+ consecutive points)
        trends = []
        increasing = 0
        decreasing = 0
        
        for i in range(1, len(data)):
            if data[i] > data[i-1]:
                increasing += 1
                decreasing = 0
            elif data[i] < data[i-1]:
                decreasing += 1
                increasing = 0
            else:
                increasing = 0
                decreasing = 0
            
            if increasing >= 6:
                patterns.append({
                    "type": "increasing_trend",
                    "description": f"6+ consecutive increasing points ending at index {i}",
                    "end_index": i,
                    "severity": "high"
                })
            elif decreasing >= 6:
                patterns.append({
                    "type": "decreasing_trend", 
                    "description": f"6+ consecutive decreasing points ending at index {i}",
                    "end_index": i,
                    "severity": "high"
                })
        
        return patterns
    
    def _calculate_performance(self, data: np.ndarray, ucl: float, lcl: float, 
                             mean: float, sigma: float) -> Dict[str, Any]:
        """Calculate process performance metrics.
        
        Args:
            data: Process measurements.
            ucl: Upper control limit.
            lcl: Lower control limit.
            mean: Process mean.
            sigma: Process sigma estimate.
            
        Returns:
            Dictionary with performance metrics.
        """
        # Process spread
        process_spread = 6 * sigma  # 99.73% of data should fall within ±3σ
        control_width = ucl - lcl
        
        # Actual data spread
        data_range = np.max(data) - np.min(data)
        
        # Stability metrics
        within_limits = np.sum((data >= lcl) & (data <= ucl))
        stability_percentage = (within_limits / len(data)) * 100
        
        return {
            "process_spread_6sigma": float(process_spread),
            "control_limit_width": float(control_width),
            "actual_data_range": float(data_range),
            "stability_percentage": float(stability_percentage),
            "points_within_limits": int(within_limits),
            "total_points": len(data)
        }
    
    def _interpret_results(self, ooc_indices: List[int], runs: Dict, 
                          patterns: List[Dict], performance: Dict) -> str:
        """Generate comprehensive interpretation of control chart results.
        
        Args:
            ooc_indices: Out-of-control point indices.
            runs: Runs analysis results.
            patterns: Additional patterns detected.
            performance: Process performance metrics.
            
        Returns:
            Human-readable interpretation string.
        """
        interpretation_parts = []
        
        # Overall process state
        if not ooc_indices and not runs["runs_violation"] and not patterns:
            interpretation_parts.append(
                "✅ PROCESS IS IN STATISTICAL CONTROL: No special cause variation detected."
            )
            interpretation_parts.append(
                f"Process stability: {performance['stability_percentage']:.1f}% of points within control limits."
            )
        else:
            interpretation_parts.append(
                "⚠️  PROCESS IS OUT OF STATISTICAL CONTROL: Special cause variation detected."
            )
        
        # Specific issues
        issues = []
        
        if ooc_indices:
            issues.append(f"{len(ooc_indices)} points outside control limits")
        
        if runs["runs_violation"]:
            issues.append(f"Run of {runs['max_consecutive_total']} consecutive points on one side")
        
        if patterns:
            for pattern in patterns:
                issues.append(pattern["description"])
        
        if issues:
            interpretation_parts.append(f"Issues identified: {'; '.join(issues)}")
        
        # Recommendations
        if ooc_indices or runs["runs_violation"] or patterns:
            interpretation_parts.append(
                "\n📋 RECOMMENDED ACTIONS:"
            )
            interpretation_parts.append(
                "1. Investigate special causes for out-of-control signals"
            )
            interpretation_parts.append(
                "2. Review process conditions during flagged time periods"
            )
            interpretation_parts.append(
                "3. Implement corrective actions to eliminate special causes"
            )
            interpretation_parts.append(
                "4. Continue monitoring with updated control limits if process changes"
            )
        else:
            interpretation_parts.append(
                "\n📋 RECOMMENDED ACTIONS:"
            )
            interpretation_parts.append(
                "1. Continue routine monitoring"
            )
            interpretation_parts.append(
                "2. Focus on common cause variation reduction if improvement needed"
            )
        
        return "\n".join(interpretation_parts)