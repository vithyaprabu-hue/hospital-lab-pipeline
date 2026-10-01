import os
import random
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

random.seed(42)

# Directory setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "lab_analytics.db")
ORDERS_CSV = os.path.join(CURRENT_DIR, "lab_orders.csv")
RESULTS_CSV = os.path.join(CURRENT_DIR, "lab_results.csv")

# Test configurations: (Department, Normal Min, Normal Max, Panic Low, Panic High, Unit)
TEST_CONFIG = {
    "FBS": ("Biochemistry", 70.0, 99.0, 50.0, 350.0, "mg/dL"),
    "PPBS": ("Biochemistry", 90.0, 140.0, 50.0, 400.0, "mg/dL"),
    "Lipid_Cholesterol": ("Biochemistry", 120.0, 200.0, None, 300.0, "mg/dL"),
    "Serum_Creatinine": ("Biochemistry", 0.7, 1.3, None, 4.0, "mg/dL"),
    "Serum_Potassium": ("Critical Care", 3.5, 5.0, 2.8, 6.0, "mmol/L"),
    "TSH": ("Immunoassay", 0.4, 4.5, 0.01, 20.0, "uIU/mL"),
    "CBC_Hemoglobin": ("Hematology", 12.0, 16.0, 6.0, 20.0, "g/dL"),
    "CBC_Platelets": ("Hematology", 150.0, 450.0, 20.0, 1000.0, "x10^3/uL"),
    "Urine_Routine_PusCells": ("Pathology", 0.0, 5.0, None, 30.0, "cells/HPF"),
}

# 1. Generate Orders Data
orders = []
results = []
start_date = datetime(2026, 8, 1, 7, 0, 0)

for order_idx in range(1, 1001):
    order_id = f"ORD{order_idx:05d}"
    patient_id = f"PT{random.randint(1001, 1400):04d}"
    age = random.randint(18, 80)
    gender = random.choice(["Male", "Female"])

    collected_time = start_date + timedelta(
        days=random.randint(0, 55),
        hours=random.randint(0, 12),
        minutes=random.randint(0, 59),
    )

    # Turnaround time simulation (Transit + Analysis)
    transit_mins = random.randint(15, 60)
    received_time = collected_time + timedelta(minutes=transit_mins)

    # Some orders take longer to simulate TAT SLA breach (> 180 mins)
    analysis_mins = random.choices(
        [random.randint(45, 120), random.randint(185, 300)], weights=[0.85, 0.15]
    )[0]
    authorized_time = received_time + timedelta(minutes=analysis_mins)

    tat_minutes = int(
        (authorized_time - collected_time).total_seconds() / 60
    )

    orders.append(
        {
            "order_id": order_id,
            "patient_id": patient_id,
            "age": age,
            "gender": gender,
            "collected_time": collected_time.strftime("%Y-%m-%d %H:%M:%S"),
            "received_time": received_time.strftime("%Y-%m-%d %H:%M:%S"),
            "authorized_time": authorized_time.strftime("%Y-%m-%d %H:%M:%S"),
            "tat_minutes": tat_minutes,
        }
    )

    # 2. Assign 1 to 3 random tests per order
    assigned_tests = random.sample(
        list(TEST_CONFIG.keys()), k=random.randint(1, 3)
    )

    for test in assigned_tests:
        dept, norm_min, norm_max, panic_low, panic_high, unit = TEST_CONFIG[
            test
        ]

        # 85% normal or slightly abnormal, 15% critical alert values
        is_critical_draw = random.random() < 0.10

        if is_critical_draw:
            if panic_low and random.random() < 0.5:
                val = round(random.uniform(panic_low * 0.5, panic_low * 0.95), 2)
            elif panic_high:
                val = round(
                    random.uniform(panic_high * 1.05, panic_high * 1.5), 2
                )
            else:
                val = round(random.uniform(norm_max * 1.1, norm_max * 1.5), 2)
            is_critical = 1
        else:
            val = round(random.uniform(norm_min * 0.95, norm_max * 1.05), 2)
            is_critical = 0

        results.append(
            {
                "result_id": f"RES{len(results) + 1:06d}",
                "order_id": order_id,
                "department": dept,
                "test_name": test,
                "result_value": val,
                "unit": unit,
                "ref_range": f"{norm_min}-{norm_max}",
                "is_critical": is_critical,
            }
        )

# Convert to DataFrame
df_orders = pd.DataFrame(orders)
df_results = pd.DataFrame(results)

# Export to CSV
df_orders.to_csv(ORDERS_CSV, index=False)
df_results.to_csv(RESULTS_CSV, index=False)

# Export to SQLite DB
conn = sqlite3.connect(DB_PATH)
df_orders.to_sql("orders", conn, if_exists="replace", index=False)
df_results.to_sql("test_results", conn, if_exists="replace", index=False)
conn.close()

print(f"Data Generation Success!")
print(f"Total Orders: {len(df_orders)}")
print(f"Total Test Results: {len(df_results)}")
print(f"Database created at: {DB_PATH}")