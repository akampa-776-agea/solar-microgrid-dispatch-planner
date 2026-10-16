
"""Tests for reproducible micro-grid demand data generation."""

import numpy as np
import pandas as pd
import pytest

from src.solar_microgrid.data_generator import generate_demand_data


def test_generates_requested_number_of_days(tmp_path):
    """Generate the requested number of daily records."""
    output = tmp_path / "demand.csv"

    df = generate_demand_data(n_days=30, seed=42,  output_path=output, )

    assert len(df) == 30
    assert output.exists()


def test_generated_data_has_expected_columns(tmp_path):
    """Check the structure of the generated dataset."""
    df = generate_demand_data( n_days=7, seed=42,  output_path=tmp_path / "demand.csv",)

    assert list(df.columns) == [  "day", "day_of_week",  "D1_kwh",  "D2_kwh", ]


def test_generated_demands_are_positive(tmp_path):
    """Both demand variables must be strictly positive."""
    df = generate_demand_data( n_days=30,  seed=42, output_path=tmp_path / "demand.csv", )

    assert (df["D1_kwh"] > 0).all()
    assert (df["D2_kwh"] > 0).all()


def test_generated_data_has_no_missing_values(tmp_path):
    """Generated records should have no missing values."""
    df = generate_demand_data(n_days=30,  seed=42, output_path=tmp_path / "demand.csv", )

    assert df.isna().sum().sum() == 0


def test_generation_is_reproducible(tmp_path):
    """The same seed should produce identical demand data."""
    df1 = generate_demand_data( n_days=30,seed=42,output_path=tmp_path / "first.csv", )

    df2 = generate_demand_data( n_days=30, seed=42, output_path=tmp_path / "second.csv", )

    pd.testing.assert_frame_equal(df1, df2)


def test_csv_matches_generated_dataframe(tmp_path):
    """The saved CSV should contain the generated records."""
    output = tmp_path / "demand.csv"

    df = generate_demand_data(  n_days=10,  seed=42,  output_path=output, )

    saved_df = pd.read_csv(output)

    pd.testing.assert_frame_equal(df, saved_df)


@pytest.mark.parametrize("n_days", [0, -1, 1.5, True])
def test_invalid_number_of_days_raises_value_error(n_days, tmp_path):
    """Reject invalid day counts."""
    with pytest.raises(ValueError):
        generate_demand_data( n_days=n_days,  output_path=tmp_path / "invalid.csv",)
