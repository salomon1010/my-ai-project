import pandas as pd
import streamlit as st

STATUS_EMOJI = {
    "on_track": "🟢", "completed": "🔵", "at_risk": "🟠", "delayed": "🔴"
}
RISK_EMOJI = {
    "low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"
}


def render_project_table(projects: list[dict]) -> None:
    if not projects:
        st.warning("No projects match the current filters.")
        return

    df = pd.DataFrame(projects).copy()
    df["status_display"]   = df["status"].map(lambda s: f"{STATUS_EMOJI.get(s,'')} {s}")
    df["risk_display"]     = df["risk_level"].map(lambda r: f"{RISK_EMOJI.get(r,'')} {r}")

    display_cols = [
        "project_name", "department", "status_display", "risk_display",
        "budget_variance_pct", "schedule_delay_days",
        "is_over_budget", "is_late", "owner"
    ]
    display_cols = [c for c in display_cols if c in df.columns]

    st.caption(f"{len(df)} project{'s' if len(df) != 1 else ''}")

    st.dataframe(
        df[display_cols],
        use_container_width=True,
        column_config={
            "project_name":        st.column_config.TextColumn("Project"),
            "department":          st.column_config.TextColumn("Department"),
            "status_display":      st.column_config.TextColumn("Status"),
            "risk_display":        st.column_config.TextColumn("Risk"),
            "budget_variance_pct": st.column_config.NumberColumn(
                "Budget Var %", format="%.1f%%"
            ),
            "schedule_delay_days": st.column_config.NumberColumn("Delay (days)"),
            "is_over_budget":      st.column_config.CheckboxColumn("Over Budget"),
            "is_late":             st.column_config.CheckboxColumn("Late"),
            "owner":               st.column_config.TextColumn("Owner"),
        },
        hide_index=True,
        height=500,
    )
