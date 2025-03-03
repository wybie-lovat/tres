from database import db
from models import Example

def create_tables():
    """Create database tables for all models."""
    with db:
        db.create_tables([Example])

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully.")
