
"""Tests for the MicroGrid class."""

import numpy as np
import pytest

from src.solar_microgrid.microgrid import MicroGrid


def test_determinant():
    """The coefficient matrix should have determinant -5."""
    grid = MicroGrid()

    assert np.isclose(grid.determinant(), -5.0)


def test_condition_number_is_positive():
    """The coefficient matrix should have a positive condition number."""
    grid = MicroGrid()

    assert grid.condition_number() > 0


def test_solve_day_returns_correct_dispatch():
    """Check the solution for D1=100 and D2=80."""
    grid = MicroGrid()

    result = grid.solve_day(100, 80)

    assert np.isclose(result["solar_kwh"], 12.0)
    assert np.isclose(result["battery_kwh"], 32.0)
    assert result["feasible"] is True


def test_infeasible_dispatch_is_flagged():
    """Negative battery usage should be flagged as infeasible."""
    grid = MicroGrid()

    result = grid.solve_day(10, 100)

    assert result["battery_kwh"] < 0
    assert result["feasible"] is False


@pytest.mark.parametrize("d1, d2",[
        (-10, 50),
        (50, -10),
        (float("nan"), 50),
        (50, float("inf")),
        (0, 50),
    ],
)
def test_invalid_demands_raise_value_error(d1, d2):
    """Reject negative, zero and non-finite demand values."""
    grid = MicroGrid()

    with pytest.raises(ValueError):
        grid.solve_day(d1, d2)

# python -m pytest tests/test_microgrid.py -v