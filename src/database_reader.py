"""Read-only database service for Discord bot to access existing database."""
import os
import sys
import logging
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import json
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ReadOnlyDatabaseService:
    """Read-only database service for Discord bot queries."""
    
    def __init__(self):
        """Initialize the read-only database service."""
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.is_connected = False
        self.host_ip = None
        
    def connect(self, host_ip: Optional[str] = None) -> bool:
        """Connect to the database."""
        try:
            # Use provided host_ip or try to discover
            if not host_ip:
                host_ip = self._discover_host_ip()
            
            if not host_ip:
                self.logger.error("No database host IP provided or discovered")
                return False
            
            # Default credentials
            connection_params = {
                'host': host_ip,
                'port': 3306,
                'user': 'root',
                'password': 'Meridian0723',
                'database': 'MyACG_data',
                'autocommit': True,
                'charset': 'utf8mb4'
            }
            
            # Try to connect
            self.connection = mysql.connector.connect(**connection_params)
            self.is_connected = True
            self.host_ip = host_ip
            
            self.logger.info(f"Successfully connected to database at {host_ip}")
            return True
            
        except Error as e:
            self.logger.error(f"Database connection error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to database: {e}")
            return False
    
    def _discover_host_ip(self) -> Optional[str]:
        """Try to discover the database host IP."""
        # Try common local network IPs
        common_ips = [
            "localhost",
            "127.0.0.1",
            "192.168.1.100",
            "192.168.1.101",
            "192.168.0.100",
            "192.168.0.101"
        ]
        
        for ip in common_ips:
            try:
                test_conn = mysql.connector.connect(
                    host=ip,
                    port=3306,
                    user='root',
                    password='Meridian0723',
                    database='MyACG_data',
                    connect_timeout=3
                )
                test_conn.close()
                self.logger.info(f"Discovered database at {ip}")
                return ip
            except:
                continue
        
        return None
    
    def health_check(self) -> Tuple[bool, str]:
        """Check database health."""
        try:
            if not self.is_connected or not self.connection:
                return False, "Database not connected"
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0] == 1:
                return True, "Database health check passed - all systems operational"
            else:
                return False, "Database is not responding correctly"
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False, f"Health check failed: {e}"
    
    def _execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries."""
        try:
            if not self.is_connected or not self.connection:
                raise Exception("Database not connected")
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            
            # Return results directly - the dictionary cursor should handle the conversion
            return results if results else []  # type: ignore
        except Exception as e:
            self.logger.error(f"Query execution error: {e}")
            raise
    
    # Order queries
    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get order by ID."""
        try:
            query = """
                SELECT * FROM orders WHERE id = %s
            """
            results = self._execute_query(query, (order_id,))
            return results[0] if results else None
        except Exception as e:
            self.logger.error(f"Error getting order by ID {order_id}: {e}")
            return None
    
    def get_order_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Get order by external order ID."""
        try:
            query = """
                SELECT * FROM orders WHERE external_order_id = %s
            """
            results = self._execute_query(query, (external_id,))
            return results[0] if results else None
        except Exception as e:
            self.logger.error(f"Error getting order by external ID {external_id}: {e}")
            return None
    
    def search_orders(self, search_term: str) -> List[Dict[str, Any]]:
        """Search orders by customer name or order ID."""
        try:
            # First try with created_at column
            try:
                query = """
                    SELECT * FROM orders 
                    WHERE customer_name LIKE %s OR external_order_id LIKE %s
                    ORDER BY created_at DESC
                """
                search_pattern = f"%{search_term}%"
                results = self._execute_query(query, (search_pattern, search_pattern))
                if results is not None:
                    return results
            except Exception as e:
                self.logger.warning(f"Search with created_at failed, trying with order_date: {e}")
            
            # Fallback to order_date column
            query = """
                SELECT * FROM orders 
                WHERE customer_name LIKE %s OR external_order_id LIKE %s
                ORDER BY order_date DESC
            """
            search_pattern = f"%{search_term}%"
            results = self._execute_query(query, (search_pattern, search_pattern))
            return results
        except Exception as e:
            self.logger.error(f"Error searching orders with term {search_term}: {e}")
            return []
    
    def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent orders."""
        try:
            # First try with created_at column
            try:
                query = """
                    SELECT * FROM orders 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """
                results = self._execute_query(query, (limit,))
                if results is not None:
                    return results
            except Exception as e:
                self.logger.warning(f"Recent orders with created_at failed, trying with order_date: {e}")
            
            # Fallback to order_date column
            query = """
                SELECT * FROM orders 
                ORDER BY order_date DESC 
                LIMIT %s
            """
            return self._execute_query(query, (limit,))
        except Exception as e:
            self.logger.error(f"Error getting recent orders: {e}")
            return []
    
    def get_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get orders by status."""
        try:
            # First try with created_at column
            try:
                query = """
                    SELECT * FROM orders 
                    WHERE status = %s
                    ORDER BY created_at DESC
                """
                results = self._execute_query(query, (status,))
                if results is not None:
                    return results
            except Exception as e:
                self.logger.warning(f"Orders by status with created_at failed, trying with order_date: {e}")
            
            # Fallback to order_date column
            query = """
                SELECT * FROM orders 
                WHERE status = %s
                ORDER BY order_date DESC
            """
            return self._execute_query(query, (status,))
        except Exception as e:
            self.logger.error(f"Error getting orders by status {status}: {e}")
            return []
    
    def get_orders_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get orders within a date range."""
        try:
            query = """
                SELECT * FROM orders 
                WHERE order_date >= %s AND order_date <= %s
                ORDER BY order_date DESC
            """
            return self._execute_query(query, (start_date, end_date))
        except Exception as e:
            self.logger.error(f"Error getting orders by date range: {e}")
            return []
    
    # Product queries
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        try:
            query = """
                SELECT * FROM products WHERE id = %s
            """
            results = self._execute_query(query, (product_id,))
            return results[0] if results else None
        except Exception as e:
            self.logger.error(f"Error getting product by ID {product_id}: {e}")
            return None
    
    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product by SKU."""
        try:
            query = """
                SELECT * FROM products WHERE sku = %s
            """
            results = self._execute_query(query, (sku,))
            return results[0] if results else None
        except Exception as e:
            self.logger.error(f"Error getting product by SKU {sku}: {e}")
            return None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products."""
        try:
            query = """
                SELECT * FROM products 
                WHERE is_active = 1
                ORDER BY name
            """
            return self._execute_query(query)
        except Exception as e:
            self.logger.error(f"Error getting all products: {e}")
            return []
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get products by category."""
        try:
            query = """
                SELECT * FROM products 
                WHERE category = %s AND is_active = 1
                ORDER BY name
            """
            return self._execute_query(query, (category,))
        except Exception as e:
            self.logger.error(f"Error getting products by category {category}: {e}")
            return []
    
    # User queries
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            query = """
                SELECT * FROM users WHERE id = %s
            """
            results = self._execute_query(query, (user_id,))
            return results[0] if results else None
        except Exception as e:
            self.logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        try:
            query = """
                SELECT * FROM users WHERE username = %s
            """
            results = self._execute_query(query, (username,))
            return results[0] if results else None
        except Exception as e:
            self.logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        try:
            query = """
                SELECT * FROM users 
                WHERE is_active = 1
                ORDER BY name
            """
            return self._execute_query(query)
        except Exception as e:
            self.logger.error(f"Error getting all users: {e}")
            return []
    
    # MyACG Account queries
    def get_myacg_accounts(self) -> List[Dict[str, Any]]:
        """Get all MyACG accounts."""
        try:
            query = """
                SELECT id, name, username, api_key, is_default, is_active, 
                       created_at, updated_at
                FROM myacg_accounts 
                WHERE is_active = 1
                ORDER BY name
            """
            return self._execute_query(query)
        except Exception as e:
            self.logger.error(f"Error getting MyACG accounts: {e}")
            return []
    
    def get_default_myacg_account(self) -> Optional[Dict[str, Any]]:
        """Get the default MyACG account."""
        try:
            query = """
                SELECT id, name, username, api_key, is_default, is_active, 
                       created_at, updated_at
                FROM myacg_accounts 
                WHERE is_default = 1 AND is_active = 1
                LIMIT 1
            """
            results = self._execute_query(query)
            return results[0] if results else None
        except Exception as e:
            self.logger.error(f"Error getting default MyACG account: {e}")
            return None
    
    # Statistics queries
    def get_order_statistics(self) -> Dict[str, Any]:
        """Get order statistics."""
        try:
            # Get total orders
            total_query = "SELECT COUNT(*) as total FROM orders"
            total_result = self._execute_query(total_query)
            total_orders = total_result[0]['total'] if total_result else 0
            
            # Get status counts
            status_query = """
                SELECT status, COUNT(*) as count 
                FROM orders 
                GROUP BY status
            """
            status_results = self._execute_query(status_query)
            status_counts = {row['status']: row['count'] for row in status_results}
            
            # Get total revenue
            revenue_query = "SELECT SUM(total) as total_revenue FROM orders WHERE total IS NOT NULL"
            revenue_result = self._execute_query(revenue_query)
            total_revenue = revenue_result[0]['total_revenue'] if revenue_result and revenue_result[0]['total_revenue'] else 0.0
            
            # Calculate average
            average_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
            
            return {
                'total_orders': total_orders,
                'status_counts': status_counts,
                'total_revenue': float(total_revenue),
                'average_order_value': float(average_order_value)
            }
        except Exception as e:
            self.logger.error(f"Error getting order statistics: {e}")
            return {}
    
    def get_product_statistics(self) -> Dict[str, Any]:
        """Get product statistics."""
        try:
            # Get total products
            total_query = "SELECT COUNT(*) as total FROM products WHERE is_active = 1"
            total_result = self._execute_query(total_query)
            total_products = total_result[0]['total'] if total_result else 0
            
            # Get category counts
            category_query = """
                SELECT category, COUNT(*) as count 
                FROM products 
                WHERE is_active = 1
                GROUP BY category
            """
            category_results = self._execute_query(category_query)
            category_counts = {row['category']: row['count'] for row in category_results}
            
            # Get low stock products
            low_stock_query = """
                SELECT COUNT(*) as count 
                FROM products 
                WHERE stock_quantity <= low_stock_threshold AND is_active = 1
            """
            low_stock_result = self._execute_query(low_stock_query)
            low_stock_products = low_stock_result[0]['count'] if low_stock_result else 0
            
            # Get total stock value
            stock_value_query = """
                SELECT SUM(cost * stock_quantity) as total_value 
                FROM products 
                WHERE cost IS NOT NULL AND stock_quantity IS NOT NULL AND is_active = 1
            """
            stock_value_result = self._execute_query(stock_value_query)
            total_stock_value = stock_value_result[0]['total_value'] if stock_value_result and stock_value_result[0]['total_value'] else 0.0
            
            return {
                'total_products': total_products,
                'category_counts': category_counts,
                'low_stock_products': low_stock_products,
                'total_stock_value': float(total_stock_value)
            }
        except Exception as e:
            self.logger.error(f"Error getting product statistics: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.is_connected = False
                self.logger.info("Database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database connection: {e}")


# Global instance
db_reader = ReadOnlyDatabaseService() 