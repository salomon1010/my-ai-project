from loguru import logger
from src.storage.db import get_connection


def bronze_to_silver() -> int:
    con = get_connection()
    con.execute("""
        CREATE OR REPLACE TABLE silver_project_clean AS
        SELECT
            TRIM(project_name)                                              AS project_name,
            TRIM(department)                                                AS department,
            TRY_CAST(planned_cost AS DOUBLE)                               AS planned_cost,
            TRY_CAST(actual_cost AS DOUBLE)                                AS actual_cost,
            CAST(TRY_STRPTIME(planned_finish_date, '%Y-%m-%d') AS DATE)     AS planned_finish_date,
            CAST(TRY_STRPTIME(actual_finish_date,  '%Y-%m-%d') AS DATE)    AS actual_finish_date,
            CASE LOWER(TRIM(status))
                WHEN 'on track'   THEN 'on_track'
                WHEN 'on_track'   THEN 'on_track'
                WHEN 'green'      THEN 'on_track'
                WHEN 'at risk'    THEN 'at_risk'
                WHEN 'at_risk'    THEN 'at_risk'
                WHEN 'amber'      THEN 'at_risk'
                WHEN 'delayed'    THEN 'delayed'
                WHEN 'red'        THEN 'delayed'
                WHEN 'completed'  THEN 'completed'
                ELSE LOWER(TRIM(status))
            END                                                             AS status,
            LOWER(TRIM(risk_level))                                         AS risk_level,
            COALESCE(issue_description, '')                                 AS issue_description,
            COALESCE(owner, 'Unassigned')                                   AS owner
        FROM bronze_project_raw
        WHERE project_name IS NOT NULL
          AND planned_cost IS NOT NULL
    """)
    count = con.execute("SELECT COUNT(*) FROM silver_project_clean").fetchone()[0]
    con.close()
    logger.info(f"Silver layer: {count} rows in silver_project_clean")
    return count
