#!/usr/bin/env python
"""
Database migration script to update the schema with new fields.
"""
import os
import logging
from dotenv import load_dotenv
from peewee import PostgresqlDatabase, SqliteDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = os.getenv("DB_NAME", "tres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

# Connect to the database
db = PostgresqlDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

def migrate():
    """Run database migrations."""
    try:
        logger.info("Starting database migration...")
        
        # Connect to the database
        db.connect()
        
        # Add transaction_count column to blockrange table if it doesn't exist
        logger.info("Adding transaction_count column to blockrange table...")
        try:
            db.execute_sql(
                "ALTER TABLE blockrange ADD COLUMN IF NOT EXISTS transaction_count INTEGER DEFAULT 0"
            )
            logger.info("Successfully added transaction_count column")
        except Exception as e:
            logger.error(f"Error adding transaction_count column: {e}")
            raise
        
        # Add constraints and indexes
        logger.info("Adding constraints and indexes...")
        try:
            # Add check constraint for end_block >= start_block
            db.execute_sql(
                "ALTER TABLE blockrange DROP CONSTRAINT IF EXISTS blockrange_end_block_check"
            )
            db.execute_sql(
                "ALTER TABLE blockrange ADD CONSTRAINT blockrange_end_block_check CHECK (end_block >= start_block)"
            )
            
            # Add unique index for wallet + block range
            db.execute_sql(
                "DROP INDEX IF EXISTS blockrange_wallet_id_start_block_end_block"
            )
            db.execute_sql(
                "CREATE UNIQUE INDEX IF NOT EXISTS blockrange_wallet_id_start_block_end_block ON blockrange (wallet_id, start_block, end_block)"
            )
            
            # Add composite indexes for transaction queries
            db.execute_sql(
                "CREATE INDEX IF NOT EXISTS transaction_wallet_id_block_number ON transaction (wallet_id, block_number)"
            )
            db.execute_sql(
                "CREATE INDEX IF NOT EXISTS transaction_wallet_id_time_stamp ON transaction (wallet_id, time_stamp)"
            )
            db.execute_sql(
                "CREATE INDEX IF NOT EXISTS transaction_wallet_id_is_error ON transaction (wallet_id, is_error)"
            )
            
            logger.info("Successfully added constraints and indexes")
        except Exception as e:
            logger.error(f"Error adding constraints and indexes: {e}")
            # Continue even if this fails
        
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        # Close the database connection
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    migrate()
