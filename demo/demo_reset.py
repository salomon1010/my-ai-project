"""
Run this before any client demo to reset to a clean, known state.

Usage: python demo/demo_reset.py

What it does:
1. Drops all DuckDB tables (bronze, silver, gold)
2. Regenerates the sample CSV from SAMPLE_PROJECTS
3. Runs the data pipeline (no LLM — fast reset)
4. Prints confirmation and next steps
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv

load_dotenv()


def reset():
    start = time.time()
    print("Resetting demo environment...")

    # 1. Drop all tables
    from src.storage.db import get_connection
    con = get_connection()
    for table in ["gold_project_kpi", "silver_project_clean", "bronze_project_raw"]:
        con.execute(f"DROP TABLE IF EXISTS {table}")
    con.close()
    print("  Database cleared")

    # 2. Regenerate sample CSV
    from demo.sample_data import write_sample_csv
    csv_path = "data/input/project_data.csv"
    write_sample_csv(csv_path)
    print(f"  Sample data written → {csv_path}")

    # 3. Run pipeline (data only — skip LLM for speed)
    from src.ingestion.csv_loader import load_csv_to_bronze
    from src.transforms.bronze_to_silver import bronze_to_silver
    from src.transforms.silver_to_gold import silver_to_gold
    from src.transforms.kpi_aggregator import compute_kpi_summary

    load_csv_to_bronze(csv_path)
    bronze_to_silver()
    silver_to_gold()
    summary = compute_kpi_summary()

    elapsed = round(time.time() - start, 1)
    total = summary["total_projects"]

    print(f"  Pipeline complete — {total} projects loaded")
    print(f"\nReset complete in {elapsed}s")
    print("\nDemo is ready. Run:")
    print("  streamlit run app/main.py")
    print("\nThen click 'Load Sample Data' in the sidebar.")


if __name__ == "__main__":
    reset()
