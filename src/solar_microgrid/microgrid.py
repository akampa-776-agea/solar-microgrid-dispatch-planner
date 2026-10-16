
"""Core classes for solar micro-grid energy dispatch."""

import numpy as np
from scipy.linalg import solve


class MicroGrid:
    """Solve daily solar and battery energy dispatch requirements."""

    def __init__(self) -> None: # creates the matrix.
        """Initialise the micro-grid coefficient matrix."""
        self.coefficients = np.array([[3.0, 2.0], 
                                      [4.0, 1.0], ])

    def determinant(self) -> float: # checks whether the equations have a unique solution.
        """Return the determinant of the coefficient matrix."""
        return float(np.linalg.det(self.coefficients))

    def condition_number(self) -> float: # measures how sensitive the solution can be to changes in the inputs.
        """Return the condition number of the coefficient matrix."""
        return float(np.linalg.cond(self.coefficients))

    def solve_day(self, d1: float, d2: float) -> dict: # solves for solar and battery usage and flags physically infeasible results.
        """
        This solves for solar (x) and battery (y) usage.

        Parameters
        ----------
        d1 : float
            Daytime load demand in kWh.
        d2 : float
            Critical-equipment load demand in kWh.

        Returns
        -------
        dict
            Demand, solar usage, battery usage and feasibility status.
        """
        demands = np.array([d1, d2], dtype=float)

        if not np.all(np.isfinite(demands)):
            raise ValueError("Demand values must be finite numbers.")

        if np.any(demands < 0):
            raise ValueError("Demand values cannot be negative.")

        if np.any(demands == 0):
            raise ValueError("Demand values must be greater than zero.")

        if self.determinant() == 0:
            raise ValueError("The system has no unique solution.")

        solution = solve(self.coefficients, demands)

        solar = float(solution[0])
        battery = float(solution[1])

        return {
            "d1": float(d1),
            "d2": float(d2),
            "solar_kwh": solar,
            "battery_kwh": battery,
            "feasible": solar >= 0 and battery >= 0,
        }

# 10 - Implement interactive input validation

def get_positive_demand(prompt: str) -> float:
    """Prompt until the user enters a finite positive demand."""
    while True:
        raw_value = input(prompt).strip()

        if not raw_value:
            print("Input cannot be empty. Please try again.")
            continue

        try:
            value = float(raw_value)
        except ValueError:
            print("Please enter a numeric value.")
            continue

        if not np.isfinite(value):
            print("Please enter a finite number.")
            continue

        if value <= 0:
            print("Demand must be greater than zero.")
            continue

        return value


def interactive_dispatch(grid: MicroGrid) -> dict:
    """Collect daily demands interactively and solve the dispatch."""
    d1 = get_positive_demand("Enter daytime demand D1 (kWh): ")
    d2 = get_positive_demand("Enter critical-equipment demand D2 (kWh): ")

    result = grid.solve_day(d1, d2)
    print("Dispatch result:", result)

    if not result["feasible"]:
        print("Warning: the mathematical solution is physically infeasible.")

    return result

# we have added positive demand and interactive dispatch method
# test

#cd "C:\Users\GodfreyAkampa\OneDrive - raisingthevillage.org\12 OCTOBER 2026\Mini-Project 2 Solar Micro-Grid Dispatch Planner"

#python -c "from src.solar_microgrid.microgrid import MicroGrid, interactive_dispatch; interactive_dispatch(MicroGrid())"
#D1 = 100
#d2 = 80
