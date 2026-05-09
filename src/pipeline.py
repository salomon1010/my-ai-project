import time
from loguru import logger

from src.ingestion.csv_loader import load_csv_to_bronze
from src.transforms.bronze_to_silver import bronze_to_silver
from src.transforms.silver_to_gold import silver_to_gold
from src.transforms.kpi_aggregator import compute_kpi_summary
from src.llm.prompt_builder import build_prompt
from src.llm.claude_client import generate_report


def run_pipeline(csv_path: str) -> dict:
    start = time.time()

    logger.info("Stage 1: Ingestion")
    loaded, skipped = load_csv_to_bronze(csv_path)
    logger.info(f"  → {loaded} rows loaded, {skipped} skipped")

    logger.info("Stage 2: Bronze → Silver")
    n = bronze_to_silver()
    logger.info(f"  → {n} rows in silver")

    logger.info("Stage 3: Silver → Gold")
    n = silver_to_gold()
    logger.info(f"  → {n} rows in gold")

    logger.info("Stage 4: KPI Aggregation")
    kpi_summary = compute_kpi_summary()
    logger.info(f"  → {kpi_summary['total_projects']} projects summarized")

    logger.info("Stage 5: Generating AI Report")
    prompt = build_prompt(kpi_summary)
    ai_report = generate_report(prompt)
    logger.info(f"  → Report generated ({len(ai_report)} chars)")

    elapsed = round(time.time() - start, 2)
    logger.info(f"Pipeline complete in {elapsed}s")

    return {"kpi_summary": kpi_summary, "ai_report": ai_report}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    result = run_pipeline("data/input/project_data.csv")
    print(result["ai_report"])
