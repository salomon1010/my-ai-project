import pytest
import csv


@pytest.fixture
def sample_csv(tmp_path):
    from demo.sample_data import SAMPLE_PROJECTS
    csv_path = tmp_path / "test_projects.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SAMPLE_PROJECTS[0].keys())
        writer.writeheader()
        writer.writerows(SAMPLE_PROJECTS)
    return str(csv_path)


@pytest.fixture(autouse=True)
def set_test_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.duckdb"))


def test_load_happy_path(sample_csv):
    from src.ingestion.csv_loader import load_csv_to_bronze
    from src.storage.db import get_connection

    loaded, skipped = load_csv_to_bronze(sample_csv)
    assert loaded == 15
    assert skipped == 0

    con = get_connection()
    count = con.execute("SELECT COUNT(*) FROM bronze_project_raw").fetchone()[0]
    con.close()
    assert count == 15


def test_missing_required_column(tmp_path):
    from src.ingestion.csv_loader import load_csv_to_bronze

    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("project_name,department\nProject A,IT\n")
    with pytest.raises(ValueError, match="missing required columns"):
        load_csv_to_bronze(str(bad_csv))


def test_empty_project_name_rows_skipped(tmp_path):
    from src.ingestion.csv_loader import load_csv_to_bronze

    rows = "project_name,planned_cost,actual_cost,department,planned_finish_date,actual_finish_date,status,risk_level,issue_description,owner\n"
    rows += ",50000,55000,IT,2024-01-01,2024-02-01,delayed,low,desc,owner\n"
    rows += ",60000,60000,Finance,2024-01-01,2024-01-01,on_track,low,desc,owner\n"
    rows += "Real Project,70000,70000,IT,2024-01-01,2024-01-01,on_track,low,desc,owner\n"

    csv_path = tmp_path / "empty_names.csv"
    csv_path.write_text(rows)
    loaded, skipped = load_csv_to_bronze(str(csv_path))
    assert loaded == 1
    assert skipped == 2
