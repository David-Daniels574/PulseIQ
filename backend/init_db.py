"""
Database initialization script
Run this to create tables in your existing 'growkarodatabase'
"""

import psycopg2
from psycopg2 import sql
from database import DATABASE_URL, engine, init_db
from db_models import Base
import logging
from sqlalchemy import inspect, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """
    Drop all existing tables and recreate schema from models.
    """
    try:
        logger.info("Dropping all existing tables in public schema (CASCADE)...")
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names(schema="public")

        if existing_tables:
            with engine.begin() as conn:
                for table_name in existing_tables:
                    conn.execute(text(f'DROP TABLE IF EXISTS "public"."{table_name}" CASCADE'))
            logger.info(f"✅ Dropped {len(existing_tables)} tables")
        else:
            logger.info("No existing tables found to drop")

        logger.info("Creating fresh tables from SQLAlchemy models...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables created successfully!")

        # List created tables
        tables = inspect(engine).get_table_names(schema="public")
        logger.info(f"📊 Created tables: {', '.join(tables)}")
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise


def verify_connection():
    """
    Verify database connection
    """
    try:
        logger.info("Verifying database connection...")
        connection = engine.connect()
        connection.close()
        logger.info("✅ Database connection verified!")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Supabase Database Setup for GrowKaro ABSA")
    print("=" * 60)
    print()
    
    print("Step 1: Verifying connection to Supabase...")
    if not verify_connection():
        print("❌ Setup failed! Check your Supabase password and network.")
        exit(1)
    print()
    
    print("Step 2: Creating tables...")
    create_tables()
    print()
    
    print("=" * 60)
    print("✅ Database setup completed successfully!")
    print("=" * 60)
