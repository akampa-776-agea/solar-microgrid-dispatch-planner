
"""Generate reproducible illustrative demand data for a solar micro-grid."""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_demand_data(
    n_days: int = 30,
    seed: int = 42,
    output_path: str | Path = "data/microgrid_demand_30days.csv",)-> pd.DataFrame:
    """
    Generate daily demand data with a weekly pattern and random noise.

    The values are illustrative, not measurements from a real health centre.

    Parameters
    ----------
    n_days : int
        Number of days to generate.
    seed : int
        Random seed for reproducibility.
    output_path : str or Path
        Destination path for the generated CSV file.

    Returns
    -------
    pandas.DataFrame
        Daily demand values for D1 and D2.
    """
    if not isinstance(n_days, int) or isinstance(n_days, bool) or n_days <= 0:
        raise ValueError("n_days must be a positive integer.")

    rng = np.random.default_rng(seed)
    day_number = np.arange(1, n_days + 1)
    day_of_week = (day_number - 1) % 7

    # Illustrative daytime demand: higher on weekdays.
    weekday_pattern = np.array([0, 5, 7, 6, 4, -3, -5])
    d1 = 120 + weekday_pattern[day_of_week] + rng.normal(0, 5, n_days)

    # Critical-equipment demand is steadier throughout the week.
    d2 = 100 + 2 * np.sin(2 * np.pi * day_number / 7)
    d2 += rng.normal(0, 3, n_days)

    # Keep generated demand positive.
    d1 = np.maximum(d1, 1)
    d2 = np.maximum(d2, 1)

    df = pd.DataFrame({
            "day": day_number,
            "day_of_week": np.array([
                "Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"
            ])[day_of_week],
            "D1_kwh": np.round(d1, 2),
            "D2_kwh": np.round(d2, 2), })

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

    return df

# NB: This creates demand data, not observed energy consumption.
# check if they are missing values
# python -c "import pandas as pd; df = pd.read_csv('data/microgrid_demand_30days.csv'); print('Rows:', len(df)); print('Missing values:', df.isna().sum().sum())"