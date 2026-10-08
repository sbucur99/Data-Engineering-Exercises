import pandas as pd
from sqlalchemy import create_engine, text
 
# 1. Create your SQLAlchemy engine
engine = create_engine("mysql+pymysql://root:1234@localhost/company_db")
 
# 2. Extract data safely using SQLAlchemy text constructs
df_source = pd.read_sql(text("SELECT * FROM employees"), con=engine)
df_target = pd.read_sql(text("SELECT * FROM employees_target"), con=engine)
 
# 3. Identify completely new records (No changes here, pandas handles this perfectly)
df_new = df_source[~df_source['id'].isin(df_target['id'])]
 
# 4. Identify updated records
df_merge = df_source.merge(df_target, on='id', suffixes=('_src', '_tgt'))
df_update = df_merge[
    (df_merge['salary_src'] != df_merge['salary_tgt']) |
    (df_merge['department_src'] != df_merge['department_tgt'])
]

print(df_new.head(3))


# Can check deletes with another line of code?

# Major throwback for timestamps is DELETES (can't check)
# Timestamp based deletion
# 

"""

last upd
today
yest


src
insert today

In timestamp you will alwasy miss deletes. You can only check for updates and inserts. 
Deletes are not captured in timestamp based incremental loading.


Delta logic compares everything in src with everything in target. It will capture deletes, 
updates and inserts.
This is CDC which is Change Data Capture?

The reverse of insert is delete. 

"""