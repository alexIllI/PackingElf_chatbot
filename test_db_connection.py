#!/usr/bin/env python3
"""
Test database connection and create database if needed.
"""

import mysql.connector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test database connection."""
    try:
        # Try to connect without specifying database
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Meridian0723'
        )
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if 'MyACG_data' not in databases:
            logger.info("Database 'MyACG_data' does not exist, creating it...")
            cursor.execute("CREATE DATABASE MyACG_data")
            logger.info("Database 'MyACG_data' created successfully")
        else:
            logger.info("Database 'MyACG_data' already exists")
        
        cursor.close()
        connection.close()
        
        # Test connection to the specific database
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Meridian0723',
            database='MyACG_data'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            logger.info("Database connection successful!")
            return True
        else:
            logger.error("Database connection test failed")
            return False
            
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing database connection...")
    success = test_connection()
    if success:
        print("✓ Database connection successful!")
        print("You can now run: python create_database_tables.py")
    else:
        print("✗ Database connection failed")
        print("Please check if MySQL is running and credentials are correct") 