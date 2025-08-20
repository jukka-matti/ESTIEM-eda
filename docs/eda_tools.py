"""
ESTIEM EDA Toolkit - Browser Exploratory Data Analysis Tools
Pure NumPy/SciPy implementation for reliable browser execution
"""

try:
    import numpy as np
    from scipy import stats
    import json
    import math
    print("✅ All required packages imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    raise


# Core validation functions (copied from core module for browser compatibility)

def validate_numeric_data(data, min_points=3):
    """Validate and clean numeric data for browser environment"""
    if isinstance(data, dict):
        if 'data' in data:
            data = data['data']
        else:
            for value in data.values():
                if isinstance(value, (list, tuple)):
                    data = value
                    break
            else:
                raise ValueError("No suitable numeric data found")
    
    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], dict):
            # Find first numeric column
            numeric_col = None
            for key in data[0].keys():
                try:
                    float(data[0][key])
                    numeric_col = key
                    break
                except (ValueError, TypeError):
                    continue
            
            if numeric_col is None:
                raise ValueError("No numeric columns found")
            
            values = []
            for row in data:
                try:
                    val = float(row[numeric_col])
                    if not (math.isnan(val) or math.isinf(val)):
                        values.append(val)
                except (ValueError, TypeError, KeyError):
                    continue
            data = values
    
    # Convert to numpy array
    try:
        values = np.array(data, dtype=float)
        values = values[np.isfinite(values)]
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot convert to numeric array: {e}")
    
    if len(values) < min_points:
        raise ValueError(f"Need at least {min_points} valid points, got {len(values)}")
    
    return values


def validate_groups_data(data):
    """Validate groups data for ANOVA"""
    if not isinstance(data, dict) or len(data) < 2:
        raise ValueError("Need at least 2 groups")
    
    validated_groups = {}
    for name, group_data in data.items():
        values = validate_numeric_data(group_data, min_points=2)
        validated_groups[str(name)] = values
    
    if len(validated_groups) < 2:
        raise ValueError("Need at least 2 valid groups")
    
    return validated_groups


def validate_pareto_data(data):
    """Validate Pareto data"""
    if isinstance(data, list) and data and isinstance(data[0], dict):
        # Convert list of records
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
            categories = {}
            for row in data:
                cat = str(row[cat_col])
                categories[cat] = categories.get(cat, 0) + 1
            data = categories
        else:
            categories = {}
            for row in data:
                cat = str(row[cat_col])
                val = float(row[val_col])
                categories[cat] = categories.get(cat, 0) + val
            data = categories
    
    if not isinstance(data, dict) or not data:
        raise ValueError("Invalid Pareto data format")
    
    validated_data = {}
    for category, value in data.items():
        try:
            val = float(value)
            if val < 0:
                raise ValueError(f"Negative value: {val}")
            validated_data[str(category)] = val
        except (ValueError, TypeError):
            raise ValueError(f"Invalid value for {category}")
    
    if sum(validated_data.values()) == 0:
        raise ValueError("All values are zero")
    
    return validated_data


# Core calculation functions (simplified for browser)

def calculate_i_chart(values, title="I-Chart Analysis"):
    """Calculate I-Chart statistics"""
    n = len(values)
    mean = np.mean(values)
    
    # Moving range
    moving_range = np.abs(np.diff(values))
    avg_mr = np.mean(moving_range)
    
    # Control limits
    d2 = 1.128
    sigma_hat = avg_mr / d2
    ucl = mean + 3 * sigma_hat
    lcl = mean - 3 * sigma_hat
    
    # Out of control points
    out_of_control = []
    for i, value in enumerate(values):
        if value > ucl or value < lcl:
            out_of_control.append(i)
    
    return {
        'success': True,
        'statistics': {
            'sample_size': n,
            'mean': mean,
            'sigma_hat': sigma_hat,
            'ucl': ucl,
            'lcl': lcl,
            'out_of_control_points': len(out_of_control)
        },
        'out_of_control_indices': out_of_control,
        'data_points': values.tolist(),
        'interpretation': f"Process {'appears stable' if len(out_of_control) == 0 else f'has {len(out_of_control)} out-of-control points'} with mean {mean:.3f}",
        'analysis_type': 'i_chart'
    }


def calculate_process_capability(values, lsl, usl, target=None):
    """Calculate process capability"""
    n = len(values)
    mean = np.mean(values)
    std_dev = np.std(values, ddof=1)
    
    if target is None:
        target = (lsl + usl) / 2
    
    # Capability indices
    tolerance = usl - lsl
    cp = tolerance / (6 * std_dev) if std_dev > 0 else float('inf')
    
    cpu = (usl - mean) / (3 * std_dev) if std_dev > 0 else float('inf')
    cpl = (mean - lsl) / (3 * std_dev) if std_dev > 0 else float('inf')
    cpk = min(cpu, cpl)
    
    # Performance indices
    pp = tolerance / (6 * np.std(values, ddof=0)) if np.std(values, ddof=0) > 0 else float('inf')
    ppk = min((usl - mean) / (3 * np.std(values, ddof=0)), 
              (mean - lsl) / (3 * np.std(values, ddof=0))) if np.std(values, ddof=0) > 0 else float('inf')
    
    # Defect analysis
    z_lower = (lsl - mean) / std_dev if std_dev > 0 else -float('inf')
    z_upper = (usl - mean) / std_dev if std_dev > 0 else float('inf')
    
    ppm_lower = stats.norm.cdf(z_lower) * 1_000_000
    ppm_upper = (1 - stats.norm.cdf(z_upper)) * 1_000_000
    ppm_total = ppm_lower + ppm_upper
    
    # Six Sigma level
    if ppm_total > 0:
        z_shift = stats.norm.ppf(1 - ppm_total / 2_000_000)
        sigma_level = z_shift + 1.5
    else:
        sigma_level = 6.0
    
    capability = "Excellent" if cpk >= 1.67 else "Good" if cpk >= 1.33 else "Marginal" if cpk >= 1.0 else "Poor"
    
    return {
        'success': True,
        'capability_indices': {
            'cp': cp, 'cpk': cpk, 'cpu': cpu, 'cpl': cpl,
            'pp': pp, 'ppk': ppk
        },
        'statistics': {
            'sample_size': n, 'mean': mean, 'std_dev': std_dev,
            'lsl': lsl, 'usl': usl, 'target': target
        },
        'defect_analysis': {
            'ppm_lower': ppm_lower, 'ppm_upper': ppm_upper,
            'ppm_total': ppm_total, 'sigma_level': sigma_level
        },
        'interpretation': f"{capability} process capability (Cpk = {cpk:.3f}). Expected defect rate: {ppm_total:.0f} PPM",
        'analysis_type': 'capability'
    }


def calculate_anova(groups, alpha=0.05):
    """Calculate one-way ANOVA"""
    group_names = list(groups.keys())
    group_data = list(groups.values())
    
    k = len(groups)
    n_total = sum(len(group) for group in group_data)
    
    # Grand mean and group means
    all_data = np.concatenate(group_data)
    grand_mean = np.mean(all_data)
    group_means = [np.mean(group) for group in group_data]
    group_sizes = [len(group) for group in group_data]
    
    # Sum of squares
    ssb = sum(n * (mean - grand_mean)**2 for n, mean in zip(group_sizes, group_means))
    ssw = sum(np.sum((group - np.mean(group))**2) for group in group_data)
    
    # Degrees of freedom
    df_between = k - 1
    df_within = n_total - k
    
    # Mean squares
    msb = ssb / df_between if df_between > 0 else 0
    msw = ssw / df_within if df_within > 0 else 0
    
    # F-statistic
    f_statistic = msb / msw if msw > 0 else float('inf')
    p_value = 1 - stats.f.cdf(f_statistic, df_between, df_within)
    significant = p_value < alpha
    
    return {
        'success': True,
        'anova_results': {
            'f_statistic': f_statistic,
            'p_value': p_value,
            'significant': significant,
            'alpha': alpha
        },
        'group_statistics': {
            name: {
                'mean': np.mean(data),
                'std': np.std(data, ddof=1),
                'size': len(data)
            } for name, data in groups.items()
        },
        'grand_mean': grand_mean,
        'interpretation': f"{'Significant' if significant else 'No significant'} difference between groups (F = {f_statistic:.3f}, p = {p_value:.4f})",
        'analysis_type': 'anova'
    }


def calculate_pareto(data, threshold=0.8):
    """Calculate Pareto analysis"""
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    total = sum(data.values())
    
    categories = []
    values = []
    percentages = []
    cumulative_percentages = []
    
    cumulative = 0
    for category, value in sorted_items:
        categories.append(category)
        values.append(value)
        
        percentage = (value / total) * 100
        percentages.append(percentage)
        
        cumulative += percentage
        cumulative_percentages.append(cumulative)
    
    # Find vital few
    vital_few_indices = []
    for i, cum_pct in enumerate(cumulative_percentages):
        vital_few_indices.append(i)
        if cum_pct >= threshold * 100:
            break
    
    vital_few_categories = [categories[i] for i in vital_few_indices]
    vital_few_percentage = cumulative_percentages[vital_few_indices[-1]]
    
    # Gini coefficient
    sorted_values = sorted(values)
    n = len(sorted_values)
    gini_sum = sum((2 * (i + 1) - n - 1) * value for i, value in enumerate(sorted_values))
    gini = gini_sum / (n * total) if total > 0 else 0
    
    return {
        'success': True,
        'categories': categories,
        'values': values,
        'percentages': percentages,
        'cumulative_percentages': cumulative_percentages,
        'vital_few': {
            'categories': vital_few_categories,
            'count': len(vital_few_categories),
            'percentage': vital_few_percentage
        },
        'gini_coefficient': {
            'value': gini,
            'interpretation': "High inequality" if gini > 0.5 else "Moderate inequality" if gini > 0.2 else "Low inequality"
        },
        'total_value': total,
        'interpretation': f"{len(vital_few_categories)} categories account for {vital_few_percentage:.1f}% of total impact",
        'analysis_type': 'pareto'
    }


def calculate_probability_plot(values, distribution='normal', confidence_level=0.95):
    """Calculate probability plot"""
    n = len(values)
    sorted_values = np.sort(values)
    plotting_positions = np.array([(i + 0.5) / n for i in range(n)])
    
    if distribution == 'normal':
        theoretical_quantiles = stats.norm.ppf(plotting_positions)
        transformed_data = sorted_values
    elif distribution == 'lognormal':
        if np.any(sorted_values <= 0):
            raise ValueError("Lognormal requires positive values")
        theoretical_quantiles = stats.norm.ppf(plotting_positions)
        transformed_data = np.log(sorted_values)
    elif distribution == 'weibull':
        if np.any(sorted_values <= 0):
            raise ValueError("Weibull requires positive values")
        theoretical_quantiles = np.log(-np.log(1 - plotting_positions))
        transformed_data = np.log(sorted_values)
    else:
        raise ValueError(f"Unsupported distribution: {distribution}")
    
    # Correlation coefficient
    correlation = np.corrcoef(theoretical_quantiles, transformed_data)[0, 1]
    
    # Simple outlier detection
    residuals = transformed_data - np.mean(transformed_data)
    outlier_threshold = 2 * np.std(residuals)
    outliers = [i for i, res in enumerate(residuals) if abs(res) > outlier_threshold]
    
    # Fit quality
    if correlation >= 0.99:
        fit_quality = "Excellent"
    elif correlation >= 0.95:
        fit_quality = "Good"
    elif correlation >= 0.90:
        fit_quality = "Fair"
    else:
        fit_quality = "Poor"
    
    return {
        'success': True,
        'distribution': distribution,
        'plotting_positions': plotting_positions.tolist(),
        'theoretical_quantiles': theoretical_quantiles.tolist(),
        'sorted_values': sorted_values.tolist(),
        'goodness_of_fit': {
            'correlation_coefficient': correlation,
            'interpretation': fit_quality
        },
        'outliers': {
            'indices': outliers,
            'count': len(outliers),
            'values': [sorted_values[i] for i in outliers]
        },
        'confidence_level': confidence_level,
        'interpretation': f"{fit_quality} fit to {distribution} distribution (r = {correlation:.4f})",
        'analysis_type': 'probability_plot'
    }


# Main analysis dispatcher
def run_analysis(analysis_type, data, headers, parameters):
    """Main analysis dispatcher - browser optimized"""
    
    try:
        print(f"✅ Processing {analysis_type} analysis")
        
        if analysis_type == 'i_chart':
            values = validate_numeric_data(data, min_points=3)
            title = parameters.get('title', 'I-Chart Analysis')
            return calculate_i_chart(values, title)
            
        elif analysis_type == 'capability':
            values = validate_numeric_data(data, min_points=10)
            lsl = float(parameters.get('lsl'))
            usl = float(parameters.get('usl'))
            target = parameters.get('target')
            if target is not None:
                target = float(target)
            return calculate_process_capability(values, lsl, usl, target)
            
        elif analysis_type == 'anova':
            if isinstance(data, dict):
                groups = validate_groups_data(data)
            else:
                raise ValueError("ANOVA requires grouped data")
            alpha = float(parameters.get('alpha', 0.05))
            return calculate_anova(groups, alpha)
            
        elif analysis_type == 'pareto':
            pareto_data = validate_pareto_data(data)
            threshold = float(parameters.get('threshold', 0.8))
            return calculate_pareto(pareto_data, threshold)
            
        elif analysis_type == 'probability_plot':
            values = validate_numeric_data(data, min_points=3)
            distribution = parameters.get('distribution', 'normal')
            confidence_level = float(parameters.get('confidence_level', 0.95))
            return calculate_probability_plot(values, distribution, confidence_level)
            
        else:
            raise ValueError(f'Unknown analysis type: {analysis_type}')
            
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'analysis_type': analysis_type
        }


# Sample data generators
def generate_sample_data(sample_type):
    """Generate sample data for testing"""
    np.random.seed(42)
    
    if sample_type == 'manufacturing':
        n = 100
        lines = ['Line_A', 'Line_B', 'Line_C']
        
        data = []
        for i in range(n):
            line = np.random.choice(lines)
            if line == 'Line_A':
                measurement = np.random.normal(10.0, 0.3)
            elif line == 'Line_B':
                measurement = np.random.normal(9.8, 0.5)
            else:
                measurement = np.random.normal(10.2, 0.4)
            
            data.append({
                'sample_id': i + 1,
                'measurement': round(measurement, 3),
                'line': line,
                'defects': int(np.random.poisson(2)),
                'temperature': round(np.random.normal(25, 2), 1)
            })
        
        return {'data': data, 'headers': ['sample_id', 'measurement', 'line', 'defects', 'temperature']}
        
    elif sample_type == 'quality':
        defect_types = ['Surface', 'Dimensional', 'Assembly', 'Material', 'Electrical']
        defect_counts = [45, 32, 18, 12, 8]
        
        data = []
        for defect_type, count in zip(defect_types, defect_counts):
            data.append({
                'defect_type': defect_type,
                'count': count
            })
        
        return {'data': data, 'headers': ['defect_type', 'count']}
        
    elif sample_type == 'process':
        n = 100
        data = []
        for i in range(n):
            value = 100 + 0.1 * i + np.random.normal(0, 2)
            data.append({
                'time': i + 1,
                'process_value': round(value, 2),
                'temperature': round(np.random.normal(80, 5), 1)
            })
        
        return {'data': data, 'headers': ['time', 'process_value', 'temperature']}
    
    return {'data': [], 'headers': []}