import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data", "lab_analytics.db"))
OUTPUT_IMAGE = os.path.join(CURRENT_DIR, "lab_kpi_report.png")

conn = sqlite3.connect(DB_PATH)

# Query 1: Dept-wise avg TAT
df_dept = pd.read_sql_query("""
    SELECT tr.department, ROUND(AVG(o.tat_minutes), 1) as avg_tat, COUNT(tr.result_id) as test_count
    FROM orders o
    JOIN test_results tr ON o.order_id = tr.order_id
    GROUP BY tr.department
    ORDER BY avg_tat DESC;
""", conn)

# Query 2: SLA categories
df_sla = pd.read_sql_query("""
    SELECT 
        CASE 
            WHEN tat_minutes <= 120 THEN 'Fast Track (<=2h)'
            WHEN tat_minutes <= 180 THEN 'Normal (2-3h)'
            ELSE 'SLA Breached (>3h)'
        END AS sla_cat,
        COUNT(*) as count
    FROM orders
    GROUP BY sla_cat;
""", conn)

# Query 3: Critical values by Dept
df_crit = pd.read_sql_query("""
    SELECT department, SUM(is_critical) as critical_count
    FROM test_results
    GROUP BY department
    HAVING critical_count > 0
    ORDER BY critical_count DESC;
""", conn)

conn.close()

# Plotting
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Hospital Diagnostic Lab Operations & SLA Dashboard", fontsize=16, fontweight='bold')

# Chart 1: Dept Avg TAT
axes[0].bar(df_dept["department"], df_dept["avg_tat"], color="#2b5c8f")
axes[0].axhline(180, color="red", linestyle="--", label="180 Min SLA Target")
axes[0].set_title("Average Turnaround Time (TAT) by Department")
axes[0].set_ylabel("Average Minutes")
axes[0].set_xticklabels(df_dept["department"], rotation=20)
axes[0].legend()

# Chart 2: SLA Breaches
axes[1].bar(df_sla["sla_cat"], df_sla["count"], color=["#2e7d32", "#f9a825", "#c62828"])
axes[1].set_title("Turnaround Time SLA Adherence")
axes[1].set_ylabel("Order Count")
axes[1].set_xticklabels(df_sla["sla_cat"], rotation=15)

# Chart 3: Critical Panic Flags
axes[2].pie(df_crit["critical_count"], labels=df_crit["department"], autopct="%1.1f%%", startangle=140, colors=["#d32f2f", "#1976d2", "#388e3c", "#fbc02d", "#7b1fa2"])
axes[2].set_title("Critical Panic Alerts by Department")

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE, dpi=300)
print(f"Visual dashboard generated successfully at: {OUTPUT_IMAGE}")