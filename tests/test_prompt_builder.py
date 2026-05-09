import pytest


MOCK_KPI = {
    "total_projects": 5,
    "pct_on_track": 40.0,
    "pct_at_risk": 20.0,
    "pct_delayed": 40.0,
    "pct_completed": 0.0,
    "total_budget_variance": 50000,
    "total_budget_variance_pct": 12.5,
    "avg_schedule_delay_days": 21.0,
    "top_3_risks": [
        {"project_name": "Alpha Project", "risk_level": "critical", "budget_variance_pct": 32.0},
        {"project_name": "Beta Project",  "risk_level": "high",     "budget_variance_pct": 18.0},
        {"project_name": "Gamma Project", "risk_level": "medium",   "budget_variance_pct": 5.0},
    ],
    "over_budget_projects": [
        {"project_name": "Alpha Project", "department": "IT", "planned_cost": 100000, "actual_cost": 132000, "budget_variance_pct": 32.0},
        {"project_name": "Beta Project",  "department": "Finance", "planned_cost": 50000, "actual_cost": 59000, "budget_variance_pct": 18.0},
    ],
    "late_projects": [
        {"project_name": "Alpha Project", "schedule_delay_days": 45, "owner": "Alice"},
        {"project_name": "Delta Project", "schedule_delay_days": 10, "owner": "Bob"},
    ],
    "issues_by_dept": [
        {"department": "IT",      "issue_count": 3, "sample_issue": "Vendor delays"},
        {"department": "Finance", "issue_count": 2, "sample_issue": "Compliance gap"},
    ],
    "all_projects": [],
}


def test_no_unfilled_placeholders():
    from src.llm.prompt_builder import build_prompt
    prompt = build_prompt(MOCK_KPI)
    assert "{" not in prompt, "Prompt has unfilled {} placeholders"


def test_project_names_in_prompt():
    from src.llm.prompt_builder import build_prompt
    prompt = build_prompt(MOCK_KPI)
    for project in MOCK_KPI["over_budget_projects"]:
        assert project["project_name"] in prompt, \
            f"Expected '{project['project_name']}' in prompt"


def test_section_headers_present():
    from src.llm.prompt_builder import build_prompt
    prompt = build_prompt(MOCK_KPI)
    for header in ["## Executive Summary", "## Key Risks", "## Budget Concerns",
                   "## Schedule Delays", "## Recommended Actions"]:
        assert header in prompt, f"Missing section header: {header}"
