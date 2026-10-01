\# Hospital Diagnostic Lab Turnaround Time (TAT) \& Critical Alert Pipeline



An end-to-end healthcare data engineering and analytics pipeline simulating operational workflows across clinical departments (Biochemistry, Hematology, Immunoassay, Clinical Pathology, and Critical Care). 



The system audits Turnaround Time (TAT) Service Level Agreements (SLAs), identifies operational bottlenecks, and automates real-time panic/critical value alert dispatches for high-risk patients.



\---



\## Architecture \& Project Structure



```text

hospital-lab-pipeline/

├── data/

│   ├── generate\_lab\_data.py          # Synthetic clinical dataset generator (1000 orders, 2000+ tests)

│   ├── lab\_analytics.db              # SQLite Relational Database

│   ├── lab\_orders.csv                # Ingestion feed: order metadata \& timestamps

│   └── lab\_results.csv               # Ingestion feed: clinical values \& panic flags

├── sql\_queries/

│   ├── hospital\_kpi\_analysis.sql     # Complex analytical queries (TAT aggregations, SLA breach rates)

│   └── run\_sql\_analysis.py           # Automated SQL execution runner

├── engine/

│   └── alert\_engine.py               # Severity triaging (SEV-1, SEV-2, SEV-3) \& doctor escalation feed

├── dashboards/

│   ├── critical\_alerts\_dispatch.csv  # Real-time incident dispatch logs

│   ├── generate\_visuals.py           # Matplotlib KPI visualization generator

│   └── lab\_kpi\_report.png            # Visual operations summary chart

└── README.md

