import pandas as pd
import streamlit as st


def render_issues_panel(kpi: dict) -> None:
    over_budget = kpi.get("over_budget_projects", [])
    late        = kpi.get("late_projects", [])
    top_risks   = kpi.get("top_3_risks", [])
    issues_dept = kpi.get("issues_by_dept", [])

    # ── Critical alerts ──────────────────────────────────────────────────────
    critical = [p for p in kpi["all_projects"] if p.get("risk_level") == "critical"]
    if critical:
        for p in critical:
            st.error(
                f"🚨 **CRITICAL:** {p['project_name']} — "
                f"{p.get('budget_variance_pct', 0):+.1f}% budget, "
                f"{p.get('schedule_delay_days', 0)} days delayed"
            )

    col1, col2 = st.columns(2)

    # ── Over-budget projects ─────────────────────────────────────────────────
    with col1:
        st.subheader("Over-Budget Projects")
        if over_budget:
            for p in over_budget:
                with st.expander(
                    f"**{p['project_name']}** — {p['budget_variance_pct']:+.1f}%"
                ):
                    st.write(f"**Department:** {p['department']}")
                    st.write(f"**Planned:** ${p['planned_cost']:,.0f}")
                    st.write(f"**Actual:** ${p['actual_cost']:,.0f}")
                    overage = p['actual_cost'] - p['planned_cost']
                    st.write(f"**Overage:** ${overage:,.0f}")
        else:
            st.success("No projects are over budget.")

    # ── Late projects ────────────────────────────────────────────────────────
    with col2:
        st.subheader("Late Projects")
        if late:
            for p in late:
                severity = (
                    "🔴" if p["schedule_delay_days"] > 30
                    else "🟠" if p["schedule_delay_days"] > 10
                    else "🟡"
                )
                with st.expander(
                    f"{severity} **{p['project_name']}** — {p['schedule_delay_days']} days"
                ):
                    st.write(f"**Owner:** {p['owner']}")
                    st.write(f"**Delay:** {p['schedule_delay_days']} days behind schedule")
        else:
            st.success("All projects are on schedule.")

    st.divider()

    # ── Top risks ────────────────────────────────────────────────────────────
    st.subheader("Top Risk Projects")
    if top_risks:
        risk_cols = st.columns(len(top_risks))
        colors = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        for i, r in enumerate(top_risks):
            with risk_cols[i]:
                icon = colors.get(r["risk_level"], "⚪")
                st.metric(
                    label=f"{icon} {r['project_name']}",
                    value=r["risk_level"].upper(),
                    delta=f"{r['budget_variance_pct']:+.1f}% budget",
                    delta_color="inverse" if r["budget_variance_pct"] > 0 else "normal",
                )

    st.divider()

    # ── Issues by department ─────────────────────────────────────────────────
    st.subheader("Issues by Department")
    if issues_dept:
        df = pd.DataFrame(issues_dept)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "department":   st.column_config.TextColumn("Department"),
                "issue_count":  st.column_config.NumberColumn("Issues", format="%d"),
                "sample_issue": st.column_config.TextColumn("Sample Issue", width="large"),
            },
            hide_index=True,
        )
    else:
        st.info("No department issues logged.")

    st.divider()

    # ── Recommendations ───────────────────────────────────────────────────────
    st.subheader("Automated Recommendations")
    _render_recommendations(kpi)


def _render_recommendations(kpi: dict) -> None:
    recs = []

    critical = [p for p in kpi["all_projects"] if p.get("risk_level") == "critical"]
    if critical:
        names = ", ".join(p["project_name"] for p in critical)
        recs.append(("🚨 Immediate Escalation Required",
                      f"Critical-risk projects need executive attention: **{names}**. "
                      "Schedule emergency review within 48 hours."))

    over = kpi.get("over_budget_projects", [])
    if over:
        worst = over[0]
        recs.append(("💰 Budget Review",
                      f"**{worst['project_name']}** is {worst['budget_variance_pct']:+.1f}% over plan. "
                      "Initiate a budget re-forecast and identify cost-reduction levers."))

    late = kpi.get("late_projects", [])
    severe = [p for p in late if p["schedule_delay_days"] > 30]
    if severe:
        names = ", ".join(p["project_name"] for p in severe)
        recs.append(("📅 Schedule Recovery Plan",
                      f"Projects delayed 30+ days: **{names}**. "
                      "Require updated recovery plans with milestone commitments."))

    if kpi.get("pct_at_risk", 0) + kpi.get("pct_delayed", 0) > 40:
        recs.append(("📊 Portfolio Health Warning",
                      f"{kpi['pct_at_risk'] + kpi['pct_delayed']:.0f}% of the portfolio is at risk or delayed. "
                      "Consider a portfolio-level risk workshop this sprint."))

    dept_issues = kpi.get("issues_by_dept", [])
    if dept_issues:
        top_dept = dept_issues[0]
        recs.append(("🏢 Department Focus",
                      f"**{top_dept['department']}** has the most active issues ({top_dept['issue_count']}). "
                      "Assign a dedicated resolution owner and weekly check-in cadence."))

    if not recs:
        st.success("Portfolio is healthy — no critical recommendations at this time.")
        return

    for title, body in recs:
        st.warning(f"**{title}**\n\n{body}")
