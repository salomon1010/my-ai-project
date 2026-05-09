from loguru import logger
from src.storage.db import get_connection


def silver_to_gold() -> int:
    con = get_connection()
    con.execute("""
        CREATE OR REPLACE TABLE gold_project_kpi AS
        SELECT
            *,
            (actual_cost - planned_cost)                                        AS budget_variance,
            ROUND(((actual_cost - planned_cost) / planned_cost * 100.0), 2)    AS budget_variance_pct,
            DATEDIFF('day', planned_finish_date, actual_finish_date)            AS schedule_delay_days,
            CASE
                WHEN ((actual_cost - planned_cost) / planned_cost * 100.0) > 10
                THEN TRUE ELSE FALSE
            END                                                                  AS is_over_budget,
            CASE
                WHEN actual_finish_date > planned_finish_date
                THEN TRUE ELSE FALSE
            END                                                                  AS is_late
        FROM silver_project_clean
    """)
    count = con.execute("SELECT COUNT(*) FROM gold_project_kpi").fetchone()[0]
    con.close()
    logger.info(f"Gold layer: {count} rows in gold_project_kpi")
    return count
