#!/usr/bin/env python3
import uvicorn
from tres.database import db, connect_db, close_db
from tres.models import Wallet, Transaction, BlockRange

def create_tables():
    """Create database tables if they don't exist."""
    try:
        # Connect to the database
        connect_db()
        
        # Create tables
        db.create_tables([Wallet, Transaction, BlockRange], safe=True)
        print("Database tables created successfully.")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        # Always close the database connection
        close_db()

def run_server():
    """Run the FastAPI server."""
    uvicorn.run("tres.server:app", host="0.0.0.0", port=8000, reload=True)

def main():
    """Main function to set up the database and run the server."""
    # Create database tables
    create_tables()
    
    # Run the server
    run_server()

if __name__ == "__main__":
    main()
