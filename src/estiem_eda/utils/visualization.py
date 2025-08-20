"""Interactive visualization utilities using Plotly for exploratory data analysis charts.

This module provides functions to create professional, interactive charts for
statistical process control and quality analysis, optimized for web display
and integration with MCP protocol responses.
"""

import numpy as np
from typing import List, Optional, Dict, Any, Union
from scipy import stats

# Import ESTIEM branding
try:
    from .branding import add_estiem_branding, apply_estiem_theme, get_estiem_color_scheme
    BRANDING_AVAILABLE = True
except ImportError:
    BRANDING_AVAILABLE = False

# Try to import plotly, handle gracefully if not available
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def _check_plotly() -> None:
    """Check if Plotly is available and raise error if not."""
    if not PLOTLY_AVAILABLE:
        raise ImportError(
            "Plotly is required for visualizations. Install with: pip install plotly>=5.0.0"
        )


def create_control_chart(data: np.ndarray, 
                         center_line: float,
                         ucl: float, 
                         lcl: float,
                         ooc_indices: List[int],
                         title: str = "Individual Control Chart",
                         x_label: str = "Sample Number",
                         y_label: str = "Measurement Value") -> str:
    """Create interactive I-Chart (Individual Control Chart) with Plotly.
    
    Args:
        data: Array of measurement values.
        center_line: Process center line (mean).
        ucl: Upper control limit.
        lcl: Lower control limit.
        ooc_indices: Indices of out-of-control points.
        title: Chart title.
        x_label: X-axis label.
        y_label: Y-axis label.
        
    Returns:
        HTML string containing the interactive Plotly chart.
        
    Raises:
        ImportError: If Plotly is not available.
    """
    _check_plotly()
    
    fig = go.Figure()
    
    # Sample numbers
    x_values = list(range(1, len(data) + 1))
    
    # Determine point colors (red for out-of-control, blue for in-control)
    colors = ['red' if i in ooc_indices else 'steelblue' for i in range(len(data))]
    sizes = [10 if i in ooc_indices else 6 for i in range(len(data))]
    
    # Add data points with connecting line
    fig.add_trace(go.Scatter(
        x=x_values,
        y=data,
        mode='lines+markers',
        name='Process Data',
        line=dict(color='lightblue', width=1.5),
        marker=dict(
            color=colors,
            size=sizes,
            symbol='circle',
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>Sample %{x}</b><br>' +
                      'Value: %{y:.4f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add center line
    fig.add_hline(
        y=center_line, 
        line_dash="solid", 
        line_color="green",
        line_width=2,
        annotation_text=f"Center Line = {center_line:.4f}",
        annotation_position="top right"
    )
    
    # Add upper control limit
    fig.add_hline(
        y=ucl, 
        line_dash="dash", 
        line_color="red",
        line_width=2,
        annotation_text=f"UCL = {ucl:.4f}",
        annotation_position="top right"
    )
    
    # Add lower control limit
    fig.add_hline(
        y=lcl, 
        line_dash="dash", 
        line_color="red",
        line_width=2,
        annotation_text=f"LCL = {lcl:.4f}",
        annotation_position="bottom right"
    )
    
    # Highlight out-of-control zones
    if ooc_indices:
        for idx in ooc_indices:
            fig.add_annotation(
                x=idx + 1,
                y=data[idx],
                text="!",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowcolor="red",
                bgcolor="yellow",
                bordercolor="red",
                borderwidth=1
            )
    
    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': 'darkblue'}
        },
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=500,
        width=900,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # Update axes  
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='black'
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='black'
    )
    
    # Add ESTIEM branding
    if BRANDING_AVAILABLE:
        fig = add_estiem_branding(fig, style="subtle")
        fig = apply_estiem_theme(fig)
    
    return fig.to_html(include_plotlyjs='cdn', div_id="control_chart")


def create_capability_histogram(data: np.ndarray,
                               lsl: float,
                               usl: float,
                               target: Optional[float] = None,
                               mean: Optional[float] = None,
                               std: Optional[float] = None,
                               title: str = "Process Capability Analysis") -> str:
    """Create process capability histogram with normal curve and specification limits.
    
    Args:
        data: Process measurement data.
        lsl: Lower specification limit.
        usl: Upper specification limit.
        target: Target value (optional).
        mean: Process mean (calculated if not provided).
        std: Process standard deviation (calculated if not provided).
        title: Chart title.
        
    Returns:
        HTML string containing the interactive Plotly chart.
        
    Raises:
        ImportError: If Plotly is not available.
    """
    _check_plotly()
    
    if mean is None:
        mean = np.mean(data)
    if std is None:
        std = np.std(data, ddof=1)
    
    fig = go.Figure()
    
    # Create histogram of actual data
    fig.add_trace(go.Histogram(
        x=data,
        name='Actual Data',
        nbinsx=min(30, max(10, len(data)//5)),
        histnorm='probability density',
        marker_color='rgba(70, 130, 180, 0.7)',
        marker_line_color='rgba(70, 130, 180, 1)',
        marker_line_width=1,
        hovertemplate='Range: %{x}<br>Density: %{y:.4f}<extra></extra>'
    ))
    
    # Create normal distribution curve
    x_min = min(data.min() - std, lsl - 0.5*std)
    x_max = max(data.max() + std, usl + 0.5*std)
    x_range = np.linspace(x_min, x_max, 200)
    normal_curve = stats.norm.pdf(x_range, mean, std)
    
    fig.add_trace(go.Scatter(
        x=x_range,
        y=normal_curve,
        mode='lines',
        name='Normal Curve',
        line=dict(color='darkblue', width=3),
        hovertemplate='Value: %{x:.4f}<br>Density: %{y:.4f}<extra></extra>'
    ))
    
    # Add specification limits
    max_y = max(normal_curve) * 1.1
    
    fig.add_vline(
        x=lsl, 
        line_dash="dash", 
        line_color="red",
        line_width=3,
        annotation_text=f"LSL = {lsl}",
        annotation_position="top"
    )
    
    fig.add_vline(
        x=usl, 
        line_dash="dash", 
        line_color="red",
        line_width=3,
        annotation_text=f"USL = {usl}",
        annotation_position="top"
    )
    
    # Add target line if provided
    if target is not None:
        fig.add_vline(
            x=target, 
            line_dash="dot", 
            line_color="green",
            line_width=2,
            annotation_text=f"Target = {target}",
            annotation_position="bottom"
        )
    
    # Add mean line
    fig.add_vline(
        x=mean, 
        line_dash="solid", 
        line_color="darkblue",
        line_width=2,
        annotation_text=f"Mean = {mean:.4f}",
        annotation_position="top"
    )
    
    # Shade regions outside specification limits
    fig.add_vrect(
        x0=x_min, x1=lsl,
        fillcolor="red", opacity=0.2,
        line_width=0,
        annotation_text="Below LSL", annotation_position="top left"
    )
    
    fig.add_vrect(
        x0=usl, x1=x_max,
        fillcolor="red", opacity=0.2,
        line_width=0,
        annotation_text="Above USL", annotation_position="top right"
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': 'darkblue'}
        },
        xaxis_title="Measurement Value",
        yaxis_title="Probability Density",
        height=500,
        width=900,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # Update axes
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='black'
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='black'
    )
    
    # Add ESTIEM branding
    if BRANDING_AVAILABLE:
        fig = add_estiem_branding(fig, style="subtle")
        fig = apply_estiem_theme(fig)
    
    return fig.to_html(include_plotlyjs='cdn', div_id="capability_histogram")


def create_boxplot(data_groups: List[np.ndarray], 
                   group_names: List[str],
                   title: str = "Boxplot Comparison",
                   y_label: str = "Value") -> str:
    """Create comparative boxplots for ANOVA analysis.
    
    Args:
        data_groups: List of data arrays for each group.
        group_names: List of group names.
        title: Chart title.
        y_label: Y-axis label.
        
    Returns:
        HTML string containing the interactive Plotly chart.
        
    Raises:
        ImportError: If Plotly is not available.
    """
    _check_plotly()
    
    fig = go.Figure()
    
    # Color palette for groups
    colors = px.colors.qualitative.Set3
    
    for i, (name, data) in enumerate(zip(group_names, data_groups)):
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Box(
            y=data,
            name=str(name),
            boxmean='sd',  # Show mean and standard deviation
            marker_color=color,
            marker_size=6,
            line_width=2,
            fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.7])}',
            hovertemplate=f'<b>{name}</b><br>' +
                         'Value: %{y:.4f}<br>' +
                         '<extra></extra>',
            # Add individual points
            boxpoints='outliers',  # Show only outliers as points
            jitter=0.3,
            pointpos=-1.8
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': 'darkblue'}
        },
        yaxis_title=y_label,
        xaxis_title="Groups",
        height=500,
        width=900,
        showlegend=False,  # Group names are on x-axis
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # Update axes
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linewidth=1,
        linecolor='black'
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='black'
    )
    
    # Add ESTIEM branding
    if BRANDING_AVAILABLE:
        fig = add_estiem_branding(fig, style="subtle")
        fig = apply_estiem_theme(fig)
    
    return fig.to_html(include_plotlyjs='cdn', div_id="boxplot_comparison")


def create_pareto_chart(categories: List[str],
                        values: List[float],
                        cumulative_pct: List[float],
                        vital_few: List[str],
                        threshold: float = 80,
                        title: str = "Pareto Analysis",
                        unit: str = "Count") -> str:
    """Create Pareto chart with bars and cumulative percentage line.
    
    Args:
        categories: List of category names (sorted by value descending).
        values: List of category values (sorted descending).
        cumulative_pct: List of cumulative percentages.
        vital_few: List of categories identified as vital few.
        threshold: Threshold percentage line (typically 80).
        title: Chart title.
        unit: Unit of measurement for values.
        
    Returns:
        HTML string containing the interactive Plotly chart.
        
    Raises:
        ImportError: If Plotly is not available.
    """
    _check_plotly()
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]]
    )
    
    # Color bars based on vital few identification
    bar_colors = []
    for cat in categories:
        if cat in vital_few:
            bar_colors.append('darkgreen')
        else:
            bar_colors.append('lightgray')
    
    # Add bars (primary y-axis)
    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            name=f'{unit} (Primary)',
            marker_color=bar_colors,
            marker_line_color='white',
            marker_line_width=1,
            hovertemplate='<b>%{x}</b><br>' +
                         f'{unit}: %{y}<br>' +
                         'Percentage: %{customdata:.1f}%<br>' +
                         '<extra></extra>',
            customdata=[v/sum(values)*100 for v in values]
        ),
        secondary_y=False,
    )
    
    # Add cumulative percentage line (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            x=categories,
            y=cumulative_pct,
            mode='lines+markers',
            name='Cumulative %',
            line=dict(color='red', width=3),
            marker=dict(color='red', size=8, symbol='circle'),
            hovertemplate='<b>%{x}</b><br>' +
                         'Cumulative: %{y:.1f}%<br>' +
                         '<extra></extra>',
            yaxis='y2'
        ),
        secondary_y=True,
    )
    
    # Add threshold line
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="orange",
        line_width=2,
        annotation_text=f"{threshold}% Threshold",
        annotation_position="top right",
        secondary_y=True
    )
    
    # Add vertical lines to separate vital few from trivial many
    if vital_few and len(vital_few) < len(categories):
        vital_few_end = len(vital_few) - 0.5
        fig.add_vline(
            x=vital_few_end,
            line_dash="dot",
            line_color="blue",
            line_width=2,
            annotation_text="Vital Few | Trivial Many",
            annotation_position="top"
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': 'darkblue'}
        },
        height=500,
        width=1000,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        margin=dict(l=60, r=60, t=80, b=100)  # Extra bottom margin for long category names
    )
    
    # Set x-axis properties
    fig.update_xaxes(
        title_text="Categories (Ranked by Impact)",
        showgrid=False,
        showline=True,
        linewidth=1,
        linecolor='black',
        tickangle=-45  # Rotate labels for better readability
    )
    
    # Set y-axes properties
    fig.update_yaxes(
        title_text=f"{unit}",
        secondary_y=False,
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='black'
    )
    fig.update_yaxes(
        title_text="Cumulative Percentage (%)",
        secondary_y=True,
        range=[0, 100],
        showgrid=False,
        showline=True,
        linewidth=1,
        linecolor='black'
    )
    
    # Add ESTIEM branding
    if BRANDING_AVAILABLE:
        fig = add_estiem_branding(fig, style="subtle")
        fig = apply_estiem_theme(fig)
    
    return fig.to_html(include_plotlyjs='cdn', div_id="pareto_chart")


def create_probability_plot_chart(theoretical_quantiles: np.ndarray,
                                 observed_values: np.ndarray,
                                 confidence_intervals: Dict[str, np.ndarray],
                                 title: str = "Normal Probability Plot",
                                 distribution: str = "normal",
                                 fitted_params: tuple = None,
                                 correlation: float = 0.0) -> str:
    """Create interactive probability plot with confidence intervals.
    
    Args:
        theoretical_quantiles: Theoretical quantiles from distribution
        observed_values: Observed data values (sorted)
        confidence_intervals: Dict with 'lower' and 'upper' bound arrays
        title: Chart title
        distribution: Distribution type ('normal', 'lognormal', 'weibull')
        fitted_params: Fitted distribution parameters
        correlation: Correlation coefficient (goodness of fit)
        
    Returns:
        HTML string containing the interactive probability plot
    """
    _check_plotly()
    
    # Create figure
    fig = go.Figure()
    
    # Add confidence interval bands
    fig.add_trace(go.Scatter(
        x=np.concatenate([theoretical_quantiles, theoretical_quantiles[::-1]]),
        y=np.concatenate([confidence_intervals['upper'], confidence_intervals['lower'][::-1]]),
        fill='toself',
        fillcolor='rgba(46, 139, 87, 0.2)' if BRANDING_AVAILABLE else 'rgba(128, 128, 128, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name='95% Confidence Interval',
        showlegend=True
    ))
    
    # Add confidence interval boundary lines
    fig.add_trace(go.Scatter(
        x=theoretical_quantiles,
        y=confidence_intervals['upper'],
        mode='lines',
        line=dict(color='#2E8B57' if BRANDING_AVAILABLE else 'gray', width=1, dash='dot'),
        name='Upper CI',
        showlegend=False,
        hovertemplate='Upper CI: %{y:.3f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=theoretical_quantiles,
        y=confidence_intervals['lower'],
        mode='lines',
        line=dict(color='#2E8B57' if BRANDING_AVAILABLE else 'gray', width=1, dash='dot'),
        name='Lower CI',
        showlegend=False,
        hovertemplate='Lower CI: %{y:.3f}<extra></extra>'
    ))
    
    # Add fitted distribution line
    if fitted_params:
        line_x = np.linspace(theoretical_quantiles.min(), theoretical_quantiles.max(), 100)
        if distribution == "normal":
            mean, std = fitted_params[:2]
            line_y = mean + std * line_x
        elif distribution == "lognormal":
            s, loc, scale = fitted_params[:3]
            line_y = np.exp(loc + scale * line_x)
        elif distribution == "weibull":
            # For Weibull, relationship is more complex
            line_y = line_x  # Simplified for display
        else:
            line_y = line_x  # Default linear relationship
        
        fig.add_trace(go.Scatter(
            x=line_x,
            y=line_y,
            mode='lines',
            line=dict(color='red', width=2),
            name=f'Fitted {distribution.title()} Line',
            hovertemplate='Fitted Line<br>Theoretical: %{x:.3f}<br>Expected: %{y:.3f}<extra></extra>'
        ))
    
    # Add data points
    colors = []
    hover_texts = []
    for i, (x, y) in enumerate(zip(theoretical_quantiles, observed_values)):
        # Check if point is outlier (outside confidence intervals)
        if y < confidence_intervals['lower'][i] or y > confidence_intervals['upper'][i]:
            colors.append('red')
            hover_texts.append(f'Outlier<br>Theoretical: {x:.3f}<br>Observed: {y:.3f}<br>Position: {i+1}')
        else:
            colors.append('#2E8B57' if BRANDING_AVAILABLE else 'blue')
            hover_texts.append(f'Normal<br>Theoretical: {x:.3f}<br>Observed: {y:.3f}<br>Position: {i+1}')
    
    fig.add_trace(go.Scatter(
        x=theoretical_quantiles,
        y=observed_values,
        mode='markers',
        marker=dict(
            color=colors,
            size=8,
            symbol='circle',
            line=dict(width=1, color='white')
        ),
        name='Data Points',
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>'
    ))
    
    # Set axis labels based on distribution
    if distribution == "normal":
        x_axis_title = "Normal Theoretical Quantiles"
        y_axis_title = "Observed Values"
    elif distribution == "lognormal":
        x_axis_title = "Normal Theoretical Quantiles"
        y_axis_title = "Log(Observed Values)"
    elif distribution == "weibull":
        x_axis_title = "Weibull Theoretical Quantiles"
        y_axis_title = "Observed Values"
    else:
        x_axis_title = "Theoretical Quantiles"
        y_axis_title = "Observed Values"
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"{title}<br><sub>Distribution: {distribution.title()}, r = {correlation:.4f}</sub>",
            x=0.5,
            font=dict(size=16)
        ),
        xaxis=dict(
            title=x_axis_title,
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title=y_axis_title,
            showgrid=True,
            gridcolor='lightgray'
        ),
        hovermode='closest',
        template='plotly_white',
        width=800,
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add correlation and fit quality annotations
    fit_quality = "Excellent" if correlation > 0.99 else "Good" if correlation > 0.98 else "Fair" if correlation > 0.95 else "Poor"
    
    fig.add_annotation(
        text=f"Goodness of Fit: {fit_quality}<br>Correlation: {correlation:.4f}",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        xanchor="left", yanchor="top",
        showarrow=False,
        font=dict(size=10),
        bgcolor="white",
        bordercolor="gray",
        borderwidth=1
    )
    
    # Apply ESTIEM branding if available
    if BRANDING_AVAILABLE:
        fig = add_estiem_branding(fig, style="subtle")
        fig = apply_estiem_theme(fig)
    
    return fig.to_html(include_plotlyjs='cdn', div_id="probability_plot")


def create_multi_chart_dashboard(charts: Dict[str, str], 
                                title: str = "Exploratory Data Analysis Dashboard") -> str:
    """Create a dashboard combining multiple charts in a single HTML page.
    
    Args:
        charts: Dictionary with chart names as keys and HTML content as values.
        title: Dashboard title.
        
    Returns:
        HTML string containing all charts in a dashboard layout.
    """
    html_parts = [
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .dashboard-header {{
                    text-align: center;
                    color: #2c3e50;
                    margin-bottom: 30px;
                    padding: 20px;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .chart-container {{
                    margin: 20px 0;
                    padding: 20px;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .chart-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #34495e;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <h1>{title}</h1>
                <p>Interactive Exploratory Data Analysis Dashboard</p>
            </div>
        """
    ]
    
    for chart_name, chart_html in charts.items():
        html_parts.append(f"""
            <div class="chart-container">
                <div class="chart-title">{chart_name}</div>
                {chart_html}
            </div>
        """)
    
    html_parts.append("""
        </body>
        </html>
    """)
    
    return "".join(html_parts)


# Utility functions for chart data preparation
def prepare_control_chart_data(data: List[float], 
                              ooc_indices: List[int]) -> Dict[str, Any]:
    """Prepare data structure for control chart visualization.
    
    Args:
        data: Measurement data.
        ooc_indices: Out-of-control point indices.
        
    Returns:
        Dictionary with prepared chart data.
    """
    return {
        "x_values": list(range(1, len(data) + 1)),
        "y_values": data,
        "ooc_points": [(i+1, data[i]) for i in ooc_indices],
        "total_points": len(data),
        "ooc_count": len(ooc_indices)
    }


def calculate_chart_bounds(data: np.ndarray, 
                          padding_factor: float = 0.1) -> tuple:
    """Calculate appropriate chart bounds with padding.
    
    Args:
        data: Data array.
        padding_factor: Padding as fraction of data range.
        
    Returns:
        Tuple of (y_min, y_max) bounds.
    """
    data_min, data_max = np.min(data), np.max(data)
    data_range = data_max - data_min
    padding = data_range * padding_factor
    
    return (data_min - padding, data_max + padding)