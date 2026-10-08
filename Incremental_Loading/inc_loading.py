import pandas as pd
from sqlalchemy import create_engine, text
 
# 1. Create your SQLAlchemy engine
# Ensure the database name matches your target configuration
engine = create_engine("mysql+pymysql://root:1234@localhost/company_db")
 
# 2. Wrap your query strings in text() for SQLAlchemy safety
last_run_query = text("SELECT MAX(last_updated) FROM employees_target")
 
# 3. Read the max timestamp using the engine
last_run = pd.read_sql(last_run_query, con=engine).iloc[0, 0]
 
# 4. Construct and wrap your incremental source query
source_query = text(f"""
    SELECT * FROM employees 
    WHERE last_updated > '{last_run}'
""")
 
# 5. Extract the incremental rows
df_inc = pd.read_sql(source_query, con=engine)
 
# 6. Append the new data to your target table
df_inc.to_sql("employees_target", con=engine, if_exists='append', index=False)




# df_delete = df_target[~df_target['id'].isin(df_source['id'])]
# ids = df_delete['id'].tolist()
 
# # 3. Execute the deletion inside a transaction block
# if ids:
#     with engine.begin() as connection:
#         # If there's only 1 ID, SQL IN syntax fails with a trailing comma (e.g. IN (5,)), 
#         # so we split the syntax for safety.
#         if len(ids) == 1:
#             query = text("DELETE FROM employees_target WHERE id = :id_val")
#             connection.execute(query, {"id_val": ids[0]})
#         else:
#             query = text("DELETE FROM employees_target WHERE id IN :id_list")
#             connection.execute(query, {"id_list": tuple(ids)})



import pandas as pd
from sqlalchemy import create_engine, text
 
# 1. Create your SQLAlchemy engine
engine = create_engine("mysql+pymysql://root:password@localhost/company_db")
# 2. Extract data safely using SQLAlchemy text constructs
df_source = pd.read_sql(text("SELECT * FROM employees"), con=engine)
df_target = pd.read_sql(text("SELECT * FROM employees_target"), con=engine)
# =========================================================================
# STEP 1: HANDLE DELETIONS
# =========================================================================
df_delete = df_target[~df_target['id'].isin(df_source['id'])]
ids_to_delete = df_delete['id'].tolist()
if ids_to_delete:
    print(f"🗑️ Deleting {len(ids_to_delete)} rows from employees_target...")
    with engine.begin() as connection:
        if len(ids_to_delete) == 1:
            query = text("DELETE FROM employees_target WHERE id = :id_val")
            connection.execute(query, {"id_val": ids_to_delete[0]})
        else:
            query = text("DELETE FROM employees_target WHERE id IN :id_list")
            connection.execute(query, {"id_list": tuple(ids_to_delete)})
 
# =========================================================================
# STEP 2: HANDLE UPDATES (SCD Type 1)
# =========================================================================
df_merge = df_source.merge(df_target, on='id', suffixes=('_src', '_tgt'))
df_update = df_merge[
    (df_merge['salary_src'] != df_merge['salary_tgt']) |
    (df_merge['department_src'] != df_merge['department_tgt'])
]
 
if not df_update.empty:
    print(f"🔄 Updating {len(df_update)} rows in employees_target...")
    # Map the columns back to the target schema format
    # Make sure to include ALL columns required by your target table here
    df_update_final = pd.DataFrame({
        'id': df_update['id'],
        'name': df_update['name_src'],            # Included assuming name exists
        'salary': df_update['salary_src'],
        'department': df_update['department_src'],
        'last_updated': df_update['last_updated_src'] # Match target column names
    })
    ids_to_update = df_update_final['id'].tolist()
    # Safely delete the old version of these records inside a transaction block
    with engine.begin() as connection:
        if len(ids_to_update) == 1:
            query = text("DELETE FROM employees_target WHERE id = :id_val")
            connection.execute(query, {"id_val": ids_to_update[0]})
        else:
            query = text("DELETE FROM employees_target WHERE id IN :id_list")
            connection.execute(query, {"id_list": tuple(ids_to_update)})
    # Append the freshly updated records back into the table
    df_update_final.to_sql("employees_target", con=engine, if_exists='append', index=False)
 
# =========================================================================
# STEP 3: HANDLE INSERTS (New Records)
# =========================================================================
df_new = df_source[~df_source['id'].isin(df_target['id'])]
 
if not df_new.empty:
    print(f"✨ Inserting {len(df_new)} new rows into employees_target...")
    df_new.to_sql("employees_target", con=engine, if_exists='append', index=False)
 
print("✅ Synchronization completed successfully!")