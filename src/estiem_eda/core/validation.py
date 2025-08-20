"""
Data validation functions for ESTIEM EDA statistical analysis
Pure Python validation without pandas dependency
"""

import numpy as np
from typing import List, Dict, Any, Union, Tuple


def validate_numeric_data(data: Union[List, np.ndarray], min_points: int = 3) -> np.ndarray:
    """
    Validate and clean numeric data
    
    Args:
        data: Input data (list, array, or nested structure)
        min_points: Minimum number of valid points required
        
    Returns:
        numpy array of clean numeric values
        
    Raises:
        ValueError: If insufficient valid data points
    """
    if isinstance(data, dict):
        # Handle dict with 'data' key or similar
        if 'data' in data:
            data = data['data']
        else:
            # Try to find first numeric list/array value
            for value in data.values():
                if isinstance(value, (list, np.ndarray)):
                    data = value
                    break
            else:
                raise ValueError("No suitable numeric data found in dictionary")
    
    # Convert to flat list if nested
    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], dict):
            # List of dictionaries - find numeric column
            numeric_col = None
            for key in data[0].keys():
                try:
                    float(data[0][key])
                    numeric_col = key
                    break
                except (ValueError, TypeError):
                    continue
            
            if numeric_col is None:
                raise ValueError("No numeric columns found in data")
            
            # Extract values from dictionaries
            values = []
            for row in data:
                try:
                    val = float(row[numeric_col])
                    if not (np.isnan(val) or np.isinf(val)):
                        values.append(val)
                except (ValueError, TypeError, KeyError):
                    continue
            data = values
    
    # Convert to numpy array and clean
    try:
        values = np.array(data, dtype=float)
        # Remove NaN and infinite values
        values = values[np.isfinite(values)]
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot convert data to numeric array: {e}")
    
    if len(values) < min_points:
        raise ValueError(f"Need at least {min_points} valid data points, got {len(values)}")
    
    return values


def validate_groups_data(data: Dict[str, List]) -> Dict[str, np.ndarray]:
    """
    Validate group data for ANOVA analysis
    
    Args:
        data: Dictionary with group names as keys, data lists as values
        
    Returns:
        Dictionary with group names as keys, numpy arrays as values
        
    Raises:
        ValueError: If insufficient groups or data points
    """
    if not isinstance(data, dict):
        raise ValueError("Groups data must be a dictionary")
    
    if len(data) < 2:
        raise ValueError("Need at least 2 groups for ANOVA analysis")
    
    validated_groups = {}
    
    for group_name, group_data in data.items():
        try:
            # Validate each group's data
            values = validate_numeric_data(group_data, min_points=2)
            validated_groups[str(group_name)] = values
        except ValueError as e:
            raise ValueError(f"Invalid data for group '{group_name}': {e}")
    
    if len(validated_groups) < 2:
        raise ValueError("Need at least 2 valid groups for ANOVA analysis")
    
    return validated_groups


def validate_pareto_data(data: Union[Dict[str, Union[int, float]], List[Dict]]) -> Dict[str, float]:
    """
    Validate Pareto analysis data
    
    Args:
        data: Dictionary of categories and counts, or list of records
        
    Returns:
        Dictionary with string keys and float values
        
    Raises:
        ValueError: If data format is invalid
    """
    if isinstance(data, list):
        # Convert list of records to category counts
        if not data:
            raise ValueError("Empty data provided")
        
        if isinstance(data[0], dict):
            # Find category and value columns
            first_row = data[0]
            cat_col = None
            val_col = None
            
            for key, value in first_row.items():
                if isinstance(value, str) and cat_col is None:
                    cat_col = key
                elif isinstance(value, (int, float)) and val_col is None:
                    val_col = key
            
            if cat_col is None:
                raise ValueError("No categorical column found")
            
            if val_col is None:
                # Count occurrences
                categories = {}
                for row in data:
                    cat = str(row[cat_col])
                    categories[cat] = categories.get(cat, 0) + 1
                data = categories
            else:
                # Sum values by category
                categories = {}
                for row in data:
                    cat = str(row[cat_col])
                    val = float(row[val_col])
                    categories[cat] = categories.get(cat, 0) + val
                data = categories
    
    if not isinstance(data, dict):
        raise ValueError("Pareto data must be dictionary or list of records")
    
    if not data:
        raise ValueError("Empty data provided")
    
    # Validate and convert values
    validated_data = {}
    for category, value in data.items():
        try:
            val = float(value)
            if val < 0:
                raise ValueError(f"Negative value for category '{category}': {val}")
            validated_data[str(category)] = val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid value for category '{category}': {e}")
    
    if sum(validated_data.values()) == 0:
        raise ValueError("All category values are zero")
    
    return validated_data


def extract_column_data(data: Union[List[Dict], Dict], column_name: str) -> np.ndarray:
    """
    Extract a specific column from structured data
    
    Args:
        data: List of dictionaries or nested data structure
        column_name: Name of column to extract
        
    Returns:
        numpy array of column values
        
    Raises:
        ValueError: If column not found or invalid
    """
    if isinstance(data, list) and data and isinstance(data[0], dict):
        if column_name not in data[0]:
            available_cols = list(data[0].keys())
            raise ValueError(f"Column '{column_name}' not found. Available: {available_cols}")
        
        values = []
        for row in data:
            try:
                val = float(row[column_name])
                if np.isfinite(val):
                    values.append(val)
            except (ValueError, TypeError, KeyError):
                continue
        
        return np.array(values, dtype=float)
    
    elif isinstance(data, dict):
        if column_name in data:
            return validate_numeric_data(data[column_name])
        else:
            available_cols = list(data.keys())
            raise ValueError(f"Column '{column_name}' not found. Available: {available_cols}")
    
    else:
        raise ValueError("Data must be list of dictionaries or dictionary")


def validate_capability_params(lsl: float = None, usl: float = None, target: float = None) -> Tuple[float, float, float]:
    """
    Validate process capability parameters
    
    Args:
        lsl: Lower specification limit
        usl: Upper specification limit  
        target: Target value (optional)
        
    Returns:
        Tuple of (lsl, usl, target)
        
    Raises:
        ValueError: If parameters are invalid
    """
    if lsl is None or usl is None:
        raise ValueError("Both Lower Specification Limit (lsl) and Upper Specification Limit (usl) are required")
    
    try:
        lsl = float(lsl)
        usl = float(usl)
    except (ValueError, TypeError):
        raise ValueError("LSL and USL must be numeric values")
    
    if lsl >= usl:
        raise ValueError(f"LSL ({lsl}) must be less than USL ({usl})")
    
    if target is not None:
        try:
            target = float(target)
            if not (lsl <= target <= usl):
                raise ValueError(f"Target ({target}) must be between LSL ({lsl}) and USL ({usl})")
        except (ValueError, TypeError):
            raise ValueError("Target must be a numeric value")
    else:
        # Default target to center of spec limits
        target = (lsl + usl) / 2
    
    return lsl, usl, target