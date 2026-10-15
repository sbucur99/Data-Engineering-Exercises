/*

Employee Performance

Your task
Write one SQL query that returns:
1. Each employee's total revenue.
2. Each employee's rank within their department based on total revenue, with the highest revenue ranked first. 
3. The difference between the employee's total revenue and their department's average employee revenue.
4. Return only the #1 and #2 ranked employees from each department. where rank in 
5. If two employees have the same total revenue, they should receive the same rank.
Expected columns:
employee_id
employee_name
department
total_revenue
department_avg
revenue_difference
department_rank

- Do you need to calculate something before you can calculate something else?
- Do you need to preserve individual employees after calculating department-level information?
- Do you need to rank employees within each department?
- What happens if two employees have the same revenue?
Send me your SQL query, even if you aren't sure it's correct. I'll review it line-by-line and tell you exactly what you did right and where you can improve.
*/
USE sales_db;

SELECT * FROM employee_sales;

-- WITH employee_total_salaries AS (SELECT employee_id, employee_name, department, SUM(revenue) as total_revenue
-- FROM employee_sales
-- GROUP BY employee_name),

-- AS ranked_employees (SELECT employee_id, employee_name, department, RANK() OVER(total_revenue) AS emp_rank
-- FROM employee_total_salaries
-- ORDER BY emp_rank
-- LIMIT 2),

-- AS department_revenue (SELECT employee_id, employee_name, department, SUM(revenue) AS total_dept_revenue
-- FROM employee_sales
-- GROUP BY departments
-- ),

-- AS revenue_difference (SELECT employee_id, employee_name, department, e.employee_total_salaries - d.total_dept_revenue 
-- AS revenue_difference
-- FROM employee_total_salaries e, department_revenue d)







-- CREATE DATABASE sales_db;

-- USE sales_db;

-- CREATE TABLE employee_sales (
--     employee_id INT,
--     employee_name VARCHAR(50),
--     department VARCHAR(50),
--     sale_date DATE,
--     revenue DECIMAL(10, 2)
-- );

-- INSERT INTO employee_sales (
--     employee_id,
--     employee_name,
--     department,
--     sale_date,
--     revenue
-- )
-- VALUES
--     (1, 'Alice',   'Engineering', '2026-01-05', 5000),
--     (1, 'Alice',   'Engineering', '2026-01-12', 7000),
--     (1, 'Alice',   'Engineering', '2026-01-20', 6000),
--     (2, 'Bob',     'Engineering', '2026-01-06', 8000),
--     (2, 'Bob',     'Engineering', '2026-01-15', 4000),
--     (2, 'Bob',     'Engineering', '2026-01-25', 9000),
--     (3, 'Charlie', 'Finance',    '2026-01-03', 10000),
--     (3, 'Charlie', 'Finance',    '2026-01-18', 7000),
--     (4, 'David',   'Finance',    '2026-01-08', 6000),
--     (4, 'David',   'Finance',    '2026-01-22', 11000),
--     (5, 'Eva',     'Engineering', '2026-01-04', 9000),
--     (5, 'Eva',     'Engineering', '2026-01-19', 9000),
--     (5, 'Eva',     'Engineering', '2026-01-28', 3000);