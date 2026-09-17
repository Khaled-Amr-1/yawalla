from flask import Flask, render_template, jsonify, request
import sqlite3
import datetime

app = Flask(__name__)
DB_NAME = "network_monitor.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/networks')
def get_networks():
    conn = get_db_connection()
    networks = conn.execute('SELECT bssid, ssid FROM networks').fetchall()
    conn.close()
    return jsonify([{"bssid": n["bssid"], "ssid": n["ssid"]} for n in networks])

@app.route('/api/traffic')
def get_traffic():
    start_date = request.args.get('start_date', datetime.date.today().strftime("%Y-%m-%d"))
    end_date = request.args.get('end_date', datetime.date.today().strftime("%Y-%m-%d"))
    bssids = request.args.getlist('bssids[]')

    conn = get_db_connection()
    
    query = '''
        SELECT program_name, SUM(download_bytes) as download, SUM(upload_bytes) as upload
        FROM traffic_logs
        WHERE log_date >= ? AND log_date <= ?
    '''
    params = [start_date, end_date]

    if bssids:
        placeholders = ','.join('?' * len(bssids))
        query += f' AND bssid IN ({placeholders})'
        params.extend(bssids)

    query += '''
        GROUP BY program_name
        ORDER BY (SUM(download_bytes) + SUM(upload_bytes)) DESC
    '''
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    data = []
    total_down = 0
    total_up = 0

    for row in rows:
        down = row["download"]
        up = row["upload"]
        total_down += down
        total_up += up
        data.append({
            "program": row["program_name"],
            "download": down,
            "upload": up,
            "total": down + up
        })
        
    return jsonify({
        "apps": data,
        "total_download": total_down,
        "total_upload": total_up,
        "grand_total": total_down + total_up
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)