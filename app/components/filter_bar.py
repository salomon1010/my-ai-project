import pandas as pd
import streamlit as st


def render_filter_bar(all_projects: list[dict]) -> list[dict]:
    """Renders the global filter bar and returns the filtered project list."""
    df = pd.DataFrame(all_projects)

    with st.expander("🔍 Analytics Filters", expanded=True):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])

        departments = sorted(df["department"].unique().tolist())
        statuses    = sorted(df["status"].unique().tolist())
        risk_order  = ["critical", "high", "medium", "low"]
        risks       = [r for r in risk_order if r in df["risk_level"].unique()]
        owners      = sorted(df["owner"].unique().tolist())

        with col1:
            sel_dept = st.multiselect(
                "Department", departments,
                key="g_dept", placeholder="All departments"
            )
        with col2:
            STATUS_LABELS = {
                "on_track": "🟢 On Track", "completed": "🔵 Completed",
                "at_risk": "🟠 At Risk",   "delayed": "🔴 Delayed",
            }
            sel_status = st.multiselect(
                "Status",
                options=statuses,
                format_func=lambda s: STATUS_LABELS.get(s, s),
                key="g_status", placeholder="All statuses"
            )
        with col3:
            RISK_LABELS = {
                "critical": "🔴 Critical", "high": "🟠 High",
                "medium": "🟡 Medium",     "low": "🟢 Low",
            }
            sel_risk = st.multiselect(
                "Risk Level",
                options=risks,
                format_func=lambda r: RISK_LABELS.get(r, r),
                key="g_risk", placeholder="All risk levels"
            )
        with col4:
            sel_owner = st.multiselect(
                "Owner", owners,
                key="g_owner", placeholder="All owners"
            )
        with col5:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Reset", key="g_reset", use_container_width=True):
                for k in ["g_dept", "g_status", "g_risk", "g_owner",
                          "g_budget_min", "g_budget_max"]:
                    st.session_state.pop(k, None)
                st.rerun()

        # Budget variance range slider
        min_v = float(df["budget_variance_pct"].min())
        max_v = float(df["budget_variance_pct"].max())
        if min_v < max_v:
            budget_range = st.slider(
                "Budget Variance % range",
                min_value=round(min_v, 1),
                max_value=round(max_v, 1),
                value=(round(min_v, 1), round(max_v, 1)),
                step=0.5,
                key="g_budget_range",
                format="%.1f%%",
            )
        else:
            budget_range = (min_v, max_v)

        # Search box
        search = st.text_input(
            "Search project name", key="g_search", placeholder="Type to search..."
        )

    # ── Apply all filters ──────────────────────────────────────────────────────
    filtered = df.copy()

    if sel_dept:
        filtered = filtered[filtered["department"].isin(sel_dept)]
    if sel_status:
        filtered = filtered[filtered["status"].isin(sel_status)]
    if sel_risk:
        filtered = filtered[filtered["risk_level"].isin(sel_risk)]
    if sel_owner:
        filtered = filtered[filtered["owner"].isin(sel_owner)]

    filtered = filtered[
        (filtered["budget_variance_pct"] >= budget_range[0]) &
        (filtered["budget_variance_pct"] <= budget_range[1])
    ]

    if search:
        filtered = filtered[
            filtered["project_name"].str.contains(search, case=False, na=False)
        ]

    active_filters = sum([
        bool(sel_dept), bool(sel_status), bool(sel_risk), bool(sel_owner),
        bool(search),
        budget_range != (round(min_v, 1), round(max_v, 1)),
    ])

    # Summary badge
    if active_filters:
        st.info(
            f"**{len(filtered)} of {len(df)} projects** match your filters "
            f"({active_filters} filter{'s' if active_filters > 1 else ''} active)"
        )
    else:
        st.caption(f"Showing all {len(df)} projects — use filters above to narrow down")

    return filtered.to_dict("records")
