# SwasthaSeve(CP-RMS)

A web-based system for hospitals to manage patient queues, drug inventory, and broadcast emergency alerts in real-time.

## Features

- **Centralized Patient Token Queue**: Generate, view, and manage patient tokens per department. Real-time queue status for patients and hospital staff.
- **Drug Inventory Management**: Track stock, update quantities, and receive low-stock alerts for hospital pharmacy drugs via MongoDB backend.
- **Emergency Alerts**: Broadcast Code Red and other alerts to display screens and connected clients instantly.
- **Smart Display Dashboard**: Web frontend (HTML/JS) for real-time display of patient queues, inventory, and emergency alerts. Includes sound notification for critical alerts.
- **Data Import Utilities**: Scripts to import CSV data for tokens, inventory, departments, and emergency alerts into MongoDB.
- **RESTful API Endpoints**: For tokens, inventory, alerts, and broadcasting, built on Flask.
- **Background Scheduler**: Automatic low-stock checks and alert broadcasting.
- **WebSocket (Socket.IO)**: For live updates and event-driven alerts.

## Technology Stack

- **Backend**: Python (Flask, Flask-SocketIO, APScheduler, pymongo, pandas)
- **Frontend**: HTML, JavaScript, Chart.js
- **Database**: MongoDB
- **Environment Management**: python-dotenv
- **CSV Integration**: pandas, csv

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/msranjana/CP-RMS.git
cd CP-RMS
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file with your MongoDB details:

```
MONGO_URI=mongodb://localhost:27017
```

### 4. Run the application

```bash
python app.py
```

### 5. Access the dashboard

Open [http://localhost:5000/display](http://localhost:5000/display) in your browser.

## Key Files

- `app.py`: Main Flask application, API endpoints, scheduling, and SocketIO setup.
- `templates/display.html`: Real-time hospital dashboard UI.
- `requirements.txt`: Python dependencies.


## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

---

*Developed by Ranjana, 2025.*
