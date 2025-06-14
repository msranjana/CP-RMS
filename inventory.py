from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from broadcast import create_broadcast

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["hospital"]
inventory = db["drug_inventory"]

def get_inventory():
    drugs = list(inventory.find())
    for drug in drugs:
        drug["_id"] = str(drug["_id"])
    return drugs

def update_stock(drug_name, amount):
    result = inventory.update_one(
        {"name": drug_name},
        {"$inc": {"stock": amount}}
    )
    
    if result.matched_count == 0:
        return 0  # Drug not found

    updated_doc = inventory.find_one({"name": drug_name})
    if updated_doc and updated_doc["stock"] < updated_doc.get("reorder_level", 20):
        create_broadcast(
            alert_type="Code Red",
            message=f"Low stock for {drug_name}: Only {updated_doc['stock']} left!"
        )

    return result.modified_count

def get_low_stock():
    drugs = list(inventory.find())
    low = [drug for drug in drugs if drug["stock"] < drug.get("reorder_level", 20)]
    for drug in low:
        drug["_id"] = str(drug["_id"])
    return low


