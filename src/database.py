import sqlite3
from config import DB_PATH

def check_plate_status(plate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM cars WHERE registration_no = ?", (plate,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Unknown"

