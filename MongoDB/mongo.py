from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['school']
# Insert a document
db.students.insert_one({ 'name': 'Bob', 'age': 23 })
# Print all students
for student in db.students.find():
    print(student)