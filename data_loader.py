import pandas as pd
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def load_csv_to_mongo(csv_path, collection_name):
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient='records')
    db[collection_name].delete_many({})  # Clear old data
    db[collection_name].insert_many(records)
    print(f"[+] Loaded {len(records)} records into {collection_name}")

if __name__ == "__main__":
    load_csv_to_mongo('data/token_queue.csv', 'token_queue')
    load_csv_to_mongo('data/drug_inventory.csv', 'drug_inventory')
    load_csv_to_mongo('data/emergency_alerts.csv', 'emergency_alerts')
    load_csv_to_mongo('data/departments.csv', 'departments')
    load_csv_to_mongo('data/blood_bank.csv', 'blood_bank')
