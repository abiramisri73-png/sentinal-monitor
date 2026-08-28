def normalize_text(value):
    if pd.isna(value):
        return ""
    return " ".join(
        str(value).lower().split()
    )


def find_duplicate_candidates(df):
    d = df.copy()

    d["normalized_title"] = (
        d["work_title"].map(normalize_text)
    )

    pairs = []

    # Block by state and district instead of
    # comparing every project nationally.
    for (state, district), group in d.groupby(
        ["state", "district"],
        dropna=False,
    ):
        rows = list(
            group.to_dict("records")
        )

        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                left = rows[i]
                right = rows[j]

                if left["work_id"] == right["work_id"]:
                    continue

                left_amount = float(
                    left.get(
                        "sanctioned_amount",
                        0,
                    ) or 0
                )

                right_amount = float(
                    right.get(
                        "sanctioned_amount",
                        0,
                    ) or 0
                )

                maximum = max(
                    left_amount,
                    right_amount,
                )

                if maximum == 0:
                    continue

                amount_gap = abs(
                    left_amount - right_amount
                ) / maximum

                title_similarity = (
                    token_set_ratio(
                        left["normalized_title"],
                        right["normalized_title"],
                    ) / 100
                )

                same_agency = (
                    left.get("implementing_agency")
                    == right.get("implementing_agency")
                )

                same_constituency = (
                    left.get("constituency")
                    == right.get("constituency")
                )

                location_signal = int(
                    same_agency
                    or same_constituency
                )

                signal = (
                    0.60 * title_similarity
                    + 0.25 * (1 - amount_gap)
                    + 0.15 * location_signal
                )

                if (
                    title_similarity >= 0.80
                    and amount_gap <= 0.20
                    and signal >= 0.75
                ):
                    pairs.append({
                        "work_id": left["work_id"],
                        "matched_work_id": right["work_id"],
                        "duplicate_signal": signal,
                        "title_similarity": title_similarity,
                        "amount_gap": amount_gap,
                        "reason": (
                            "Similar title and amount "
                            "within the same district"
                        ),
                    })

    return pd.DataFrame(pairs)
