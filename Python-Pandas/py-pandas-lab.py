# rows = ["John,25,5000", "Alice,30,7000"]
# rows.insert(0, "Header")
# rows.remove("John,25,5000")
# rows.pop(0)
# print(rows)

# data = ["100", "200", "abc", "300", ""]

# lis = []
# for i in data:
#     num = i
#     if (len(num) == 0):
#         continue
#     try:                    #could use i.isnumeric()
#         num = int(num)
       
#         lis.append(num)
#     except:
#         Exception
# print(lis)


# tup = (1,2,[1,2])

# tup[2].append(3)
# print(tup)


# record = (1,2,3)
# name, age = record
# print(name)



# ids = {105, 103,101, 102,  101}
# print(ids)

# ls = [100, 200, 400, 400, 100]
# s = set(ls)

# if (500 not in s):
#     s.add(500)

# print(s)
# print(s)
# print(s)



# row = {
#  "name": "John",
#  "age": "25",
#  "salary": "5000"
# }

# # print(row["name"])

# print(row.get("age"))
# [] raises KeyError
# • .get() returns None if missing

# response = {
#     "user": {
#         "profile": {
#         "name": "Alice"
#         }
#     }
# }
# print(response["user"]["profile"]["name"])
# response.get("user", {}).get("profile", {}).get("name")


# with open("data.csv", "r") as file:
#     for line in file:
#         print(line.strip())

# with open("output.csv", "w+") as file:
#     file.write("John,25,5000\n")
#     for line in file:
#         print(line.strip())

import pandas as pd

# s = pd.Series([100, 200, 300])

# s = pd.Series([10,20,30], index=["a","b","c"])

# print(s["a"])

# data = {
#  "name": ["Alice", "Bob"],
#  "age": [25, 30]
# }
# df = pd.DataFrame(data)
# print(df)


# df = pd.read_csv("data.csv")
# df = pd.read_csv(
#     "data.csv",
#     sep=",",
#     header=0,
#     dtype={"age": "int32"},
#     # parse_dates=["created_at"],
#     na_values=["NA", ""]
#     )
# print(df)

df = pd.read_csv("data.csv",na_values=["NA","NaN"])

# print(df)
# print(df.shape)
# print(df.columns)
# print(df.dtypes) #What is dtype: Object???????????????????????
# df.info()
# print(df.describe())
# df["salary"] = pd.to_numeric(df['salary'], errors='coerce')
# df = df.dropna()
# print(df)

# print(df[(df["age"] > 25) & (df["salary"] > 5000)])

# print(df[(df["region"] == "North") & ((df["salary"] >= 5000) & (df["salary"] <= 8000)) & \
#  (df['name'].str.startswith('A'))])

# Filter rows where region is North.
# • Filter rows where salary between 5000 and 8000.
# • Filter rows where name starts with "A".

# print(df.agg({
#  "salary": ["sum","mean"],
#  "age": ["min","max"]
# }))

# print(df.columns)
# print(df.groupby("department")["salary"].sum().reset_index())


# print(df.dtype)


# def validate_row(row):
#     b = False
#     # name = row["name"].strip()
#     if ((int(row["age"]) >= 0) & (float(row["salary"]) >= 0)):
#         b = True
#     else:
#         b = False
#     return b
 
# validate_row()


import logging
logging.basicConfig(
 filename="pipeline.log",
 level=logging.INFO,
 format="%(asctime)s - %(levelname)s - %(message)s"
)

# # logging.info("Pipeline started")
# # logging.error("Invalid row encountered")

# salary = -11
# try:
#     salary = float(salary)

#     if salary < 0:
#         raise ValueError("Salary cannot be negative")

# except ValueError as e:
#     logging.error("Invalid salary: %s", e)

#     with open("logging.log", "w") as file:
#         file.write(str(e))



# total_rows
# valid_rows
# invalid_rows

#    row_count = sum(1 for row in reader) 
# row_count = len(df) # for pandasd




import csv

# # WRITE INITAL CSV
# with open("data.csv", "w", newline="") as file:
#     writer = csv.writer(file)

#     writer.writerow(["name", "age", "salary"])
#     writer.writerow(["John", 25, 5000])
#     writer.writerow(["Alice", "", 7000])
#     writer.writerow(["Bob", "abc", 4000])
#     writer.writerow(["Tom", 30, ""])
 
# READ AND CLEAN THE CSV THEN WRITE TO NEW CSV
# Maintain metrics (counters for cleaned rows and error rows)
total_rows = 0
cleaned_rows = 0
invalid_rows = 0

with open("data.csv") as file:
    reader = csv.DictReader(file)

    with open("data2.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "age", "salary"]
        )

        writer.writeheader()
        for row in reader:
            total_rows += 1

            try:
                # Keep name as string
                name = row["name"]

                # Convert age to int
                age = int(row["age"])

                # Skip invalid age
                if age < 0:
                    raise ValueError("Age cannot be negative")

                # Replace missing salary with 0
                if row["salary"] == "":
                    salary = 0
                else:
                    salary = float(row["salary"])

            except ValueError as e:
                invalid_rows += 1
                logging.error("Invalid row: %s | Error: %s", row, e)
                continue

            cleaned_rows += 1

            # Write cleaned output
            writer.writerow({
                "name": name,
                "age": age,
                "salary": salary
            })

#     # Full implementation provided earlier.

# with open("data2.csv") as file:
#     reader = csv.DictReader(file)
#     for row in reader:
#         print(row)

# print("Total rows:", total_rows)
# print("Cleaned rows:", cleaned_rows)
# print("Invalid rows:", invalid_rows)

    # ADVANCED CHALLENGE
    #   Enhance pipeline to:
    # • Stop job if invalid rows > 30%
    # • Accept input filename as argument
    # • Add execution time measurement
    # • Add DEBUG mode switch


df[df['Role'] == 'Developer']


# Small ETL proj