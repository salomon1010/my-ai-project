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
        st.info("No project data available.")
        return

    df = pd.DataFrame(projects)

    # ── Filter bar ────────────────────────────────────────────────────────────
    st.markdown("**Filter Projects**")
    fcol1, fcol2, fcol3, fcol4 = st.columns([2, 2, 2, 1])

    departments = sorted(df["department"].unique().tolist())
    statuses    = sorted(df["status"].unique().tolist())
    risks       = sorted(df["risk_level"].unique().tolist(),
                         key=lambda x: ["critical","high","medium","low"].index(x)
                         if x in ["critical","high","medium","low"] else 99)

    with fcol1:
        sel_dept = st.multiselect("Department", departments, key="filter_dept")
    with fcol2:
        sel_status = st.multiselect("Status", statuses, key="filter_status")
    with fcol3:
        sel_risk = st.multiselect("Risk Level", risks, key="filter_risk")
    with fcol4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear filters", key="clear_filters"):
            st.session_state.pop("filter_dept", None)
            st.session_state.pop("filter_status", None)
            st.session_state.pop("filter_risk", None)
            st.rerun()

    # Apply filters
    filtered = df.copy()
    if sel_dept:
        filtered = filtered[filtered["department"].isin(sel_dept)]
    if sel_status:
        filtered = filtered[filtered["status"].isin(sel_status)]
    if sel_risk:
        filtered = filtered[filtered["risk_level"].isin(sel_risk)]

    st.caption(f"Showing {len(filtered)} of {len(df)} projects")

    # Add emoji columns
    filtered = filtered.copy()
    filtered["status_display"]    = filtered["status"].map(
        lambda s: f"{STATUS_EMOJI.get(s, '')} {s}"
    )
    filtered["risk_display"]      = filtered["risk_level"].map(
        lambda r: f"{RISK_EMOJI.get(r, '')} {r}"
    )

    display_cols = [
        "project_name", "department", "status_display", "risk_display",
        "budget_variance_pct", "schedule_delay_days",
        "is_over_budget", "is_late", "owner"
    ]
    display_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[display_cols],
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
        height=450,
    )
