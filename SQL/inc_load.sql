-- CREATE DATABASE company_db; 
USE company_db; 
 
-- CREATE TABLE employees ( 
--     id INT PRIMARY KEY, 
--     name VARCHAR(50), 
--     department VARCHAR(50), 
--     salary INT, 
--     last_updated TIMESTAMP 
-- ); 
 
-- INSERT INTO employees VALUES 
-- (1,'Alice','HR',5000,NOW()), 
-- (2,'Bob','IT',7000,NOW()), 
-- (3,'Charlie','Finance',6000,NOW()); 
 
-- CREATE TABLE employees_target LIKE employees; 

-- 

SELECT * 
FROM employees 
-- WHERE name = 'Alice'
-- -------------------
-- WHERE last_updated > ( 
--     SELECT MAX(last_updated) FROM employees_target 
-- );

-- UPDATE employees  
-- SET salary = 8000, last_updated = NOW()  
-- WHERE id = 2;

-- INSERT INTO employees VALUES 
-- (4,'David','IT',6500,NOW());

-- You want to upsert
-- When you do comparisons between tables like if they exist that is DELTA (logic)