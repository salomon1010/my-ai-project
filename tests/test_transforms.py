import pytest
import csv
from demo.sample_data import SAMPLE_PROJECTS


@pytest.fixture(autouse=True)
def set_test_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.duckdb"))


@pytest.fixture
def loaded_bronze(tmp_path):
    """Load sample data into bronze, return csv path."""
    from src.ingestion.csv_loader import load_csv_to_bronze
    csv_path = tmp_path / "projects.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SAMPLE_PROJECTS[0].keys())
        writer.writeheader()
        writer.writerows(SAMPLE_PROJECTS)
    load_csv_to_bronze(str(csv_path))
    return str(csv_path)


def test_silver_date_type(loaded_bronze):
    from src.transforms.bronze_to_silver import bronze_to_silver
    from src.storage.db import get_connection
    bronze_to_silver()
    con = get_connection()
    col_types = {row[0]: row[1] for row in con.execute("DESCRIBE silver_project_clean").fetchall()}
    con.close()
    assert "DATE" in col_types.get("planned_finish_date", ""), \
        f"Expected DATE type, got: {col_types.get('planned_finish_date')}"


def test_silver_status_normalization(tmp_path):
    """Insert a row with status 'On Track' and verify it becomes 'on_track'."""
    from src.ingestion.csv_loader import load_csv_to_bronze
    from src.transforms.bronze_to_silver import bronze_to_silver
    from src.storage.db import get_connection

    row = dict(SAMPLE_PROJECTS[0])
    row["status"] = "On Track"
    csv_path = tmp_path / "norm_test.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerow(row)

    load_csv_to_bronze(str(csv_path))
    bronze_to_silver()
    con = get_connection()
    result = con.execute("SELECT status FROM silver_project_clean LIMIT 1").fetchone()[0]
    con.close()
    assert result == "on_track"


def test_silver_null_issue_description(tmp_path):
    from src.ingestion.csv_loader import load_csv_to_bronze
    from src.transforms.bronze_to_silver import bronze_to_silver
    from src.storage.db import get_connection

    row = dict(SAMPLE_PROJECTS[0])
    row["issue_description"] = ""
    csv_path = tmp_path / "null_test.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerow(row)

    load_csv_to_bronze(str(csv_path))
    bronze_to_silver()
    con = get_connection()
    result = con.execute("SELECT issue_description FROM silver_project_clean LIMIT 1").fetchone()[0]
    con.close()
    assert result == ""


def test_gold_budget_variance_math(tmp_path):
    from src.ingestion.csv_loader import load_csv_to_bronze
    from src.transforms.bronze_to_silver import bronze_to_silver
    from src.transforms.silver_to_gold import silver_to_gold
    from src.storage.db import get_connection

    row = dict(SAMPLE_PROJECTS[0])
    row["planned_cost"] = 100000
    row["actual_cost"] = 115000
    csv_path = tmp_path / "math_test.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerow(row)

    load_csv_to_bronze(str(csv_path))
    bronze_to_silver()
    silver_to_gold()
    con = get_connection()
    row_result = con.execute(
        "SELECT budget_variance, budget_variance_pct, is_over_budget FROM gold_project_kpi LIMIT 1"
    ).fetchone()
    con.close()

    assert row_result[0] == 15000.0, f"budget_variance should be 15000, got {row_result[0]}"
    assert row_result[1] == 15.0, f"budget_variance_pct should be 15.0, got {row_result[1]}"
    assert row_result[2] is True, "is_over_budget should be True for 15% over"


def test_gold_is_late_flag(tmp_path):
    from src.ingestion.csv_loader import load_csv_to_bronze
    from src.transforms.bronze_to_silver import bronze_to_silver
    from src.transforms.silver_to_gold import silver_to_gold
    from src.storage.db import get_connection

    row = dict(SAMPLE_PROJECTS[0])
    row["planned_finish_date"] = "2024-01-01"
    row["actual_finish_date"] = "2024-02-01"
    csv_path = tmp_path / "late_test.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerow(row)

    load_csv_to_bronze(str(csv_path))
    bronze_to_silver()
    silver_to_gold()
    con = get_connection()
    result = con.execute("SELECT is_late, schedule_delay_days FROM gold_project_kpi LIMIT 1").fetchone()
    con.close()
    assert result[0] is True
    assert result[1] == 31


def test_gold_on_time_not_late(tmp_path):
    from src.ingestion.csv_loader import load_csv_to_bronze
    from src.transforms.bronze_to_silver import bronze_to_silver
    from src.transforms.silver_to_gold import silver_to_gold
    from src.storage.db import get_connection

    row = dict(SAMPLE_PROJECTS[0])
    row["planned_finish_date"] = "2024-01-01"
    row["actual_finish_date"] = "2024-01-01"
    csv_path = tmp_path / "ontime_test.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerow(row)

    load_csv_to_bronze(str(csv_path))
    bronze_to_silver()
    silver_to_gold()
    con = get_connection()
    result = con.execute("SELECT is_late, schedule_delay_days FROM gold_project_kpi LIMIT 1").fetchone()
    con.close()
    assert result[0] is False
    assert result[1] == 0
