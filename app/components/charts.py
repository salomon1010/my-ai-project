import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

STATUS_COLORS = {
    "on_track":  "#10B981",
    "completed": "#3B82F6",
    "at_risk":   "#F59E0B",
    "delayed":   "#EF4444",
}
RISK_COLORS = {
    "low":      "#10B981",
    "medium":   "#F59E0B",
    "high":     "#F97316",
    "critical": "#EF4444",
}


def render_status_donut(projects: list[dict]) -> None:
    df = pd.DataFrame(projects)
    counts = df["status"].value_counts().reset_index()
    counts.columns = ["status", "count"]
    colors = [STATUS_COLORS.get(s, "#6B7280") for s in counts["status"]]
    fig = go.Figure(go.Pie(
        labels=counts["status"],
        values=counts["count"],
        hole=0.55,
        marker_colors=colors,
        textinfo="label+percent",
        hovertemplate="%{label}: %{value} projects<extra></extra>",
    ))
    fig.update_layout(
        title="Project Status", height=300, margin=dict(t=40, b=10, l=10, r=10),
        showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_risk_bar(projects: list[dict]) -> None:
    df = pd.DataFrame(projects)
    order = ["critical", "high", "medium", "low"]
    counts = df["risk_level"].value_counts().reindex(order, fill_value=0).reset_index()
    counts.columns = ["risk_level", "count"]
    colors = [RISK_COLORS.get(r, "#6B7280") for r in counts["risk_level"]]
    fig = go.Figure(go.Bar(
        x=counts["risk_level"],
        y=counts["count"],
        marker_color=colors,
        text=counts["count"],
        textposition="outside",
        hovertemplate="%{x}: %{y} projects<extra></extra>",
    ))
    fig.update_layout(
        title="Risk Distribution", height=300, margin=dict(t=40, b=10, l=10, r=10),
        yaxis_title="Projects", xaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_dept_issues(issues_by_dept: list[dict]) -> None:
    if not issues_by_dept:
        st.info("No department issues logged.")
        return
    df = pd.DataFrame(issues_by_dept)
    fig = go.Figure(go.Bar(
        x=df["issue_count"],
        y=df["department"],
        orientation="h",
        marker_color="#6366F1",
        text=df["issue_count"],
        textposition="outside",
        hovertemplate="%{y}: %{x} issues<extra></extra>",
    ))
    fig.update_layout(
        title="Issues by Department", height=300, margin=dict(t=40, b=10, l=10, r=10),
        xaxis_title="Issue Count", yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_budget_variance_chart(projects: list[dict]) -> None:
    df = pd.DataFrame(projects)
    df = df.sort_values("budget_variance_pct", ascending=True)
    colors = ["#EF4444" if v > 0 else "#10B981" for v in df["budget_variance_pct"]]
    fig = go.Figure(go.Bar(
        x=df["budget_variance_pct"],
        y=df["project_name"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in df["budget_variance_pct"]],
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title="Budget Variance by Project (% over/under plan)",
        height=420, margin=dict(t=40, b=10, l=10, r=80),
        xaxis_title="Variance %", yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#F3F4F6", zeroline=True, zerolinecolor="#9CA3AF"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_schedule_delay_chart(projects: list[dict]) -> None:
    df = pd.DataFrame(projects)
    late = df[df["schedule_delay_days"] > 0].sort_values("schedule_delay_days", ascending=False)
    if late.empty:
        st.success("No projects are currently delayed.")
        return
    severity = ["#EF4444" if d > 30 else "#F59E0B" if d > 10 else "#FCD34D"
                for d in late["schedule_delay_days"]]
    fig = go.Figure(go.Bar(
        x=late["project_name"],
        y=late["schedule_delay_days"],
        marker_color=severity,
        text=late["schedule_delay_days"],
        textposition="outside",
        hovertemplate="%{x}: %{y} days delayed<extra></extra>",
    ))
    fig.update_layout(
        title="Schedule Delays (days behind plan)",
        height=350, margin=dict(t=40, b=80, l=10, r=10),
        yaxis_title="Days Delayed", xaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
        xaxis=dict(tickangle=-30),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_dept_performance(projects: list[dict]) -> None:
    df = pd.DataFrame(projects)
    dept = df.groupby("department").agg(
        projects=("project_name", "count"),
        avg_variance=("budget_variance_pct", "mean"),
        avg_delay=("schedule_delay_days", "mean"),
    ).reset_index()
    fig = px.scatter(
        dept, x="avg_variance", y="avg_delay",
        size="projects", color="department", text="department",
        labels={"avg_variance": "Avg Budget Variance %", "avg_delay": "Avg Delay (days)"},
        title="Department Performance: Budget vs Schedule",
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        height=380, margin=dict(t=50, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(zeroline=True, zerolinecolor="#9CA3AF", showgrid=True, gridcolor="#F3F4F6"),
        yaxis=dict(zeroline=True, zerolinecolor="#9CA3AF", showgrid=True, gridcolor="#F3F4F6"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
