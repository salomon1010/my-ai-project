from src.storage.db import get_connection


def compute_kpi_summary() -> dict:
    con = get_connection()

    total = con.execute("SELECT COUNT(*) FROM gold_project_kpi").fetchone()[0]

    def pct(status_val):
        n = con.execute(
            "SELECT COUNT(*) FROM gold_project_kpi WHERE status = ?", [status_val]
        ).fetchone()[0]
        return round((n / total * 100) if total else 0, 1)

    pct_on_track = pct("on_track")
    pct_at_risk = pct("at_risk")
    pct_delayed = pct("delayed")
    pct_completed = pct("completed")

    budget_row = con.execute("""
        SELECT
            SUM(budget_variance)                                        AS total_variance,
            ROUND(SUM(budget_variance) / SUM(planned_cost) * 100, 2)   AS total_variance_pct
        FROM gold_project_kpi
    """).fetchone()
    total_budget_variance = budget_row[0] or 0
    total_budget_variance_pct = budget_row[1] or 0

    avg_delay = con.execute("""
        SELECT ROUND(AVG(schedule_delay_days), 1)
        FROM gold_project_kpi
        WHERE is_late = TRUE
    """).fetchone()[0] or 0

    top_3_risks = con.execute("""
        SELECT project_name, risk_level, budget_variance_pct
        FROM gold_project_kpi
        ORDER BY
            CASE risk_level
                WHEN 'critical' THEN 4
                WHEN 'high'     THEN 3
                WHEN 'medium'   THEN 2
                ELSE 1
            END DESC,
            budget_variance_pct DESC
        LIMIT 3
    """).df().to_dict("records")

    over_budget = con.execute("""
        SELECT project_name, department, planned_cost, actual_cost, budget_variance_pct
        FROM gold_project_kpi
        WHERE is_over_budget = TRUE
        ORDER BY budget_variance_pct DESC
    """).df().to_dict("records")

    late_projects = con.execute("""
        SELECT project_name, schedule_delay_days, owner
        FROM gold_project_kpi
        WHERE is_late = TRUE
        ORDER BY schedule_delay_days DESC
    """).df().to_dict("records")

    issues_by_dept = con.execute("""
        SELECT
            department,
            COUNT(*) AS issue_count,
            FIRST(issue_description) AS sample_issue
        FROM gold_project_kpi
        WHERE issue_description != ''
        GROUP BY department
        ORDER BY issue_count DESC
    """).df().to_dict("records")

    all_projects = con.execute("SELECT * FROM gold_project_kpi").df().to_dict("records")

    con.close()

    return {
        "total_projects": total,
        "pct_on_track": pct_on_track,
        "pct_at_risk": pct_at_risk,
        "pct_delayed": pct_delayed,
        "pct_completed": pct_completed,
        "total_budget_variance": total_budget_variance,
        "total_budget_variance_pct": total_budget_variance_pct,
        "avg_schedule_delay_days": avg_delay,
        "top_3_risks": top_3_risks,
        "over_budget_projects": over_budget,
        "late_projects": late_projects,
        "issues_by_dept": issues_by_dept,
        "all_projects": all_projects,
    }
