import sqlite3
import datetime

DB_NAME = "network_monitor.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS networks (
            bssid TEXT PRIMARY KEY,
            ssid TEXT NOT NULL,
            alias TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_logs (
            log_date TEXT NOT NULL,
            bssid TEXT NOT NULL,
            program_name TEXT NOT NULL,
            download_bytes INTEGER DEFAULT 0,
            upload_bytes INTEGER DEFAULT 0,
            PRIMARY KEY (log_date, bssid, program_name),
            FOREIGN KEY (bssid) REFERENCES networks (bssid)
        )
    ''')

    conn.commit()
    conn.close()

def register_network(bssid, ssid):
    if not bssid or not ssid:
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO networks (bssid, ssid)
        VALUES (?, ?)
        ON CONFLICT(bssid) DO NOTHING
    ''', (bssid, ssid))
    conn.commit()
    conn.close()

def update_traffic(bssid, program_name, download_delta, upload_delta):
    if not bssid or not program_name:
        return

    today_date = datetime.date.today().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO traffic_logs (log_date, bssid, program_name, download_bytes, upload_bytes)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(log_date, bssid, program_name) DO UPDATE SET
            download_bytes = download_bytes + excluded.download_bytes,
            upload_bytes = upload_bytes + excluded.upload_bytes
    ''', (today_date, bssid, program_name, download_delta, upload_delta))

    conn.commit()
    conn.close()