"""Simplified Base MCP Tool Implementation.

This module provides a streamlined base class for MCP tools, removing the complexity
of multi-format visualization in favor of reliable single-format output.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

from .base import BaseMCPTool
# from ..browser.core_browser import generate_sample_data_browser


class SimplifiedMCPTool(BaseMCPTool):
    """Simplified base tool class for reliable MCP integration.
    
    This class removes the multi-format complexity and focuses on reliable
    statistical analysis with simple visualization integration.
    """
    
    def __init__(self, name: str, description: str):
        """Initialize the simplified MCP tool.
        
        Args:
            name: Tool name for MCP registration
            description: Tool description for MCP schema
        """
        super().__init__()
        self.name = name
        self.description = description
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis and return simple statistical results.
        
        This method handles validation, analysis execution, and returns
        the raw statistical results without complex visualization formatting.
        
        Args:
            arguments: Tool execution parameters
            
        Returns:
            Dictionary containing statistical analysis results
        """
        try:
            self.logger.debug(f"Executing {self.name} with arguments: {arguments}")
            
            # Validate input arguments
            validated_args = self.validate_arguments(arguments)
            
            # Execute the statistical analysis
            analysis_result = self.analyze(validated_args)
            
            # Add tool identification
            analysis_result["analysis_type"] = self.name
            analysis_result["success"] = True
            
            self.logger.debug(f"{self.name} analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error executing {self.name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": self.name
            }
    
    @abstractmethod
    def analyze(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the statistical analysis.
        
        This method should be implemented by subclasses to perform the actual
        statistical calculations and return the results.
        
        Args:
            arguments: Validated analysis parameters
            
        Returns:
            Dictionary containing analysis results including:
            - statistics: Dictionary of calculated statistics
            - interpretation: Human-readable interpretation
            - data_points: Original or processed data points
            - Any other analysis-specific results
        """
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean input arguments.
        
        This base implementation provides common validation patterns.
        Subclasses can override for specific validation requirements.
        
        Args:
            arguments: Raw input arguments
            
        Returns:
            Dictionary of validated arguments
            
        Raises:
            ValueError: If arguments are invalid
        """
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a dictionary")
        
        # Common validation patterns
        validated = {}
        
        # Validate data arrays
        if "data" in arguments:
            data = arguments["data"]
            if not isinstance(data, list):
                raise ValueError("Data must be a list")
            
            # Convert to numeric and filter out invalid values
            numeric_data = []
            for item in data:
                try:
                    numeric_data.append(float(item))
                except (ValueError, TypeError):
                    continue
            
            if not numeric_data:
                raise ValueError("No valid numeric data found")
            
            validated["data"] = numeric_data
        
        # Validate title
        if "title" in arguments:
            validated["title"] = str(arguments["title"])
        
        # Validate numeric parameters
        numeric_params = ["lsl", "usl", "target", "alpha", "confidence_level"]
        for param in numeric_params:
            if param in arguments:
                try:
                    validated[param] = float(arguments[param])
                except (ValueError, TypeError):
                    raise ValueError(f"Parameter '{param}' must be numeric")
        
        # Validate string parameters
        string_params = ["distribution", "value_column", "group_column"]
        for param in string_params:
            if param in arguments:
                validated[param] = str(arguments[param])
        
        # Copy any remaining parameters
        for key, value in arguments.items():
            if key not in validated:
                validated[key] = value
        
        return validated
    
    def format_statistics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Format statistics for consistent output.
        
        Args:
            stats: Raw statistics dictionary
            
        Returns:
            Formatted statistics with consistent precision
        """
        formatted = {}
        
        for key, value in stats.items():
            if isinstance(value, float):
                # Round to 4 decimal places for display
                formatted[key] = round(value, 4)
            elif isinstance(value, int):
                formatted[key] = value
            elif isinstance(value, bool):
                # Convert booleans to strings for JSON compatibility
                formatted[key] = value
            elif isinstance(value, list):
                # Format lists of numbers
                try:
                    formatted[key] = [round(float(x), 4) if isinstance(x, (int, float)) else x for x in value]
                except (ValueError, TypeError):
                    formatted[key] = value
            elif isinstance(value, dict):
                # Recursively format nested dictionaries
                formatted[key] = self.format_statistics(value)
            else:
                formatted[key] = value
        
        return formatted
    
    def create_interpretation(self, stats: Dict[str, Any], **kwargs) -> str:
        """Create a basic interpretation of the results.
        
        This base implementation provides a generic interpretation.
        Subclasses should override for analysis-specific interpretations.
        
        Args:
            stats: Analysis statistics
            **kwargs: Additional context for interpretation
            
        Returns:
            Human-readable interpretation string
        """
        analysis_name = self.name.replace('_', ' ').title()
        return f"{analysis_name} completed successfully with {len(stats)} statistical measures calculated."
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this tool.
        
        This base implementation provides a generic schema.
        Subclasses should override for tool-specific schemas.
        
        Returns:
            JSON schema dictionary for tool input validation
        """
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Array of numeric data points for analysis",
                    "minItems": 3
                },
                "title": {
                    "type": "string", 
                    "description": "Optional title for the analysis",
                    "default": f"{self.name.replace('_', ' ').title()} Analysis"
                }
            },
            "required": ["data"],
            "additionalProperties": True
        }
    
    @staticmethod
    def generate_sample_data(sample_type: str = 'manufacturing') -> Dict[str, Any]:
        """Generate sample data using unified browser-compatible generator.
        
        Args:
            sample_type: Type of sample data ('manufacturing', 'quality', 'process')
            
        Returns:
            Dictionary with sample data, headers, and filename
        """
        import random
        import numpy as np
        
        if sample_type == 'manufacturing':
            data = np.random.normal(100, 5, 30).tolist()
            return {
                'data': data,
                'headers': ['value'],
                'filename': 'sample_manufacturing.csv'
            }
        elif sample_type == 'quality':
            data = np.random.normal(50, 2, 25).tolist()
            return {
                'data': data,
                'headers': ['measurement'],
                'filename': 'sample_quality.csv'
            }
        else:  # process
            data = np.random.normal(75, 3, 35).tolist()
            return {
                'data': data,
                'headers': ['process_value'],
                'filename': 'sample_process.csv'
            }