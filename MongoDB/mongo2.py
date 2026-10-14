from pymongo import MongoClient
from datetime import datetime
# --- Step 1: Connect ---
client = MongoClient('mongodb://localhost:27017/')
db = client['de_practice']
runs = db['runs']
# --- Step 2: Insert data ---
runs.insert_one({
'name': 'python_etl_job',
'status': 'success',
'records': 25000,
'duration': 60,
'env': 'prod',
'timestamp': datetime.utcnow()
})
# --- Step 3: Query ---
print('All successful runs:')
for doc in runs.find({ 'status': 'success' }, { '_id': 0, 'name': 1,
'records': 1 }):
    print(' -', doc['name'], ':', doc['records'], 'records')
# --- Step 4: Run an aggregation ---
pipeline = [
{ '$match': { 'env': 'prod' } },
{ '$group': { '_id': '$name', 'total': { '$sum': '$records' } } },
{ '$sort': { 'total': -1 } }
]
print('\nTotal records per pipeline:')
for r in runs.aggregate(pipeline):
    print(f" {r['_id']:20s} {r['total']:,} records")