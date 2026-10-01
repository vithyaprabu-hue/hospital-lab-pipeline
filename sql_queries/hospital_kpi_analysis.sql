-- 1. Department-wise TAT & Volume Metrics
SELECT 
    tr.department,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(tr.result_id) AS total_tests_processed,
    ROUND(AVG(o.tat_minutes), 1) AS avg_turnaround_time_mins,
    MIN(o.tat_minutes) AS min_tat_mins,
    MAX(o.tat_minutes) AS max_tat_mins
FROM orders o
JOIN test_results tr ON o.order_id = tr.order_id
GROUP BY tr.department
ORDER BY avg_turnaround_time_mins DESC;

-- 2. Turnaround Time SLA Breach Analysis (> 180 Mins)
SELECT 
    CASE 
        WHEN tat_minutes <= 120 THEN '0-2 Hours (Fast Track)'
        WHEN tat_minutes <= 180 THEN '2-3 Hours (Within SLA)'
        ELSE '3+ Hours (SLA Breached)'
    END AS sla_category,
    COUNT(*) AS total_orders,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 2) AS percentage_of_total
FROM orders
GROUP BY sla_category
ORDER BY total_orders DESC;

-- 3. Critical Value (Panic Alert) Summary by Test
SELECT 
    test_name,
    department,
    COUNT(*) AS total_tests,
    SUM(is_critical) AS total_critical_alerts,
    ROUND(100.0 * SUM(is_critical) / COUNT(*), 2) AS critical_rate_pct
FROM test_results
GROUP BY test_name, department
ORDER BY total_critical_alerts DESC;

-- 4. High-Risk Patient Flagging (Patients with multiple critical results)
SELECT 
    o.patient_id,
    o.age,
    o.gender,
    COUNT(tr.result_id) AS critical_tests_count,
    GROUP_CONCAT(tr.test_name, ', ') AS critical_test_list
FROM orders o
JOIN test_results tr ON o.order_id = tr.order_id
WHERE tr.is_critical = 1
GROUP BY o.patient_id, o.age, o.gender
HAVING COUNT(tr.result_id) >= 2
ORDER BY critical_tests_count DESC
LIMIT 10;