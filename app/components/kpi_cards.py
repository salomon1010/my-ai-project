import streamlit as st


def render_kpi_cards(kpi_summary: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Projects",
            value=kpi_summary["total_projects"]
        )

    with col2:
        st.metric(
            label="On Track",
            value=f"{kpi_summary['pct_on_track']:.1f}%",
            delta=f"{kpi_summary['pct_completed']:.1f}% completed",
            delta_color="normal"
        )

    with col3:
        at_risk_delayed = kpi_summary["pct_at_risk"] + kpi_summary["pct_delayed"]
        st.metric(
            label="At Risk / Delayed",
            value=f"{at_risk_delayed:.1f}%",
            delta=f"{kpi_summary['pct_at_risk']:.1f}% at risk",
            delta_color="inverse"
        )

    with col4:
        variance = kpi_summary["total_budget_variance"]
        variance_pct = kpi_summary["total_budget_variance_pct"]
        sign = "+" if variance >= 0 else ""
        st.metric(
            label="Budget Variance",
            value=f"${abs(variance):,.0f}",
            delta=f"{sign}{variance_pct:.1f}% vs plan",
            delta_color="inverse" if variance > 0 else "normal"
        )
