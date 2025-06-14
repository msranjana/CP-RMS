import csv
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["hospital"]
inventory = db["drug_inventory"]

def import_csv_to_mongo(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]  # normalize headers
        drugs = []

        for row in reader:
            row = {k.strip().lower(): v.strip() for k, v in row.items()}
            try:
                drug_doc = {
                    "drug_id": row["drug_id"],
                    "name": row["drug_name"],
                    "stock": int(row["stock_qty"]),
                    "unit": "units",  # default unit
                    "reorder_level": int(row["reorder_level"]),
                    "status": row["status"]
                }
                drugs.append(drug_doc)
            except (ValueError, KeyError):
                print(f"Skipping invalid row: {row}")

        if drugs:
            inventory.insert_many(drugs)
            print(f"✅ Inserted {len(drugs)} drugs into MongoDB.")
        else:
            print("⚠️ No valid data found in CSV.")

if __name__ == "__main__":
    import_csv_to_mongo("data/drug_inventory.csv")
