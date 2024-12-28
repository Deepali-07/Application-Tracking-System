from pymongo import MongoClient

MONGO_DB_URL = "mongodb+srv://deepali:<test1234>@cluster0.9ftvh.mongodb.net/ats_database?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_DB_URL)
    db = client['ats_database']
    print("Connected to MongoDB")
    print("Collections:", db.list_collection_names())
except Exception as e:
    print(f"MongoDB connection error: {e}")

