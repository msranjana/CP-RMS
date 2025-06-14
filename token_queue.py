import csv
import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["hospital_db"]
token_collection = db["token_queue"]

def import_tokens(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        inserted = 0

        for row in reader:
            try:
                token_doc = {
                    "token_number": int(row["token_id"]),
                    "department": row["dept_id"],
                    "patient_name": row["patient_name"],
                    "status": row["status"],
                    "issued_at": datetime.datetime.utcnow()
                }
                token_collection.insert_one(token_doc)
                inserted += 1
            except Exception as e:
                print(f"Skipping row due to error: {e}\nRow: {row}")

        print(f"✅ Inserted {inserted} tokens successfully.")

def get_queue(department=None):
    if department:
        return list(token_collection.find({"department": department}))
    else:
        return list(token_collection.find({}))

def generate_token(department):
    latest = token_collection.find_one(
        {"department": department},
        sort=[("issued_at", -1)]
    )

    next_token = latest["token_number"] + 1 if latest else 1

    token_data = {
        "department": department,
        "token_number": next_token,
        "issued_at": datetime.datetime.utcnow(),
        "status": "waiting"
    }

    token_collection.insert_one(token_data)
    return token_data

if __name__ == "__main__":
    import_tokens("data/token_queue.csv")  # adjust path as needed
