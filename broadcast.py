# broadcast.py

from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["hospital"]
broadcasts = db["broadcasts"]
def create_broadcast(alert_type, message, socketio=None):
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    existing_alert = broadcasts.find_one({
        "alert_type": alert_type,
        "message": message,
        "timestamp": {"$gte": one_hour_ago}
    })

    if existing_alert:
        print("Recent alert already exists.")
        return None

    alert = {
        "alert_type": alert_type,
        "message": message,
        "timestamp": datetime.utcnow()
    }

    broadcasts.insert_one(alert)
    print("New alert inserted:", alert)

    # Emit alert over socket if socketio provided
    if socketio:
        socketio.emit("new_alert", {
            "alert_type": alert["alert_type"],
            "message": alert["message"],
            "timestamp": alert["timestamp"].isoformat()
        })

    return alert



def get_broadcasts():
    all_alerts = list(broadcasts.find().sort("timestamp", -1))
    for alert in all_alerts:
        alert["_id"] = str(alert["_id"])
    return all_alerts
