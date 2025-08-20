#!/usr/bin/env python3
"""
ESTIEM EDA Toolkit - Command Line Interface
Professional statistical analysis from the command line
"""

import click
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json

from .tools.i_chart import IChartTool
from .tools.capability import CapabilityTool
from .tools.anova import ANOVATool
from .tools.pareto import ParetoTool
from .tools.probability_plot import ProbabilityPlotTool


class EstiemCLI:
    """ESTIEM EDA command line interface"""
    
    def __init__(self):
        self.tools = {
            'i-chart': IChartTool(),
            'capability': CapabilityTool(),
            'anova': ANOVATool(),
            'pareto': ParetoTool(),
            'probability': ProbabilityPlotTool()
        }
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            df = pd.read_csv(file_path)
            if df.empty:
                raise ValueError("CSV file is empty")
            
            click.echo(f"✅ Loaded {len(df)} rows × {len(df.columns)} columns from {file_path}")
            return df
        
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
            <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
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

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
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
    
    Perform statistical process control analysis from the command line.
    Perfect for Lean Six Sigma, quality control, and process improvement.
    
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
    df = cli.load_data(data_file)
    
    # Prepare parameters
    data_list = df[column].tolist() if column else df.select_dtypes(include=[np.number]).iloc[:, 0].tolist()
    
    try:
        # Run analysis
        tool = cli.tools['i-chart']
        results = tool.execute({
            'data': data_list,
            'title': title or f'I-Chart Analysis: {data_file}'
        })
        
        if results['success']:
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
            
        else:
            click.echo(f"❌ Analysis failed: {results.get('error')}", err=True)
            sys.exit(1)
    
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
    df = cli.load_data(data_file)
    
    # Prepare parameters
    data_list = df[column].tolist() if column else df.select_dtypes(include=[np.number]).iloc[:, 0].tolist()
    
    params = {'lsl': lsl, 'usl': usl}
    if target:
        params['target'] = target
    
    try:
        # Run analysis
        tool = cli.tools['capability']
        results = tool.execute({
            'data': data_list,
            **params
        })
        
        if results['success']:
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
            
        else:
            click.echo(f"❌ Analysis failed: {results.get('error')}", err=True)
            sys.exit(1)
    
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
    df = cli.load_data(data_file)
    
    # Prepare groups
    groups = {}
    for group_name in df[group].unique():
        if pd.notna(group_name):
            group_data = df[df[group] == group_name][value].dropna().tolist()
            if len(group_data) >= 2:
                groups[str(group_name)] = group_data
    
    try:
        # Run analysis
        tool = cli.tools['anova']
        results = tool.execute({'groups': groups})
        
        if results['success']:
            # Display summary
            stats = results['anova_results']
            click.echo(f"\n📊 ANOVA Results:")
            click.echo(f"   F-statistic: {stats['f_statistic']:.4f}")
            click.echo(f"   p-value: {stats['p_value']:.6f}")
            click.echo(f"   Significant: {'Yes' if stats['significant'] else 'No'}")
            
            click.echo(f"\n🎯 {results['interpretation']}")
            
            # Save results
            cli.save_results(results, output, format)
            
        else:
            click.echo(f"❌ Analysis failed: {results.get('error')}", err=True)
            sys.exit(1)
    
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
    df = cli.load_data(data_file)
    
    # Auto-detect columns if not specified
    if not category:
        text_cols = df.select_dtypes(include=['object', 'string']).columns
        if len(text_cols) == 0:
            click.echo("❌ No categorical columns found", err=True)
            sys.exit(1)
        category = text_cols[0]
        click.echo(f"🔍 Using category column: {category}")
    
    # Prepare data
    if value:
        # Sum values by category
        data_dict = df.groupby(category)[value].sum().to_dict()
    else:
        # Count occurrences
        data_dict = df[category].value_counts().to_dict()
    
    try:
        # Run analysis
        tool = cli.tools['pareto']
        results = tool.execute({'data': data_dict})
        
        if results['success']:
            # Display summary
            stats = results['vital_few']
            click.echo(f"\n📊 Pareto Results:")
            click.echo(f"   Total Categories: {len(data_dict)}")
            click.echo(f"   Vital Few: {len(stats['categories'])} categories")
            click.echo(f"   Impact: {stats['percentage']:.1f}% of total")
            click.echo(f"   Top 3: {', '.join(list(data_dict.keys())[:3])}")
            
            click.echo(f"\n🎯 {results['interpretation']}")
            
            # Save results
            cli.save_results(results, output, format)
            
        else:
            click.echo(f"❌ Analysis failed: {results.get('error')}", err=True)
            sys.exit(1)
    
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
    df = cli.load_data(data_file)
    
    # Prepare parameters
    data_list = df[column].tolist() if column else df.select_dtypes(include=[np.number]).iloc[:, 0].tolist()
    
    try:
        # Run analysis
        tool = cli.tools['probability']
        results = tool.execute({
            'data': data_list,
            'distribution': distribution
        })
        
        if results['success']:
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
            
        else:
            click.echo(f"❌ Analysis failed: {results.get('error')}", err=True)
            sys.exit(1)
    
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
        df = pd.DataFrame(data)
        df.to_csv(output, index=False)
        
        click.echo(f"✅ Generated {len(data)} samples of {sample_type} data")
        click.echo(f"💾 Saved to: {output}")
        click.echo(f"📊 Columns: {', '.join(df.columns.tolist())}")
        
        # Show preview
        click.echo(f"\n🔍 Data Preview:")
        click.echo(df.head().to_string(index=False))
        
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
   - Designed for Lean Six Sigma methodology (DMAIC)
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