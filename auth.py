import pandas as pd
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)


def load_users():
    return pd.read_csv("data/users.csv")


def authenticate(username, password):
    users = load_users()

    match = users[
        users["username"] == username
    ]

    if match.empty:
        return None

    user = match.iloc[0].to_dict()

    stored_password = str(
        user.get("password_hash", "")
    )

    # Prototype-only fallback.
    # Replace with password-hash validation.
    if stored_password == password:
        return user

    try:
        if check_password_hash(
            stored_password,
            password,
        ):
            return user
    except ValueError:
        pass

    return None


def apply_role_scope(df, user):
    role = user["role"]
    result = df.copy()

    if role == "Ministry":
        return result

    if role == "State":
        states = str(
            user.get("states", "")
        ).split("|")

        return result[
            result["state"].isin(states)
        ]

    if role == "District":
        states = str(
            user.get("states", "")
        ).split("|")

        districts = str(
            user.get("districts", "")
        ).split("|")

        return result[
            result["state"].isin(states)
            & result["district"].isin(districts)
        ]

    if role == "MP":
        constituencies = str(
            user.get("constituencies", "")
        ).split("|")

        return result[
            result["constituency"].isin(
                constituencies
            )
        ]

    if role == "Agency":
        agencies = str(
            user.get("agencies", "")
        ).split("|")

        return result[
            result["implementing_agency"].isin(
                agencies
            )
        ]

    if role == "Auditor":
        states = str(
            user.get("states", "")
        ).split("|")

        districts = str(
            user.get("districts", "")
        ).split("|")

        return result[
            result["state"].isin(states)
            & result["district"].isin(districts)
        ]

    return result.iloc[0:0]
