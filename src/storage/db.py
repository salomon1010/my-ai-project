import os
import duckdb
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> duckdb.DuckDBPyConnection:
    db_path = os.getenv("DB_PATH", "data/db/reporting.duckdb")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(db_path)
