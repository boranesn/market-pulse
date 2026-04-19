"""Z-score and IQR-based anomaly detection on price/volume series."""
from __future__ import annotations

import polars as pl


def zscore_anomalies(values: list[float], threshold: float = 3.0) -> list[bool]:
    """Return a boolean mask: True where |z-score| > threshold."""
    s = pl.Series("v", values)
    mean = s.mean()
    std = s.std()
    if std is None or std == 0:
        return [False] * len(values)
    z = (s - mean) / std
    return (z.abs() > threshold).to_list()


def iqr_anomalies(values: list[float], factor: float = 1.5) -> list[bool]:
    """Return a boolean mask: True where value is outside IQR fences."""
    s = pl.Series("v", values)
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    if q1 is None or q3 is None:
        return [False] * len(values)
    iqr = q3 - q1
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    return ((s < lower) | (s > upper)).to_list()


def detect_price_anomalies(prices: list[float]) -> list[str]:
    if len(prices) < 5:
        return []
    flags = zscore_anomalies(prices)
    anomalies = []
    for i, is_anomaly in enumerate(flags):
        if is_anomaly and i == len(flags) - 1:
            anomalies.append(f"Price anomaly: {prices[i]:.2f} is a statistical outlier")
    return anomalies


def detect_volume_anomalies(volumes: list[int]) -> list[str]:
    if len(volumes) < 5:
        return []
    float_vols = [float(v) for v in volumes]
    flags = zscore_anomalies(float_vols)
    anomalies = []
    for i, is_anomaly in enumerate(flags):
        if is_anomaly and i == len(flags) - 1:
            anomalies.append(f"Volume anomaly: {volumes[i]:,} is a statistical outlier")
    return anomalies
