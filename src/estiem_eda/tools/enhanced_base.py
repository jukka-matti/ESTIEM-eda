"""Enhanced Base Tool Class - DEPRECATED.

This module is deprecated in favor of simplified_base.py for better reliability.
The multi-format approach has been simplified to HTML-first for maximum compatibility.

Use SimplifiedMCPTool from simplified_base.py instead.
"""

import logging
from typing import Dict, Any


class EnhancedBaseTool:
    """Deprecated enhanced base tool class.
    
    This class is no longer maintained. Use SimplifiedMCPTool instead.
    """
    
    def __init__(self):
        """Initialize deprecated tool."""
        self.logger = logging.getLogger(__name__)
        self.logger.warning("EnhancedBaseTool is deprecated. Use SimplifiedMCPTool instead.")
    
    def execute(self, *args, **kwargs):
        """Deprecated execute method."""
        raise NotImplementedError("This class is deprecated. Use SimplifiedMCPTool instead.")


# Legacy compatibility
def create_estiem_chart_data(*args, **kwargs):
    """Deprecated chart data creation function."""
    logging.getLogger(__name__).warning("create_estiem_chart_data is deprecated")
    return {}