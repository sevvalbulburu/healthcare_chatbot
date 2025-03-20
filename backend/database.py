import sqlite3

DB_NAME = "appointments.db"


# Create db connection and cursor
def create_connection():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    return connection, cursor

# Create table for booking
def create_booking_table():
    try:
        connection, cursor = create_connection()
        cursor.execute("""CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            personal_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            description TEXT
        )
        """
        )
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False


# Drop table 
def drop_table():
    try:
        connection, cursor = create_connection()
        cursor.execute("DROP TABLE IF EXISTS appointments")
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error dropping table: {e}")
        return False

create_booking_table()        