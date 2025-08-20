# Browser-Compatible Statistical Analysis

This directory contains browser-compatible implementations of statistical functions that work with Pyodide (Python in WebAssembly).

## Purpose

The browser-compatible core provides the same statistical calculations as the server-side implementation but without dependencies on scipy.stats, making it suitable for web browsers.

## Architecture

- **Server-side** (`src/estiem_eda/core/`): Full NumPy + SciPy implementation
- **Browser-side** (`src/estiem_eda/browser/`): Browser-compatible with Pyodide
- **Unified Output**: Both produce identical results

## Current Implementation

The browser tools are currently auto-generated and deployed as `docs/eda_tools.py`. This directory serves as the architectural foundation for future browser-specific optimizations.

## Future Development

This directory will be expanded to include:
- `core_browser.py` - Browser-compatible statistical calculations
- `web_adapter.py` - Unified response formatting
- `generator.py` - Automated browser tools generator