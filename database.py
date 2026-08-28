import duckdb
import pandas as pd

DB_PATH = "mplads.duckdb"


def get_connection():
    return duckdb.connect(DB_PATH)


def initialize_database():
    con = get_connection()

    con.execute("""
        CREATE TABLE IF NOT EXISTS works (
            work_id VARCHAR PRIMARY KEY,
            state VARCHAR,
            district VARCHAR,
            constituency VARCHAR,
            mp_name VARCHAR,
            work_title VARCHAR,
            sector VARCHAR,
            implementing_agency VARCHAR,
            recommendation_date DATE,
            sanction_date DATE,
            expected_completion_date DATE,
            completion_date DATE,
            sanctioned_amount DOUBLE,
            actual_expenditure DOUBLE,
            progress_percentage DOUBLE,
            latitude DOUBLE,
            longitude DOUBLE,
            status VARCHAR,
            source_system VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS alert_reviews (
            alert_id VARCHAR,
            work_id VARCHAR,
            username VARCHAR,
            status VARCHAR,
            reviewer_note VARCHAR,
            updated_at TIMESTAMP
        )
    """)

    con.close()


def save_works(df):
    con = get_connection()

    con.register("works_df", df)

    con.execute("""
        INSERT OR REPLACE INTO works
        SELECT * FROM works_df
    """)

    con.close()


def load_works():
    con = get_connection()
    result = con.execute(
        "SELECT * FROM works"
    ).df()
    con.close()
    return result
