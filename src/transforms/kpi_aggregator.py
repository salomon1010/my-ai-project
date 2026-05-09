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

    # ── Financial summaries ────────────────────────────────────────────────────
    fin_totals = con.execute("""
        SELECT
            SUM(revenue)     AS total_revenue,
            SUM(actual_cost) AS total_expense,
            SUM(profit)      AS total_profit,
            ROUND(SUM(profit) / NULLIF(SUM(actual_cost),0) * 100, 2) AS overall_roi_pct
        FROM gold_project_kpi
    """).fetchone()

    financial_by_month = con.execute("""
        SELECT period_month AS period,
               SUM(revenue)     AS revenue,
               SUM(actual_cost) AS expense,
               SUM(profit)      AS profit,
               SUM(planned_cost) AS planned_cost
        FROM gold_project_kpi
        GROUP BY period_month ORDER BY period_month
    """).df().to_dict("records")

    financial_by_quarter = con.execute("""
        SELECT period_quarter AS period,
               SUM(revenue)     AS revenue,
               SUM(actual_cost) AS expense,
               SUM(profit)      AS profit,
               SUM(planned_cost) AS planned_cost
        FROM gold_project_kpi
        GROUP BY period_quarter, start_year, start_quarter
        ORDER BY start_year, start_quarter
    """).df().to_dict("records")

    financial_by_year = con.execute("""
        SELECT period_year AS period,
               SUM(revenue)     AS revenue,
               SUM(actual_cost) AS expense,
               SUM(profit)      AS profit,
               SUM(planned_cost) AS planned_cost
        FROM gold_project_kpi
        GROUP BY period_year ORDER BY period_year
    """).df().to_dict("records")

    financial_by_dept = con.execute("""
        SELECT department,
               SUM(revenue)     AS revenue,
               SUM(actual_cost) AS expense,
               SUM(profit)      AS profit,
               ROUND(SUM(profit)/NULLIF(SUM(actual_cost),0)*100,2) AS roi_pct
        FROM gold_project_kpi
        GROUP BY department ORDER BY revenue DESC
    """).df().to_dict("records")

    top_roi = con.execute("""
        SELECT project_name, department, revenue, actual_cost, profit, roi_pct
        FROM gold_project_kpi
        ORDER BY roi_pct DESC LIMIT 5
    """).df().to_dict("records")

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
        # Financial
        "total_revenue":        fin_totals[0] or 0,
        "total_expense":        fin_totals[1] or 0,
        "total_profit":         fin_totals[2] or 0,
        "overall_roi_pct":      fin_totals[3] or 0,
        "financial_by_month":   financial_by_month,
        "financial_by_quarter": financial_by_quarter,
        "financial_by_year":    financial_by_year,
        "financial_by_dept":    financial_by_dept,
        "top_roi_projects":     top_roi,
    }
