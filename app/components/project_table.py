import streamlit as st
import pandas as pd


def render_project_table(projects: list[dict]) -> None:
    if not projects:
        st.info("No project data available.")
        return

    df = pd.DataFrame(projects)

    display_cols = [
        "project_name", "department", "status", "risk_level",
        "budget_variance_pct", "schedule_delay_days",
        "is_over_budget", "is_late", "owner"
    ]
    display_cols = [c for c in display_cols if c in df.columns]
    df = df[display_cols]

    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "project_name":        st.column_config.TextColumn("Project"),
            "department":          st.column_config.TextColumn("Department"),
            "status":              st.column_config.TextColumn("Status"),
            "risk_level":          st.column_config.TextColumn("Risk"),
            "budget_variance_pct": st.column_config.NumberColumn(
                "Budget Var %", format="%.1f%%"
            ),
            "schedule_delay_days": st.column_config.NumberColumn("Delay (days)"),
            "is_over_budget":      st.column_config.CheckboxColumn("Over Budget"),
            "is_late":             st.column_config.CheckboxColumn("Late"),
            "owner":               st.column_config.TextColumn("Owner"),
        },
        hide_index=True,
    )
