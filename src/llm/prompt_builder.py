def build_prompt(kpi_summary: dict) -> str:
    s = kpi_summary

    risk_lines = "\n".join(
        f"- {r['project_name']} | Risk: {r['risk_level'].upper()} | "
        f"Budget: {r['budget_variance_pct']:+.1f}%"
        for r in s["top_3_risks"]
    ) or "None identified"

    over_budget_lines = "\n".join(
        f"- {r['project_name']} ({r['department']}): "
        f"planned ${r['planned_cost']:,.0f} → actual ${r['actual_cost']:,.0f} "
        f"({r['budget_variance_pct']:+.1f}%)"
        for r in s["over_budget_projects"]
    ) or "None"

    late_lines = "\n".join(
        f"- {r['project_name']}: {r['schedule_delay_days']} days late | Owner: {r['owner']}"
        for r in s["late_projects"]
    ) or "None"

    dept_lines = "\n".join(
        f"- {r['department']}: {r['issue_count']} active issues — \"{r['sample_issue']}\""
        for r in s["issues_by_dept"]
    ) or "No issues logged"

    prompt = f"""You are a senior management consultant writing an executive briefing.
You MUST only reference the data provided below. Do not invent project names, costs, or dates not present in the data. Be direct, professional, and concise.

Generate an executive portfolio report based on the following KPI data.

=== PORTFOLIO SUMMARY ===
Total Projects: {s['total_projects']}
On Track: {s['pct_on_track']:.1f}%  |  At Risk: {s['pct_at_risk']:.1f}%  |  Delayed: {s['pct_delayed']:.1f}%  |  Completed: {s['pct_completed']:.1f}%
Total Budget Variance: ${s['total_budget_variance']:,.0f} ({s['total_budget_variance_pct']:+.1f}%)
Average Schedule Delay (late projects): {s['avg_schedule_delay_days']:.1f} days

=== TOP 3 HIGH-RISK PROJECTS ===
{risk_lines}

=== OVER-BUDGET PROJECTS (>10%) ===
{over_budget_lines}

=== LATE PROJECTS ===
{late_lines}

=== ISSUES BY DEPARTMENT ===
{dept_lines}

---
Write the following sections using these EXACT headers (markdown ## format):

## Executive Summary
(3-5 sentences covering overall portfolio health, key numbers, and urgency level)

## Key Risks
(Top 3 risks with specific project names and data from the list above)

## Budget Concerns
(List all over-budget projects with dollar amounts — reference only the projects listed above)

## Schedule Delays
(List all late projects with delay duration — reference only the projects listed above)

## Recommended Actions
(3-5 concrete bullet points tied to the specific issues identified above)"""

    return prompt
