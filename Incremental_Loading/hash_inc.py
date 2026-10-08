import pandas as pd
import hashlib
from sqlalchemy import create_engine, text
# pip install hashlib ########################################
 
# 1. Create your SQLAlchemy engine
engine = create_engine("mysql+pymysql://root:1234@localhost/company_db")
# 2. Extract data safely 
df_source = pd.read_sql(text("SELECT * FROM employees"), con=engine)
df_target = pd.read_sql(text("SELECT * FROM employees_target"), con=engine)
 
# =========================================================================
# STEP 1: APPLY MD5 HASHING FOR CHANGE DETECTION
# =========================================================================
def gen_hash(row):
    # Concatenating tracking values together to create a single string fingerprint

    # THINGS that MIGHT CHANGE IN FUTURE: only pick them up for the HASH...........

    # String comparison takes longer than Hash comparision. Integer takes longer than Hash comparision.
    # but faster than String comparison
    #    
    # Does hash use vectorization? No, it uses apply which is row-wise. It is not vectorized.
    # For hash update is it a tree structure? No, it is a linear structure. It is not a tree structure.
    #  
    track_string = str(row['name']) + str(row['salary']) + str(row['department'])
    return hashlib.md5(track_string.encode()).hexdigest()
 
# Apply the hash to both source and target dataframes
df_source['hash'] = df_source.apply(gen_hash, axis=1) # apply iterates over rows axis=1 means row-wise
df_target['hash'] = df_target.apply(gen_hash, axis=1)
# makes New column called hash in both source and target dataframes

# iter
# <- apply
# vectorized
 
# =========================================================================
# STEP 2: HANDLE DELETIONS
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


# ==========================================================
# STEP 3: HANDLE UPDATES (Using Hash Comparison)
# =========================================================================
# Merge on id to align matching records
df_merge = df_source.merge(df_target, on='id', suffixes=('_src', '_tgt'))
 
# If hashes don't match, something in name, salary, or department changed
df_update = df_merge[df_merge['hash_src'] != df_merge['hash_tgt']]
# hash_x is hash_src and hash_y is hash_tgt
 
if not df_update.empty:
    print(f"🔄 Updating {len(df_update)} rows in employees_target...")
    # Reconstruct the target structure using the fresh source values (_src)
    df_update_final = pd.DataFrame({
        'id': df_update['id'],
        'name': df_update['name_src'],
        'salary': df_update['salary_src'],
        'department': df_update['department_src'],
        'last_updated': df_update['last_updated_src']
    })
    ids_to_update = df_update_final['id'].tolist()
    # Clear out the stale database records before inserting new copies
    with engine.begin() as connection:
        if len(ids_to_update) == 1:
            query = text("DELETE FROM employees_target WHERE id = :id_val")
            connection.execute(query, {"id_val": ids_to_update[0]})
        else:
            query = text("DELETE FROM employees_target WHERE id IN :id_list")
            connection.execute(query, {"id_list": tuple(ids_to_update)})
    # Write updated rows back to database
    df_update_final.to_sql("employees_target", con=engine, if_exists='append', index=False)
 
# =========================================================================
# STEP 4: HANDLE INSERTS (New Records)
# =========================================================================
df_new = df_source[~df_source['id'].isin(df_target['id'])]
 
if not df_new.empty:
    print(f"✨ Inserting {len(df_new)} new rows into employees_target...")
    # Drop the temporary hash column so it matches the MySQL schema structure exactly
    df_new_final = df_new.drop(columns=['hash'])
    df_new_final.to_sql("employees_target", con=engine, if_exists='append', index=False)
 
print("✅ Synchronization completed successfully!")