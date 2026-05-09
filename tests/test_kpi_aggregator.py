import pytest
import csv
from demo.sample_data import SAMPLE_PROJECTS


@pytest.fixture(autouse=True)
def set_test_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.duckdb"))


@pytest.fixture
def gold_data(tmp_path):
    """Load sample data all the way through to gold layer."""
    from src.ingestion.csv_loader import load_csv_to_bronze
    from src.transforms.bronze_to_silver import bronze_to_silver
    from src.transforms.silver_to_gold import silver_to_gold

    csv_path = tmp_path / "projects.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SAMPLE_PROJECTS[0].keys())
        writer.writeheader()
        writer.writerows(SAMPLE_PROJECTS)

    load_csv_to_bronze(str(csv_path))
    bronze_to_silver()
    silver_to_gold()


def test_total_projects(gold_data):
    from src.transforms.kpi_aggregator import compute_kpi_summary
    summary = compute_kpi_summary()
    assert summary["total_projects"] == 15


def test_pct_sums_to_100(gold_data):
    from src.transforms.kpi_aggregator import compute_kpi_summary
    summary = compute_kpi_summary()
    total = (
        summary["pct_on_track"]
        + summary["pct_at_risk"]
        + summary["pct_delayed"]
        + summary["pct_completed"]
    )
    assert abs(total - 100.0) < 0.5, f"Percentages sum to {total}, expected ~100"


def test_top_3_risks_length(gold_data):
    from src.transforms.kpi_aggregator import compute_kpi_summary
    summary = compute_kpi_summary()
    assert len(summary["top_3_risks"]) == 3


def test_issues_by_dept_has_3_departments(gold_data):
    from src.transforms.kpi_aggregator import compute_kpi_summary
    summary = compute_kpi_summary()
    depts = {row["department"] for row in summary["issues_by_dept"]}
    assert len(depts) == 3
