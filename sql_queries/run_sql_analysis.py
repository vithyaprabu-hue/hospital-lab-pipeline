import os
import sqlite3
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data", "lab_analytics.db"))
SQL_FILE = os.path.join(CURRENT_DIR, "hospital_kpi_analysis.sql")

conn = sqlite3.connect(DB_PATH)

with open(SQL_FILE, "r") as f:
    sql_script = f.read()

# Split statements by semicolon
queries = [q.strip() for q in sql_script.split(";") if q.strip()]

titles = [
    "1. Department-wise TAT & Volume Metrics",
    "2. TAT SLA Breach Analysis (> 180 Mins)",
    "3. Critical Value (Panic Alert) Summary by Test",
    "4. High-Risk Patient Flagging (>=2 Critical Results)"
]

for title, query in zip(titles, queries):
    print("=" * 65)
    print(title)
    print("=" * 65)
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    print("\n")

conn.close()