"""Enhanced Base Tool Class for Multi-Format MCP Tools.

This module provides the enhanced base class that all statistical tools inherit from,
enabling multi-format visualization responses compatible with different Claude interfaces.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union

from ..utils.visualization_response import (
    EnhancedVisualizationResponse, ChartData, create_chart_data
)
from ..utils.format_generators import MultiFormatGenerator


class EnhancedBaseTool(ABC):
    """Enhanced base class for statistical analysis tools with multi-format support.
    
    This class provides the foundation for all ESTIEM EDA statistical tools,
    enabling them to generate multiple visualization formats automatically.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.format_generator = MultiFormatGenerator()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for MCP registration."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for MCP listing."""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for tool input validation."""
        pass
    
    @abstractmethod
    def calculate_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the statistical calculations.
        
        Args:
            params: Validated input parameters
            
        Returns:
            Statistical analysis results
        """
        pass
    
    @abstractmethod
    def create_chart_data(self, results: Dict[str, Any], params: Dict[str, Any]) -> ChartData:
        """Create structured chart data from analysis results.
        
        Args:
            results: Statistical analysis results
            params: Original input parameters
            
        Returns:
            Structured chart data for visualization
        """
        pass
    
    def validate_input(self, params: Dict[str, Any]) -> None:
        """Validate input parameters against schema.
        
        Args:
            params: Input parameters to validate
            
        Raises:
            ValueError: If parameters don't match schema requirements
        """
        schema = self.get_input_schema()
        required_fields = schema.get("required", [])
        
        # Check required fields
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate data types and constraints
        properties = schema.get("properties", {})
        for field, constraints in properties.items():
            if field in params:
                value = params[field]
                self._validate_field(field, value, constraints)
    
    def _validate_field(self, field: str, value: Any, constraints: Dict[str, Any]) -> None:
        """Validate a single field against its constraints.
        
        Args:
            field: Field name
            value: Field value
            constraints: Field constraints from schema
            
        Raises:
            ValueError: If field value doesn't meet constraints
        """
        field_type = constraints.get("type")
        
        if field_type == "array":
            if not isinstance(value, list):
                raise ValueError(f"Field '{field}' must be an array")
            
            # Check array length constraints
            min_items = constraints.get("minItems")
            if min_items is not None and len(value) < min_items:
                raise ValueError(f"Field '{field}' must have at least {min_items} items")
            
            max_items = constraints.get("maxItems")
            if max_items is not None and len(value) > max_items:
                raise ValueError(f"Field '{field}' must have at most {max_items} items")
            
            # Check array item types
            items_schema = constraints.get("items", {})
            items_type = items_schema.get("type")
            if items_type:
                for i, item in enumerate(value):
                    if items_type == "number" and not isinstance(item, (int, float)):
                        raise ValueError(f"Field '{field}[{i}]' must be a number")
        
        elif field_type == "number":
            if not isinstance(value, (int, float)):
                raise ValueError(f"Field '{field}' must be a number")
            
            minimum = constraints.get("minimum")
            if minimum is not None and value < minimum:
                raise ValueError(f"Field '{field}' must be >= {minimum}")
            
            maximum = constraints.get("maximum")
            if maximum is not None and value > maximum:
                raise ValueError(f"Field '{field}' must be <= {maximum}")
        
        elif field_type == "string":
            if not isinstance(value, str):
                raise ValueError(f"Field '{field}' must be a string")
            
            max_length = constraints.get("maxLength")
            if max_length is not None and len(value) > max_length:
                raise ValueError(f"Field '{field}' must be <= {max_length} characters")
        
        elif field_type == "object":
            if not isinstance(value, dict):
                raise ValueError(f"Field '{field}' must be an object")
    
    def create_enhanced_response(self, analysis_results: Dict[str, Any], 
                               chart_data: ChartData,
                               client_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create enhanced multi-format response.
        
        Args:
            analysis_results: Statistical analysis results
            chart_data: Structured chart data
            client_info: Optional client information for optimization
            
        Returns:
            Enhanced response with multiple visualization formats
        """
        # Create enhanced visualization response
        enhanced_response = EnhancedVisualizationResponse(
            analysis_data=analysis_results,
            analysis_type=self.name
        )
        
        # Set chart data
        enhanced_response.set_chart_data(chart_data)
        
        # Detect client capabilities if provided
        if client_info:
            enhanced_response.detect_client_capabilities(client_info)
        
        # Generate all visualization formats
        try:
            generated_formats = self.format_generator.generate_all_formats(
                chart_data=chart_data,
                analysis_results=analysis_results
            )
            
            # Add each format to the response
            for format_type, format_content in generated_formats.items():
                enhanced_response.add_format(format_type, format_content)
            
            # Validate all formats
            if not enhanced_response.validate_formats():
                self.logger.warning("Format validation failed, but continuing with available formats")
            
            self.logger.info(f"Generated {len(generated_formats)} visualization formats")
            
        except Exception as e:
            self.logger.error(f"Failed to generate visualization formats: {e}")
            # Continue with basic response even if visualization generation fails
        
        return enhanced_response.to_dict()
    
    def get_text_visualization(self, chart_data: ChartData, analysis_results: Dict[str, Any]) -> str:
        """Generate text-based visualization for accessibility.
        
        Args:
            chart_data: Structured chart data
            analysis_results: Statistical analysis results
            
        Returns:
            Text representation of the visualization
        """
        try:
            text_format = self.format_generator.text_generator.generate(
                chart_data, analysis_results
            )
            return text_format.content
        except Exception as e:
            self.logger.error(f"Failed to generate text visualization: {e}")
            return f"Text visualization not available. Analysis type: {self.name}"
    
    def execute(self, params: Dict[str, Any], client_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the statistical analysis with enhanced response generation.
        
        Args:
            params: Input parameters for analysis
            client_info: Optional client information for response optimization
            
        Returns:
            Enhanced response with multiple visualization formats
        """
        try:
            # Validate input parameters
            self.validate_input(params)
            self.logger.debug(f"Input validation passed for {self.name}")
            
            # Perform statistical calculations
            analysis_results = self.calculate_statistics(params)
            self.logger.debug(f"Statistical calculations completed for {self.name}")
            
            # Create structured chart data
            chart_data = self.create_chart_data(analysis_results, params)
            self.logger.debug(f"Chart data created for {self.name}")
            
            # Generate enhanced multi-format response
            enhanced_response = self.create_enhanced_response(
                analysis_results, chart_data, client_info
            )
            
            self.logger.info(f"Enhanced response generated successfully for {self.name}")
            return enhanced_response
            
        except ValueError as e:
            self.logger.error(f"Validation error in {self.name}: {e}")
            return self._create_error_response("VALIDATION_ERROR", str(e))
        
        except Exception as e:
            self.logger.error(f"Execution error in {self.name}: {e}")
            return self._create_error_response("EXECUTION_ERROR", f"Tool execution failed: {str(e)}")
    
    def _create_error_response(self, error_code: str, error_message: str) -> Dict[str, Any]:
        """Create standardized error response.
        
        Args:
            error_code: Error classification code
            error_message: Human-readable error message
            
        Returns:
            Standardized error response
        """
        return {
            "success": False,
            "error": {
                "code": error_code,
                "message": error_message,
                "tool": self.name
            },
            "analysis_type": self.name,
            "fallback_visualization": {
                "type": "error_message",
                "content": f"Unable to perform {self.name} analysis: {error_message}"
            }
        }
    
    def _apply_estiem_styling(self, layout: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ESTIEM branding to chart layout.
        
        Args:
            layout: Base Plotly layout dictionary
            
        Returns:
            Layout with ESTIEM styling applied
        """
        # ESTIEM brand colors
        brand_colors = {
            "primary": "#1f4e79",
            "secondary": "#7ba7d1", 
            "accent": "#f8a978",
            "gray": "#666666"
        }
        
        # Apply consistent styling
        layout.update({
            "font": {
                "family": "Open Sans, sans-serif",
                "color": brand_colors["gray"]
            },
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "colorway": [
                brand_colors["primary"],
                brand_colors["secondary"],
                brand_colors["accent"],
                "#2E86AB", "#A23B72", "#F18F01", "#C73E1D"
            ]
        })
        
        # Style title
        if "title" in layout:
            if isinstance(layout["title"], str):
                layout["title"] = {
                    "text": layout["title"],
                    "font": {"size": 16, "color": brand_colors["primary"]},
                    "x": 0.5,
                    "xanchor": "center"
                }
            elif isinstance(layout["title"], dict):
                layout["title"]["font"] = {
                    "size": 16, 
                    "color": brand_colors["primary"]
                }
        
        # Style axes
        axis_style = {
            "showgrid": True,
            "gridcolor": "#E0E0E0",
            "linecolor": brand_colors["gray"],
            "tickcolor": brand_colors["gray"]
        }
        
        if "xaxis" in layout:
            layout["xaxis"].update(axis_style)
        if "yaxis" in layout:
            layout["yaxis"].update(axis_style)
        
        return layout
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default Plotly configuration for ESTIEM charts.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "responsive": True,
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "pan2d", "lasso2d", "select2d", "autoScale2d"
            ],
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"estiem_{self.name}_chart",
                "height": 600,
                "width": 900,
                "scale": 2
            }
        }


def create_estiem_chart_data(tool_name: str, plotly_data: List[Dict], 
                           plotly_layout: Dict[str, Any],
                           chart_type: Optional[str] = None) -> ChartData:
    """Convenience function to create ESTIEM-branded chart data.
    
    Args:
        tool_name: Name of the statistical tool
        plotly_data: Plotly data traces
        plotly_layout: Plotly layout configuration  
        chart_type: Optional chart type override
        
    Returns:
        ChartData with ESTIEM styling applied
    """
    # Default chart type mapping
    chart_type_map = {
        "i_chart": "control_chart",
        "process_capability": "histogram", 
        "anova_boxplot": "boxplot",
        "pareto_analysis": "pareto",
        "probability_plot": "probability_plot"
    }
    
    if chart_type is None:
        chart_type = chart_type_map.get(tool_name, tool_name)
    
    # ESTIEM styling configuration
    estiem_styling = {
        "color_scheme": "ESTIEM",
        "font_family": "Open Sans, sans-serif",
        "brand_colors": {
            "primary": "#1f4e79",
            "secondary": "#7ba7d1", 
            "accent": "#f8a978"
        },
        "theme": "plotly_white"
    }
    
    return create_chart_data(
        chart_type=chart_type,
        plotly_data=plotly_data,
        plotly_layout=plotly_layout,
        estiem_styling=estiem_styling
    )