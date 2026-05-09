# AI Executive Reporting System

Turn raw project data into AI-generated executive reports — automatically.

> "I help organizations automate reporting and decision-making by connecting
> their raw data to AI-generated executive insights."

## What it does

1. Ingests raw CSV project data
2. Cleans and normalizes it (bronze → silver → gold pipeline)
3. Computes portfolio KPIs (budget variance, schedule delays, risk levels)
4. Generates an AI-written executive summary using Claude
5. Displays results in a web dashboard
6. Exports a professional PDF report

## Prerequisites

- Python 3.11+
- Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com)

## Setup (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Load sample data and run pipeline
python demo/demo_reset.py
```

## Run the demo

```bash
streamlit run app/main.py
```

Open your browser to http://localhost:8501

**Demo flow:**
1. Click **Load Sample Data** in the sidebar
2. Review the KPI summary cards and project table
3. Click **Generate Report** to create an AI executive summary
4. Click **Export PDF** to download the full report

## Reset for a fresh demo

```bash
python demo/demo_reset.py
```

Run this before every client meeting.

## Run tests (no API key required)

```bash
pytest tests/ -v
```

## Architecture

```
CSV  →  DuckDB Bronze  →  Silver (clean)  →  Gold (KPIs)
     →  Portfolio Summary  →  Claude AI  →  Report + PDF
```

See `.claude/specs/ai-executive-reporting/design.md` for the full architecture.

## Consulting offer

**AI Reporting Automation Pilot**
- Price: $5,000–$10,000
- Timeline: 30 days
- Deliverables: data pipeline, KPI model, AI report, dashboard, executive demo
