from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import sqlite3
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
CORS(app)

DB_NAME = 'gps_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS gps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    latitude REAL,
                    longitude REAL,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/api/receive', methods=['POST'])
def receive_data():
    data = request.json
    latitude = data['latitude']
    longitude = data['longitude']
    timestamp = datetime.datetime.now().isoformat()
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO gps (latitude, longitude, timestamp) VALUES (?, ?, ?)",
              (latitude, longitude, timestamp))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT latitude, longitude, timestamp FROM gps ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"latitude": row[0], "longitude": row[1], "timestamp": row[2]} for row in rows])

@app.route('/api/download', methods=['GET'])
def download_pdf():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM gps ORDER BY id ASC")
    data = c.fetchall()
    conn.close()

    pdf_path = "gps_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y = height - 50
    c.drawString(100, y, "Smart Agro Car - GPS Report")
    y -= 30

    for row in data:
        text = f"ID: {row[0]}, Lat: {row[1]}, Long: {row[2]}, Time: {row[3]}"
        c.drawString(50, y, text)
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
