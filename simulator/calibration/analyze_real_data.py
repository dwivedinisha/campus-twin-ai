"""
Calibration script: analyzes a real building energy/occupancy dataset
to extract patterns we can use to tune our simulator's parameters.

This script does NOT feed real data into our simulated dataset.
It only prints findings for us to manually compare against our config.

Run with:
    python simulator/calibration/analyze_real_data.py
"""

import pandas as pd
import numpy as np
import os

DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "raw", "real_energy_data.xlsx"
)

TIMESTAMP_COL = "date"
POWER_COL = "Power Consumption"
TEMP_COL = "Outdoor Temperature"
OCCUPANCY_COL = "Occupancy"


def main():
    if not os.path.exists(DATA_PATH):
        print(f"Real dataset not found at: {DATA_PATH}")
        return

    df = pd.read_excel(DATA_PATH)
    df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL])
    df["hour"] = df[TIMESTAMP_COL].dt.hour
    df["is_weekend"] = df[TIMESTAMP_COL].dt.weekday >= 5

    print(f"Total rows: {len(df)}")
    print(f"Date range: {df[TIMESTAMP_COL].min()} to {df[TIMESTAMP_COL].max()}")
    print(f"Occupancy range: {df[OCCUPANCY_COL].min()} to {df[OCCUPANCY_COL].max()}")
    print(f"Power range: {df[POWER_COL].min():.2f} to {df[POWER_COL].max():.2f}")

    print("\n--- Real hourly occupancy pattern (weekday) ---")
    weekday_occ = df[~df["is_weekend"]].groupby("hour")[OCCUPANCY_COL].mean()
    print(weekday_occ.round(2))

    print("\n--- Real hourly occupancy pattern (weekend) ---")
    weekend_occ = df[df["is_weekend"]].groupby("hour")[OCCUPANCY_COL].mean()
    print(weekend_occ.round(2))

    print("\n--- Real hourly temperature pattern ---")
    temp_profile = df.groupby("hour")[TEMP_COL].mean()
    print(temp_profile.round(2))

    print("\n--- Correlations with power ---")
    print(df[[OCCUPANCY_COL, TEMP_COL, POWER_COL]].corr()[POWER_COL])

    # Linear regression: power ≈ a + b*occupancy + c*temperature
    X = df[[OCCUPANCY_COL, TEMP_COL]].values
    y = df[POWER_COL].values
    X_design = np.column_stack([np.ones(len(X)), X])
    coeffs, *_ = np.linalg.lstsq(X_design, y, rcond=None)

    print("\n--- Estimated linear relationship ---")
    print(f"power ≈ {coeffs[0]:.3f} + {coeffs[1]:.4f}*occupancy + {coeffs[2]:.4f}*temperature")

    # Normalize occupancy pattern to a 0-1 ratio (for comparing shape to our profiles)
    max_occ = df[OCCUPANCY_COL].max()
    print("\n--- Normalized weekday occupancy ratio (0-1 scale, for shape comparison) ---")
    print((weekday_occ / max_occ).round(2))


if __name__ == "__main__":
    main()