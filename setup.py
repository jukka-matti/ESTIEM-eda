from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="estiem-eda-toolkit",
    version="0.1.0",
    author="ESTIEM",
    description="MCP server for statistical analysis including I-charts, process capability, ANOVA, and Pareto analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ESTIEM/eda-toolkit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "test": ["pytest", "pytest-cov"],
        "dev": ["black", "mypy", "pre-commit"],
    },
    entry_points={
        "console_scripts": [
            "estiem-eda-server=estiem_eda.mcp_server:main",
        ],
    },
)