import streamlit as st
import pandas as pd

from auth import authenticate, apply_role_scope
from map_view import create_india_map
from risk_engine import (
    build_features,
    add_peer_features,
    find_duplicate_candidates,
    apply_duplicate_signals,
    add_ml_signal,
    calculate_score,
)

st.set_page_config(
    page_title="MPLADS Risk Monitor",
    layout="wide",
)


def login_screen():
    st.title("MPLADS Risk Monitoring Platform")
    st.caption(
        "Decision-support prototype. "
        "Alerts require human verification."
    )

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password",
    )

    if st.button("Login"):
        user = authenticate(
            username,
            password,
        )

        if user:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Invalid login")


if "user" not in st.session_state:
    login_screen()
    st.stop()

user = st.session_state["user"]

st.sidebar.success(
    f"{user['display_name']} — {user['role']}"
)

if st.sidebar.button("Logout"):
    del st.session_state["user"]
    st.rerun()

uploaded_file = st.sidebar.file_uploader(
    "Upload works data",
    type=["csv", "xlsx"],
)

if uploaded_file is None:
    data = pd.read_csv("data/works.csv")
else:
    if uploaded_file.name.endswith(".xlsx"):
        data = pd.read_excel(uploaded_file)
    else:
        data = pd.read_csv(uploaded_file)

# Apply jurisdiction restrictions before displaying data.
data = apply_role_scope(data, user)

if data.empty:
    st.warning(
        "No projects are available for your assigned jurisdiction."
    )
    st.stop()

features = build_features(data)
features = add_peer_features(features)

duplicate_pairs = find_duplicate_candidates(features)
features = apply_duplicate_signals(
    features,
    duplicate_pairs,
)

features, model = add_ml_signal(features)
scored = calculate_score(features)

st.title("MPLADS Risk Monitoring Platform")

st.caption(
    f"Visible jurisdiction: {user['role']} | "
    f"Projects: {len(scored)}"
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Overview",
        "India Risk Map",
        "Alert Queue",
        "Data Quality",
    ]
)

with tab1:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Projects",
        len(scored),
    )

    col2.metric(
        "Risk projects",
        int(
            (scored["risk_score"] >= 0.60).sum()
        ),
    ) **…**

_This response is too long to display in full._
