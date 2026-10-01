import os
import sqlite3
import pandas as pd
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data", "lab_analytics.db"))
OUTPUT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "dashboards"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALERT_EXPORT_CSV = os.path.join(OUTPUT_DIR, "critical_alerts_dispatch.csv")

def run_alert_engine():
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        o.order_id,
        o.patient_id,
        o.age,
        o.gender,
        o.tat_minutes,
        tr.department,
        tr.test_name,
        tr.result_value,
        tr.unit,
        tr.ref_range,
        tr.is_critical
    FROM orders o
    JOIN test_results tr ON o.order_id = tr.order_id
    WHERE tr.is_critical = 1 OR o.tat_minutes > 180
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Alert severity classification
    def assign_alert_level(row):
        if row["is_critical"] == 1 and row["tat_minutes"] > 180:
            return "CRITICAL_SEV_1_BREACH_DELAY"
        elif row["is_critical"] == 1:
            return "CRITICAL_SEV_2_PANIC_VALUE"
        else:
            return "WARNING_SEV_3_TAT_BREACH"

    df["alert_priority"] = df.apply(assign_alert_level, axis=1)
    df["action_required"] = df["alert_priority"].map({
        "CRITICAL_SEV_1_BREACH_DELAY": "Call Duty Doctor Immediately + Escalate Lab Supervisor",
        "CRITICAL_SEV_2_PANIC_VALUE": "Urgent SMS/Call to Ordering Physician",
        "WARNING_SEV_3_TAT_BREACH": "Log Logistics & Analyzer Delay"
    })
    df["flagged_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Export to dashboards directory
    df.to_csv(ALERT_EXPORT_CSV, index=False)

    print("=" * 65)
    print("HOSPITAL LAB REAL-TIME ALERT ENGINE COMPLETED")
    print("=" * 65)
    print(f"Total Flagged Exceptions : {len(df)}")
    print(f"Severity Breakdown:\n{df['alert_priority'].value_counts().to_string()}")
    print("-" * 65)
    print(f"Alert Feed Exported To   : {ALERT_EXPORT_CSV}")
    print("=" * 65)

if __name__ == "__main__":
    run_alert_engine()