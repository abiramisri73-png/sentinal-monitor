import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from rapidfuzz.fuzz import token_set_ratio


def clip01(series):
    return series.clip(0, 1).fillna(0)


def build_features(df, as_of_date="2026-08-28"):
    d = df.copy()

    date_columns = [
        "recommendation_date",
        "sanction_date",
        "expected_completion_date",
        "completion_date",
    ]

    for column in date_columns:
        if column in d.columns:
            d[column] = pd.to_datetime(
                d[column],
                errors="coerce",
            )

    numeric_columns = [
        "sanctioned_amount",
        "actual_expenditure",
        "progress_percentage",
        "latitude",
        "longitude",
    ]

    for column in numeric_columns:
        if column in d.columns:
            d[column] = pd.to_numeric(
                d[column],
                errors="coerce",
            )

    d["sanctioned_amount"] = d[
        "sanctioned_amount"
    ].fillna(0)

    d["actual_expenditure"] = d[
        "actual_expenditure"
    ].fillna(0)

    d["progress_percentage"] = d[
        "progress_percentage"
    ].fillna(0)

    d["utilization_ratio"] = np.where(
        d["sanctioned_amount"] > 0,
        d["actual_expenditure"]
        / d["sanctioned_amount"],
        0,
    )

    d["cost_overrun_ratio"] = (
        d["utilization_ratio"] - 1
    ).clip(lower=0)

    # 25% cost overrun = maximum cost-overrun signal.
    d["cost_overrun_signal"] = clip01(
        d["cost_overrun_ratio"] / 0.25
    )

    start_date = d["sanction_date"].fillna(
        d["recommendation_date"]
    )

    d["expected_duration_days"] = (
        d["expected_completion_date"]
        - start_date
    ).dt.days

    d["expected_duration_days"] = (
        d["expected_duration_days"]
        .fillna(365)
        .clip(lower=1)
    )

    as_of = pd.Timestamp(as_of_date)
    actual_end = d["completion_date"].fillna(as_of)

    d["elapsed_days"] = (
        actual_end - start_date
    ).dt.days.fillna(0).clip(lower=0)

    d["delay_days"] = np.where(
        d["completion_date"].notna(),
        (
            d["completion_date"]
            - d["expected_completion_date"]
        ).dt.days,
        (
            as_of
            - d["expected_completion_date"]
        ).dt.days,
    )

    d["delay_days"] = (
        pd.Series(d["delay_days"], index=d.index)
        .fillna(0)
        .clip(lower=0)
    )

    # 180 days late = maximum delay signal.
    d["delay_signal"] = clip01(
        d["delay_days"] / 180
    )

    d["maturity_ratio"] = clip01(
        d["elapsed_days"]
        / d["expected_duration_days"]
    )

    # Low spending after the work is already mature.
    d["underutilization_signal"] = np.where(
        d["maturity_ratio"] > 0.50,
        clip01(
            (0.50 - d["utilization_ratio"])
            / 0.50
        ),
        0,
    )

    d["progress_fraction"] = (
        d["progress_percentage"] / 100
    )

    d["spend_progress_gap"] = (
        d["utilization_ratio"]
        - d["progress_fraction"]
    ).clip(lower=0)

    d["progress_spend_signal"] = clip01(
        d["spend_progress_gap"] / 0.50
    )

    d["peer_group"] = (
        d["state"].fillna("UNKNOWN").astype(str)
        + "|"
        + d["sector"].fillna("UNKNOWN").astype(str)
    )

    return d
