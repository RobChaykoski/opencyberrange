"""Small, transparent projections for aggregate activity charts.

The projection is deliberately simple: a least-squares line over the most recent
buckets, clamped to non-negative values and to twice the observed peak. It is a
visual aid for staffing and pacing, not a prediction about a learner.
"""

from __future__ import annotations

from statistics import linear_regression


def linear_forecast(
    values: list[int | float],
    periods: int,
    *,
    min_points: int = 3,
    max_history: int = 14,
    cap_factor: float = 2.0,
) -> list[int]:
    series = [float(value or 0) for value in values]
    if periods <= 0 or len(series) < min_points:
        return []

    window = series[-max_history:]
    peak = max(window)
    if peak <= 0:
        return []

    xs = list(range(len(window)))
    slope, intercept = linear_regression(xs, window)
    ceiling = peak * cap_factor
    points: list[int] = []
    for index in range(periods):
        predicted = intercept + slope * (len(window) + index)
        points.append(max(0, round(min(predicted, ceiling))))
    return points
