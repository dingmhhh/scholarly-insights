import sqlite3
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent

# Database and schema file paths
DB_PATH = BASE_DIR / "scholarly.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def get_connection():
    """Establish a connection to the SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
    return connection

def intialize_database():
    """Initialize the database using the schema.sql file."""
    conn = get_connection()
    try:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema)
        print("Database schema created successfully.")
    finally:
        conn.close()    

if __name__ == "__main__":
    intialize_database()