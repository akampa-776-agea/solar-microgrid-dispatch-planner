
"""Analysis utilities for micro-grid dispatch results."""

from timeit import timeit

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from scipy.linalg import solve
from scipy.optimize import nnls # to find non-negative solar and battery values that minimise the mismatch with the original demand equations.

from .microgrid import MicroGrid


def solve_with_loop(grid: MicroGrid, demands: pd.DataFrame) -> pd.DataFrame: # solves the 30 days individually.
    """Solve daily demand equations one day at a time."""
    results = []

    for row in demands.itertuples(index=False):
        result = grid.solve_day(row.D1_kwh, row.D2_kwh)
        results.append(result)

    return pd.DataFrame(results)


def solve_vectorised(grid: MicroGrid, demands: pd.DataFrame) -> pd.DataFrame: # olves all 30 days in one matrix operation.
    """Solve all demand days in one vectorised linear algebra call."""
    rhs = demands[["D1_kwh", "D2_kwh"]].to_numpy().T
    solutions = solve(grid.coefficients, rhs)

    results = demands.copy()
    results["solar_kwh"] = solutions[0]
    results["battery_kwh"] = solutions[1]
    results["feasible"] = ((results["solar_kwh"] >= 0) & (results["battery_kwh"] >= 0))

    return results

def compare_execution_times(grid: MicroGrid, demands: pd.DataFrame, number: int = 100,) -> dict[str, float]: # ses timeit to compare the approaches.
    """Time loop and vectorised approaches using timeit."""
    loop_seconds = timeit(lambda: solve_with_loop(grid, demands),number=number,) / number

    vectorised_seconds = timeit(lambda: solve_vectorised(grid, demands), number=number,) / number

    return {"loop_seconds_per_run": loop_seconds, "vectorised_seconds_per_run": vectorised_seconds, }

def summarise_usage(results: pd.DataFrame) -> pd.DataFrame: # calculates mean, variance and standard deviation.
    """Calculate mean, variance and standard deviation of energy use."""
    return results[["solar_kwh", "battery_kwh"]].agg(["mean", "var", "std"])


def calculate_costs(results: pd.DataFrame) -> pd.DataFrame: # calculates daily solar, battery and total costs.
    """Calculate illustrative daily energy costs in Ugandan shillings."""
    costs = results.copy()

    costs["solar_cost_ugx"] = costs["solar_kwh"] * 150
    costs["battery_cost_ugx"] = costs["battery_kwh"] * 450
    costs["daily_cost_ugx"] = (costs["solar_cost_ugx"] + costs["battery_cost_ugx"])

    return costs


# first analysis test
'''
python -c "import pandas as pd; from src.solar_microgrid.microgrid import MicroGrid; from src.solar_microgrid.analysis import solve_with_loop, solve_vectorised; df = pd.read_csv('data/microgrid_demand_30days.csv'); grid = MicroGrid(); loop_results = solve_with_loop(grid, df); vector_results = solve_vectorised(grid, df); print('Loop results:'); print(loop_results.head()); print('\nVectorised results:'); print(vector_results[['solar_kwh', 'battery_kwh', 'feasible']].head()); print('\nRows solved:', len(loop_results), len(vector_results)); print('\nSolutions agree:', __import__('numpy').allclose(loop_results[['solar_kwh', 'battery_kwh']].to_numpy(), vector_results[['solar_kwh', 'battery_kwh']].to_numpy()))"
'''
# Both approaches solve all 30 days.
# Both produce the same solar and battery solutions.

# Test timing, statistics and costs
'''
python -c "import pandas as pd; from src.solar_microgrid.microgrid import MicroGrid; from src.solar_microgrid.analysis import solve_vectorised, compare_execution_times, summarise_usage, calculate_costs; df = pd.read_csv('data/microgrid_demand_30days.csv'); grid = MicroGrid(); results = solve_vectorised(grid, df); print('TIMING:'); print(compare_execution_times(grid, df)); print('\nUSAGE STATISTICS:'); print(summarise_usage(results)); costs = calculate_costs(results); print('\nDAILY COSTS:'); print(costs[['solar_cost_ugx', 'battery_cost_ugx', 'daily_cost_ugx']].head()); print('\n30-DAY TOTAL COST (UGX):', round(costs['daily_cost_ugx'].sum(), 2))"
'''
# The average execution time for both approaches.
# Mean, variance and standard deviation of solar and battery usage.
# Daily costs and the total cost across the 30 days.


def handle_infeasible_days(grid: MicroGrid, results: pd.DataFrame,) -> pd.DataFrame:
    """
    Apply non-negative least squares to physically infeasible days.

    Original unconstrained estimates are preserved. Adjusted estimates
    are stored separately, together with the resulting demand residuals.
    """
    handled = results.copy()

    handled["adjusted_solar_kwh"] = handled["solar_kwh"]
    handled["adjusted_battery_kwh"] = handled["battery_kwh"]
    handled["adjustment_method"] = "Exact solution"

    for index, row in handled.iterrows():
        if not row["feasible"]:
            solution, residual_norm = nnls(grid.coefficients, np.array([row["d1"], row["d2"]], dtype=float),)

            handled.loc[index, "adjusted_solar_kwh"] = solution[0]
            handled.loc[index, "adjusted_battery_kwh"] = solution[1]
            handled.loc[index, "adjustment_method"] = (f"NNLS; residual norm={residual_norm:.4f}")

    return handled

# NNLS - produces the closest non-negative least-squares solution, not a perfect dispatch solution.

def plot_dispatch_and_cost(results: pd.DataFrame,) -> None:
    """Plot stacked daily energy usage and daily energy cost."""
    days = np.arange(1, len(results) + 1)

    fig, ax1 = plt.subplots(figsize=(13, 6))

    ax1.bar(days,  results["solar_kwh"],  label="Solar usage",)
    ax1.bar( days, results["battery_kwh"], bottom=results["solar_kwh"], label="Battery usage",)

    ax1.set_xlabel("Day")
    ax1.set_ylabel("Energy usage (kWh)")
    ax1.set_title("Daily Micro-Grid Dispatch and Energy Cost")
    ax1.set_xticks(days)
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(days,results["daily_cost_ugx"], marker="o", linestyle="-", label="Daily energy cost",)
    ax2.set_ylabel("Daily energy cost (UGX)")
    ax2.legend(loc="upper right")

    fig.tight_layout()
    plt.show()

# Run the plotting test
'''
python -c "import pandas as pd; from src.solar_microgrid.microgrid import MicroGrid; from src.solar_microgrid.analysis import solve_vectorised, calculate_costs, plot_dispatch_and_cost; df = pd.read_csv('data/microgrid_demand_30days.csv'); grid = MicroGrid(); results = solve_vectorised(grid, df); results = calculate_costs(results); plot_dispatch_and_cost(results)"
'''
# WILL Load the 30-day demand data.; Solve the energy equations using the vectorised method.
# Calculate the daily energy costs.
# Display the stacked bar chart with daily cost on the second axis.

# 9.1 - Add the sensitivity-analysis function
def sensitivity_analysis(grid: MicroGrid,demands: pd.DataFrame,n_simulations: int = 1000,seed: int = 42,) -> dict[str, object]:
    """
    Assess sensitivity to independent demand perturbations of +/- 5%.

    Random demand changes are uniformly distributed between -5% and +5%.
    A fixed seed makes the simulation reproducible.
    """
    if n_simulations <= 0:
        raise ValueError("n_simulations must be positive.")

    if demands.empty:
        raise ValueError("Demand data cannot be empty.")

    base_demands = demands[["D1_kwh", "D2_kwh"]].to_numpy(dtype=float)

    if not np.all(np.isfinite(base_demands)) or np.any(base_demands <= 0):
        raise ValueError("Demands must be finite and greater than zero.")

    rng = np.random.default_rng(seed)

    # Shape: simulations x days x demand variables.
    perturbations = rng.uniform(0.95, 1.05, size=(n_simulations, len(demands), 2))
    simulated_demands = base_demands[np.newaxis, :, :] * perturbations

    # Solve all simulated systems in one batched matrix operation.
    simulated_solutions = np.linalg.solve( grid.coefficients, simulated_demands.reshape(-1, 2).T,).T.reshape(n_simulations, len(demands), 2)

    baseline_solutions = np.linalg.solve( grid.coefficients, base_demands.T).T

    changes = simulated_solutions - baseline_solutions[np.newaxis, :, :]

    summary = {
        "solar_mean_absolute_change_kwh": float(np.mean(np.abs(changes[:, :, 0]))),
        "battery_mean_absolute_change_kwh": float(np.mean(np.abs(changes[:, :, 1]))),
        "solar_max_absolute_change_kwh": float(np.max(np.abs(changes[:, :, 0]))),
        "battery_max_absolute_change_kwh": float(np.max(np.abs(changes[:, :, 1]))),
        "solar_95th_percentile_change_kwh": float(np.percentile(np.abs(changes[:, :, 0]), 95)),
        "battery_95th_percentile_change_kwh": float(np.percentile(np.abs(changes[:, :, 1]), 95)),
        "condition_number": grid.condition_number(),
        "n_simulations": n_simulations,
        "seed": seed,
    }

    return summary

# Test the function
'''
python -c "import pandas as pd; from src.solar_microgrid.microgrid import MicroGrid; from src.solar_microgrid.analysis import sensitivity_analysis; df = pd.read_csv('data/microgrid_demand_30days.csv'); result = sensitivity_analysis(MicroGrid(), df); print(result)"
'''