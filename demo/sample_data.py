import csv
from pathlib import Path

SAMPLE_PROJECTS = [
    # IT Department
    {"project_name": "Cloud Migration Phase 1",    "department": "IT",         "start_date": "2023-10-01", "planned_cost": 250000, "actual_cost": 310000, "revenue": 420000, "planned_finish_date": "2024-03-31", "actual_finish_date": "2024-05-15", "status": "delayed",   "risk_level": "high",     "issue_description": "Vendor delays and scope creep on infrastructure setup",            "owner": "Sarah Chen"},
    {"project_name": "ERP Upgrade",                "department": "IT",         "start_date": "2023-11-15", "planned_cost": 180000, "actual_cost": 175000, "revenue": 280000, "planned_finish_date": "2024-04-30", "actual_finish_date": "2024-04-28", "status": "completed", "risk_level": "low",      "issue_description": "Minor config issues resolved",                                   "owner": "James Liu"},
    {"project_name": "Security Audit Program",     "department": "IT",         "start_date": "2024-01-15", "planned_cost":  95000, "actual_cost": 104000, "revenue":  75000, "planned_finish_date": "2024-05-31", "actual_finish_date": "2024-06-20", "status": "delayed",   "risk_level": "medium",   "issue_description": "Resource contention with cloud migration team",                  "owner": "Maria Santos"},
    {"project_name": "Data Warehouse Rebuild",     "department": "IT",         "start_date": "2023-12-01", "planned_cost": 320000, "actual_cost": 298000, "revenue": 480000, "planned_finish_date": "2024-06-30", "actual_finish_date": "2024-06-30", "status": "on_track",  "risk_level": "low",      "issue_description": "On schedule and under budget",                                   "owner": "Kevin Park"},
    {"project_name": "Mobile App Launch",          "department": "IT",         "start_date": "2023-11-01", "planned_cost": 140000, "actual_cost": 185000, "revenue": 520000, "planned_finish_date": "2024-04-15", "actual_finish_date": "2024-07-01", "status": "at_risk",   "risk_level": "critical", "issue_description": "Design rework required; original vendor terminated",             "owner": "Lisa Wang"},
    # Finance Department
    {"project_name": "Annual Budget Reconciliation","department": "Finance",   "start_date": "2024-01-01", "planned_cost":  45000, "actual_cost":  44000, "revenue":  35000, "planned_finish_date": "2024-03-31", "actual_finish_date": "2024-03-29", "status": "completed", "risk_level": "low",      "issue_description": "Completed two days early",                                       "owner": "Robert Kim"},
    {"project_name": "Regulatory Compliance Report","department": "Finance",   "start_date": "2024-01-15", "planned_cost":  60000, "actual_cost":  68000, "revenue":  25000, "planned_finish_date": "2024-04-30", "actual_finish_date": "2024-05-10", "status": "delayed",   "risk_level": "medium",   "issue_description": "New regulatory requirements added post-kickoff",                 "owner": "Emma Thompson"},
    {"project_name": "Financial System Integration","department": "Finance",   "start_date": "2023-10-15", "planned_cost": 210000, "actual_cost": 255000, "revenue": 380000, "planned_finish_date": "2024-05-31", "actual_finish_date": "2024-08-15", "status": "at_risk",   "risk_level": "high",     "issue_description": "Integration complexity underestimated; third-party API issues",   "owner": "David Brown"},
    {"project_name": "Cost Reduction Initiative",  "department": "Finance",    "start_date": "2024-01-01", "planned_cost":  30000, "actual_cost":  29000, "revenue": 180000, "planned_finish_date": "2024-04-15", "actual_finish_date": "2024-04-10", "status": "completed", "risk_level": "low",      "issue_description": "Delivered savings ahead of plan",                                "owner": "Anna Lee"},
    {"project_name": "Vendor Contract Renegotiation","department": "Finance",  "start_date": "2024-02-01", "planned_cost":  25000, "actual_cost":  27000, "revenue":  95000, "planned_finish_date": "2024-05-15", "actual_finish_date": "2024-05-20", "status": "on_track",  "risk_level": "low",      "issue_description": "Minor delay due to legal review",                                "owner": "Tom Wilson"},
    # Operations Department
    {"project_name": "Supply Chain Optimization",  "department": "Operations", "start_date": "2023-12-01", "planned_cost": 175000, "actual_cost": 192000, "revenue": 310000, "planned_finish_date": "2024-05-31", "actual_finish_date": "2024-06-30", "status": "delayed",   "risk_level": "high",     "issue_description": "Supplier disruption in Q1; backup vendor onboarding",           "owner": "Rachel Green"},
    {"project_name": "Warehouse Automation",       "department": "Operations", "start_date": "2023-11-01", "planned_cost": 400000, "actual_cost": 390000, "revenue": 650000, "planned_finish_date": "2024-07-31", "actual_finish_date": "2024-07-31", "status": "on_track",  "risk_level": "medium",   "issue_description": "On track; minor equipment delays absorbed",                      "owner": "Michael Scott"},
    {"project_name": "Quality Management System",  "department": "Operations", "start_date": "2024-01-01", "planned_cost":  85000, "actual_cost":  97000, "revenue": 145000, "planned_finish_date": "2024-04-30", "actual_finish_date": "2024-05-25", "status": "delayed",   "risk_level": "medium",   "issue_description": "ISO certification scope more extensive than planned",           "owner": "Jennifer Adams"},
    {"project_name": "Logistics Partner Integration","department": "Operations","start_date": "2024-02-15", "planned_cost": 120000, "actual_cost": 118000, "revenue": 195000, "planned_finish_date": "2024-06-15", "actual_finish_date": "2024-06-15", "status": "on_track",  "risk_level": "low",      "issue_description": "On track and on budget",                                         "owner": "Chris Johnson"},
    {"project_name": "Fleet Management Upgrade",   "department": "Operations", "start_date": "2023-11-15", "planned_cost":  65000, "actual_cost":  82000, "revenue": 120000, "planned_finish_date": "2024-03-31", "actual_finish_date": "2024-05-01", "status": "delayed",   "risk_level": "high",     "issue_description": "Hardware procurement delays; fleet managers unavailable",        "owner": "Patricia Davis"},
]


def write_sample_csv(path: str = "data/input/project_data.csv") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SAMPLE_PROJECTS[0].keys())
        writer.writeheader()
        writer.writerows(SAMPLE_PROJECTS)


if __name__ == "__main__":
    write_sample_csv()
    print("Sample CSV written.")
