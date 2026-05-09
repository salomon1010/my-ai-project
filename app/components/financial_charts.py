import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

REVENUE_COLOR  = "#10B981"
EXPENSE_COLOR  = "#EF4444"
PROFIT_COLOR   = "#3B82F6"
PLANNED_COLOR  = "#9CA3AF"


def render_financial_summary_cards(kpi: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Revenue",  f"${kpi['total_revenue']:,.0f}")
    with c2:
        st.metric("Total Expenses", f"${kpi['total_expense']:,.0f}")
    with c3:
        profit = kpi["total_profit"]
        st.metric("Total Profit", f"${profit:,.0f}",
                  delta=f"{'▲' if profit>=0 else '▼'} {abs(profit)/max(kpi['total_revenue'],1)*100:.1f}% margin",
                  delta_color="normal" if profit >= 0 else "inverse")
    with c4:
        st.metric("Overall ROI", f"{kpi['overall_roi_pct']:.1f}%",
                  delta="return on investment",
                  delta_color="normal" if kpi["overall_roi_pct"] >= 0 else "inverse")


def render_revenue_expense_profit(data: list[dict], period_label: str) -> None:
    if not data:
        st.info("No financial data available.")
        return
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_bar(name="Revenue",  x=df["period"], y=df["revenue"],  marker_color=REVENUE_COLOR)
    fig.add_bar(name="Expenses", x=df["period"], y=df["expense"],  marker_color=EXPENSE_COLOR)
    fig.add_bar(name="Profit",   x=df["period"], y=df["profit"],
                marker_color=[PROFIT_COLOR if v >= 0 else "#F97316" for v in df["profit"]])
    fig.update_layout(
        title=f"Revenue vs Expenses vs Profit — {period_label}",
        barmode="group", height=380,
        margin=dict(t=50, b=40, l=10, r=10),
        yaxis_title="$ Amount", xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_planned_vs_actual(data: list[dict], period_label: str) -> None:
    if not data:
        return
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_bar(name="Planned Cost", x=df["period"], y=df["planned_cost"], marker_color=PLANNED_COLOR)
    fig.add_bar(name="Actual Spend", x=df["period"], y=df["expense"],      marker_color=EXPENSE_COLOR, opacity=0.85)
    fig.update_layout(
        title=f"Planned vs Actual Spend — {period_label}",
        barmode="overlay", height=320,
        margin=dict(t=50, b=40, l=10, r=10),
        yaxis_title="$ Amount", xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_cumulative_cost(data: list[dict], period_label: str) -> None:
    if not data:
        return
    df = pd.DataFrame(data).copy()
    df["cum_revenue"] = df["revenue"].cumsum()
    df["cum_expense"] = df["expense"].cumsum()
    df["cum_profit"]  = df["profit"].cumsum()
    fig = go.Figure()
    fig.add_scatter(name="Cumulative Revenue", x=df["period"], y=df["cum_revenue"],
                    mode="lines+markers", line=dict(color=REVENUE_COLOR, width=2.5))
    fig.add_scatter(name="Cumulative Expenses", x=df["period"], y=df["cum_expense"],
                    mode="lines+markers", line=dict(color=EXPENSE_COLOR, width=2.5, dash="dash"))
    fig.add_scatter(name="Cumulative Profit", x=df["period"], y=df["cum_profit"],
                    mode="lines+markers", line=dict(color=PROFIT_COLOR, width=2),
                    fill="tozeroy", fillcolor="rgba(59,130,246,0.08)")
    fig.update_layout(
        title=f"Cumulative Financial Performance — {period_label}",
        height=340, margin=dict(t=50, b=40, l=10, r=10),
        yaxis_title="$ Cumulative", xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_dept_financials(data: list[dict]) -> None:
    if not data:
        return
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_bar(name="Revenue",  x=df["department"], y=df["revenue"],  marker_color=REVENUE_COLOR)
    fig.add_bar(name="Expenses", x=df["department"], y=df["expense"],  marker_color=EXPENSE_COLOR)
    fig.add_bar(name="Profit",   x=df["department"], y=df["profit"],   marker_color=PROFIT_COLOR)
    fig.update_layout(
        title="Revenue / Expenses / Profit by Department",
        barmode="group", height=350,
        margin=dict(t=50, b=40, l=10, r=10),
        yaxis_title="$ Amount", xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_roi_by_project(data: list[dict]) -> None:
    if not data:
        return
    df = pd.DataFrame(data).sort_values("roi_pct", ascending=True)
    colors = [PROFIT_COLOR if v >= 0 else EXPENSE_COLOR for v in df["roi_pct"]]
    fig = go.Figure(go.Bar(
        x=df["roi_pct"], y=df["project_name"], orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in df["roi_pct"]], textposition="outside",
        hovertemplate="%{y}: %{x:.1f}% ROI<extra></extra>",
    ))
    fig.update_layout(
        title="Top 5 Projects by ROI",
        height=300, margin=dict(t=50, b=20, l=10, r=80),
        xaxis_title="ROI %", yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#F3F4F6", zeroline=True, zerolinecolor="#9CA3AF"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_profit_margin_pie(data: list[dict]) -> None:
    if not data:
        return
    df = pd.DataFrame(data)
    fig = px.pie(df, names="department", values="profit",
                 title="Profit Distribution by Department",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_traces(textinfo="label+percent", hole=0.4)
    fig.update_layout(height=300, margin=dict(t=50, b=10, l=10, r=10),
                      showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
