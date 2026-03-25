"""
Database initialization script
Run this to create tables in your existing 'growkarodatabase'
"""

import psycopg2
from psycopg2 import sql
from database import DATABASE_URL, engine, init_db
from db_models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """
    Create all tables defined in models
    """
    try:
        logger.info("Creating tables in growkarodatabase...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
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
