import sqlite3
try:
    # Step 1: Connect to SQLite database (or create it if it doesn't exist)
    connection = sqlite3.connect("free.db")

    # Step 2: Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Step 3: Create the table with 4 columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id TEXT NOT NULL,
        registration_no TEXT NOT NULL UNIQUE,
        status TEXT CHECK(status IN ('Paid', 'Unpaid')) NOT NULL
    )
    """)

    # Step 4: Insert sample data into the table with 'Paid' and 'Unpaid' status
    cursor.execute("""
    INSERT OR IGNORE INTO cars (car_id, registration_no, status)
    VALUES 
        ('CAR001', 'AUZ407', 'Paid'),
        ('CAR002', 'UJ703', 'Paid'),
        ('CAR003', 'AVK320', 'Unpaid'),
        ('CAR004', 'XYZ5678', 'Unpaid'),
        ('CAR005', 'LMN9876', 'Paid'),
        ('CAR006', 'ADE289', 'Paid'),
        ('CAR007', 'RB469', 'Paid'),
        ('CAR008', 'AFR2012', 'Unpaid'),
        ('CAR009', 'B8222', 'Unpaid'),
        ('CAR0010', 'BC9976', 'Unpaid')
    """)

    # Commit the changes to save the data
    connection.commit()

    # Step 5: Query the data to check
    cursor.execute("SELECT * FROM cars")
    rows = cursor.fetchall()

    # Print the data
    for row in rows:
        print(row)

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

finally:
    # Step 6: Close the connection
    if connection:
        connection.close()