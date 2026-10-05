import pandas as pd

# 1. Load data
employees = pd.read_csv("employee_data.csv")

employees.info()

# 2. Validate schema
required_columns = {
    "employee_id",
    "name",
    "age",
    "department",
    "region",
    "salary",
    "joining_date"
}


missing_columns = required_columns - set(employees.columns)

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# 3. Clean salary
employees["salary"] = pd.to_numeric(
    employees["salary"],
    errors="coerce"
)

# Replace missing salary with 0
employees["salary"] = employees["salary"].fillna(0)

# 4. Remove invalid records
employees = employees[employees["salary"] >= 0]

# 5. Parse joining date
employees["joining_date"] = pd.to_datetime(
    employees["joining_date"],
    errors="coerce"
)

# Remove rows with invalid dates
employees = employees.dropna(subset=["joining_date"])

# 6. Add computed columns
employees["tax"] = employees["salary"] * 0.15

employees["net_salary"] = (
    employees["salary"] - employees["tax"]
)

employees["high_earner"] = employees["salary"] > 6000

# 7. Filter salary > 6000
high_salary = employees[
    employees["salary"] > 6000
]

# 8. Group by department
department_payroll = (
    employees
    .groupby("department")["salary"]
    .sum()
    .reset_index(name="total_payroll")
)

# 9. Export clean employee data
employees.to_csv(
    "clean_employee_data.csv",
    index=False
)

# 10. Export department summary
department_payroll.to_csv(
    "employee_summary.csv",
    index=False
)


sales = pd.read_csv("sales_data.csv")

# sales.info()

# Validate schema
required_columns = {
    "order_id",
    "customer",
    "region",
    "product",
    "category",
    "sales_amount",
    "order_date"
}

missing_columns = required_columns - set(sales.columns)

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Convert sales_amount to numeric
sales["sales_amount"] = pd.to_numeric(
    sales["sales_amount"],
    errors="coerce"
)

# Remove invalid sales amounts
sales = sales[
    sales["sales_amount"].notna()
]

# Remove negative sales
sales = sales[
    sales["sales_amount"] >= 0
]

# Fill missing categorical values
sales["region"] = sales["region"].fillna("Unknown")
sales["product"] = sales["product"].fillna("Unknown")
sales["category"] = sales["category"].fillna("Unknown")

# Revenue per region
revenue_by_region = (
    sales
    .groupby("region")["sales_amount"]
    .sum()
    .reset_index(name="revenue")
)

# Revenue by product
revenue_by_product = (
    sales
    .groupby("product")["sales_amount"]
    .sum()
    .reset_index(name="revenue")
)

# Revenue by category
revenue_by_category = (
    sales
    .groupby("category")["sales_amount"]
    .sum()
    .reset_index(name="revenue")
)

# Multi-level groupby
region_category = (
    sales
    .groupby(["region", "category"])["sales_amount"]
    .sum()
    .reset_index(name="revenue")
)

# Sort highest revenue first
revenue_by_region = revenue_by_region.sort_values(
    "revenue",
    ascending=False
)

# Export
sales.to_csv(
    "clean_sales_data.csv",
    index=False
)

revenue_by_region.to_csv(
    "sales_by_region.csv",
    index=False
)

region_category.to_csv(
    "sales_by_region_category.csv",
    index=False
)


transactions = pd.read_csv("transactions_data.csv")

transactions.info()

# Validate schema
required_columns = {
    "transaction_id",
    "customer_id",
    "region",
    "amount",
    "status"
}

missing_columns = required_columns - set(transactions.columns)

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Remove duplicate transactions
transactions = transactions.drop_duplicates(
    subset="transaction_id"
)

# Convert amount to numeric
transactions["amount"] = pd.to_numeric(
    transactions["amount"],
    errors="coerce"
)

# Remove invalid amounts
transactions = transactions[
    transactions["amount"].notna()
]

# Remove negative amounts
transactions = transactions[
    transactions["amount"] >= 0
]

# Keep only completed transactions
completed = transactions[
    transactions["status"] == "Completed"
]

# Total revenue by region
revenue_by_region = (
    completed
    .groupby("region")["amount"]
    .sum()
    .reset_index(name="revenue")
)

# Top customer
customer_revenue = (
    completed
    .groupby("customer_id")["amount"]
    .sum()
    .sort_values(ascending=False)
)

top_customer = customer_revenue.idxmax()
top_customer_revenue = customer_revenue.max()

# Count failed transactions
failed_count = (
    transactions["status"] == "Failed"
).sum()

# Export clean transactions
transactions.to_csv(
    "clean_transactions.csv",
    index=False
)

# Export regional summary
revenue_by_region.to_csv(
    "transaction_revenue_by_region.csv",
    index=False
)

print("Top customer:", top_customer)
print("Top customer revenue:", top_customer_revenue)
print("Failed transactions:", failed_count)
