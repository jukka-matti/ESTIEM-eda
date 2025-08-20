"""Enhanced Visualization Response System for Multi-Format Chart Generation.

This module provides the core architecture for generating multiple visualization
formats from statistical analysis results, enabling seamless chart display
across different Claude interfaces.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
import json
import time
import logging


class VisualizationFormat(Enum):
    """Supported visualization formats for multi-client compatibility."""
    
    HTML_PLOTLY = "html_plotly"           # Interactive HTML with embedded Plotly
    ARTIFACT_REACT = "artifact_react"     # React component for Claude Artifacts
    ARTIFACT_HTML = "artifact_html"       # Standalone HTML artifact
    CHART_CONFIG = "chart_config"         # Structured Plotly configuration
    TEXT_FALLBACK = "text_fallback"       # ASCII/text representation


@dataclass
class ChartData:
    """Structured chart data for consistent multi-format generation."""
    
    chart_type: str                       # Type of chart (control_chart, histogram, etc.)
    data_series: List[Dict[str, Any]]     # Plotly data traces
    layout_config: Dict[str, Any]         # Plotly layout configuration
    styling_info: Dict[str, Any]          # ESTIEM branding and styling
    interactivity: Dict[str, Any]         # Interactive features and config
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


@dataclass
class ArtifactData:
    """Claude Artifact-compatible data structure."""
    
    artifact_type: str                    # "react" or "html"
    language: str                         # "jsx" or "html"
    content: str                          # Artifact source code
    dependencies: List[str] = field(default_factory=list)  # Required dependencies
    props_schema: Optional[Dict[str, str]] = None           # React props schema


@dataclass
class FormatContent:
    """Container for format-specific content and metadata."""
    
    content: Union[str, Dict[str, Any]]   # The actual content
    content_type: str                     # MIME type or format identifier
    size_kb: float = 0.0                  # Content size in KB
    features: List[str] = field(default_factory=list)      # Feature list
    dependencies: List[str] = field(default_factory=list)  # Required dependencies
    standalone: bool = True               # Whether content is self-contained


class EnhancedVisualizationResponse:
    """Multi-format visualization response orchestrator.
    
    This class manages the generation and optimization of multiple visualization
    formats from a single set of statistical analysis results.
    """
    
    def __init__(self, analysis_data: Dict[str, Any], analysis_type: str):
        """Initialize the enhanced visualization response.
        
        Args:
            analysis_data: Statistical analysis results
            analysis_type: Type of analysis (i_chart, process_capability, etc.)
        """
        self.analysis_data = analysis_data
        self.analysis_type = analysis_type
        self.chart_data: Optional[ChartData] = None
        self.formats: Dict[VisualizationFormat, FormatContent] = {}
        self.generation_start_time = time.time()
        self.logger = logging.getLogger(__name__)
        
        # Client capability detection results
        self.client_capabilities: Dict[str, bool] = {}
        self.recommended_format: Optional[VisualizationFormat] = None
    
    def set_chart_data(self, chart_data: ChartData) -> None:
        """Set the structured chart data for format generation.
        
        Args:
            chart_data: Structured chart information
        """
        self.chart_data = chart_data
        self.logger.debug(f"Chart data set for {self.analysis_type}")
    
    def add_format(self, format_type: VisualizationFormat, content: FormatContent) -> None:
        """Add a visualization format to the response.
        
        Args:
            format_type: The visualization format type
            content: Format-specific content and metadata
        """
        self.formats[format_type] = content
        self.logger.debug(f"Added format {format_type.value} ({content.size_kb:.1f}KB)")
    
    def detect_client_capabilities(self, client_info: Dict[str, Any]) -> Dict[str, bool]:
        """Detect client capabilities from MCP request context.
        
        Args:
            client_info: Client information from MCP request
            
        Returns:
            Dictionary of client capabilities
        """
        client_name = client_info.get('name', '').lower()
        
        if "claude-desktop" in client_name or "claude" in client_name:
            # Claude Desktop supports artifacts but not raw HTML
            capabilities = {
                "supports_html": False,
                "supports_artifacts": True,
                "supports_react": True,
                "supports_interactive": True,
                "preferred_format": "artifact_react"
            }
            self.recommended_format = VisualizationFormat.ARTIFACT_REACT
            
        elif "claude-code" in client_name:
            # Claude Code supports HTML and artifacts
            capabilities = {
                "supports_html": True,
                "supports_artifacts": True,
                "supports_interactive": True,
                "preferred_format": "html_plotly"
            }
            self.recommended_format = VisualizationFormat.HTML_PLOTLY
            
        else:
            # Unknown client - use safe fallback
            capabilities = {
                "supports_html": False,
                "supports_artifacts": False,
                "preferred_format": "text_fallback"
            }
            self.recommended_format = VisualizationFormat.TEXT_FALLBACK
        
        self.client_capabilities = capabilities
        self.logger.info(f"Detected client: {client_name}, preferred: {self.recommended_format.value}")
        
        return capabilities
    
    def get_best_format(self, client_capabilities: Optional[Dict[str, bool]] = None) -> FormatContent:
        """Get the best visualization format for the client.
        
        Args:
            client_capabilities: Optional client capability override
            
        Returns:
            The optimal format content for the client
        """
        if client_capabilities:
            self.client_capabilities = client_capabilities
        
        # Define fallback chain based on client capabilities
        if self.client_capabilities.get("supports_artifacts", False):
            fallback_chain = [
                VisualizationFormat.ARTIFACT_REACT,
                VisualizationFormat.ARTIFACT_HTML,
                VisualizationFormat.CHART_CONFIG,
                VisualizationFormat.TEXT_FALLBACK
            ]
        elif self.client_capabilities.get("supports_html", False):
            fallback_chain = [
                VisualizationFormat.HTML_PLOTLY,
                VisualizationFormat.CHART_CONFIG,
                VisualizationFormat.TEXT_FALLBACK
            ]
        else:
            fallback_chain = [
                VisualizationFormat.CHART_CONFIG,
                VisualizationFormat.TEXT_FALLBACK
            ]
        
        # Try each format in the fallback chain
        for format_type in fallback_chain:
            if format_type in self.formats:
                self.logger.debug(f"Selected format: {format_type.value}")
                return self.formats[format_type]
        
        # Should never happen, but provide ultimate fallback
        self.logger.warning("No suitable format found, using text fallback")
        return FormatContent(
            content="Chart visualization not available",
            content_type="text/plain",
            size_kb=0.1
        )
    
    def optimize_for_client(self, client_type: str) -> Dict[str, Any]:
        """Optimize response specifically for a client type.
        
        Args:
            client_type: Type of client (claude-desktop, claude-code, etc.)
            
        Returns:
            Optimized response dictionary
        """
        client_info = {"name": client_type}
        self.detect_client_capabilities(client_info)
        
        best_format = self.get_best_format()
        
        return {
            "primary_format": self.recommended_format.value if self.recommended_format else None,
            "content": best_format.content,
            "metadata": {
                "content_type": best_format.content_type,
                "size_kb": best_format.size_kb,
                "features": best_format.features,
                "dependencies": best_format.dependencies
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the enhanced response to a dictionary format.
        
        Returns:
            Complete response dictionary with all formats and metadata
        """
        generation_time_ms = (time.time() - self.generation_start_time) * 1000
        total_size_kb = sum(fmt.size_kb for fmt in self.formats.values())
        
        # Build visualization_formats section
        visualization_formats = {}
        
        for format_type, format_content in self.formats.items():
            if format_type == VisualizationFormat.HTML_PLOTLY:
                visualization_formats["html_plotly"] = {
                    "content": format_content.content,
                    "type": format_content.content_type,
                    "size_kb": format_content.size_kb,
                    "features": format_content.features,
                    "dependencies": format_content.dependencies
                }
            
            elif format_type in [VisualizationFormat.ARTIFACT_REACT, VisualizationFormat.ARTIFACT_HTML]:
                if "artifact_data" not in visualization_formats:
                    visualization_formats["artifact_data"] = {}
                
                if format_type == VisualizationFormat.ARTIFACT_REACT:
                    artifact_data = format_content.content
                    if isinstance(artifact_data, ArtifactData):
                        visualization_formats["artifact_data"]["react"] = {
                            "type": artifact_data.artifact_type,
                            "language": artifact_data.language,
                            "content": artifact_data.content,
                            "dependencies": artifact_data.dependencies,
                            "props_schema": artifact_data.props_schema or {}
                        }
                
                elif format_type == VisualizationFormat.ARTIFACT_HTML:
                    artifact_data = format_content.content
                    if isinstance(artifact_data, ArtifactData):
                        visualization_formats["artifact_data"]["html"] = {
                            "type": artifact_data.artifact_type,
                            "language": artifact_data.language,
                            "content": artifact_data.content,
                            "dependencies": artifact_data.dependencies,
                            "standalone": format_content.standalone
                        }
            
            elif format_type == VisualizationFormat.CHART_CONFIG:
                visualization_formats["chart_config"] = format_content.content
            
            elif format_type == VisualizationFormat.TEXT_FALLBACK:
                visualization_formats["fallback_text"] = format_content.content
        
        # Build fallback chain
        fallback_chain = []
        if VisualizationFormat.HTML_PLOTLY in self.formats:
            fallback_chain.append("html_plotly")
        if VisualizationFormat.ARTIFACT_REACT in self.formats:
            fallback_chain.append("artifact_data")
        if VisualizationFormat.CHART_CONFIG in self.formats:
            fallback_chain.append("chart_config")
        if VisualizationFormat.TEXT_FALLBACK in self.formats:
            fallback_chain.append("fallback_text")
        
        return {
            "success": True,
            "analysis_type": self.analysis_type,
            **self.analysis_data,  # Include all original statistical results
            "visualization_formats": visualization_formats,
            "rendering_metadata": {
                "primary_format": self.recommended_format.value if self.recommended_format else "chart_config",
                "fallback_chain": fallback_chain,
                "client_hints": self.client_capabilities,
                "generation_time_ms": round(generation_time_ms, 1),
                "total_size_kb": round(total_size_kb, 1)
            }
        }
    
    def validate_formats(self) -> bool:
        """Validate all generated formats for consistency.
        
        Returns:
            True if all formats are valid and consistent
        """
        if not self.formats:
            self.logger.error("No formats generated")
            return False
        
        if not self.chart_data:
            self.logger.warning("No chart data available for validation")
        
        # Validate each format
        for format_type, format_content in self.formats.items():
            if not format_content.content:
                self.logger.error(f"Empty content for format {format_type.value}")
                return False
            
            if format_content.size_kb < 0:
                self.logger.error(f"Invalid size for format {format_type.value}")
                return False
        
        # Ensure at least one fallback format exists
        fallback_formats = [VisualizationFormat.CHART_CONFIG, VisualizationFormat.TEXT_FALLBACK]
        if not any(fmt in self.formats for fmt in fallback_formats):
            self.logger.error("No fallback format available")
            return False
        
        self.logger.debug(f"All {len(self.formats)} formats validated successfully")
        return True


def create_chart_data(chart_type: str, plotly_data: List[Dict], 
                     plotly_layout: Dict[str, Any], 
                     estiem_styling: Optional[Dict[str, Any]] = None) -> ChartData:
    """Create structured chart data from Plotly components.
    
    Args:
        chart_type: Type of chart being created
        plotly_data: Plotly data traces
        plotly_layout: Plotly layout configuration
        estiem_styling: Optional ESTIEM-specific styling
        
    Returns:
        Structured ChartData object
    """
    default_styling = {
        "color_scheme": "ESTIEM",
        "font_family": "Open Sans, sans-serif",
        "brand_colors": {
            "primary": "#1f4e79",
            "secondary": "#7ba7d1", 
            "accent": "#f8a978"
        }
    }
    
    styling = {**default_styling, **(estiem_styling or {})}
    
    interactivity = {
        "responsive": True,
        "displayModeBar": True,
        "export_formats": ["png", "svg", "pdf"],
        "zoom_enabled": True,
        "pan_enabled": True
    }
    
    return ChartData(
        chart_type=chart_type,
        data_series=plotly_data,
        layout_config=plotly_layout,
        styling_info=styling,
        interactivity=interactivity,
        metadata={
            "created_at": time.time(),
            "generator": "ESTIEM EDA Enhanced MCP Server"
        }
    )