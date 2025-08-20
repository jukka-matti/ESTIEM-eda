"""Base class for all statistical tools in ESTIEM EDA toolkit."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseTool(ABC):
    """Base class for all statistical tools.
    
    All exploratory data analysis tools must inherit from this class and implement
    the required abstract methods for MCP protocol compliance.
    """
    
    def __init__(self):
        """Initialize the tool with basic attributes."""
        self.name = ""
        self.description = ""
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for tool inputs.
        
        Returns:
            Dict containing the JSON schema that defines the expected
            input parameters for this tool.
        """
        pass
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool and return results.
        
        Args:
            params: Dictionary containing the input parameters for the tool.
            
        Returns:
            Dictionary containing the analysis results, including statistics,
            interpretations, and visualizations.
            
        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        pass
    
    def validate_inputs(self, params: Dict, required: List[str]) -> None:
        """Validate required parameters exist.
        
        Args:
            params: Input parameters dictionary to validate.
            required: List of required parameter names.
            
        Raises:
            ValueError: If any required parameters are missing.
        """
        missing = [p for p in required if p not in params]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")
    
    def validate_data_array(self, data: List[float], min_length: int = 1) -> None:
        """Validate data array input.
        
        Args:
            data: List of numerical data points.
            min_length: Minimum required length for the data array.
            
        Raises:
            ValueError: If data is invalid (empty, too short, contains non-numeric values).
        """
        if not data:
            raise ValueError("Data array cannot be empty")
        
        if len(data) < min_length:
            raise ValueError(f"Data array must contain at least {min_length} points")
        
        try:
            # Attempt to convert to float to validate numeric data
            [float(x) for x in data]
        except (ValueError, TypeError):
            raise ValueError("Data array must contain only numeric values")


# Alias for MCP compatibility
BaseMCPTool = BaseTool