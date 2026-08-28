def add_peer_features(df):
    d = df.copy()

    grouped = d.groupby("peer_group")

    median_utilization = grouped[
        "utilization_ratio"
    ].transform("median")

    d["peer_median_utilization"] = (
        median_utilization
    )

    d["peer_utilization_gap"] = (
        d["utilization_ratio"]
        - d["peer_median_utilization"]
    ).abs()

    d["peer_utilization_signal"] = clip01(
        d["peer_utilization_gap"] / 0.50
    )

    d["peer_count"] = grouped[
        "work_id"
    ].transform("count")

    # Do not trust very small comparison groups.
    d.loc[
        d["peer_count"] < 5,
        "peer_utilization_signal"
    ] = 0

    return d
