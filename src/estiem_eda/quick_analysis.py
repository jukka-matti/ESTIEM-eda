#!/usr/bin/env python3
"""
ESTIEM EDA Toolkit - Quick Analysis Module
Streamlined interface for rapid statistical analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union, List
import warnings
from pathlib import Path

from .tools.i_chart import IChartTool
from .tools.capability import CapabilityTool
from .tools.anova import ANOVATool
from .tools.pareto import ParetoTool
from .tools.probability_plot import ProbabilityPlotTool


class QuickEDA:
    """
    Streamlined interface for ESTIEM EDA statistical analysis
    
    Examples:
        >>> from estiem_eda import QuickEDA
        >>> eda = QuickEDA()
        >>> eda.load_csv('data.csv')
        >>> eda.i_chart('measurement')
        >>> eda.capability('measurement', lsl=9.5, usl=10.5)
    """
    
    def __init__(self):
        self.data = None
        self.tools = {
            'i_chart': IChartTool(),
            'capability': CapabilityTool(),
            'anova': ANOVATool(),
            'pareto': ParetoTool(),
            'probability': ProbabilityPlotTool()
        }
    
    def load_csv(self, file_path: str) -> 'QuickEDA':
        """Load data from CSV file"""
        try:
            self.data = pd.read_csv(file_path)
            print(f"✅ Loaded {len(self.data)} rows × {len(self.data.columns)} columns")
            print(f"📋 Columns: {', '.join(self.data.columns.tolist())}")
            return self
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            raise
    
    def load_data(self, data: Union[pd.DataFrame, Dict, List]) -> 'QuickEDA':
        """Load data from DataFrame, dictionary, or list"""
        if isinstance(data, pd.DataFrame):
            self.data = data
        elif isinstance(data, dict):
            self.data = pd.DataFrame(data)
        elif isinstance(data, list):
            self.data = pd.DataFrame({'values': data})
        else:
            raise ValueError("Data must be DataFrame, dict, or list")
        
        print(f"✅ Data loaded: {len(self.data)} rows × {len(self.data.columns)} columns")
        return self
    
    def preview(self, n: int = 5) -> 'QuickEDA':
        """Preview the loaded data"""
        if self.data is None:
            print("❌ No data loaded")
            return self
        
        print(f"📊 Data Preview ({len(self.data)} rows × {len(self.data.columns)} columns):")
        print(self.data.head(n))
        
        # Show numeric columns summary
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(f"\n📈 Numeric columns: {', '.join(numeric_cols)}")
            print(self.data[numeric_cols].describe())
        
        return self
    
    def i_chart(self, column: str = None, title: str = None) -> Dict[str, Any]:
        """Create Individual Control Chart"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")
        
        # Auto-select column if not specified
        if column is None:
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise ValueError("No numeric columns found")
            column = numeric_cols[0]
            print(f"🔍 Using column: {column}")
        
        data_values = self.data[column].dropna().tolist()
        
        results = self.tools['i_chart'].execute({
            'data': data_values,
            'title': title or f'I-Chart: {column}'
        })
        
        self._print_results(results, 'I-Chart')
        return results
    
    def capability(self, column: str = None, lsl: float = None, usl: float = None, 
                  target: float = None) -> Dict[str, Any]:
        """Process Capability Analysis"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")
        
        if lsl is None or usl is None:
            raise ValueError("Must specify both lsl (Lower Spec Limit) and usl (Upper Spec Limit)")
        
        # Auto-select column if not specified
        if column is None:
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise ValueError("No numeric columns found")
            column = numeric_cols[0]
            print(f"🔍 Using column: {column}")
        
        data_values = self.data[column].dropna().tolist()
        
        params = {'data': data_values, 'lsl': lsl, 'usl': usl}
        if target is not None:
            params['target'] = target
        
        results = self.tools['capability'].execute(params)
        self._print_results(results, 'Process Capability')
        return results
    
    def anova(self, value_column: str, group_column: str) -> Dict[str, Any]:
        """One-way Analysis of Variance"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")
        
        if value_column not in self.data.columns:
            raise ValueError(f"Value column '{value_column}' not found")
        if group_column not in self.data.columns:
            raise ValueError(f"Group column '{group_column}' not found")
        
        # Prepare groups
        groups = {}
        for group_name in self.data[group_column].unique():
            if pd.notna(group_name):
                group_data = self.data[self.data[group_column] == group_name][value_column].dropna().tolist()
                if len(group_data) >= 2:
                    groups[str(group_name)] = group_data
        
        if len(groups) < 2:
            raise ValueError("Need at least 2 groups with 2+ data points each")
        
        results = self.tools['anova'].execute({'groups': groups})
        self._print_results(results, 'ANOVA')
        return results
    
    def pareto(self, category_column: str = None, value_column: str = None) -> Dict[str, Any]:
        """Pareto Analysis (80/20 rule)"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")
        
        # Auto-detect category column
        if category_column is None:
            text_cols = self.data.select_dtypes(include=['object', 'string']).columns
            if len(text_cols) == 0:
                raise ValueError("No categorical columns found")
            category_column = text_cols[0]
            print(f"🔍 Using category column: {category_column}")
        
        # Prepare data
        if value_column:
            if value_column not in self.data.columns:
                raise ValueError(f"Value column '{value_column}' not found")
            data_dict = self.data.groupby(category_column)[value_column].sum().to_dict()
        else:
            data_dict = self.data[category_column].value_counts().to_dict()
        
        results = self.tools['pareto'].execute({'data': data_dict})
        self._print_results(results, 'Pareto Analysis')
        return results
    
    def probability_plot(self, column: str = None, distribution: str = 'normal') -> Dict[str, Any]:
        """Probability Plot for distribution assessment"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")
        
        # Auto-select column if not specified
        if column is None:
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise ValueError("No numeric columns found")
            column = numeric_cols[0]
            print(f"🔍 Using column: {column}")
        
        data_values = self.data[column].dropna().tolist()
        
        results = self.tools['probability'].execute({
            'data': data_values,
            'distribution': distribution
        })
        
        self._print_results(results, 'Probability Plot')
        return results
    
    def analyze_all(self, measurement_column: str, lsl: float = None, usl: float = None,
                   group_column: str = None) -> Dict[str, Any]:
        """Run comprehensive analysis suite"""
        print("🏭 ESTIEM EDA - Comprehensive Analysis Suite")
        print("=" * 50)
        
        results = {}
        
        # 1. I-Chart
        print("\n📈 1. Individual Control Chart")
        print("-" * 30)
        try:
            results['i_chart'] = self.i_chart(measurement_column)
        except Exception as e:
            print(f"❌ I-Chart failed: {e}")
        
        # 2. Capability (if specs provided)
        if lsl is not None and usl is not None:
            print("\n🎯 2. Process Capability Analysis")
            print("-" * 35)
            try:
                results['capability'] = self.capability(measurement_column, lsl, usl)
            except Exception as e:
                print(f"❌ Capability analysis failed: {e}")
        
        # 3. Probability Plot
        print("\n📋 3. Probability Plot")
        print("-" * 20)
        try:
            results['probability'] = self.probability_plot(measurement_column)
        except Exception as e:
            print(f"❌ Probability plot failed: {e}")
        
        # 4. ANOVA (if group column provided)
        if group_column is not None and group_column in self.data.columns:
            print("\n📊 4. ANOVA - Group Comparison")
            print("-" * 30)
            try:
                results['anova'] = self.anova(measurement_column, group_column)
            except Exception as e:
                print(f"❌ ANOVA failed: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Comprehensive analysis complete!")
        
        return results
    
    def _print_results(self, results: Dict[str, Any], analysis_type: str):
        """Print analysis results summary"""
        if not results.get('success', False):
            print(f"❌ {analysis_type} failed: {results.get('error', 'Unknown error')}")
            return
        
        print(f"✅ {analysis_type} completed successfully")
        
        # Print key statistics
        if 'statistics' in results:
            print("📊 Key Results:")
            stats = results['statistics']
            for key, value in list(stats.items())[:5]:  # Show top 5
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (int, float)):
                    print(f"   {formatted_key}: {value:.4f}")
                else:
                    print(f"   {formatted_key}: {value}")
        
        # Print interpretation
        if 'interpretation' in results:
            print(f"🎯 {results['interpretation']}")
        
        print()


# Convenience functions for quick analysis
def quick_i_chart(data: Union[List, np.ndarray, pd.Series], title: str = None) -> Dict[str, Any]:
    """Quick I-Chart analysis from data list/array"""
    tool = IChartTool()
    if hasattr(data, 'tolist'):
        data = data.tolist()
    elif isinstance(data, pd.Series):
        data = data.dropna().tolist()
    
    return tool.execute({'data': list(data), 'title': title or 'Quick I-Chart'})


def quick_capability(data: Union[List, np.ndarray, pd.Series], lsl: float, usl: float, 
                    target: float = None) -> Dict[str, Any]:
    """Quick capability analysis from data list/array"""
    tool = CapabilityTool()
    if hasattr(data, 'tolist'):
        data = data.tolist()
    elif isinstance(data, pd.Series):
        data = data.dropna().tolist()
    
    params = {'data': list(data), 'lsl': lsl, 'usl': usl}
    if target is not None:
        params['target'] = target
    
    return tool.execute(params)


def quick_pareto(data: Dict[str, Union[int, float]]) -> Dict[str, Any]:
    """Quick Pareto analysis from dictionary"""
    tool = ParetoTool()
    return tool.execute({'data': data})


def generate_sample_data(data_type: str = 'manufacturing', n: int = 100) -> pd.DataFrame:
    """Generate sample datasets for testing"""
    np.random.seed(42)
    
    if data_type == 'manufacturing':
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
                'defects': np.random.poisson(2),
                'temperature': round(np.random.normal(25, 2), 1)
            })
        
        return pd.DataFrame(data)
    
    elif data_type == 'quality':
        defect_types = ['Surface', 'Dimensional', 'Assembly', 'Material', 'Electrical']
        data = []
        for i in range(n):
            defect_type = np.random.choice(defect_types, p=[0.4, 0.3, 0.2, 0.08, 0.02])
            data.append({
                'inspection_id': i + 1,
                'defect_type': defect_type,
                'defect_count': np.random.poisson(3),
                'severity': np.random.choice(['Minor', 'Major', 'Critical'], p=[0.6, 0.3, 0.1]),
                'cost': round(np.random.uniform(10, 100), 2)
            })
        
        return pd.DataFrame(data)
    
    elif data_type == 'process':
        data = []
        for i in range(n):
            # Process with slight trend and variation
            value = 100 + 0.1 * i + np.random.normal(0, 2)
            data.append({
                'time': i + 1,
                'process_value': round(value, 2),
                'temperature': round(np.random.normal(80, 5), 1),
                'pressure': round(np.random.normal(15, 1), 2)
            })
        
        return pd.DataFrame(data)
    
    else:
        raise ValueError("data_type must be 'manufacturing', 'quality', or 'process'")