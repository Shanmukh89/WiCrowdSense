"""
WiCrowdSense — ML Model Training & Evaluation
Trains a Gradient Boosting Regressor on aggregated Wi-Fi signal features
to predict people_count.

Features (per-link): rssi, mean_csi_amplitude, variance_csi_amplitude,
                     spectral_entropy, doppler_shift
Aggregation: mean across all 6 links within each timestamp window.
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "wicrowdsense_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "crowd_model.pkl")

FEATURE_COLS = [
    "rssi",
    "mean_csi_amplitude",
    "variance_csi_amplitude",
    "spectral_entropy",
    "doppler_shift",
]
TARGET = "people_count"


def load_and_aggregate(path):
    """
    Load raw dataset, round timestamps to group per-time-step rows,
    and aggregate the 6 link readings into a single feature vector per step.
    """
    df = pd.read_csv(path)
    print(f"Raw dataset: {len(df)} rows, {len(df.columns)} columns")

    # Group by rounded timestamp (each step has 6 link rows at ~same time)
    df["ts_group"] = (df["timestamp"] * 1000).astype(int) // 6

    agg = df.groupby("ts_group").agg(
        rssi_mean=("rssi", "mean"),
        rssi_std=("rssi", "std"),
        mean_csi_amplitude=("mean_csi_amplitude", "mean"),
        variance_csi_amplitude=("variance_csi_amplitude", "mean"),
        spectral_entropy=("spectral_entropy", "mean"),
        doppler_shift=("doppler_shift", "mean"),
        people_count=("people_count", "first"),
    ).reset_index(drop=True)

    agg.rename(columns={"rssi_mean": "rssi"}, inplace=True)
    agg.drop(columns=["rssi_std"], inplace=True, errors="ignore")

    print(f"Aggregated: {len(agg)} samples")
    return agg


def train(df):
    X = df[FEATURE_COLS].values
    y = df[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nTrain size: {len(X_train)}  |  Test size: {len(X_test)}")

    # ── Gradient Boosting Regressor ──────────────────────────────────────
    model = GradientBoostingRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.9,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n--- Gradient Boosting Results ---")
    print(f"  MAE  : {mae:.3f}")
    print(f"  R^2  : {r2:.5f}")

    # ── Feature importances ──────────────────────────────────────────────
    print(f"\n--- Feature Importances ---")
    for name, imp in sorted(
        zip(FEATURE_COLS, model.feature_importances_), key=lambda x: -x[1]
    ):
        print(f"  {name:30s} {imp:.4f}")

    # ── Save model ───────────────────────────────────────────────────────
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"\n[OK] Model saved -> {MODEL_PATH}")

    # ── Print a simple lookup table for the dashboard ────────────────────
    print("\n--- Lookup table (for dashboard approximation) ---")
    print("  people | rssi     | mean_csi | var_csi   | entropy | doppler")
    print("  " + "-" * 70)
    for pc in [0, 5, 10, 20, 30, 50, 75, 100, 150]:
        subset = df[df[TARGET] == pc]
        if len(subset) == 0:
            continue
        row = subset[FEATURE_COLS].mean()
        print(
            f"  {pc:>6d} | {row['rssi']:>7.2f} | {row['mean_csi_amplitude']:.4f}"
            f"  | {row['variance_csi_amplitude']:.6f} | {row['spectral_entropy']:.4f}"
            f"  | {row['doppler_shift']:.4f}"
        )

    return model


def main():
    df = load_and_aggregate(DATASET_PATH)
    train(df)


if __name__ == "__main__":
    main()
