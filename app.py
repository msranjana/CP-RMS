from flask import Flask, request, jsonify, render_template
from token_queue import import_tokens, get_queue, generate_token
from inventory import get_inventory, update_stock, get_low_stock
from broadcast import create_broadcast, get_broadcasts
from apscheduler.schedulers.background import BackgroundScheduler
from bson import ObjectId
from flask_socketio import SocketIO
import csv
from datetime import datetime, timedelta
import os
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")


def generate_random_token_csv(filename="token_queue.csv", num_entries=20):
    departments = ['D001', 'D002', 'D003', 'D004']
    patient_names = ['A. Kumar', 'B. Reddy', 'C. Fernandes', 'D. Shetty', 'E. Nair', 'F. Rao']
    statuses = ['Waiting', 'Called', 'In Progress']

    now = datetime.now()
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["token_id", "dept_id", "patient_name", "status", "timestamp"])
        current_time = datetime.now()

        for i in range(num_entries):  # Generate 20 time slots
            num_tokens = random.randint(0, 5)  # 👈 Random tokens per time slot
            for _ in range(num_tokens):
                token_id = random.randint(100, 999)
                row = [
                    token_id,
                    random.choice(departments),
                    random.choice(patient_names),
                    random.choice(statuses),
                    (current_time + timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S')
                ]
                writer.writerow(row)
# Call it when app starts
generate_random_token_csv()

# --- TOKEN ENDPOINTS ---

@app.route("/token", methods=["POST"])
def create_token():
    data = request.json
    department = data.get("department")

    if not department:
        return jsonify({"error": "Department is required"}), 400

    token = generate_token(department)
    token["_id"] = str(token["_id"])
    return jsonify(token), 201


@app.route('/api/token_chart')
def token_chart():
    from collections import Counter
    time_counts = Counter()
    with open("token_queue.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                dt = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                time_key = dt.strftime("%H:%M")
                time_counts[time_key] += 1
            except:
                continue

    sorted_data = sorted(time_counts.items())
    return jsonify([{"time": t, "count": c} for t, c in sorted_data])


@app.route("/token/<department>", methods=["GET"])
def queue(department):
    tokens = get_queue(department)
    for token in tokens:
        token["_id"] = str(token["_id"])
    return jsonify(tokens), 200

@app.route('/api/tokens')
def get_tokens():
    tokens = []
    
    # Load department metadata
    dept_map = {}
    with open("data/departments.csv", "r") as dept_file:
        reader = csv.DictReader(dept_file)
        for row in reader:
            dept_map[row["dept_id"]] = {
                "department_name": row["department_name"],
                "location": row["location"]
            }

    # Read token data and join with department
    with open("token_queue.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            dept_id = row["dept_id"]
            dept_info = dept_map.get(dept_id, {"department_name": "Unknown", "location": "Unknown"})

            tokens.append({
                "token_number": row["token_id"],
                "department": dept_info["department_name"],
                "location": dept_info["location"],
                "patient_name": row["patient_name"],
                "status": row["status"],
                "timestamp": row["timestamp"]
            })
    return jsonify(tokens)

# --- INVENTORY ENDPOINTS ---

@app.route("/inventory", methods=["GET"])
def fetch_inventory():
    return jsonify(get_inventory()), 200

@app.route("/inventory/update", methods=["POST"])
def modify_stock():
    data = request.json
    name = data.get("name")
    change = data.get("change")

    if not name or change is None:
        return jsonify({"error": "Drug name and change amount are required"}), 400

    updated = update_stock(name, change)
    if updated:
        return jsonify({"message": "Stock updated"}), 200
    else:
        return jsonify({"error": "Drug not found"}), 404

@app.route("/inventory/low", methods=["GET"])
def low_stock_alerts():
    threshold = int(request.args.get("threshold", 20))
    return jsonify(get_low_stock(threshold)), 200

# --- BROADCAST ENDPOINTS ---

@app.route("/broadcasts", methods=["GET"])
def fetch_broadcasts():
    alerts = get_broadcasts()
    for a in alerts:
        a["_id"] = str(a["_id"])
        a["timestamp"] = a["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(alerts), 200

@app.route("/broadcasts/send", methods=["POST"])
def manual_broadcast():
    data = request.json
    alert_type = data.get("alert_type")
    message = data.get("message")

    if not alert_type or not message:
        return jsonify({"error": "Missing alert_type or message"}), 400

    alert = create_broadcast(alert_type, message)
    alert["_id"] = str(alert["_id"])
    alert["timestamp"] = alert["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(alert), 201

@app.route("/api/alerts", methods=["GET"])
def api_alerts():
    alerts = get_broadcasts()
    for a in alerts:
        a["_id"] = str(a["_id"])
        a["timestamp"] = a["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(alerts), 200

# --- DISPLAY SCREEN ---
@app.route("/display")
def display_screen():
    alerts = get_broadcasts()[:5]
    inventory = get_inventory()
    tokens = get_queue()

    # Ensure timestamps are formatted as strings
    for token in tokens:
        issued_at = token.get("issued_at") or token.get("timestamp")
        if isinstance(issued_at, datetime):
            token["issued_at"] = issued_at.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(issued_at, str):
            token["issued_at"] = issued_at
        else:
            token["issued_at"] = "N/A"
    print("Tokens Data:", tokens)

    for alert in alerts:
        alert["_id"] = str(alert["_id"])
        alert["timestamp"] = alert["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    return render_template("display.html", alerts=alerts, inventory=inventory, tokens=tokens)

# --- BACKGROUND LOW STOCK CHECK ---

def check_and_broadcast_low_stock():
    low_stock_drugs = get_low_stock()
    for drug in low_stock_drugs:
        create_broadcast(
            alert_type="Code Red",
            message=f"Low stock for {drug['name']}: Only {drug['stock']} left!"
        )

# --- SCHEDULER SETUP ---

scheduler = BackgroundScheduler()
scheduler.add_job(check_and_broadcast_low_stock, 'interval', seconds=30)
scheduler.start()



from bson import ObjectId
from datetime import datetime

@app.route("/api/broadcast", methods=["POST"])
def broadcast_alert():
    data = request.json
    alert_type = data.get("alert_type")
    message = data.get("message")

    alert = create_broadcast(alert_type, message, socketio)
    if alert:
        # Convert ObjectId and timestamp to string
        alert["_id"] = str(alert["_id"])
        alert["timestamp"] = alert["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({"status": "success", "alert": alert}), 200
    else:
        return jsonify({"status": "duplicate", "message": "Alert already exists"}), 409



@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

# --- RUN FLASK APP ---
if __name__ == "__main__":
    socketio.run(app, debug=True)