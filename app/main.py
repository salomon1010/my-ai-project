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
    uploaded   = st.file_uploader("Upload CSV", type="csv")
    load_sample = st.button("Load Sample Data", type="primary")

    if st.session_state.get("pipeline_result"):
        st.success("Data loaded")
        total = st.session_state["pipeline_result"]["kpi_summary"]["total_projects"]
        st.caption(f"{total} projects in pipeline")

    st.divider()
    st.caption("Built with Claude AI · Streamlit · DuckDB")

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
    kpi    = result["kpi_summary"]

    # ── Global analytics filter bar (drives all tabs) ─────────────────────────
    from app.components.filter_bar import render_filter_bar
    filtered_projects = render_filter_bar(kpi["all_projects"])

    # Build a filtered KPI dict so charts and panels reflect filter state
    import pandas as _pd
    filtered_kpi = dict(kpi)
    filtered_kpi["all_projects"] = filtered_projects
    if filtered_projects:
        fdf = _pd.DataFrame(filtered_projects)
        total_f = len(fdf)
        filtered_kpi["total_projects"]         = total_f
        filtered_kpi["pct_on_track"]           = round(len(fdf[fdf.status=="on_track"])  /total_f*100,1)
        filtered_kpi["pct_at_risk"]            = round(len(fdf[fdf.status=="at_risk"])   /total_f*100,1)
        filtered_kpi["pct_delayed"]            = round(len(fdf[fdf.status=="delayed"])   /total_f*100,1)
        filtered_kpi["pct_completed"]          = round(len(fdf[fdf.status=="completed"]) /total_f*100,1)
        filtered_kpi["total_budget_variance"]  = float(fdf["budget_variance"].sum()) if "budget_variance" in fdf else kpi["total_budget_variance"]
        planned = fdf["planned_cost"].sum() if "planned_cost" in fdf.columns else 1
        filtered_kpi["total_budget_variance_pct"] = round(filtered_kpi["total_budget_variance"] / planned * 100, 2) if planned else 0
        late_f = fdf[fdf.schedule_delay_days > 0]
        filtered_kpi["avg_schedule_delay_days"] = round(late_f["schedule_delay_days"].mean(), 1) if len(late_f) else 0
        filtered_kpi["over_budget_projects"]   = fdf[fdf.is_over_budget==True].to_dict("records") if "is_over_budget" in fdf.columns else []
        filtered_kpi["late_projects"]          = late_f[["project_name","schedule_delay_days","owner"]].to_dict("records") if len(late_f) else []
        filtered_kpi["top_3_risks"]            = fdf.nlargest(3, "budget_variance_pct")[["project_name","risk_level","budget_variance_pct"]].to_dict("records") if "budget_variance_pct" in fdf.columns else []

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard",
        "📋 Projects",
        "⚠️ Issues & Recommendations",
        "💰 Financial Analysis",
        "🤖 AI Report",
        "📄 Export",
    ])

    # ── TAB 1: Dashboard ───────────────────────────────────────────────────────
    with tab1:
        st.subheader("Balanced Scorecard")
        from app.components.kpi_cards import render_kpi_cards
        render_kpi_cards(filtered_kpi)

        st.divider()

        from app.components.charts import (
            render_status_donut,
            render_risk_bar,
            render_dept_issues,
            render_budget_variance_chart,
            render_schedule_delay_chart,
            render_dept_performance,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            render_status_donut(filtered_projects)
        with col2:
            render_risk_bar(filtered_projects)
        with col3:
            render_dept_issues(filtered_kpi["issues_by_dept"])

        st.divider()

        col4, col5 = st.columns(2)
        with col4:
            render_budget_variance_chart(filtered_projects)
        with col5:
            render_schedule_delay_chart(filtered_projects)

        st.divider()
        render_dept_performance(filtered_projects)

    # ── TAB 2: Projects ────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Project Portfolio")
        from app.components.project_table import render_project_table
        render_project_table(filtered_projects)

    # ── TAB 3: Issues & Recommendations ───────────────────────────────────────
    with tab3:
        st.subheader("Issues, Risks & Recommendations")
        from app.components.issues_panel import render_issues_panel
        render_issues_panel(filtered_kpi)

    # ── TAB 4: Financial Analysis ──────────────────────────────────────────────
    with tab4:
        st.subheader("Financial Analysis — Cost Management")

        from app.components.financial_charts import (
            render_financial_summary_cards,
            render_revenue_expense_profit,
            render_planned_vs_actual,
            render_cumulative_cost,
            render_dept_financials,
            render_roi_by_project,
            render_profit_margin_pie,
        )
        from app.components.filter_bar import render_period_selector

        render_financial_summary_cards(kpi)
        st.divider()

        period = render_period_selector()
        period_map = {
            "Monthly":   ("financial_by_month",   "Monthly"),
            "Quarterly": ("financial_by_quarter", "Quarterly"),
            "Annually":  ("financial_by_year",    "Annual"),
        }
        data_key, label = period_map[period]
        fin_data = kpi.get(data_key, [])

        col_a, col_b = st.columns(2)
        with col_a:
            render_revenue_expense_profit(fin_data, label)
        with col_b:
            render_planned_vs_actual(fin_data, label)

        render_cumulative_cost(fin_data, label)

        st.divider()

        col_c, col_d = st.columns(2)
        with col_c:
            render_dept_financials(kpi.get("financial_by_dept", []))
        with col_d:
            render_profit_margin_pie(kpi.get("financial_by_dept", []))

        st.divider()
        render_roi_by_project(kpi.get("top_roi_projects", []))

        st.divider()
        st.subheader("Project-Level Cost Detail")
        if filtered_projects:
            import pandas as _pd2
            cost_df = _pd2.DataFrame(filtered_projects)
            cost_cols = [c for c in [
                "project_name", "department", "start_date",
                "planned_cost", "actual_cost", "revenue", "profit", "roi_pct",
                "budget_variance_pct", "status"
            ] if c in cost_df.columns]
            st.dataframe(
                cost_df[cost_cols],
                use_container_width=True,
                column_config={
                    "project_name":        st.column_config.TextColumn("Project"),
                    "department":          st.column_config.TextColumn("Dept"),
                    "start_date":          st.column_config.DateColumn("Start"),
                    "planned_cost":        st.column_config.NumberColumn("Planned $", format="$%.0f"),
                    "actual_cost":         st.column_config.NumberColumn("Actual $",  format="$%.0f"),
                    "revenue":             st.column_config.NumberColumn("Revenue $", format="$%.0f"),
                    "profit":              st.column_config.NumberColumn("Profit $",  format="$%.0f"),
                    "roi_pct":             st.column_config.NumberColumn("ROI %",     format="%.1f%%"),
                    "budget_variance_pct": st.column_config.NumberColumn("Budget Var %", format="%.1f%%"),
                    "status":              st.column_config.TextColumn("Status"),
                },
                hide_index=True,
            )

    # ── TAB 5: AI Report ───────────────────────────────────────────────────────
    with tab5:
        st.subheader("AI Executive Summary")

        def on_generate():
            from src.llm.prompt_builder import build_prompt
            from src.llm.claude_client import generate_report
            with st.spinner("Generating AI report... (5–10 seconds)"):
                prompt = build_prompt(kpi)
                st.session_state["pipeline_result"]["ai_report"] = generate_report(prompt)

        from app.components.ai_summary import render_ai_summary
        render_ai_summary(result.get("ai_report"), on_generate)

    # ── TAB 6: Export ──────────────────────────────────────────────────────────
    with tab6:
        st.subheader("Export Report")
        st.info("Generate an AI report first (AI Report tab), then export to PDF.")

        ai_report = result.get("ai_report", "")
        if ai_report and not ai_report.startswith("["):
            if st.button("Export PDF", type="primary"):
                from src.reporting.pdf_generator import generate_pdf
                output_dir = os.getenv("REPORTS_OUTPUT_DIR", "outputs/reports")
                os.makedirs(output_dir, exist_ok=True)
                pdf_path = f"{output_dir}/report_{date.today().strftime('%Y%m%d')}.pdf"
                with st.spinner("Building PDF..."):
                    generate_pdf(kpi, ai_report, pdf_path)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                    )
        else:
            st.button("Export PDF", disabled=True)
            st.caption("Go to the AI Report tab and click Generate Report first.")

else:
    st.info("Use the sidebar to load data and run the pipeline.")
    st.markdown("""
    **Getting started:**
    1. Click **Load Sample Data** in the sidebar to use the built-in 15-project dataset
    2. Explore the **Dashboard** tab for charts and balanced scorecard
    3. Use **Projects** tab to filter and search all projects
    4. Check **Issues & Recommendations** for automated risk analysis
    5. Click **Generate Report** in the AI Report tab for the AI executive summary
    6. Export to PDF from the Export tab
    """)
