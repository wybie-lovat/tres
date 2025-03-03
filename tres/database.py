from peewee import PostgresqlDatabase
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database connection settings from environment variables
DB_NAME = os.getenv("DB_NAME", "tres_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

# Create Peewee database instance
db = PostgresqlDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

# Function to connect to the database
def connect_db():
    if db.is_closed():
        db.connect()

# Function to close the database connection
def close_db():
    if not db.is_closed():
        db.close()
