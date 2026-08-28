from sklearn.ensemble import IsolationForest


MODEL_COLUMNS = [
    "sanctioned_amount",
    "utilization_ratio",
    "cost_overrun_ratio",
    "delay_days",
    "progress_percentage",
    "maturity_ratio",
    "spend_progress_gap",
    "peer_utilization_signal",
]


def add_ml_signal(df):
    d = df.copy()

    columns = [
        column for column in MODEL_COLUMNS
        if column in d.columns
    ]

    X = d[columns].replace(
        [np.inf, -np.inf],
        np.nan,
    )

    X = X.fillna(
        X.median(numeric_only=True)
    ).fillna(0)

    model = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X)

    raw = model.decision_function(X)

    low = np.percentile(raw, 5)
    high = np.percentile(raw, 95)

    d["ml_anomaly_signal"] = np.clip(
        (high - raw)
        / (high - low + 1e-9),
        0,
        1,
    )

    return d, model
