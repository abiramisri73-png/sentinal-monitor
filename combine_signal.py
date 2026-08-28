WEIGHTS = {
    "duplicate_signal": 0.25,
    "cost_overrun_signal": 0.20,
    "delay_signal": 0.20,
    "payment_pattern_signal": 0.15,
    "underutilization_signal": 0.10,
    "progress_spend_signal": 0.10,
}


def build_reasons(row):
    reasons = []

    if row.get("duplicate_signal", 0) >= 0.75:
        reasons.append(
            "Possible duplicate based on title, "
            "amount, or location similarity"
        )

    if row.get("cost_overrun_signal", 0) >= 0.60:
        reasons.append(
            f"Expenditure is "
            f"{row['utilization_ratio']:.0%} "
            "of the sanctioned amount"
        )

    if row.get("delay_signal", 0) >= 0.60:
        reasons.append(
            f"Project is approximately "
            f"{row['delay_days']:.0f} days late"
        )

    if row.get("underutilization_signal", 0) >= 0.60:
        reasons.append(
            "Elapsed project time is high "
            "relative to expenditure"
        )

    if row.get("progress_spend_signal", 0) >= 0.60:
        reasons.append(
            "Expenditure is materially ahead "
            "of reported physical progress"
        )

    if row.get("ml_anomaly_signal", 0) >= 0.75:
        reasons.append(
            "Combined features are unusual "
            "compared with similar records"
        )

    if not reasons:
        reasons.append(
            "No strong risk signal was triggered"
        )

    return reasons


def calculate_score(df):
    d = df.copy()

    for signal in WEIGHTS:
        if signal not in d.columns:
            d[signal] = 0.0

        d[signal] = (
            pd.to_numeric(
                d[signal],
                errors="coerce",
            )
            .fillna(0)
            .clip(0, 1)
        )

    d["explainable_score"] = 0.0

    for signal, weight in WEIGHTS.items():
        d["explainable_score"] += (
            d[signal] * weight
        )

    d["risk_score"] = (
        0.80 * d["explainable_score"]
        + 0.20 * d.get(
            "ml_anomaly_signal",
            0,
        )
    ).clip(0, 1)

    d["risk_category"] = np.select(
        [
            d["risk_score"] >= 0.60,
            d["risk_score"] < 0.60,
        ],
        [
            "Risk",
            "No Risk",
        ],
        default="No Risk",
    )

    d["reasons"] = d.apply(
        build_reasons,
        axis=1,
    )

    return d
