
"""Tests for the HybridMicroGrid class."""

import numpy as np
import pytest

from src.solar_microgrid.hybrid_microgrid import HybridMicroGrid


def test_hybrid_determinant_is_nonzero():
    """The hybrid coefficient matrix should be invertible."""
    grid = HybridMicroGrid()

    assert np.isclose(np.linalg.det(grid.hybrid_coefficients), -5.0)


def test_hybrid_condition_number_is_positive():
    """The hybrid coefficient matrix should have a positive condition number."""
    grid = HybridMicroGrid()

    assert grid.condition_number() > 0


def test_solve_hybrid_day_returns_correct_dispatch():
    """Check solar, battery and diesel dispatch."""
    grid = HybridMicroGrid()

    result = grid.solve_hybrid_day(100, 80, 60)

    assert np.isclose(result["solar_kwh"], 12.0)
    assert np.isclose(result["battery_kwh"], 32.0)
    assert np.isclose(result["diesel_kwh"], 16.0)
    assert result["feasible"] is True


@pytest.mark.parametrize(
    "d1, d2, d3",
    [
        (0, 80, 60),
        (100, -80, 60),
        (100, 80, -60),
        (float("nan"), 80, 60),
        (100, float("inf"), 60),
    ],
)
def test_invalid_hybrid_demands_raise_value_error(d1, d2, d3):
    """Reject zero, negative and non-finite demand values."""
    grid = HybridMicroGrid()

    with pytest.raises(ValueError):
        grid.solve_hybrid_day(d1, d2, d3)

# python -m pytest tests/test_hybrid_microgrid.py -v
# python -m pytest -v this verifies all three modules together.