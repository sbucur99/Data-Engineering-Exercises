# import pandas as pd 
# import mysql.connector 
 
# conn = mysql.connector.connect( 
#     host="localhost", 
#     user="root", 
#     password="1234", 
#     database="company_db" 
# ) 
 
# df = pd.read_sql("SELECT * FROM employees", conn) 
 
# df.to_sql("employees_target", 
#           con="mysql+pymysql://root:password@localhost/company_db", 
#           if_exists='replace', 
#           index=False)



import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="company_db"
)

df = pd.read_sql(
    "SELECT * FROM employees",
    conn
)

df.to_sql(
    "employees_target",
    con="mysql+pymysql://root:1234@localhost/company_db",
    if_exists="replace",
    index=False
)


# import pandas as pd
# from sqlalchemy import create_engine
 
# # 1. Create a reusable SQLAlchemy engine object
# engine = create_engine("mysql+pymysql://root:1234@localhost/company_db")
 
# # 2. Read data using the engine
# df = pd.read_sql("SELECT * FROM employees", con=engine)
 
# # 3. Write data using the same engine
# df.to_sql("employees_target", con=engine, if_exists='replace', index=False)