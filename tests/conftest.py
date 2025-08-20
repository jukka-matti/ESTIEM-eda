"""Test configuration and fixtures for ESTIEM EDA tests."""


import numpy as np
import pytest


@pytest.fixture
def sample_stable_process():
    """Generate stable process data for testing control charts."""
    np.random.seed(42)
    return np.random.normal(10.0, 0.5, 50).tolist()


@pytest.fixture
def sample_unstable_process():
    """Generate unstable process data with out-of-control points."""
    np.random.seed(42)
    data = np.random.normal(10.0, 0.5, 50)
    # Add out-of-control points
    data[10] = 15.0  # Above UCL
    data[25] = 5.0  # Below LCL
    return data.tolist()


@pytest.fixture
def sample_capability_data():
    """Generate process data for capability analysis."""
    np.random.seed(42)
    return np.random.normal(10.0, 0.3, 100).tolist()


@pytest.fixture
def sample_anova_groups():
    """Generate sample data for ANOVA analysis."""
    np.random.seed(42)
    return {
        "Group A": np.random.normal(10, 1, 20).tolist(),
        "Group B": np.random.normal(12, 1.5, 25).tolist(),
        "Group C": np.random.normal(11, 0.8, 22).tolist(),
    }


@pytest.fixture
def sample_pareto_data():
    """Generate sample data for Pareto analysis."""
    return {
        "Defect Type A": 45,
        "Defect Type B": 32,
        "Defect Type C": 28,
        "Defect Type D": 15,
        "Defect Type E": 12,
        "Defect Type F": 8,
        "Defect Type G": 5,
    }


@pytest.fixture
def specification_limits():
    """Common specification limits for testing."""
    return {"lsl": 9.0, "usl": 11.0, "target": 10.0}


@pytest.fixture
def mcp_server():
    """Create MCP server instance for testing."""
    from estiem_eda.mcp_server import ESTIEMMCPServer

    return ESTIEMMCPServer()


class TestDataGenerator:
    """Utility class for generating test data with known statistical properties."""

    @staticmethod
    def generate_normal_data(mean: float, std: float, size: int, seed: int = 42) -> list[float]:
        """Generate normally distributed data."""
        np.random.seed(seed)
        return np.random.normal(mean, std, size).tolist()

    @staticmethod
    def generate_skewed_data(size: int, seed: int = 42) -> list[float]:
        """Generate skewed data for testing normality assumptions."""
        np.random.seed(seed)
        return np.random.exponential(2.0, size).tolist()

    @staticmethod
    def generate_unequal_variance_groups(seed: int = 42) -> dict[str, list[float]]:
        """Generate groups with unequal variances for ANOVA testing."""
        np.random.seed(seed)
        return {
            "Low Variance": np.random.normal(10, 0.5, 20).tolist(),
            "High Variance": np.random.normal(10, 2.0, 20).tolist(),
            "Medium Variance": np.random.normal(10, 1.0, 20).tolist(),
        }

    @staticmethod
    def generate_capability_scenarios():
        """Generate different capability scenarios for testing."""
        np.random.seed(42)
        return {
            "capable": np.random.normal(10.0, 0.2, 100).tolist(),  # Cpk > 1.33
            "marginal": np.random.normal(10.0, 0.4, 100).tolist(),  # 1.0 < Cpk < 1.33
            "not_capable": np.random.normal(10.0, 0.8, 100).tolist(),  # Cpk < 1.0
            "off_center": np.random.normal(9.5, 0.3, 100).tolist(),  # Good Cp, poor Cpk
        }


@pytest.fixture
def test_data_generator():
    """Provide test data generator fixture."""
    return TestDataGenerator()
