# Solar Micro-Grid Dispatch Planner

## 1. Project Overview

The Solar Micro-Grid Dispatch Planner is a Python-based project that models energy dispatch in a small solar micro-grid. It uses linear algebra to estimate solar and battery energy contributions needed to meet electricity demand.

The project also explores vectorised computation, dispatch feasibility, cost estimation, sensitivity analysis, and a hybrid energy system that includes diesel generation.

## 2. Objectives

- Model solar and battery dispatch using a system of linear equations.
- Generate and analyse daily electricity-demand data.
- Compare loop-based and vectorised calculations.
- Identify infeasible dispatch scenarios.
- Estimate energy dispatch costs.
- Investigate how changes in demand affect dispatch outputs.
- Extend the model to include a third energy source.
- Validate the implementation using automated tests.

## 3. Technologies Used

- Python
- NumPy
- pandas
- Matplotlib
- SciPy
- Jupyter Notebook
- pytest

## 4. Project Structure

```text
Mini-Project 2 Solar Micro-Grid Dispatch Planner/
├── data/
│   └── microgrid_demand_30days.csv
├── notebooks/
│   └── project2_solar_microgrid.ipynb
├── src/
│   └── solar_microgrid/
│       ├── __init__.py
│       ├── microgrid.py
│       ├── data_generator.py
│       ├── analysis.py
│       └── hybrid_microgrid.py
├── tests/
│   ├── test_microgrid.py
│   ├── test_data_generator.py
│   └── test_hybrid_microgrid.py
├── .gitignore
├── pytest.ini
├── README.md
└── requirements.txt
```

## 5. Main Features

### Standard Micro-Grid Model
Uses a coefficient matrix and linear algebra to calculate solar and battery dispatch. The model also evaluates whether a dispatch solution is feasible.

### Demand Data Generation
Generates daily demand data for analysis and supports reproducible results.

### Performance Comparison
Compares loop-based and vectorised calculations to examine their execution times.

### Cost Analysis
Estimates solar and battery dispatch costs using the rates configured in the model.

### Infeasibility Handling
Uses non-negative least squares to find adjusted non-negative dispatch values when the original system cannot provide a feasible non-negative solution. Such adjustments may not satisfy the original demand equations exactly.

### Sensitivity Analysis
Uses 1,000 simulations with a fixed random seed to assess how demand perturbations affect dispatch outputs.

### Hybrid Micro-Grid
Extends the model to include a third energy source, representing diesel generation, and evaluates the resulting dispatch solution.

## 6. Installation

Python and Git should be installed before setting up the project.

Install the required Python packages from the project root:

```bash
python -m pip install -r requirements.txt
```

## 7. Running the Project

Open the notebook:

```text
notebooks/project2_solar_microgrid.ipynb
```

Select the appropriate Python environment and run the notebook cells from beginning to end.

## 8. Running Tests

From the project root, execute:

```bash
python -m pytest -v
```

The current automated test suite contains 27 tests, all of which passed during the latest recorded verification.

## 9. Interpretation and Limitations

The model is an educational simulation rather than a complete engineering-grade micro-grid controller. Its results depend on the selected coefficient matrices, demand inputs, and cost assumptions.

The sensitivity analysis measures the response of the mathematical model to simulated demand changes. It does not establish actual field performance or guarantee real-world energy availability.

The hybrid model is simplified and does not yet represent all practical factors such as battery state of charge, solar irradiance forecasts, generator operating constraints, fuel consumption curves, storage degradation, or equipment losses.

## 10. Reproducibility

The sensitivity analysis uses a fixed random seed of 42 and 1,000 simulations in the configured analysis. Automated tests are included to validate core model behaviour, input validation, and data generation.

## 11. Project Status

The notebook has been reported to run successfully from beginning to end, and all 27 automated tests passed in the latest verification.

