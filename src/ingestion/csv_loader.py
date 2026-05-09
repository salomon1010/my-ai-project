import pandas as pd
from loguru import logger
from src.storage.db import get_connection


def load_csv_to_bronze(file_path: str) -> tuple[int, int]:
    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)

    required = {"project_name", "planned_cost"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"CSV is missing required columns: {missing}")

    initial_count = len(df)
    df = df[df["project_name"].notna() & (df["project_name"].str.strip() != "")]
    skipped = initial_count - len(df)

    con = get_connection()
    con.execute("CREATE OR REPLACE TABLE bronze_project_raw AS SELECT * FROM df")
    con.close()

    loaded = len(df)
    logger.info(f"Loaded {loaded} rows into bronze_project_raw ({skipped} skipped)")
    return loaded, skipped
