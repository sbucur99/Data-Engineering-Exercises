import random
from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017/')
db = client['de_project']
db.runs.drop() # fresh start
# --- Generate fake data ---
pipelines = ['orders_etl', 'users_sync', 'stock_etl', 'payments_etl']
statuses = ['success', 'success', 'success', 'failed'] # 75% success rate
docs = []
for i in range(20):
    docs.append({
    'name': random.choice(pipelines),
    'status': random.choice(statuses),
    'records': random.randint(100, 50000),
    'duration': random.randint(2, 120),
    'env': 'prod',
    'date': datetime.utcnow() - timedelta(days=random.randint(0,30))
    })
db.runs.insert_many(docs)
print(f'Inserted {len(docs)} documents.')
# --- Aggregation: success rate per pipeline ---
pipeline = [
{ '$group': {
'_id': '$name',
'total': { '$sum': 1 },
'success': { '$sum': { '$cond': [{ '$eq': ['$status','success'] }, 1,
0] } },
'avg_dur': { '$avg': '$duration' }
}},
{ '$sort': { '_id': 1 } }
]
print('\n=== Pipeline Health Report ===')
print(f'{"Pipeline":<20} {"Runs":>5} {"Success%":>9} {"Avg Duration":>13}')
print('-' * 52)
for r in db.runs.aggregate(pipeline):
    rate = round(r['success'] / r['total'] * 100)
    print(f"{r['_id']:<20} {r['total']:>5} {rate:>8}%{r['avg_dur']:>10.1f}s")