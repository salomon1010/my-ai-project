import streamlit as st


def render_kpi_cards(kpi: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Projects", kpi["total_projects"])

    with col2:
        st.metric(
            "On Track",
            f"{kpi['pct_on_track']:.1f}%",
            delta=f"{kpi['pct_completed']:.1f}% completed",
        )

    with col3:
        at_risk_delayed = kpi["pct_at_risk"] + kpi["pct_delayed"]
        st.metric(
            "At Risk / Delayed",
            f"{at_risk_delayed:.1f}%",
            delta=f"{kpi['pct_at_risk']:.1f}% at risk",
            delta_color="inverse",
        )

    with col4:
        v = kpi["total_budget_variance"]
        sign = "+" if v >= 0 else ""
        st.metric(
            "Budget Variance",
            f"${abs(v):,.0f}",
            delta=f"{sign}{kpi['total_budget_variance_pct']:.1f}% vs plan",
            delta_color="inverse" if v > 0 else "normal",
        )

    # Second row
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        critical_count = sum(
            1 for p in kpi["all_projects"] if p.get("risk_level") == "critical"
        )
        st.metric("Critical Projects", critical_count,
                  delta="needs immediate action" if critical_count else "none",
                  delta_color="inverse" if critical_count else "normal")

    with col6:
        st.metric("Avg Delay (late projects)",
                  f"{kpi['avg_schedule_delay_days']:.0f} days")

    with col7:
        over = len(kpi.get("over_budget_projects", []))
        st.metric("Over-Budget Projects", over,
                  delta=f"{over} projects need review" if over else "all within budget",
                  delta_color="inverse" if over else "normal")

    with col8:
        completed = sum(
            1 for p in kpi["all_projects"] if p.get("status") == "completed"
        )
        st.metric("Completed", completed,
                  delta=f"of {kpi['total_projects']} total")
