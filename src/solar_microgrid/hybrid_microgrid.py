
"""Hybrid micro-grid with solar, battery and diesel generation."""
# this linear dependence asks; asks what happens if the third equation is linearly dependent on the first two.
# the eqn is x+y+z=D3
import numpy as np
from scipy.linalg import solve

from .microgrid import MicroGrid


class HybridMicroGrid(MicroGrid):
    """Extend MicroGrid to include a diesel generator."""

    def __init__(self) -> None:
        """Initialise the three-source coefficient matrix."""
        super().__init__()

        self.hybrid_coefficients = np.array([
            [3.0, 2.0, 0.0],
            [4.0, 1.0, 0.0],
            [1.0, 1.0, 1.0],])

    def solve_hybrid_day(self, d1: float, d2: float, d3: float) -> dict[str, float | bool]:
        """
        Solve for solar, battery and diesel energy supply.

        D1: daytime load constraint.
        D2: critical-equipment load constraint.
        D3: total energy supply constraint.
        """
        demands = np.array([d1, d2, d3], dtype=float)

        if not np.all(np.isfinite(demands)):
            raise ValueError("Demand values must be finite numbers.")

        if np.any(demands <= 0):
            raise ValueError("Demand values must be greater than zero.")

        determinant = float(np.linalg.det(self.hybrid_coefficients))

        if np.isclose(determinant, 0.0):
            raise ValueError( "The hybrid system has no unique solution." )

        solution = solve(self.hybrid_coefficients, demands)

        solar = float(solution[0])
        battery = float(solution[1])
        diesel = float(solution[2])

        return {
            "solar_kwh": solar,
            "battery_kwh": battery,
            "diesel_kwh": diesel,
            "feasible": bool(solar >= 0 and battery >= 0 and diesel >= 0),}

    def condition_number(self) -> float:
        """Return the condition number of the hybrid matrix."""
        return float(np.linalg.cond(self.hybrid_coefficients))
# testing the hybrid model with 
'''
python -c "from src.solar_microgrid.hybrid_microgrid import HybridMicroGrid; grid = HybridMicroGrid(); print('Determinant:', __import__('numpy').linalg.det(grid.hybrid_coefficients)); print('Condition number:', grid.condition_number()); print(grid.solve_hybrid_day(100, 80, 60))"
'''

# conclusion
'''
If we instead chose a third equation whose coefficient row was a linear combination of the first two, the three equations would no longer provide three independent constraints.
The system would have no unique solution: it would either have infinitely many solutions if the demands were consistent, or no exact solution if they were inconsistent.
'''

# python -c "import numpy as np; A = np.array([[3., 2., 0.], [4., 1., 0.], [7., 3., 0.]]); print('Determinant:', np.linalg.det(A)); print('Rank:', np.linalg.matrix_rank(A)); print('Number of unknowns:', A.shape[1])"
# determinant os 0 (matrix is singular)
# rank 2 (only two rows are linearly independent)
# 3 unkowns We have three energy-source variables.)

