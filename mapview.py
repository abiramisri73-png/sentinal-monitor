import numpy as np
import plotly.express as px


def create_india_map(df):
    map_df = df.copy()

    map_df = map_df[
        map_df["latitude"].notna()
        & map_df["longitude"].notna()
    ].copy()

    if map_df.empty:
        return None

    # Aggregate multiple projects at one location.
    # The maximum risk wins so that one risky project
    # is not hidden by several normal projects.
    map_df = (
        map_df.groupby(
            [
                "state",
                "district",
                "latitude",
                "longitude",
            ],
            as_index=False,
        )
        .agg(
            risk_score=("risk_score", "max"),
            project_count=("work_id", "count"),
            high_risk_projects=(
                "risk_score",
                lambda values: int(
                    (values >= 0.60).sum()
                ),
            ),
        )
    )

    map_df["map_status"] = np.where(
        map_df["risk_score"] >= 0.60,
        "Risk",
        "No Risk",
    )

    fig = px.scatter_geo(
        map_df,
        lat="latitude",
        lon="longitude",
        color="map_status",
        color_discrete_map={
            "Risk": "#dc2626",
            "No Risk": "#16a34a",
        },
        size="project_count",
        size_max=18,
        hover_name="district",
        hover_data={
            "state": True,
            "project_count": True,
            "high_risk_projects": True,
            "risk_score": ":.2f",
            "latitude": False,
            "longitude": False,
        },
        scope="asia",
        projection="mercator",
        title="MPLADS Project Risk Map",
    )

    fig.update_geos(
        center={
            "lat": 22.5,
            "lon": 79.0,
        },
        projection_scale=4.5,
        showcountries=True,
        countrycolor="#94a3b8",
        showland=True,
        landcolor="#f8fafc",
        showocean=True,
        oceancolor="#e0f2fe",
        showlakes=True,
    )

    fig.update_layout(
        height=650,
        margin={
            "l": 0,
            "r": 0,
            "t": 50,
            "b": 0,
        },
        legend_title_text="Project status",
    )

    return fig
