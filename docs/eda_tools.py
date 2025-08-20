"""
ESTIEM EDA Toolkit - Python Statistical Analysis Tools
Runs in browser via Pyodide for client-side statistical analysis
"""

try:
    import numpy as np
    import pandas as pd
    from scipy import stats
    import json
    import math
    print("✅ All required packages imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    raise


def generate_sample_data(sample_type):
    """Generate realistic sample datasets for demonstration"""
    
    if sample_type == 'manufacturing':
        np.random.seed(42)
        n = 100
        
        # Generate manufacturing data with different lines
        lines = ['Line_A', 'Line_B', 'Line_C']
        shifts = ['Day', 'Night']
        
        data = []
        for i in range(n):
            line = np.random.choice(lines)
            shift = np.random.choice(shifts)
            
            # Different lines have different characteristics
            if line == 'Line_A':
                measurement = np.random.normal(10.0, 0.3)
                defects = np.random.poisson(2)
            elif line == 'Line_B':
                measurement = np.random.normal(9.8, 0.5)
                defects = np.random.poisson(3)
            else:  # Line_C
                measurement = np.random.normal(10.2, 0.4)
                defects = np.random.poisson(1)
            
            # Shift effect
            if shift == 'Night':
                measurement += np.random.normal(0, 0.1)
                defects += np.random.poisson(0.5)
            
            data.append({
                'sample_id': i + 1,
                'measurement': round(measurement, 3),
                'line': line,
                'shift': shift,
                'defects': int(defects),
                'temperature': round(np.random.normal(25, 2), 1),
                'operator': f'OP_{np.random.randint(1, 6):02d}'
            })
        
        return {
            'data': data,
            'headers': ['sample_id', 'measurement', 'line', 'shift', 'defects', 'temperature', 'operator'],
            'filename': 'manufacturing_sample_data.csv'
        }
    
    elif sample_type == 'quality':
        np.random.seed(123)
        n = 75
        
        defect_types = ['Surface', 'Dimensional', 'Assembly', 'Material', 'Other']
        
        data = []
        for i in range(n):
            defect_type = np.random.choice(defect_types, p=[0.4, 0.25, 0.2, 0.1, 0.05])
            
            # Different defect patterns
            if defect_type == 'Surface':
                count = np.random.poisson(15)
                severity = np.random.choice(['Minor', 'Major', 'Critical'], p=[0.6, 0.3, 0.1])
            elif defect_type == 'Dimensional':
                count = np.random.poisson(8)
                severity = np.random.choice(['Minor', 'Major', 'Critical'], p=[0.4, 0.5, 0.1])
            elif defect_type == 'Assembly':
                count = np.random.poisson(5)
                severity = np.random.choice(['Minor', 'Major', 'Critical'], p=[0.3, 0.6, 0.1])
            else:
                count = np.random.poisson(3)
                severity = np.random.choice(['Minor', 'Major', 'Critical'], p=[0.5, 0.4, 0.1])
            
            data.append({
                'inspection_id': i + 1,
                'defect_type': defect_type,
                'defect_count': int(count),
                'severity': severity,
                'inspector': f'INS_{np.random.randint(1, 4)}',
                'date': f'2024-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}',
                'cost': round(count * np.random.uniform(10, 50), 2)
            })
        
        return {
            'data': data,
            'headers': ['inspection_id', 'defect_type', 'defect_count', 'severity', 'inspector', 'date', 'cost'],
            'filename': 'quality_control_sample_data.csv'
        }
    
    elif sample_type == 'process':
        np.random.seed(789)
        n = 120
        
        # Process monitoring data with trends
        base_value = 100
        trend = 0.1
        
        data = []
        for i in range(n):
            # Add trend and noise
            value = base_value + trend * i + np.random.normal(0, 2)
            
            # Add some special cause variation
            if i > 50 and i < 70:
                value += np.random.normal(5, 1)  # Process shift
            
            data.append({
                'time': i + 1,
                'process_value': round(value, 2),
                'temperature': round(np.random.normal(80, 5), 1),
                'pressure': round(np.random.normal(15, 1), 2),
                'flow_rate': round(np.random.normal(50, 3), 1),
                'operator': f'OP_{((i // 8) % 3) + 1}'
            })
        
        return {
            'data': data,
            'headers': ['time', 'process_value', 'temperature', 'pressure', 'flow_rate', 'operator'],
            'filename': 'process_monitoring_sample_data.csv'
        }
    
    return {'data': [], 'headers': [], 'filename': 'sample_data.csv'}


def run_analysis(analysis_type, data, headers, parameters):
    """Main analysis dispatcher"""
    
    try:
        # Ensure data is properly formatted for DataFrame creation
        if isinstance(data, str):
            data = json.loads(data)
        
        # Handle different data formats
        if isinstance(data, dict) and 'data' in data:
            df = pd.DataFrame(data['data'])
        elif isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
            else:
                # Simple list of values
                df = pd.DataFrame({'values': data})
        else:
            df = pd.DataFrame(data)
            
    except Exception as e:
        raise ValueError(f"Error creating DataFrame: {str(e)}")
    
    if analysis_type == 'i_chart':
        return create_i_chart(df, headers, parameters)
    elif analysis_type == 'capability':
        return create_capability_analysis(df, headers, parameters)
    elif analysis_type == 'anova':
        return create_anova_analysis(df, headers, parameters)
    elif analysis_type == 'pareto':
        return create_pareto_analysis(df, headers, parameters)
    elif analysis_type == 'probability_plot':
        return create_probability_plot(df, headers, parameters)
    else:
        raise ValueError(f'Unknown analysis type: {analysis_type}')


def create_i_chart(df, headers, parameters):
    """Create Individual Control Chart (I-Chart)"""
    
    try:
        # Find numeric column (assume first numeric column is the measurement)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            raise ValueError('No numeric columns found for I-Chart analysis')
    except Exception as e:
        raise ValueError(f'Error processing DataFrame: {str(e)}')
    
    measurement_col = numeric_cols[0]
    values = df[measurement_col].dropna().values
    
    if len(values) < 3:
        raise ValueError('Need at least 3 data points for I-Chart')
    
    # Calculate statistics
    mean = np.mean(values)
    
    # Moving range for sigma estimation
    moving_range = np.abs(np.diff(values))
    avg_mr = np.mean(moving_range)
    d2 = 1.128  # For n=2 moving range
    sigma = avg_mr / d2
    
    ucl = mean + 3 * sigma
    lcl = mean - 3 * sigma
    
    # Find out-of-control points
    ooc_indices = []
    for i, val in enumerate(values):
        if val > ucl or val < lcl:
            ooc_indices.append(i)
    
    # Western Electric rules (basic implementation)
    patterns = check_western_electric_rules(values, mean, sigma)
    
    # Create chart data
    chart_data = {
        'data': [
            {
                'x': list(range(1, len(values) + 1)),
                'y': values.tolist(),
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Measurements',
                'line': {'color': '#1f77b4'},
                'marker': {
                    'color': ['red' if i in ooc_indices else '#1f77b4' for i in range(len(values))],
                    'size': 8
                },
                'hovertemplate': 'Sample %{x}<br>Value: %{y:.3f}<extra></extra>'
            }
        ],
        'layout': {
            'title': {
                'text': f'I-Chart: Individual Control Chart<br><sub>{measurement_col}</sub>',
                'x': 0.5,
                'font': {'size': 16}
            },
            'xaxis': {
                'title': 'Sample Number',
                'showgrid': True,
                'gridcolor': 'lightgray'
            },
            'yaxis': {
                'title': f'{measurement_col}',
                'showgrid': True,
                'gridcolor': 'lightgray'
            },
            'shapes': [
                # UCL
                {
                    'type': 'line',
                    'x0': 1, 'x1': len(values),
                    'y0': ucl, 'y1': ucl,
                    'line': {'color': 'red', 'dash': 'dash', 'width': 2}
                },
                # Center Line
                {
                    'type': 'line',
                    'x0': 1, 'x1': len(values),
                    'y0': mean, 'y1': mean,
                    'line': {'color': 'green', 'dash': 'dash', 'width': 2}
                },
                # LCL
                {
                    'type': 'line',
                    'x0': 1, 'x1': len(values),
                    'y0': lcl, 'y1': lcl,
                    'line': {'color': 'red', 'dash': 'dash', 'width': 2}
                }
            ],
            'annotations': [
                {'x': len(values), 'y': ucl, 'text': f'UCL={ucl:.3f}', 'showarrow': False, 'xanchor': 'left'},
                {'x': len(values), 'y': mean, 'text': f'CL={mean:.3f}', 'showarrow': False, 'xanchor': 'left'},
                {'x': len(values), 'y': lcl, 'text': f'LCL={lcl:.3f}', 'showarrow': False, 'xanchor': 'left'},
                # ESTIEM Branding
                {
                    'text': 'ESTIEM EDA Toolkit | estiem.org',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.99, 'y': 0.01,
                    'showarrow': False,
                    'font': {'size': 10, 'color': 'gray'},
                    'xanchor': 'right'
                }
            ],
            'template': 'plotly_white',
            'hovermode': 'closest'
        }
    }
    
    # Statistics
    statistics = {
        'sample_size': len(values),
        'mean': mean,
        'ucl': ucl,
        'lcl': lcl,
        'sigma_estimate': sigma,
        'out_of_control_points': len(ooc_indices),
        'percentage_ooc': (len(ooc_indices) / len(values)) * 100
    }
    
    # Interpretation
    if len(ooc_indices) == 0:
        if len(patterns) == 0:
            interpretation = "✅ Process is IN CONTROL. No points outside control limits and no concerning patterns detected."
        else:
            interpretation = f"⚠️ Process shows {len(patterns)} pattern(s) of concern but no points outside control limits."
    else:
        interpretation = f"❌ Process is OUT OF CONTROL. {len(ooc_indices)} points ({statistics['percentage_ooc']:.1f}%) outside control limits."
    
    return {
        'analysis_type': 'i_chart',
        'chart_data': json.dumps(chart_data),
        'statistics': statistics,
        'interpretation': interpretation
    }


def create_capability_analysis(df, headers, parameters):
    """Process Capability Analysis"""
    
    lsl = parameters.get('lsl')
    usl = parameters.get('usl')
    target = parameters.get('target')
    
    if lsl is None or usl is None:
        raise ValueError('LSL and USL are required for capability analysis')
    
    # Find numeric column
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        raise ValueError('No numeric columns found')
    
    measurement_col = numeric_cols[0]
    values = df[measurement_col].dropna().values
    
    if len(values) < 10:
        raise ValueError('Need at least 10 data points for capability analysis')
    
    # Calculate statistics
    mean = np.mean(values)
    std = np.std(values, ddof=1)
    
    # Calculate capability indices
    cp = (usl - lsl) / (6 * std)
    cpu = (usl - mean) / (3 * std)
    cpl = (mean - lsl) / (3 * std)
    cpk = min(cpu, cpl)
    
    # Process performance (if target specified)
    if target:
        cpm = cp / np.sqrt(1 + ((mean - target) / std) ** 2)
    else:
        cpm = None
    
    # Defect rates
    z_usl = (usl - mean) / std
    z_lsl = (lsl - mean) / std
    
    p_above_usl = 1 - stats.norm.cdf(z_usl)
    p_below_lsl = stats.norm.cdf(z_lsl)
    total_defect_rate = p_above_usl + p_below_lsl
    ppm_total = total_defect_rate * 1000000
    
    # Sigma level approximation
    if total_defect_rate > 0:
        sigma_level = abs(stats.norm.ppf(total_defect_rate / 2))
    else:
        sigma_level = 6.0
    
    # Create histogram with spec limits
    hist, bin_edges = np.histogram(values, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Normal curve overlay
    x_range = np.linspace(min(lsl - std, values.min()), max(usl + std, values.max()), 200)
    normal_curve = len(values) * (bin_edges[1] - bin_edges[0]) * stats.norm.pdf(x_range, mean, std)
    
    chart_data = {
        'data': [
            {
                'x': bin_centers.tolist(),
                'y': hist.tolist(),
                'type': 'bar',
                'name': 'Data Distribution',
                'marker': {'color': 'lightblue', 'opacity': 0.7},
                'hovertemplate': 'Value: %{x:.3f}<br>Count: %{y}<extra></extra>'
            },
            {
                'x': x_range.tolist(),
                'y': normal_curve.tolist(),
                'type': 'scatter',
                'mode': 'lines',
                'name': 'Normal Curve',
                'line': {'color': 'blue', 'width': 2},
                'hovertemplate': 'Value: %{x:.3f}<br>Density: %{y:.1f}<extra></extra>'
            }
        ],
        'layout': {
            'title': {
                'text': f'Process Capability Analysis<br><sub>Cp={cp:.3f}, Cpk={cpk:.3f}, PPM={ppm_total:.0f}</sub>',
                'x': 0.5
            },
            'xaxis': {'title': measurement_col},
            'yaxis': {'title': 'Frequency'},
            'shapes': [
                # LSL
                {
                    'type': 'line',
                    'x0': lsl, 'x1': lsl,
                    'y0': 0, 'y1': 1,
                    'yref': 'paper',
                    'line': {'color': 'red', 'width': 3, 'dash': 'dash'}
                },
                # USL
                {
                    'type': 'line',
                    'x0': usl, 'x1': usl,
                    'y0': 0, 'y1': 1,
                    'yref': 'paper',
                    'line': {'color': 'red', 'width': 3, 'dash': 'dash'}
                },
                # Target (if specified)
                *([{
                    'type': 'line',
                    'x0': target, 'x1': target,
                    'y0': 0, 'y1': 1,
                    'yref': 'paper',
                    'line': {'color': 'green', 'width': 2}
                }] if target else [])
            ],
            'annotations': [
                {'x': lsl, 'y': 1.02, 'yref': 'paper', 'text': f'LSL={lsl}', 'showarrow': False},
                {'x': usl, 'y': 1.02, 'yref': 'paper', 'text': f'USL={usl}', 'showarrow': False},
                *([{'x': target, 'y': 1.02, 'yref': 'paper', 'text': f'Target={target}', 'showarrow': False}] if target else []),
                # ESTIEM Branding
                {
                    'text': 'ESTIEM EDA Toolkit | estiem.org',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.99, 'y': 0.01,
                    'showarrow': False,
                    'font': {'size': 10, 'color': 'gray'},
                    'xanchor': 'right'
                }
            ],
            'template': 'plotly_white'
        }
    }
    
    # Statistics
    statistics = {
        'sample_size': len(values),
        'mean': mean,
        'std': std,
        'cp': cp,
        'cpu': cpu,
        'cpl': cpl,
        'cpk': cpk,
        'ppm_total': ppm_total,
        'sigma_level': sigma_level
    }
    
    if target:
        statistics['cpm'] = cpm
    
    # Interpretation
    if cpk < 1.0:
        capability_status = "❌ NOT CAPABLE"
        recommendation = "Process cannot meet specifications reliably. Reduce variation and/or adjust centering."
    elif cpk < 1.33:
        capability_status = "⚠️ MARGINALLY CAPABLE"
        recommendation = "Process barely meets specifications. Improvement recommended."
    elif cpk < 2.0:
        capability_status = "✅ CAPABLE"
        recommendation = "Process is capable but monitor for drift."
    else:
        capability_status = "🏆 EXCELLENT"
        recommendation = "World-class process capability. Maintain current performance."
    
    interpretation = f"{capability_status} (Cpk={cpk:.3f}). Expected defect rate: {ppm_total:.0f} PPM (Sigma Level: {sigma_level:.1f}). {recommendation}"
    
    return {
        'analysis_type': 'capability',
        'chart_data': json.dumps(chart_data),
        'statistics': statistics,
        'interpretation': interpretation
    }


def create_anova_analysis(df, headers, parameters):
    """One-way ANOVA Analysis"""
    
    value_col = parameters.get('valueColumn')
    group_col = parameters.get('groupColumn')
    
    if not value_col or not group_col:
        raise ValueError('Value column and group column must be specified')
    
    if value_col not in df.columns or group_col not in df.columns:
        raise ValueError('Specified columns not found in data')
    
    # Clean data
    clean_df = df[[value_col, group_col]].dropna()
    
    if len(clean_df) < 6:
        raise ValueError('Need at least 6 data points for ANOVA')
    
    # Group data
    groups = {}
    group_names = clean_df[group_col].unique()
    
    for group in group_names:
        group_data = clean_df[clean_df[group_col] == group][value_col].values
        if len(group_data) >= 2:  # Need at least 2 points per group
            groups[str(group)] = group_data
    
    if len(groups) < 2:
        raise ValueError('Need at least 2 groups with sufficient data for ANOVA')
    
    # Perform ANOVA
    group_arrays = list(groups.values())
    f_stat, p_value = stats.f_oneway(*group_arrays)
    
    # Effect size (eta squared)
    grand_mean = np.mean([val for group in group_arrays for val in group])
    ss_total = sum([(val - grand_mean) ** 2 for group in group_arrays for val in group])
    ss_within = sum([np.sum((group - np.mean(group)) ** 2) for group in group_arrays])
    ss_between = ss_total - ss_within
    eta_squared = ss_between / ss_total if ss_total > 0 else 0
    
    # Group statistics
    group_stats = {}
    for name, data in groups.items():
        group_stats[name] = {
            'mean': np.mean(data),
            'std': np.std(data, ddof=1),
            'count': len(data)
        }
    
    # Post-hoc analysis (Tukey HSD) if significant
    post_hoc = None
    if p_value < 0.05 and len(groups) > 2:
        try:
            # Simple pairwise t-tests with Bonferroni correction
            group_names_list = list(groups.keys())
            comparisons = []
            n_comparisons = len(group_names_list) * (len(group_names_list) - 1) // 2
            
            for i in range(len(group_names_list)):
                for j in range(i + 1, len(group_names_list)):
                    group1_name = group_names_list[i]
                    group2_name = group_names_list[j]
                    t_stat, p_val = stats.ttest_ind(groups[group1_name], groups[group2_name])
                    adjusted_p = min(1.0, p_val * n_comparisons)  # Bonferroni correction
                    
                    comparisons.append({
                        'groups': f'{group1_name} vs {group2_name}',
                        'p_value': adjusted_p,
                        'significant': adjusted_p < 0.05
                    })
            
            post_hoc = {'comparisons': comparisons}
        except:
            post_hoc = None
    
    # Create box plot
    box_data = []
    for name, data in groups.items():
        box_data.append({
            'y': data.tolist(),
            'name': name,
            'type': 'box',
            'boxpoints': 'outliers',
            'jitter': 0.3,
            'pointpos': -1.8
        })
    
    chart_data = {
        'data': box_data,
        'layout': {
            'title': {
                'text': f'ANOVA: {value_col} by {group_col}<br><sub>F({len(groups)-1}, {len(clean_df)-len(groups)}) = {f_stat:.3f}, p = {p_value:.4f}</sub>',
                'x': 0.5
            },
            'xaxis': {'title': group_col},
            'yaxis': {'title': value_col},
            'annotations': [
                # ESTIEM Branding
                {
                    'text': 'ESTIEM EDA Toolkit | estiem.org',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.99, 'y': 0.01,
                    'showarrow': False,
                    'font': {'size': 10, 'color': 'gray'},
                    'xanchor': 'right'
                }
            ],
            'template': 'plotly_white'
        }
    }
    
    # Statistics
    statistics = {
        'f_statistic': f_stat,
        'p_value': p_value,
        'effect_size_eta_squared': eta_squared,
        'groups_count': len(groups),
        'total_sample_size': len(clean_df),
        'significant': p_value < 0.05
    }
    
    # Add group statistics
    for name, stats_dict in group_stats.items():
        statistics[f'group_{name}_mean'] = stats_dict['mean']
        statistics[f'group_{name}_std'] = stats_dict['std']
        statistics[f'group_{name}_n'] = stats_dict['count']
    
    # Interpretation
    if p_value < 0.001:
        significance_level = "highly significant (p < 0.001)"
    elif p_value < 0.01:
        significance_level = "very significant (p < 0.01)"
    elif p_value < 0.05:
        significance_level = "significant (p < 0.05)"
    else:
        significance_level = f"not significant (p = {p_value:.3f})"
    
    effect_interpretation = ""
    if eta_squared > 0.14:
        effect_interpretation = " with a large effect size"
    elif eta_squared > 0.06:
        effect_interpretation = " with a medium effect size"
    elif eta_squared > 0.01:
        effect_interpretation = " with a small effect size"
    
    interpretation = f"The ANOVA result is {significance_level}{effect_interpretation} (η² = {eta_squared:.3f}). "
    
    if p_value < 0.05:
        interpretation += f"There are statistically significant differences between the {len(groups)} groups."
        if post_hoc:
            sig_pairs = [comp['groups'] for comp in post_hoc['comparisons'] if comp['significant']]
            if sig_pairs:
                interpretation += f" Post-hoc tests show significant differences between: {', '.join(sig_pairs)}."
    else:
        interpretation += "No statistically significant differences found between groups."
    
    return {
        'analysis_type': 'anova',
        'chart_data': json.dumps(chart_data),
        'statistics': statistics,
        'interpretation': interpretation,
        'post_hoc': post_hoc
    }


def create_pareto_analysis(df, headers, parameters):
    """Pareto Analysis (80/20 Rule)"""
    
    # Auto-detect category and count columns
    text_cols = df.select_dtypes(include=['object', 'string']).columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(text_cols) == 0:
        raise ValueError('No categorical columns found for Pareto analysis')
    
    # Use first text column as category, sum numeric columns if available
    category_col = text_cols[0]
    
    if len(numeric_cols) > 0:
        # Sum by category
        count_col = numeric_cols[0]
        category_counts = df.groupby(category_col)[count_col].sum().sort_values(ascending=False)
    else:
        # Count occurrences
        category_counts = df[category_col].value_counts()
    
    if len(category_counts) < 2:
        raise ValueError('Need at least 2 categories for Pareto analysis')
    
    # Calculate percentages and cumulative percentages
    total = category_counts.sum()
    percentages = (category_counts / total * 100)
    cumulative_percentages = percentages.cumsum()
    
    # Identify vital few (80% threshold)
    vital_few_mask = cumulative_percentages <= 80
    vital_few_categories = category_counts[vital_few_mask].index.tolist()
    vital_few_percentage = cumulative_percentages[vital_few_mask].iloc[-1] if len(vital_few_categories) > 0 else 0
    
    # Calculate Gini coefficient (inequality measure)
    sorted_counts = np.sort(category_counts.values)
    n = len(sorted_counts)
    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * sorted_counts)) / (n * np.sum(sorted_counts)) - (n + 1) / n
    
    # Create Pareto chart
    categories = category_counts.index.tolist()
    counts = category_counts.values.tolist()
    
    chart_data = {
        'data': [
            {
                'x': categories,
                'y': counts,
                'type': 'bar',
                'name': 'Count',
                'marker': {
                    'color': ['#d62728' if cat in vital_few_categories else '#1f77b4' 
                             for cat in categories]
                },
                'yaxis': 'y',
                'hovertemplate': 'Category: %{x}<br>Count: %{y}<br>Percentage: %{customdata:.1f}%<extra></extra>',
                'customdata': percentages.values.tolist()
            },
            {
                'x': categories,
                'y': cumulative_percentages.values.tolist(),
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Cumulative %',
                'line': {'color': 'orange', 'width': 3},
                'marker': {'color': 'orange', 'size': 8},
                'yaxis': 'y2',
                'hovertemplate': 'Category: %{x}<br>Cumulative: %{y:.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': {
                'text': f'Pareto Analysis: {category_col}<br><sub>Vital Few: {len(vital_few_categories)} categories = {vital_few_percentage:.1f}%</sub>',
                'x': 0.5
            },
            'xaxis': {'title': category_col},
            'yaxis': {
                'title': 'Count',
                'side': 'left'
            },
            'yaxis2': {
                'title': 'Cumulative Percentage (%)',
                'side': 'right',
                'overlaying': 'y',
                'range': [0, 100]
            },
            'shapes': [
                # 80% line
                {
                    'type': 'line',
                    'x0': 0, 'x1': 1,
                    'y0': 80, 'y1': 80,
                    'xref': 'paper',
                    'yref': 'y2',
                    'line': {'color': 'red', 'dash': 'dash', 'width': 2}
                }
            ],
            'annotations': [
                {
                    'x': 0.5, 'y': 82,
                    'xref': 'paper', 'yref': 'y2',
                    'text': '80% Threshold',
                    'showarrow': False,
                    'font': {'color': 'red'}
                },
                # ESTIEM Branding
                {
                    'text': 'ESTIEM EDA Toolkit | estiem.org',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.99, 'y': 0.01,
                    'showarrow': False,
                    'font': {'size': 10, 'color': 'gray'},
                    'xanchor': 'right'
                }
            ],
            'template': 'plotly_white',
            'legend': {'x': 0.7, 'y': 0.95}
        }
    }
    
    # Statistics
    statistics = {
        'total_categories': len(categories),
        'vital_few_count': len(vital_few_categories),
        'vital_few_percentage': vital_few_percentage,
        'trivial_many_count': len(categories) - len(vital_few_categories),
        'gini_coefficient': gini,
        'top_3_categories': categories[:3] if len(categories) >= 3 else categories
    }
    
    # Add top category statistics
    for i, (cat, count) in enumerate(category_counts.head(5).items()):
        statistics[f'rank_{i+1}_category'] = str(cat)
        statistics[f'rank_{i+1}_count'] = count
        statistics[f'rank_{i+1}_percentage'] = float(percentages.iloc[i])
    
    # Interpretation
    inequality_level = ""
    if gini > 0.7:
        inequality_level = "very high inequality (strong 80/20 pattern)"
    elif gini > 0.5:
        inequality_level = "high inequality (moderate 80/20 pattern)"
    elif gini > 0.3:
        inequality_level = "moderate inequality (weak 80/20 pattern)"
    else:
        inequality_level = "low inequality (no clear 80/20 pattern)"
    
    interpretation = f"📊 Pareto Analysis reveals {inequality_level} (Gini = {gini:.3f}). "
    interpretation += f"The vital few ({len(vital_few_categories)} out of {len(categories)} categories) account for {vital_few_percentage:.1f}% of the total impact. "
    interpretation += f"Focus improvement efforts on: {', '.join(vital_few_categories[:3])}."
    
    return {
        'analysis_type': 'pareto',
        'chart_data': json.dumps(chart_data),
        'statistics': statistics,
        'interpretation': interpretation
    }


def create_probability_plot(df, headers, parameters):
    """Probability Plot with Confidence Intervals"""
    
    # Find numeric column
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        raise ValueError('No numeric columns found for probability plot')
    
    measurement_col = numeric_cols[0]
    values = df[measurement_col].dropna().values
    
    if len(values) < 5:
        raise ValueError('Need at least 5 data points for probability plot')
    
    # Sort data
    sorted_values = np.sort(values)
    n = len(sorted_values)
    
    # Calculate plotting positions (median rank formula)
    plotting_positions = (np.arange(1, n + 1) - 0.3) / (n + 0.4)
    
    # Theoretical quantiles (normal distribution)
    theoretical_quantiles = stats.norm.ppf(plotting_positions)
    
    # Fit normal distribution
    mean, std = stats.norm.fit(values)
    
    # Calculate 95% confidence intervals for percentiles
    alpha = 0.05
    z_score = stats.norm.ppf(1 - alpha/2)
    
    # Standard error for plotting positions
    se = np.sqrt(plotting_positions * (1 - plotting_positions) / n)
    
    # Confidence intervals for plotting positions
    p_lower = np.maximum(0.001, plotting_positions - z_score * se)
    p_upper = np.minimum(0.999, plotting_positions + z_score * se)
    
    # Transform to value space
    ci_lower = stats.norm.ppf(p_lower, mean, std)
    ci_upper = stats.norm.ppf(p_upper, mean, std)
    
    # Calculate correlation coefficient (goodness of fit)
    correlation = np.corrcoef(theoretical_quantiles, sorted_values)[0, 1]
    
    # Anderson-Darling test
    ad_statistic, critical_values, significance_level = stats.anderson(values, dist='norm')
    
    # Identify outliers (points outside confidence intervals)
    outliers = []
    for i, val in enumerate(sorted_values):
        if val < ci_lower[i] or val > ci_upper[i]:
            outliers.append(val)
    
    # Create probability plot
    fitted_line_x = np.linspace(theoretical_quantiles.min(), theoretical_quantiles.max(), 100)
    fitted_line_y = mean + std * fitted_line_x
    
    chart_data = {
        'data': [
            # Confidence interval band
            {
                'x': np.concatenate([theoretical_quantiles, theoretical_quantiles[::-1]]).tolist(),
                'y': np.concatenate([ci_upper, ci_lower[::-1]]).tolist(),
                'fill': 'toself',
                'fillcolor': 'rgba(128, 128, 128, 0.2)',
                'line': {'color': 'rgba(255,255,255,0)'},
                'showlegend': False,
                'hoverinfo': 'skip',
                'name': '95% Confidence Interval'
            },
            # Data points
            {
                'x': theoretical_quantiles.tolist(),
                'y': sorted_values.tolist(),
                'mode': 'markers',
                'type': 'scatter',
                'name': 'Data Points',
                'marker': {
                    'size': 8,
                    'color': ['red' if val in outliers else '#1f77b4' for val in sorted_values],
                    'line': {'width': 1, 'color': 'white'}
                },
                'hovertemplate': 'Theoretical: %{x:.3f}<br>Observed: %{y:.3f}<extra></extra>'
            },
            # Fitted line
            {
                'x': fitted_line_x.tolist(),
                'y': fitted_line_y.tolist(),
                'mode': 'lines',
                'type': 'scatter',
                'name': 'Normal Fit',
                'line': {'color': 'red', 'width': 2},
                'hovertemplate': 'Normal Fit<br>Theoretical: %{x:.3f}<br>Expected: %{y:.3f}<extra></extra>'
            }
        ],
        'layout': {
            'title': {
                'text': f'Normal Probability Plot: {measurement_col}<br><sub>Correlation = {correlation:.4f}, Anderson-Darling = {ad_statistic:.3f}</sub>',
                'x': 0.5
            },
            'xaxis': {
                'title': 'Theoretical Quantiles',
                'showgrid': True,
                'gridcolor': 'lightgray'
            },
            'yaxis': {
                'title': 'Sample Quantiles',
                'showgrid': True,
                'gridcolor': 'lightgray'
            },
            'annotations': [
                # Goodness of fit annotation
                {
                    'text': f'Goodness of Fit: {"Excellent" if correlation > 0.99 else "Good" if correlation > 0.98 else "Fair" if correlation > 0.95 else "Poor"}',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.02, 'y': 0.98,
                    'showarrow': False,
                    'bgcolor': 'white',
                    'bordercolor': 'gray',
                    'borderwidth': 1,
                    'font': {'size': 10}
                },
                # ESTIEM Branding
                {
                    'text': 'ESTIEM EDA Toolkit | estiem.org',
                    'xref': 'paper', 'yref': 'paper',
                    'x': 0.99, 'y': 0.01,
                    'showarrow': False,
                    'font': {'size': 10, 'color': 'gray'},
                    'xanchor': 'right'
                }
            ],
            'template': 'plotly_white',
            'hovermode': 'closest'
        }
    }
    
    # Statistics
    statistics = {
        'sample_size': n,
        'mean': mean,
        'std': std,
        'correlation_coefficient': correlation,
        'anderson_darling_statistic': ad_statistic,
        'outliers_count': len(outliers),
        'percentile_5': np.percentile(values, 5),
        'percentile_25': np.percentile(values, 25),
        'percentile_50': np.percentile(values, 50),
        'percentile_75': np.percentile(values, 75),
        'percentile_95': np.percentile(values, 95)
    }
    
    # Interpretation
    fit_quality = "excellent" if correlation > 0.99 else "good" if correlation > 0.98 else "fair" if correlation > 0.95 else "poor"
    
    if correlation > 0.98:
        normality_assessment = "✅ Data strongly follows a normal distribution"
    elif correlation > 0.95:
        normality_assessment = "⚠️ Data reasonably follows a normal distribution with some deviation"
    else:
        normality_assessment = "❌ Data shows poor fit to normal distribution"
    
    outlier_assessment = ""
    if len(outliers) == 0:
        outlier_assessment = "✅ No outliers detected"
    elif len(outliers) <= 2:
        outlier_assessment = f"⚠️ {len(outliers)} potential outlier(s) detected"
    else:
        outlier_assessment = f"❌ {len(outliers)} outliers detected - investigate data quality"
    
    interpretation = f"{normality_assessment} ({fit_quality} fit, r={correlation:.4f}). {outlier_assessment}. Anderson-Darling statistic = {ad_statistic:.3f}."
    
    return {
        'analysis_type': 'probability_plot',
        'chart_data': json.dumps(chart_data),
        'statistics': statistics,
        'interpretation': interpretation
    }


def check_western_electric_rules(values, mean, sigma):
    """Check for Western Electric Rules patterns"""
    patterns = []
    
    # Rule 1: One point beyond 3 sigma (handled in main function)
    
    # Rule 2: Nine points in a row on same side of centerline
    if len(values) >= 9:
        for i in range(len(values) - 8):
            segment = values[i:i+9]
            if all(x > mean for x in segment) or all(x < mean for x in segment):
                patterns.append(f"Rule 2: Nine consecutive points on same side (starting at point {i+1})")
    
    # Rule 3: Six points in a row steadily increasing or decreasing
    if len(values) >= 6:
        for i in range(len(values) - 5):
            segment = values[i:i+6]
            if all(segment[j] < segment[j+1] for j in range(5)) or all(segment[j] > segment[j+1] for j in range(5)):
                patterns.append(f"Rule 3: Six consecutive trending points (starting at point {i+1})")
    
    return patterns