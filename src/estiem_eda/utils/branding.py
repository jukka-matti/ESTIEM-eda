"""ESTIEM branding utilities for charts and visualizations."""


import plotly.graph_objects as go

# ESTIEM logo as base64 data URI (placeholder - will need actual conversion)
# This would be the actual ESTIEM logo converted to base64
ESTIEM_LOGO_BASE64 = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="""

# Alternative: Use the uploaded image path if available
ESTIEM_LOGO_URL = "https://estiem.org/assets/images/logo.png"


def add_estiem_branding(fig: go.Figure, style: str = "subtle") -> go.Figure:
    """Add ESTIEM logo branding to any Plotly figure.

    Args:
        fig: Plotly figure to add branding to
        style: Branding style ('subtle', 'prominent', 'none')

    Returns:
        Figure with ESTIEM branding added
    """
    if style == "none":
        return fig

    # Determine opacity based on style
    opacity = 0.4 if style == "subtle" else 0.7

    # Determine size based on style
    if style == "prominent":
        sizex, sizey = 0.12, 0.08
    else:
        sizex, sizey = 0.08, 0.05

    try:
        # Add ESTIEM logo image
        fig.add_layout_image(
            {
                "source": ESTIEM_LOGO_BASE64,  # Use base64 for reliability
                "xref": "paper",
                "yref": "paper",
                "x": 0.98,
                "y": 0.02,  # Bottom-right corner
                "sizex": sizex,
                "sizey": sizey,
                "xanchor": "right",
                "yanchor": "bottom",
                "opacity": opacity,
                "layer": "above",
            }
        )
    except Exception:
        # Fallback to text branding if image fails
        fig.add_annotation(
            text="ESTIEM",
            xref="paper",
            yref="paper",
            x=0.98,
            y=0.02,
            xanchor="right",
            yanchor="bottom",
            showarrow=False,
            font={"size": 10, "color": "#2E8B57", "family": "Arial", "weight": "bold"},
            opacity=opacity,
        )

    return fig


def add_estiem_footer(
    fig: go.Figure, analysis_type: str, sample_size: int | None = None
) -> go.Figure:
    """Add ESTIEM footer with analysis information.

    Args:
        fig: Plotly figure
        analysis_type: Type of exploratory data analysis
        sample_size: Number of data points (optional)

    Returns:
        Figure with footer added
    """
    # Build footer text
    footer_parts = ["ESTIEM Exploratory Data Analysis"]

    if analysis_type:
        footer_parts.append(f"Method: {analysis_type}")

    if sample_size:
        footer_parts.append(f"n = {sample_size}")

    footer_text = " | ".join(footer_parts)

    fig.add_annotation(
        text=footer_text,
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.08,
        xanchor="center",
        yanchor="top",
        showarrow=False,
        font={"size": 9, "color": "#666666", "family": "Arial"},
        opacity=0.8,
    )

    return fig


def get_estiem_color_scheme() -> dict:
    """Get ESTIEM brand colors for consistent styling.

    Returns:
        Dictionary of ESTIEM brand colors
    """
    return {
        "primary_green": "#2E8B57",  # ESTIEM main green
        "secondary_green": "#228B22",  # Darker green
        "light_green": "#90EE90",  # Light green for fills
        "text_gray": "#333333",  # Professional text
        "light_gray": "#666666",  # Secondary text
        "background": "#FFFFFF",  # Clean background
    }


def apply_estiem_theme(fig: go.Figure) -> go.Figure:
    """Apply ESTIEM visual theme to figure.

    Args:
        fig: Plotly figure to theme

    Returns:
        Figure with ESTIEM theme applied
    """
    colors = get_estiem_color_scheme()

    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font={"family": "Arial, sans-serif", "size": 12, "color": colors["text_gray"]},
        title_font={
            "family": "Arial, sans-serif", "size": 16, "color": colors["text_gray"], "weight": "bold"
        },
    )

    # Update axes styling
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightgray",
        showline=True,
        linewidth=2,
        linecolor=colors["primary_green"],
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightgray",
        showline=True,
        linewidth=2,
        linecolor=colors["primary_green"],
    )

    return fig
