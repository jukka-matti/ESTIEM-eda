#!/usr/bin/env python3
"""
ESTIEM EDA Toolkit - Command Line Interface
Exploratory Data Analysis from the command line
"""

import click
import numpy as np
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, Union
import json
import csv
from datetime import datetime

from .core.calculations import (
    calculate_i_chart,
    calculate_process_capability,
    calculate_anova,
    calculate_pareto,
    calculate_probability_plot
)
from .core.validation import (
    validate_numeric_data,
    validate_groups_data,
    validate_pareto_data
)


class EstiemCLI:
    """ESTIEM EDA command line interface"""
    
    def __init__(self):
        pass
    
    def load_data(self, file_path: str) -> Dict[str, Any]:
        """Load data from CSV file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                for row in reader:
                    # Convert numeric values
                    converted_row = {}
                    for key, value in row.items():
                        try:
                            converted_row[key] = float(value)
                        except (ValueError, TypeError):
                            converted_row[key] = value
                    data.append(converted_row)
            
            if not data:
                raise ValueError("CSV file is empty")
            
            result = {'data': data, 'headers': headers}
            click.echo(f"✅ Loaded {len(data)} rows × {len(headers)} columns from {file_path}")
            return result
        
        except Exception as e:
            click.echo(f"❌ Error loading data: {e}", err=True)
            sys.exit(1)
    
    def save_results(self, results: Dict[str, Any], output_path: str, format: str = 'html'):
        """Save analysis results to file"""
        try:
            output_file = Path(output_path)
            
            if format == 'html' and 'visualization' in results:
                # Save HTML with chart
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(self._create_html_report(results))
                click.echo(f"💾 HTML report saved to: {output_file}")
            
            elif format == 'json':
                # Save JSON results (excluding HTML)
                json_results = {k: v for k, v in results.items() if k != 'visualization'}
                with open(output_file, 'w') as f:
                    json.dump(json_results, f, indent=2, default=str)
                click.echo(f"💾 JSON results saved to: {output_file}")
            
            else:
                # Save text summary
                with open(output_file, 'w') as f:
                    f.write(self._create_text_report(results))
                click.echo(f"💾 Text report saved to: {output_file}")
        
        except Exception as e:
            click.echo(f"❌ Error saving results: {e}", err=True)
    
    def _create_html_report(self, results: Dict[str, Any]) -> str:
        """Create HTML report with embedded chart"""
        title = results.get('analysis_type', 'Analysis').replace('_', ' ').title()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESTIEM EDA - {title} Report</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background: #f8f9fa;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px; 
            border-bottom: 2px solid #0066cc; 
            padding-bottom: 20px;
        }}
        .header h1 {{ 
            color: #003f7f; 
            margin-bottom: 10px; 
        }}
        .chart-container {{ 
            margin: 30px 0; 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px;
        }}
        .stats-section {{ 
            background: #f0f8ff; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0;
        }}
        .stats-table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
        }}
        .stats-table td {{ 
            padding: 8px 12px; 
            border-bottom: 1px solid #ddd; 
        }}
        .stats-table td:first-child {{ 
            font-weight: bold; 
            color: #003f7f; 
        }}
        .interpretation {{ 
            background: #e8f5e8; 
            padding: 20px; 
            margin: 20px 0; 
            border-left: 4px solid #28a745; 
            border-radius: 0 8px 8px 0;
        }}
        .footer {{ 
            text-align: center; 
            margin-top: 40px; 
            padding-top: 20px; 
            border-top: 1px solid #ddd; 
            color: #666; 
            font-size: 14px;
        }}
        .estiem-badge {{
            background: linear-gradient(135deg, #003f7f, #0066cc);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {title} Analysis</h1>
            <div class="estiem-badge">ESTIEM EDA Toolkit</div>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="chart-container">
            <div id="chart"></div>
        </div>
        
        <div class="stats-section">
            <h2>📈 Statistical Summary</h2>
            <table class="stats-table">
        """
        
        # Add statistics table
        if 'statistics' in results:
            for key, value in results['statistics'].items():
                formatted_key = key.replace('_', ' ').title()
                formatted_value = f"{value:.4f}" if isinstance(value, (int, float)) else str(value)
                html += f"<tr><td>{formatted_key}</td><td>{formatted_value}</td></tr>"
        
        html += """
            </table>
        </div>
        """
        
        # Add interpretation
        if 'interpretation' in results:
            html += f"""
        <div class="interpretation">
            <h2>🎯 Interpretation</h2>
            <p>{results['interpretation']}</p>
        </div>
        """
        
        html += f"""
        <div class="footer">
            <p><strong>Generated by ESTIEM EDA Toolkit</strong></p>
            <p>CLI Tool • Web App: <a href="https://jukka-matti.github.io/ESTIEM-eda/">https://jukka-matti.github.io/ESTIEM-eda/</a></p>
            <p>ESTIEM - Connecting 60,000+ Industrial Engineering students across Europe</p>
        </div>
    </div>
    
    <script>
        // Load chart if available
        const chartData = {json.dumps(results.get('chart_data', '{}'))};
        if (chartData && chartData !== '{{}}') {{
            try {{
                const data = JSON.parse(chartData);
                Plotly.newPlot('chart', data.data, data.layout, {{responsive: true}});
            }} catch (e) {{
                document.getElementById('chart').innerHTML = '<p>Chart visualization not available</p>';
            }}
        }} else {{
            document.getElementById('chart').innerHTML = '<p>Chart visualization not available in CLI mode</p>';
        }}
    </script>
</body>
</html>
        """
        return html
    
    def _create_text_report(self, results: Dict[str, Any]) -> str:
        """Create text-based report"""
        title = results.get('analysis_type', 'Analysis').replace('_', ' ').title()
        
        report = f"""
ESTIEM EDA TOOLKIT - {title.upper()} ANALYSIS
{'=' * 60}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Tool: ESTIEM EDA CLI

STATISTICAL SUMMARY:
{'-' * 20}
"""
        
        if 'statistics' in results:
            for key, value in results['statistics'].items():
                formatted_key = key.replace('_', ' ').title()
                formatted_value = f"{value:.4f}" if isinstance(value, (int, float)) else str(value)
                report += f"{formatted_key:.<30} {formatted_value}\n"
        
        if 'interpretation' in results:
            report += f"""
INTERPRETATION:
{'-' * 15}
{results['interpretation']}
"""
        
        report += f"""
{'-' * 60}
Generated by ESTIEM EDA Toolkit
Web App: https://jukka-matti.github.io/ESTIEM-eda/
ESTIEM - Connecting 60,000+ Industrial Engineering students
        """
        
        return report


# CLI Commands
cli = EstiemCLI()

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version')
@click.pass_context
def main(ctx, version):
    """
    🏭 ESTIEM EDA Toolkit - Exploratory Data Analysis CLI
    
    Perform exploratory data analysis from the command line.
    Perfect for Industrial Engineering applications, quality control, and process improvement.
    
    Examples:
      estiem-eda i-chart data.csv
      estiem-eda capability data.csv --lsl 9.5 --usl 10.5
      estiem-eda anova data.csv --value measurement --group line
      
    🌐 Web Version: https://jukka-matti.github.io/ESTIEM-eda/
    """
    if version:
        from . import __version__
        click.echo(f"ESTIEM EDA Toolkit v{__version__}")
        return
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        click.echo("\n🎓 Built by ESTIEM for 60,000+ Industrial Engineering students")


@main.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--column', '-c', help='Column name to analyze (default: first numeric column)')
@click.option('--output', '-o', default='i_chart_results.html', help='Output file path')
@click.option('--format', type=click.Choice(['html', 'json', 'txt']), default='html', help='Output format')
@click.option('--title', help='Chart title')
def i_chart(data_file, column, output, format, title):
    """Create Individual Control Chart (I-Chart) for process monitoring."""
    
    click.echo("🏭 ESTIEM EDA - Individual Control Chart Analysis")
    click.echo("=" * 50)
    
    # Load data
    dataset = cli.load_data(data_file)
    
    # Get numeric data
    if column:
        # Extract specific column
        data_values = [row[column] for row in dataset['data'] if isinstance(row.get(column), (int, float))]
    else:
        # Find first numeric column
        for header in dataset['headers']:
            data_values = [row[header] for row in dataset['data'] if isinstance(row.get(header), (int, float))]
            if len(data_values) >= 3:
                column = header
                click.echo(f"🔍 Using column: {column}")
                break
        else:
            click.echo("❌ No suitable numeric column found", err=True)
            sys.exit(1)
    
    try:
        # Validate and run analysis
        values = validate_numeric_data(data_values, min_points=3)
        results = calculate_i_chart(values, title or f'I-Chart Analysis: {data_file}')
        
        # Display summary
        stats = results['statistics']
        click.echo(f"\n📊 Results Summary:")
        click.echo(f"   Sample Size: {stats['sample_size']}")
        click.echo(f"   Process Mean: {stats['mean']:.4f}")
        click.echo(f"   UCL: {stats['ucl']:.4f}")
        click.echo(f"   LCL: {stats['lcl']:.4f}")
        click.echo(f"   Out of Control: {stats['out_of_control_points']} points")
        
        click.echo(f"\n🎯 {results['interpretation']}")
        
        # Save results
        cli.save_results(results, output, format)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--lsl', type=float, required=True, help='Lower Specification Limit')
@click.option('--usl', type=float, required=True, help='Upper Specification Limit')
@click.option('--target', type=float, help='Target value (optional)')
@click.option('--column', '-c', help='Column name to analyze')
@click.option('--output', '-o', default='capability_results.html', help='Output file path')
@click.option('--format', type=click.Choice(['html', 'json', 'txt']), default='html', help='Output format')
def capability(data_file, lsl, usl, target, column, output, format):
    """Process Capability Analysis (Cp, Cpk, Six Sigma level)."""
    
    click.echo("🎯 ESTIEM EDA - Process Capability Analysis")
    click.echo("=" * 50)
    
    # Load data
    dataset = cli.load_data(data_file)
    
    # Get numeric data
    if column:
        # Extract specific column
        data_values = [row[column] for row in dataset['data'] if isinstance(row.get(column), (int, float))]
    else:
        # Find first numeric column
        for header in dataset['headers']:
            data_values = [row[header] for row in dataset['data'] if isinstance(row.get(header), (int, float))]
            if len(data_values) >= 10:
                column = header
                click.echo(f"🔍 Using column: {column}")
                break
        else:
            click.echo("❌ No suitable numeric column found (need 10+ points)", err=True)
            sys.exit(1)
    
    try:
        # Validate and run analysis
        values = validate_numeric_data(data_values, min_points=10)
        results = calculate_process_capability(values, lsl, usl, target)
        
        # Display summary
        stats = results['capability_indices']
        click.echo(f"\n📊 Capability Results:")
        click.echo(f"   Cp:  {stats['cp']:.4f}")
        click.echo(f"   Cpk: {stats['cpk']:.4f}")
        
        defects = results['defect_analysis']
        click.echo(f"   Expected Defects: {defects['ppm_total']:.0f} PPM")
        click.echo(f"   Sigma Level: {defects['sigma_level']:.1f}")
        
        click.echo(f"\n🎯 {results['interpretation']}")
        
        # Save results
        cli.save_results(results, output, format)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--value', required=True, help='Value column name')
@click.option('--group', required=True, help='Group column name')
@click.option('--output', '-o', default='anova_results.html', help='Output file path')
@click.option('--format', type=click.Choice(['html', 'json', 'txt']), default='html', help='Output format')
def anova(data_file, value, group, output, format):
    """One-way Analysis of Variance (ANOVA) for group comparisons."""
    
    click.echo("📊 ESTIEM EDA - ANOVA Analysis")
    click.echo("=" * 50)
    
    # Load data
    dataset = cli.load_data(data_file)
    
    # Prepare groups
    groups_dict = {}
    for row in dataset['data']:
        group_name = row.get(group)
        value_data = row.get(value)
        
        if group_name is not None and isinstance(value_data, (int, float)):
            group_key = str(group_name)
            if group_key not in groups_dict:
                groups_dict[group_key] = []
            groups_dict[group_key].append(float(value_data))
    
    # Filter groups with sufficient data
    groups = {name: data for name, data in groups_dict.items() if len(data) >= 2}
    
    if len(groups) < 2:
        click.echo("❌ Need at least 2 groups with 2+ data points each", err=True)
        sys.exit(1)
    
    try:
        # Validate and run analysis
        validated_groups = validate_groups_data(groups)
        results = calculate_anova(validated_groups)
        
        # Display summary
        stats = results['anova_results']
        click.echo(f"\n📊 ANOVA Results:")
        click.echo(f"   F-statistic: {stats['f_statistic']:.4f}")
        click.echo(f"   p-value: {stats['p_value']:.6f}")
        click.echo(f"   Significant: {'Yes' if stats['significant'] else 'No'}")
        
        click.echo(f"\n🎯 {results['interpretation']}")
        
        # Save results
        cli.save_results(results, output, format)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--category', help='Category column name')
@click.option('--value', help='Value column name (optional, will count if not provided)')
@click.option('--output', '-o', default='pareto_results.html', help='Output file path')
@click.option('--format', type=click.Choice(['html', 'json', 'txt']), default='html', help='Output format')
def pareto(data_file, category, value, output, format):
    """Pareto Analysis for identifying vital few (80/20 rule)."""
    
    click.echo("📉 ESTIEM EDA - Pareto Analysis")
    click.echo("=" * 50)
    
    # Load data
    dataset = cli.load_data(data_file)
    
    # Auto-detect category column if not specified
    if not category:
        # Find first string/categorical column
        for header in dataset['headers']:
            sample_values = [row.get(header) for row in dataset['data'][:10] if row.get(header) is not None]
            if sample_values and any(isinstance(val, str) for val in sample_values):
                category = header
                click.echo(f"🔍 Using category column: {category}")
                break
        else:
            click.echo("❌ No categorical columns found", err=True)
            sys.exit(1)
    
    # Prepare data
    data_dict = {}
    if value:
        # Sum values by category
        for row in dataset['data']:
            cat = row.get(category)
            val = row.get(value)
            if cat is not None and isinstance(val, (int, float)):
                cat_str = str(cat)
                data_dict[cat_str] = data_dict.get(cat_str, 0) + float(val)
    else:
        # Count occurrences
        for row in dataset['data']:
            cat = row.get(category)
            if cat is not None:
                cat_str = str(cat)
                data_dict[cat_str] = data_dict.get(cat_str, 0) + 1
    
    try:
        # Validate and run analysis
        validated_data = validate_pareto_data(data_dict)
        results = calculate_pareto(validated_data)
        
        # Display summary
        stats = results['vital_few']
        click.echo(f"\n📊 Pareto Results:")
        click.echo(f"   Total Categories: {len(data_dict)}")
        click.echo(f"   Vital Few: {len(stats['categories'])} categories")
        click.echo(f"   Impact: {stats['percentage']:.1f}% of total")
        
        sorted_categories = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
        top_3 = [cat for cat, _ in sorted_categories[:3]]
        click.echo(f"   Top 3: {', '.join(top_3)}")
        
        click.echo(f"\n🎯 {results['interpretation']}")
        
        # Save results
        cli.save_results(results, output, format)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--column', '-c', help='Column name to analyze')
@click.option('--distribution', type=click.Choice(['normal', 'lognormal', 'weibull']), default='normal', help='Distribution type')
@click.option('--output', '-o', default='probability_results.html', help='Output file path')
@click.option('--format', type=click.Choice(['html', 'json', 'txt']), default='html', help='Output format')
def probability(data_file, column, distribution, output, format):
    """Probability Plot for assessing distribution fit with confidence intervals."""
    
    click.echo("📋 ESTIEM EDA - Probability Plot Analysis")
    click.echo("=" * 50)
    
    # Load data
    dataset = cli.load_data(data_file)
    
    # Get numeric data
    if column:
        # Extract specific column
        data_values = [row[column] for row in dataset['data'] if isinstance(row.get(column), (int, float))]
    else:
        # Find first numeric column
        for header in dataset['headers']:
            data_values = [row[header] for row in dataset['data'] if isinstance(row.get(header), (int, float))]
            if len(data_values) >= 3:
                column = header
                click.echo(f"🔍 Using column: {column}")
                break
        else:
            click.echo("❌ No suitable numeric column found", err=True)
            sys.exit(1)
    
    try:
        # Validate and run analysis
        values = validate_numeric_data(data_values, min_points=3)
        results = calculate_probability_plot(values, distribution)
        
        # Display summary
        stats = results['goodness_of_fit']
        click.echo(f"\n📊 Probability Plot Results:")
        click.echo(f"   Distribution: {distribution.title()}")
        click.echo(f"   Correlation: {stats['correlation_coefficient']:.4f}")
        click.echo(f"   Fit Quality: {stats['interpretation']}")
        
        outliers = results['outliers']
        click.echo(f"   Outliers: {outliers['count']} detected")
        
        click.echo(f"\n🎯 {results['interpretation']}")
        
        # Save results
        cli.save_results(results, output, format)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--type', 'sample_type', type=click.Choice(['manufacturing', 'quality', 'process']), 
              default='manufacturing', help='Type of sample data to generate')
@click.option('--size', '-n', default=100, help='Number of samples to generate')
@click.option('--output', '-o', default='sample_data.csv', help='Output CSV file')
def sample_data(sample_type, size, output):
    """Generate sample datasets for testing and learning."""
    
    click.echo("🔬 ESTIEM EDA - Sample Data Generator")
    click.echo("=" * 50)
    
    try:
        # Generate sample data
        np.random.seed(42)  # Reproducible results
        
        if sample_type == 'manufacturing':
            data = []
            lines = ['Line_A', 'Line_B', 'Line_C']
            for i in range(size):
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
                    'defects': np.random.poisson(2),
                    'temperature': round(np.random.normal(25, 2), 1)
                })
        
        elif sample_type == 'quality':
            defect_types = ['Surface', 'Dimensional', 'Assembly', 'Material']
            data = []
            for i in range(size):
                defect_type = np.random.choice(defect_types, p=[0.4, 0.3, 0.2, 0.1])
                data.append({
                    'inspection_id': i + 1,
                    'defect_type': defect_type,
                    'defect_count': np.random.poisson(5),
                    'severity': np.random.choice(['Minor', 'Major', 'Critical'], p=[0.6, 0.3, 0.1]),
                    'cost': round(np.random.uniform(10, 100), 2)
                })
        
        else:  # process
            data = []
            for i in range(size):
                # Process with trend and some variation
                value = 100 + 0.1 * i + np.random.normal(0, 2)
                data.append({
                    'time': i + 1,
                    'process_value': round(value, 2),
                    'temperature': round(np.random.normal(80, 5), 1),
                    'pressure': round(np.random.normal(15, 1), 2)
                })
        
        # Save to CSV
        if data:
            headers = list(data[0].keys())
            with open(output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            
            click.echo(f"✅ Generated {len(data)} samples of {sample_type} data")
            click.echo(f"💾 Saved to: {output}")
            click.echo(f"📊 Columns: {', '.join(headers)}")
            
            # Show preview
            click.echo(f"\n🔍 Data Preview:")
            for i, row in enumerate(data[:5]):
                if i == 0:
                    click.echo('  ' + '  '.join(f"{k:>12}" for k in headers))
                    click.echo('  ' + '-' * (12 * len(headers) + 2 * (len(headers) - 1)))
                click.echo('  ' + '  '.join(f"{str(v):>12}" for v in row.values()))
        
    except Exception as e:
        click.echo(f"❌ Error generating sample data: {e}", err=True)
        sys.exit(1)


@main.command()
def info():
    """Show information about ESTIEM EDA Toolkit."""
    
    click.echo("""
🏭 ESTIEM EDA Toolkit - Exploratory Data Analysis

📊 Available Tools:
   • I-Chart        - Individual control charts for process monitoring
   • Capability     - Process capability analysis (Cp, Cpk, Six Sigma)
   • ANOVA          - One-way analysis of variance with post-hoc tests
   • Pareto         - 80/20 rule analysis for root cause identification  
   • Probability    - Distribution assessment with confidence intervals

🌐 Web Application: https://jukka-matti.github.io/ESTIEM-eda/
   - Zero installation required
   - Drag-and-drop CSV upload
   - Interactive visualizations
   - Mobile-friendly design

🎓 Educational Focus:
   - Designed for Industrial Engineering applications
   - Used by 60,000+ Industrial Engineering students
   - Professional-quality analysis results
   - ESTIEM branding for viral marketing

📚 Examples:
   estiem-eda sample-data --type manufacturing
   estiem-eda i-chart sample_data.csv
   estiem-eda capability data.csv --lsl 9.5 --usl 10.5
   estiem-eda anova data.csv --value measurement --group line

🤝 About ESTIEM:
   European Students of Technology in Engineering and Management
   Connecting students across 35+ countries for education and growth
   Learn more: https://estiem.org

👨‍💻 Creator: Jukka-Matti Turtiainen
   Lean Six Sigma Expert & Trainer
   Website: https://www.rdmaic.com

📄 License: Apache 2.0 - Free for educational use
    """)


if __name__ == '__main__':
    main()