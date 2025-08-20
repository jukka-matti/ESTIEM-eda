#!/usr/bin/env python3
"""
ESTIEM EDA Toolkit - Quick Analysis Module
Streamlined interface for rapid exploratory data analysis
"""

import csv
from typing import Any

import numpy as np

from .core.calculations import (
    calculate_anova,
    calculate_i_chart,
    calculate_pareto,
    calculate_probability_plot,
    calculate_process_capability,
)
from .core.validation import validate_groups_data, validate_numeric_data, validate_pareto_data


class QuickEDA:
    """
    Streamlined interface for ESTIEM EDA exploratory data analysis

    Examples:
        >>> from estiem_eda import QuickEDA
        >>> eda = QuickEDA()
        >>> eda.load_csv('data.csv')
        >>> eda.i_chart('measurement')
        >>> eda.capability('measurement', lsl=9.5, usl=10.5)
    """

    def __init__(self):
        self.data = None
        self.headers = []

    def load_csv(self, file_path: str) -> "QuickEDA":
        """Load data from CSV file"""
        try:
            data = []
            with open(file_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.headers = reader.fieldnames
                for row in reader:
                    # Convert numeric values
                    converted_row = {}
                    for key, value in row.items():
                        try:
                            converted_row[key] = float(value)
                        except (ValueError, TypeError):
                            converted_row[key] = value
                    data.append(converted_row)

            self.data = data
            print(f"✅ Loaded {len(self.data)} rows × {len(self.headers)} columns")
            print(f"📋 Columns: {', '.join(self.headers)}")
            return self
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            raise

    def load_data(self, data: dict | list) -> "QuickEDA":
        """Load data from dictionary or list"""
        if isinstance(data, dict):
            # Convert dict to list of records
            if data and isinstance(list(data.values())[0], list):
                # Dict of lists (columns)
                self.headers = list(data.keys())
                n_rows = len(list(data.values())[0])
                self.data = []
                for i in range(n_rows):
                    row = {col: data[col][i] for col in self.headers}
                    self.data.append(row)
            else:
                # Single record dict
                self.headers = list(data.keys())
                self.data = [data]
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                # List of records
                self.data = data
                self.headers = list(data[0].keys()) if data else []
            else:
                # Simple list
                self.data = [{"values": val} for val in data]
                self.headers = ["values"]
        else:
            raise ValueError("Data must be dict or list")

        print(f"✅ Data loaded: {len(self.data)} rows × {len(self.headers)} columns")
        return self

    def preview(self, n: int = 5) -> "QuickEDA":
        """Preview the loaded data"""
        if self.data is None:
            print("❌ No data loaded")
            return self

        print(f"📊 Data Preview ({len(self.data)} rows × {len(self.headers)} columns):")

        # Show first n rows
        preview_data = self.data[:n]
        if preview_data:
            # Print header
            print("  " + "  ".join(f"{col:>12}" for col in self.headers))
            print("  " + "-" * (12 * len(self.headers) + 2 * (len(self.headers) - 1)))

            # Print rows
            for row in preview_data:
                print("  " + "  ".join(f"{str(row.get(col, '')):>12}" for col in self.headers))

        # Show numeric columns summary
        numeric_cols = []
        for col in self.headers:
            values = [row.get(col) for row in self.data if isinstance(row.get(col), int | float)]
            if len(values) > 0:
                numeric_cols.append(col)
                print(f"\n📈 {col}: {len(values)} numeric values")
                if len(values) > 1:
                    mean_val = np.mean(values)
                    std_val = np.std(values)
                    print(f"   Mean: {mean_val:.3f}, Std: {std_val:.3f}")
                    print(f"   Range: {min(values):.3f} - {max(values):.3f}")

        return self

    def i_chart(self, column: str = None, title: str = None) -> dict[str, Any]:
        """Create Individual Control Chart"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")

        # Auto-select column if not specified
        if column is None:
            for col in self.headers:
                values = [
                    row.get(col) for row in self.data if isinstance(row.get(col), int | float)
                ]
                if len(values) >= 3:
                    column = col
                    print(f"🔍 Using column: {column}")
                    break
            else:
                raise ValueError("No suitable numeric columns found (need 3+ points)")

        # Extract data values
        data_values = [
            row.get(column) for row in self.data if isinstance(row.get(column), int | float)
        ]

        # Validate and calculate
        values = validate_numeric_data(data_values, min_points=3)
        results = calculate_i_chart(values, title or f"I-Chart: {column}")

        self._print_results(results, "I-Chart")
        return results

    def capability(
        self, column: str = None, lsl: float = None, usl: float = None, target: float = None
    ) -> dict[str, Any]:
        """Process Capability Analysis"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")

        if lsl is None or usl is None:
            raise ValueError("Must specify both lsl (Lower Spec Limit) and usl (Upper Spec Limit)")

        # Auto-select column if not specified
        if column is None:
            for col in self.headers:
                values = [
                    row.get(col) for row in self.data if isinstance(row.get(col), int | float)
                ]
                if len(values) >= 10:
                    column = col
                    print(f"🔍 Using column: {column}")
                    break
            else:
                raise ValueError("No suitable numeric columns found (need 10+ points)")

        # Extract data values
        data_values = [
            row.get(column) for row in self.data if isinstance(row.get(column), int | float)
        ]

        # Validate and calculate
        values = validate_numeric_data(data_values, min_points=10)
        results = calculate_process_capability(values, lsl, usl, target)

        self._print_results(results, "Process Capability")
        return results

    def anova(self, value_column: str, group_column: str) -> dict[str, Any]:
        """One-way Analysis of Variance"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")

        if value_column not in self.headers:
            raise ValueError(f"Value column '{value_column}' not found")
        if group_column not in self.headers:
            raise ValueError(f"Group column '{group_column}' not found")

        # Prepare groups
        groups_dict = {}
        for row in self.data:
            group_name = row.get(group_column)
            value_data = row.get(value_column)

            if group_name is not None and isinstance(value_data, int | float):
                group_key = str(group_name)
                if group_key not in groups_dict:
                    groups_dict[group_key] = []
                groups_dict[group_key].append(float(value_data))

        # Filter groups with sufficient data
        groups = {name: data for name, data in groups_dict.items() if len(data) >= 2}

        if len(groups) < 2:
            raise ValueError("Need at least 2 groups with 2+ data points each")

        # Validate and calculate
        validated_groups = validate_groups_data(groups)
        results = calculate_anova(validated_groups)

        self._print_results(results, "ANOVA")
        return results

    def pareto(self, category_column: str = None, value_column: str = None) -> dict[str, Any]:
        """Pareto Analysis (80/20 rule)"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")

        # Auto-detect category column
        if category_column is None:
            for col in self.headers:
                sample_values = [row.get(col) for row in self.data[:10] if row.get(col) is not None]
                if sample_values and any(isinstance(val, str) for val in sample_values):
                    category_column = col
                    print(f"🔍 Using category column: {category_column}")
                    break
            else:
                raise ValueError("No categorical columns found")

        # Prepare data
        data_dict = {}
        if value_column:
            if value_column not in self.headers:
                raise ValueError(f"Value column '{value_column}' not found")
            # Sum values by category
            for row in self.data:
                cat = row.get(category_column)
                val = row.get(value_column)
                if cat is not None and isinstance(val, int | float):
                    cat_str = str(cat)
                    data_dict[cat_str] = data_dict.get(cat_str, 0) + float(val)
        else:
            # Count occurrences
            for row in self.data:
                cat = row.get(category_column)
                if cat is not None:
                    cat_str = str(cat)
                    data_dict[cat_str] = data_dict.get(cat_str, 0) + 1

        # Validate and calculate
        validated_data = validate_pareto_data(data_dict)
        results = calculate_pareto(validated_data)

        self._print_results(results, "Pareto Analysis")
        return results

    def probability_plot(self, column: str = None, distribution: str = "normal") -> dict[str, Any]:
        """Probability Plot for distribution assessment"""
        if self.data is None:
            raise ValueError("No data loaded. Use load_csv() or load_data() first.")

        # Auto-select column if not specified
        if column is None:
            for col in self.headers:
                values = [
                    row.get(col) for row in self.data if isinstance(row.get(col), int | float)
                ]
                if len(values) >= 3:
                    column = col
                    print(f"🔍 Using column: {column}")
                    break
            else:
                raise ValueError("No suitable numeric columns found (need 3+ points)")

        # Extract data values
        data_values = [
            row.get(column) for row in self.data if isinstance(row.get(column), int | float)
        ]

        # Validate and calculate
        values = validate_numeric_data(data_values, min_points=3)
        results = calculate_probability_plot(values, distribution)

        self._print_results(results, "Probability Plot")
        return results

    def analyze_all(
        self,
        measurement_column: str,
        lsl: float = None,
        usl: float = None,
        group_column: str = None,
    ) -> dict[str, Any]:
        """Run comprehensive analysis suite"""
        print("🏭 ESTIEM EDA - Comprehensive Analysis Suite")
        print("=" * 50)

        results = {}

        # 1. I-Chart
        print("\n📈 1. Individual Control Chart")
        print("-" * 30)
        try:
            results["i_chart"] = self.i_chart(measurement_column)
        except Exception as e:
            print(f"❌ I-Chart failed: {e}")

        # 2. Capability (if specs provided)
        if lsl is not None and usl is not None:
            print("\n🎯 2. Process Capability Analysis")
            print("-" * 35)
            try:
                results["capability"] = self.capability(measurement_column, lsl, usl)
            except Exception as e:
                print(f"❌ Capability analysis failed: {e}")

        # 3. Probability Plot
        print("\n📋 3. Probability Plot")
        print("-" * 20)
        try:
            results["probability"] = self.probability_plot(measurement_column)
        except Exception as e:
            print(f"❌ Probability plot failed: {e}")

        # 4. ANOVA (if group column provided)
        if group_column is not None and group_column in self.headers:
            print("\n📊 4. ANOVA - Group Comparison")
            print("-" * 30)
            try:
                results["anova"] = self.anova(measurement_column, group_column)
            except Exception as e:
                print(f"❌ ANOVA failed: {e}")

        print("\n" + "=" * 50)
        print("✅ Comprehensive analysis complete!")

        return results

    def _print_results(self, results: dict[str, Any], analysis_type: str):
        """Print analysis results summary"""
        if not results.get("success", False):
            print(f"❌ {analysis_type} failed: {results.get('error', 'Unknown error')}")
            return

        print(f"✅ {analysis_type} completed successfully")

        # Print key statistics
        if "statistics" in results:
            print("📊 Key Results:")
            stats = results["statistics"]
            for key, value in list(stats.items())[:5]:  # Show top 5
                formatted_key = key.replace("_", " ").title()
                if isinstance(value, int | float):
                    print(f"   {formatted_key}: {value:.4f}")
                else:
                    print(f"   {formatted_key}: {value}")

        # Print interpretation
        if "interpretation" in results:
            print(f"🎯 {results['interpretation']}")

        print()


# Convenience functions for quick analysis
def quick_i_chart(data: list | np.ndarray, title: str = None) -> dict[str, Any]:
    """Quick I-Chart analysis from data list/array"""
    if hasattr(data, "tolist"):
        data = data.tolist()

    values = validate_numeric_data(data, min_points=3)
    return calculate_i_chart(values, title or "Quick I-Chart")


def quick_capability(
    data: list | np.ndarray, lsl: float, usl: float, target: float = None
) -> dict[str, Any]:
    """Quick capability analysis from data list/array"""
    if hasattr(data, "tolist"):
        data = data.tolist()

    values = validate_numeric_data(data, min_points=10)
    return calculate_process_capability(values, lsl, usl, target)


def quick_pareto(data: dict[str, int | float]) -> dict[str, Any]:
    """Quick Pareto analysis from dictionary"""
    validated_data = validate_pareto_data(data)
    return calculate_pareto(validated_data)


def generate_sample_data(data_type: str = "manufacturing", n: int = 100) -> list[dict]:
    """Generate sample datasets for testing"""
    np.random.seed(42)

    if data_type == "manufacturing":
        lines = ["Line_A", "Line_B", "Line_C"]
        data = []
        for i in range(n):
            line = np.random.choice(lines)
            if line == "Line_A":
                measurement = np.random.normal(10.0, 0.3)
            elif line == "Line_B":
                measurement = np.random.normal(9.8, 0.5)
            else:
                measurement = np.random.normal(10.2, 0.4)

            data.append(
                {
                    "sample_id": i + 1,
                    "measurement": round(measurement, 3),
                    "line": line,
                    "defects": int(np.random.poisson(2)),
                    "temperature": round(np.random.normal(25, 2), 1),
                }
            )

        return data

    elif data_type == "quality":
        defect_types = ["Surface", "Dimensional", "Assembly", "Material", "Electrical"]
        data = []
        for i in range(n):
            defect_type = np.random.choice(defect_types, p=[0.4, 0.3, 0.2, 0.08, 0.02])
            data.append(
                {
                    "inspection_id": i + 1,
                    "defect_type": defect_type,
                    "defect_count": int(np.random.poisson(3)),
                    "severity": np.random.choice(["Minor", "Major", "Critical"], p=[0.6, 0.3, 0.1]),
                    "cost": round(np.random.uniform(10, 100), 2),
                }
            )

        return data

    elif data_type == "process":
        data = []
        for i in range(n):
            # Process with slight trend and variation
            value = 100 + 0.1 * i + np.random.normal(0, 2)
            data.append(
                {
                    "time": i + 1,
                    "process_value": round(value, 2),
                    "temperature": round(np.random.normal(80, 5), 1),
                    "pressure": round(np.random.normal(15, 1), 2),
                }
            )

        return data

    else:
        raise ValueError("data_type must be 'manufacturing', 'quality', or 'process'")
