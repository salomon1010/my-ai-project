import pytest
import csv
from demo.sample_data import SAMPLE_PROJECTS


@pytest.fixture(autouse=True)
def set_test_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.duckdb"))


@pytest.fixture
def sample_csv(tmp_path):
    csv_path = tmp_path / "projects.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SAMPLE_PROJECTS[0].keys())
        writer.writeheader()
        writer.writerows(SAMPLE_PROJECTS)
    return str(csv_path)


def test_pipeline_returns_expected_keys(sample_csv):
    from src.pipeline import run_pipeline
    result = run_pipeline(sample_csv)
    assert "kpi_summary" in result
    assert "ai_report" in result
    assert result["kpi_summary"]["total_projects"] == 15


def test_pipeline_completes_fast(sample_csv, mocker):
    mocker.patch(
        "src.pipeline.generate_report",
        return_value="## Executive Summary\nMocked report."
    )
    import time
    from src.pipeline import run_pipeline
    start = time.time()
    run_pipeline(sample_csv)
    elapsed = time.time() - start
    assert elapsed < 10, f"Pipeline took {elapsed:.1f}s — should be under 10s without LLM"


def test_pipeline_with_mocked_llm(sample_csv, mocker):
    mocker.patch(
        "src.pipeline.generate_report",
        return_value="## Executive Summary\nMocked report."
    )
    from src.pipeline import run_pipeline
    result = run_pipeline(sample_csv)
    assert result["ai_report"].startswith("## Executive Summary")
    assert result["kpi_summary"]["total_projects"] == 15


def test_pipeline_stages_called_in_order(sample_csv, mocker):
    """Verify all pipeline stages execute — order guaranteed by the dependency chain."""
    mock_ingest = mocker.patch("src.pipeline.load_csv_to_bronze", return_value=(15, 0))
    mock_silver = mocker.patch("src.pipeline.bronze_to_silver",   return_value=15)
    mock_gold   = mocker.patch("src.pipeline.silver_to_gold",     return_value=15)
    mock_kpi    = mocker.patch("src.pipeline.compute_kpi_summary", return_value={
        "total_projects": 15, "pct_on_track": 40.0, "pct_at_risk": 20.0,
        "pct_delayed": 40.0, "pct_completed": 0.0,
        "total_budget_variance": 50000, "total_budget_variance_pct": 12.5,
        "avg_schedule_delay_days": 10.0, "top_3_risks": [], "over_budget_projects": [],
        "late_projects": [], "issues_by_dept": [], "all_projects": []
    })
    mock_prompt = mocker.patch("src.pipeline.build_prompt",    return_value="test prompt")
    mock_llm    = mocker.patch("src.pipeline.generate_report", return_value="## Executive Summary\nTest.")

    from src.pipeline import run_pipeline
    result = run_pipeline(sample_csv)

    mock_ingest.assert_called_once()
    mock_silver.assert_called_once()
    mock_gold.assert_called_once()
    mock_kpi.assert_called_once()
    mock_prompt.assert_called_once()
    mock_llm.assert_called_once()

    assert result["kpi_summary"]["total_projects"] == 15


def test_pipeline_survives_llm_failure(sample_csv, mocker):
    """Pipeline must not crash when LLM returns fallback string."""
    mocker.patch(
        "src.pipeline.generate_report",
        return_value="[Report generation unavailable. Please check API key.]"
    )
    from src.pipeline import run_pipeline
    result = run_pipeline(sample_csv)

    assert "kpi_summary" in result
    assert "ai_report" in result
    assert result["kpi_summary"]["total_projects"] == 15
    assert "unavailable" in result["ai_report"].lower()
