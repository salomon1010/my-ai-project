import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(
    page_title="AI Executive Reporting",
    page_icon="📊",
    layout="wide"
)

st.title("AI Executive Reporting System")
st.caption("Turn raw project data into AI-generated executive insights automatically.")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Data Source")
    uploaded = st.file_uploader("Upload CSV", type="csv")
    load_sample = st.button("Load Sample Data", type="primary")

    if st.session_state.get("pipeline_result"):
        st.success("Data loaded")
        total = st.session_state["pipeline_result"]["kpi_summary"]["total_projects"]
        st.caption(f"{total} projects in pipeline")

# ── Session state ──────────────────────────────────────────────────────────────
if "pipeline_result" not in st.session_state:
    st.session_state["pipeline_result"] = None

# ── Trigger pipeline ───────────────────────────────────────────────────────────
if load_sample:
    from src.pipeline import run_pipeline
    with st.spinner("Running data pipeline..."):
        st.session_state["pipeline_result"] = run_pipeline("data/input/project_data.csv")
    st.rerun()

if uploaded is not None:
    from src.pipeline import run_pipeline
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        f.write(uploaded.read())
        tmp_path = f.name
    with st.spinner("Running data pipeline..."):
        st.session_state["pipeline_result"] = run_pipeline(tmp_path)
    st.rerun()

# ── Display results ────────────────────────────────────────────────────────────
if st.session_state["pipeline_result"]:
    result = st.session_state["pipeline_result"]
    kpi = result["kpi_summary"]

    st.subheader("Portfolio KPI Summary")
    from app.components.kpi_cards import render_kpi_cards
    render_kpi_cards(kpi)

    st.divider()

    st.subheader("Project Portfolio")
    from app.components.project_table import render_project_table
    render_project_table(kpi["all_projects"])

    st.divider()

    st.subheader("AI Executive Summary")

    def on_generate():
        from src.llm.prompt_builder import build_prompt
        from src.llm.claude_client import generate_report
        with st.spinner("Generating AI report... (5-10 seconds)"):
            prompt = build_prompt(kpi)
            st.session_state["pipeline_result"]["ai_report"] = generate_report(prompt)

    from app.components.ai_summary import render_ai_summary
    render_ai_summary(result["ai_report"], on_generate)

    st.divider()

    st.subheader("Export")
    if st.button("Export PDF"):
        from src.reporting.pdf_generator import generate_pdf
        output_dir = os.getenv("REPORTS_OUTPUT_DIR", "outputs/reports")
        os.makedirs(output_dir, exist_ok=True)
        pdf_path = f"{output_dir}/report_{date.today().strftime('%Y%m%d')}.pdf"

        with st.spinner("Building PDF..."):
            generate_pdf(kpi, result["ai_report"], pdf_path)

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download PDF Report",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )

else:
    st.info("Use the sidebar to load data and run the pipeline.")
    st.markdown("""
    **Getting started:**
    1. Click **Load Sample Data** to use the built-in 15-project dataset
    2. Or upload your own CSV with project data
    3. Click **Generate Report** to create an AI executive summary
    4. Click **Export PDF** to download the full report
    """)
