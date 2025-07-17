"""
Database Manager for ChatGLM3 Discord Bot
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional, Tuple, List, Dict, Any, Union
import logging
from .config import ConfigManager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize database manager"""
        self.config = config_manager or ConfigManager()
        self._connection_params = None
        self._initialize_connection_params()

    def _initialize_connection_params(self):
        """Initialize database connection parameters"""
        try:
            self._connection_params = self.config.get_database_config()
        except Exception as e:
            logger.error(f"Failed to initialize database configuration: {e}")
            self._connection_params = None

    def _get_connection(self) -> Tuple[Optional[mysql.connector.MySQLConnection], Optional[str]]:
        """Get database connection"""
        if not self._connection_params:
            return None, "Database configuration not available"

        try:
            connection = mysql.connector.connect(**self._connection_params)
            return connection, None
        except Error as e:
            logger.error(f"Database connection error: {e}")
            return None, f"Database connection error: {e}"
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            return None, f"Unexpected database error: {e}"

    def test_connection(self) -> bool:
        """Test database connection"""
        connection, error = self._get_connection()
        if connection:
            try:
                connection.close()
                return True
            except:
                pass
        return False

    def execute_query(
        self, 
        query: str, 
        max_results: Optional[int] = None
    ) -> Tuple[Union[List[Dict], str, None], Optional[str]]:
        """Execute SQL query and return results"""
        connection, error = self._get_connection()
        if error:
            return None, error

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            # Handle different query types
            query_type = query.strip().upper()
            if query_type.startswith('SELECT'):
                results = cursor.fetchall()
                if max_results and len(results) > max_results:
                    results = results[:max_results]
                return results, None
            else:
                # For INSERT, UPDATE, DELETE, etc.
                connection.commit()
                affected_rows = cursor.rowcount
                return f"Query executed successfully. {affected_rows} rows affected.", None

        except Error as e:
            logger.error(f"Query execution error: {e}")
            return None, f"Query execution error: {e}"
        except Exception as e:
            logger.error(f"Unexpected query error: {e}")
            return None, f"Unexpected query error: {e}"
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def get_table_info(self) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Get database table information"""
        query = """
        SELECT 
            TABLE_NAME as table_name,
            TABLE_COMMENT as table_comment,
            TABLE_ROWS as estimated_rows
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME
        """
        return self.execute_query(query)

    def get_table_schema(self, table_name: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Get schema for a specific table"""
        query = """
        SELECT 
            COLUMN_NAME as column_name,
            DATA_TYPE as data_type,
            IS_NULLABLE as is_nullable,
            COLUMN_DEFAULT as default_value,
            COLUMN_COMMENT as comment
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        
        connection, error = self._get_connection()
        if error:
            return None, error

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (table_name,))
            results = cursor.fetchall()
            return results, None
        except Error as e:
            logger.error(f"Schema query error: {e}")
            return None, f"Schema query error: {e}"
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close() 