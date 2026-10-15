
USE sales_db;

-- SELECT * FROM employee_sales;

WITH employee_total_salaries AS (
    SELECT employee_id, employee_name, department, SUM(revenue) as total_revenue
    FROM employee_sales
    GROUP BY employee_id, employee_name, department
)
SELECT *
FROM employee_total_salaries;