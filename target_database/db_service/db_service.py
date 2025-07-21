"""Database service for handling all database operations."""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, time
import logging
from sqlalchemy import text
from contextlib import contextmanager
import socket
import json
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Try to import mysql.connector, with fallback to pymysql
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logging.warning("mysql-connector-python not available, using pymysql fallback")

from packing_elf.models.database import SessionLocal
from packing_elf.models.user import User, Role, MyACGAccount
from packing_elf.models.order import Order, OrderStatus
from packing_elf.models.product import Product, ProductCategory
from packing_elf.models.shipping import ShippingLabel, PackingSlip
from packing_elf.services.password_service import password_service


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class UserNotFoundError(DatabaseError):
    """Raised when a user is not found."""
    pass


class OrderNotFoundError(DatabaseError):
    """Raised when an order is not found."""
    pass


class DatabaseService:
    """Service for database operations with proper session management."""

    def __init__(self):
        """Initialize database service."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing DatabaseService")

    def _load_order_attributes(self, orders: List[Order]) -> List[Order]:
        """Load all Order attributes to prevent DetachedInstanceError."""
        for order in orders:
            # Access all scalar attributes that might be used by the UI
            # Force load by accessing the actual values
            order.created_at  # This should trigger loading
            order.updated_at
            order.external_order_id
            order.invoice
            order.status
            order.customer_name
            order.notes
            order.coupon
            order.order_date
            order.total
            order.shipping_cost
            order.payment_method
            order.export_to_excel
            
            # Handle relationships carefully - load the IDs at least
            try:
                order.created_by_id
                if order.created_by:
                    order.created_by.name
            except:
                pass
            try:
                order.myacg_account_id
                if order.myacg_account:
                    order.myacg_account.name
            except:
                pass
        return orders

    def _load_myacg_account_attributes(self, accounts: List) -> List:
        """Load all MyACGAccount attributes to prevent DetachedInstanceError."""
        for account in accounts:
            # Access all scalar attributes that might be used by the UI
            account.id
            account.name
            account.username
            account.encrypted_password
            account.api_key
            account.is_default
            account.created_at
            account.updated_at
        return accounts

    def _load_user_attributes(self, users: List) -> List:
        """Load all User attributes to prevent DetachedInstanceError."""
        for user in users:
            # Access all scalar attributes that might be used by the UI
            user.id
            user.name
            user.username
            user.hashed_password
            user.is_active
            user.created_at
            user.updated_at
            
            # Handle relationships carefully
            try:
                # Access the roles relationship
                list(user.roles)  # Force load the roles
            except:
                pass
        return users

    def _extract_user_data(self, user: User) -> Dict[str, Any]:
        """Extract user data into a dictionary to prevent DetachedInstanceError."""
        return {
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'is_active': user.is_active,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'roles': [role.name for role in user.roles] if user.roles else []
        }

    @contextmanager
    def get_session(self):
        """Get a database session with proper cleanup and transaction management."""
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error, rolling back: {e}")
            raise
        finally:
            session.close()

    def health_check(self) -> tuple[bool, str]:
        """
        Perform a comprehensive database health check.
        
        Returns:
            tuple: (is_healthy: bool, status_message: str)
        """
        try:
            with self.get_session() as session:
                # Test 1: Basic connection
                connection = session.connection()
                if not connection:
                    return False, "Unable to establish database connection"
                
                # Test 2: Execute simple query to verify database is responsive
                result = session.execute(text("SELECT 1 as health_check")).fetchone()
                if not result or result[0] != 1:
                    return False, "Database is not responding correctly to queries"
                
                # Test 3: Check if critical tables exist and are accessible
                critical_tables = ['users', 'orders', 'products']
                for table in critical_tables:
                    try:
                        session.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    except Exception as table_error:
                        # Table might not exist during initial setup, log but don't fail
                        self.logger.warning(f"Table '{table}' not accessible: {table_error}")
                
                return True, "Database health check passed - all systems operational"
        
        except Exception as e:
            error_msg = f"Database health check failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    # User operations
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    self._load_user_attributes([user])
                    session.expunge_all()
                return user
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting user by ID {user_id}: {e}")
            raise DatabaseError(f"Failed to retrieve user: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting user by ID {user_id}: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    self._load_user_attributes([user])
                    session.expunge_all()
                return user
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting user by username {username}: {e}")
            raise DatabaseError(f"Failed to retrieve user: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting user by username {username}: {e}")
            return None

    def get_all_users(self) -> List[User]:
        """Get all users."""
        try:
            with self.get_session() as session:
                users = session.query(User).all()
                
                # Force load all attributes within the session
                self._load_user_attributes(users)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return users
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting all users: {e}")
            raise DatabaseError(f"Failed to retrieve users: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting all users: {e}")
            return []

    def create_user(self, palname: str, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Create a new user with the given credentials.
        
        Args:
            palname: The user's display name (must be unique)
            username: Username for the new user (must be unique)
            password: Plain text password
            
        Returns:
            Dictionary with user data or None if there was an error
        """
        try:
            with self.get_session() as session:
                # Check if username already exists
                existing_username = session.query(User).filter(User.username == username).first()
                if existing_username:
                    self.logger.warning(f"Username already exists: {username}")
                    return None
                    
                # Check if palname already exists
                existing_palname = session.query(User).filter(User.name == palname).first()
                if existing_palname:
                    self.logger.warning(f"Palname already exists: {palname}")
                    return None
                
                # Hash the password for secure storage
                hashed_password = password_service.hash_password(password)
                
                # Create the user
                user = User(
                    name=palname,
                    username=username,
                    hashed_password=hashed_password,
                    is_active=True
                )
                
                session.add(user)
                session.flush()  # Flush to get the ID before commit
                session.refresh(user)  # Refresh to get updated data
                
                # Extract user data before session closes to prevent DetachedInstanceError
                user_data = self._extract_user_data(user)
                
                self.logger.info(f"Created new user: {username} (Palname: {palname}) with ID: {user_data['id']}")
                return user_data
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error creating user {username}: {e}")
            raise DatabaseError(f"Failed to create user: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error creating user {username}: {e}")
            return None

    def update_user(self, user: User) -> Optional[User]:
        """Update an existing user.
        
        Args:
            user: User object to update
            
        Returns:
            Updated user object or None if error
        """
        try:
            with self.get_session() as session:
                # Merge the user object into the session
                merged_user = session.merge(user)
                session.flush()  # Flush to ensure changes are persisted
                session.refresh(merged_user)  # Refresh to get updated data
                return merged_user
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating user {user.id}: {e}")
            raise DatabaseError(f"Failed to update user: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error updating user {user.id}: {e}")
            return None

    def delete_user(self, user: User) -> bool:
        """Delete a user.
        
        Args:
            user: User object to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                # Get the user in this session
                user_to_delete = session.query(User).filter(User.id == user.id).first()
                if user_to_delete:
                    session.delete(user_to_delete)
                    return True
                else:
                    self.logger.warning(f"User {user.id} not found for deletion")
                    return False
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Database error deleting user {user.id}: {e}")
            raise DatabaseError(f"Failed to delete user: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error deleting user {user.id}: {e}")
            return False

    # Order operations
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get an order by ID."""
        try:
            with self.get_session() as session:
                order = session.query(Order).filter(Order.id == order_id).first()
                if order:
                    self._load_order_attributes([order])
                return order
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting order by ID {order_id}: {e}")
            raise DatabaseError(f"Failed to retrieve order: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting order by ID {order_id}: {e}")
            return None

    def get_order_by_external_id(self, external_id: str) -> Optional[Order]:
        """Get an order by external order ID."""
        try:
            with self.get_session() as session:
                order = session.query(Order).filter(Order.external_order_id == external_id).first()
                if order:
                    self._load_order_attributes([order])
                return order
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting order by external ID {external_id}: {e}")
            raise DatabaseError(f"Failed to retrieve order: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting order by external ID {external_id}: {e}")
            return None

    def get_orders_by_external_id(self, external_id: str) -> List[Order]:
        """Get all orders by external order ID (for duplicate checking)."""
        try:
            with self.get_session() as session:
                orders = session.query(Order).filter(Order.external_order_id == external_id).all()
                
                # Force load all attributes within the session
                self._load_order_attributes(orders)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return orders
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting orders by external ID {external_id}: {e}")
            raise DatabaseError(f"Failed to retrieve orders: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting orders by external ID {external_id}: {e}")
            return []

    def get_recent_orders_by_external_id(self, external_id: str, months_back: int = 2) -> List[Order]:
        """Get orders by external order ID from the last N months (for efficient duplicate checking)."""
        try:
            with self.get_session() as session:
                # Calculate date threshold (N months ago)
                from datetime import datetime, timedelta
                threshold_date = datetime.now() - timedelta(days=months_back * 30)
                
                orders = session.query(Order).filter(
                    Order.external_order_id == external_id,
                    Order.created_at >= threshold_date
                ).order_by(Order.created_at.desc()).all()
                
                # Force load all attributes within the session
                self._load_order_attributes(orders)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return orders
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting recent orders by external ID {external_id}: {e}")
            raise DatabaseError(f"Failed to retrieve recent orders: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting recent orders by external ID {external_id}: {e}")
            return []

    def get_order_by_external_id_and_invoice(self, external_id: str, invoice: str) -> Optional[Order]:
        """Get an order by external order ID and invoice combination."""
        try:
            with self.get_session() as session:
                order = session.query(Order).filter(
                    Order.external_order_id == external_id,
                    Order.invoice == invoice
                ).first()
                if order:
                    self._load_order_attributes([order])
                return order
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting order by external ID {external_id} and invoice {invoice}: {e}")
            raise DatabaseError(f"Failed to retrieve order: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting order by external ID {external_id} and invoice {invoice}: {e}")
            return None

    def get_all_orders(self) -> List[Order]:
        """Get all orders."""
        try:
            with self.get_session() as session:
                orders = session.query(Order).all()
                
                # Force load all attributes within the session
                self._load_order_attributes(orders)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return orders
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting all orders: {e}")
            raise DatabaseError(f"Failed to retrieve orders: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting all orders: {e}")
            return []

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get orders by status."""
        try:
            with self.get_session() as session:
                orders = session.query(Order).filter(Order.status == status).all()
                
                # Force load all attributes within the session
                self._load_order_attributes(orders)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return orders
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting orders by status {status}: {e}")
            raise DatabaseError(f"Failed to retrieve orders: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting orders by status {status}: {e}")
            return []

    def get_orders_by_status_all(self) -> List[Order]:
        """Get all orders regardless of status."""
        return self.get_all_orders()

    def create_order(self, order_data: Dict[str, Any]) -> Optional[Order]:
        """Create a new order."""
        try:
            with self.get_session() as session:
                order = Order(**order_data)
                session.add(order)
                session.flush()  # Flush to get the ID before commit
                session.refresh(order)  # Refresh to get updated data
                self.logger.info(f"Created new order: {order.external_order_id}")
                return order
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error creating order: {e}")
            raise DatabaseError(f"Failed to create order: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error creating order: {e}")
            return None

    def update_order(self, order: Order, order_data: Dict[str, Any]) -> Optional[Order]:
        """Update an existing order."""
        try:
            with self.get_session() as session:
                # Get the order in this session
                order_to_update = session.query(Order).filter(Order.id == order.id).first()
                if not order_to_update:
                    self.logger.warning(f"Order {order.id} not found for update")
                    return None
                
                # Update fields
                for key, value in order_data.items():
                    if hasattr(order_to_update, key):
                        setattr(order_to_update, key, value)
                
                # Update timestamp using the data dict to avoid direct assignment
                order_data['updated_at'] = datetime.now()
                setattr(order_to_update, 'updated_at', datetime.now())
                session.flush()  # Flush to ensure changes are persisted
                session.refresh(order_to_update)  # Refresh to get updated data
                return order_to_update
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating order {order.id}: {e}")
            raise DatabaseError(f"Failed to update order: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error updating order {order.id}: {e}")
            return None

    def update_order_status(self, order_id: int, status: OrderStatus) -> Optional[str]:
        """Update the status of an order and return the external_order_id to avoid session issues.
        
        Returns:
            external_order_id if successful, None if failed
        """
        try:
            with self.get_session() as session:
                order = session.query(Order).filter(Order.id == order_id).first()
                if order:
                    setattr(order, 'status', status)
                    setattr(order, 'updated_at', datetime.now())
                    external_order_id = str(order.external_order_id)  # Get the ID while session is active
                    session.flush()  # Flush to ensure changes are persisted
                    return external_order_id  # Return the ID instead of the object
                else:
                    self.logger.warning(f"Order {order_id} not found for status update")
                    return None
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating order status for order {order_id}: {e}")
            raise DatabaseError(f"Failed to update order status: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error updating order status for order {order_id}: {e}")
            return None

    def delete_order(self, order: Order) -> bool:
        """Delete an order.
        
        Args:
            order: Order object to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                # Get the order in this session
                order_to_delete = session.query(Order).filter(Order.id == order.id).first()
                if order_to_delete:
                    session.delete(order_to_delete)
                    return True
                else:
                    self.logger.warning(f"Order {order.id} not found for deletion")
                    return False
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Database error deleting order {order.id}: {e}")
            raise DatabaseError(f"Failed to delete order: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error deleting order {order.id}: {e}")
            return False

    def delete_order_by_id(self, order_id: int) -> Tuple[bool, str]:
        """Delete an order by ID.
        
        Args:
            order_id: Order ID to delete
            
        Returns:
            Tuple of (success: bool, order_number: str)
        """
        try:
            with self.get_session() as session:
                # Get the order in this session
                order_to_delete = session.query(Order).filter(Order.id == order_id).first()
                if order_to_delete:
                    # Get order number before deletion
                    order_number = str(order_to_delete.external_order_id)
                    session.delete(order_to_delete)
                    return True, order_number
                else:
                    self.logger.warning(f"Order {order_id} not found for deletion")
                    return False, ""
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Database error deleting order {order_id}: {e}")
            raise DatabaseError(f"Failed to delete order: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error deleting order {order_id}: {e}")
            return False, ""

    def get_recent_orders(self, limit: int = 20) -> List[Order]:
        """Get recent orders."""
        try:
            with self.get_session() as session:
                orders = session.query(Order).order_by(Order.created_at.desc()).limit(limit).all()
                
                # Force load all attributes within the session
                self._load_order_attributes(orders)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return orders
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting recent orders: {e}")
            raise DatabaseError(f"Failed to retrieve recent orders: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting recent orders: {e}")
            return []

    def search_orders(self, search_term: str) -> List[Order]:
        """Search for orders by customer name or order ID."""
        try:
            with self.get_session() as session:
                orders = session.query(Order).filter(
                    (Order.customer_name.like(f"%{search_term}%")) |
                    (Order.external_order_id.like(f"%{search_term}%"))
                ).all()
                
                # Force load all attributes within the session
                self._load_order_attributes(orders)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return orders
        except SQLAlchemyError as e:
            self.logger.error(f"Database error searching orders with term {search_term}: {e}")
            raise DatabaseError(f"Failed to search orders: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error searching orders with term {search_term}: {e}")
            return []

    def get_orders_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Get orders within a date range."""
        try:
            with self.get_session() as session:
                orders = session.query(Order).filter(
                    Order.order_date >= start_date,
                    Order.order_date <= end_date
                ).all()
                
                # Force load all attributes within the session
                self._load_order_attributes(orders)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return orders
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting orders by date range: {e}")
            raise DatabaseError(f"Failed to retrieve orders by date range: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting orders by date range: {e}")
            return []

    def get_orders_by_date(self, date) -> List[Order]:
        """Get orders for a specific date."""
        try:
            with self.get_session() as session:
                # Convert date to datetime range
                start_datetime = datetime.combine(date, time.min)
                end_datetime = datetime.combine(date, time.max)
                
                orders = session.query(Order).filter(
                    Order.order_date >= start_datetime,
                    Order.order_date <= end_datetime
                ).all()
                
                # Force load all attributes within the session
                self._load_order_attributes(orders)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return orders
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting orders by date {date}: {e}")
            raise DatabaseError(f"Failed to retrieve orders by date: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting orders by date {date}: {e}")
            return []

    def get_orders_not_exported(self) -> List[Order]:
        """Get all orders that haven't been exported to Excel yet."""
        try:
            with self.get_session() as session:
                orders = session.query(Order).filter(
                    Order.export_to_excel == False
                ).all()
                
                # Force load all attributes within the session
                self._load_order_attributes(orders)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return orders
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting orders not exported: {e}")
            raise DatabaseError(f"Failed to retrieve orders not exported: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting orders not exported: {e}")
            return []

    def get_next_pending_invoice_number(self) -> str:
        """Get the next available pending invoice number (pending00, pending01, etc.)."""
        try:
            with self.get_session() as session:
                # Get all pending invoice numbers that start with 'pending'
                pending_invoices = session.query(Order.invoice).filter(
                    Order.invoice.like('pending%')
                ).all()
                
                # Extract numbers from existing pending invoices
                used_numbers = set()
                for (invoice,) in pending_invoices:
                    if invoice and invoice.startswith('pending') and len(invoice) == 9:  # pending + 2 digits
                        try:
                            number = int(invoice[7:])  # Extract the number part
                            used_numbers.add(number)
                        except ValueError:
                            continue
                
                # Find the next available number (00-99)
                for i in range(100):
                    if i not in used_numbers:
                        return f"pending{i:02d}"
                
                # If all numbers 00-99 are used, start from a higher range
                return f"pending{len(used_numbers):02d}"
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting next pending invoice number: {e}")
            # Fallback to timestamp-based
            from datetime import datetime
            return f"T{datetime.now().strftime('%m%d%H%M')}"
        except Exception as e:
            self.logger.error(f"Unexpected error getting next pending invoice number: {e}")
            # Fallback to timestamp-based
            from datetime import datetime
            return f"T{datetime.now().strftime('%m%d%H%M')}"

    # Product operations
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        try:
            with self.get_session() as session:
                return session.query(Product).filter(Product.id == product_id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting product by ID {product_id}: {e}")
            raise DatabaseError(f"Failed to retrieve product: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting product by ID {product_id}: {e}")
            return None

    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by SKU."""
        try:
            with self.get_session() as session:
                return session.query(Product).filter(Product.sku == sku).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting product by SKU {sku}: {e}")
            raise DatabaseError(f"Failed to retrieve product: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting product by SKU {sku}: {e}")
            return None

    def get_all_products(self) -> List[Product]:
        """Get all products."""
        try:
            with self.get_session() as session:
                return session.query(Product).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting all products: {e}")
            raise DatabaseError(f"Failed to retrieve products: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting all products: {e}")
            return []

    def create_product(self, product_data: Dict[str, Any]) -> Optional[Product]:
        """Create a new product."""
        try:
            with self.get_session() as session:
                product = Product(**product_data)
                session.add(product)
                session.flush()  # Flush to get the ID before commit
                session.refresh(product)  # Refresh to get updated data
                return product
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error creating product: {e}")
            raise DatabaseError(f"Failed to create product: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error creating product: {e}")
            return None

    def update_product(self, product: Product) -> Optional[Product]:
        """Update an existing product."""
        try:
            with self.get_session() as session:
                merged_product = session.merge(product)
                session.flush()  # Flush to ensure changes are persisted
                session.refresh(merged_product)  # Refresh to get updated data
                return merged_product
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating product {product.id}: {e}")
            raise DatabaseError(f"Failed to update product: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error updating product {product.id}: {e}")
            return None

    def delete_product(self, product: Product) -> bool:
        """Delete a product."""
        try:
            with self.get_session() as session:
                product_to_delete = session.query(Product).filter(Product.id == product.id).first()
                if product_to_delete:
                    session.delete(product_to_delete)
                    return True
                else:
                    self.logger.warning(f"Product {product.id} not found for deletion")
                    return False
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Database error deleting product {product.id}: {e}")
            raise DatabaseError(f"Failed to delete product: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error deleting product {product.id}: {e}")
            return False

    # Shipping operations
    def create_shipping_label(self, label_data: Dict[str, Any]) -> Optional[ShippingLabel]:
        """Create a new shipping label."""
        try:
            with self.get_session() as session:
                label = ShippingLabel(**label_data)
                session.add(label)
                session.flush()  # Flush to get the ID before commit
                session.refresh(label)  # Refresh to get updated data
                return label
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error creating shipping label: {e}")
            raise DatabaseError(f"Failed to create shipping label: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error creating shipping label: {e}")
            return None

    def get_shipping_labels_for_order(self, order_id: int) -> List[ShippingLabel]:
        """Get shipping labels for an order."""
        try:
            with self.get_session() as session:
                return session.query(ShippingLabel).filter(ShippingLabel.order_id == order_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting shipping labels for order {order_id}: {e}")
            raise DatabaseError(f"Failed to retrieve shipping labels: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting shipping labels for order {order_id}: {e}")
            return []

    def create_packing_slip(self, slip_data: Dict[str, Any]) -> Optional[PackingSlip]:
        """Create a new packing slip."""
        try:
            with self.get_session() as session:
                slip = PackingSlip(**slip_data)
                session.add(slip)
                session.flush()  # Flush to get the ID before commit
                session.refresh(slip)  # Refresh to get updated data
                return slip
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error creating packing slip: {e}")
            raise DatabaseError(f"Failed to create packing slip: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error creating packing slip: {e}")
            return None

    def get_packing_slips_for_order(self, order_id: int) -> List[PackingSlip]:
        """Get packing slips for an order."""
        try:
            with self.get_session() as session:
                return session.query(PackingSlip).filter(PackingSlip.order_id == order_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting packing slips for order {order_id}: {e}")
            raise DatabaseError(f"Failed to retrieve packing slips: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting packing slips for order {order_id}: {e}")
            return []

    # Transaction methods (for batch operations)
    @contextmanager
    def batch_operation(self):
        """Context manager for batch database operations."""
        with self.get_session() as session:
            try:
                yield session
                # Commit happens automatically in get_session context manager
            except Exception as e:
                # Rollback happens automatically in get_session context manager
                self.logger.error(f"Batch operation failed: {e}")
                raise

    # MyACG Account operations
    def create_myacg_account(self, name: str, username: str, 
                           password: str, api_key: Optional[str] = None,
                           is_default: bool = False) -> Optional[MyACGAccount]:
        """Create a new MyACG account."""
        try:
            with self.get_session() as session:
                # Check if name already exists
                existing_account = session.query(MyACGAccount).filter(MyACGAccount.name == name).first()
                if existing_account:
                    self.logger.warning(f"MyACG account name already exists: {name}")
                    return None
                
                # If setting as default, unset all other defaults first
                if is_default:
                    self._unset_default_myacg_accounts_in_session(session)
                
                # Encrypt the password
                encrypted_password = password_service.encrypt_data(password)
                
                # Create the account
                account = MyACGAccount(
                    name=name,
                    username=username,
                    encrypted_password=encrypted_password,
                    api_key=api_key,
                    is_default=is_default,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                session.add(account)
                session.flush()  # Flush to get the ID before commit
                session.refresh(account)  # Refresh to get updated data
                
                self.logger.info(f"Created new MyACG account: {name}")
                return account
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error creating MyACG account {name}: {e}")
            raise DatabaseError(f"Failed to create MyACG account: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error creating MyACG account {name}: {e}")
            return None

    def _unset_default_myacg_accounts_in_session(self, session: Session) -> None:
        """Unset default flag for all MyACG accounts within a session."""
        try:
            accounts = session.query(MyACGAccount).filter(MyACGAccount.is_default == True).all()
            for account in accounts:
                setattr(account, 'is_default', False)
                setattr(account, 'updated_at', datetime.now())
        except Exception as e:
            self.logger.error(f"Error unsetting default MyACG accounts: {e}")
            raise

    def get_myacg_accounts(self) -> List[MyACGAccount]:
        """Get all MyACG accounts."""
        try:
            with self.get_session() as session:
                accounts = session.query(MyACGAccount).all()
                
                # Force load all attributes within the session
                self._load_myacg_account_attributes(accounts)
                
                # Expunge all objects to detach them from the session
                session.expunge_all()
                
                return accounts
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting MyACG accounts: {e}")
            raise DatabaseError(f"Failed to retrieve MyACG accounts: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting MyACG accounts: {e}")
            return []

    def get_myacg_account(self, account_id: int) -> Optional[MyACGAccount]:
        """Get a MyACG account by ID."""
        try:
            with self.get_session() as session:
                account = session.query(MyACGAccount).filter(MyACGAccount.id == account_id).first()
                if account:
                    self._load_myacg_account_attributes([account])
                    session.expunge_all()
                return account
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting MyACG account {account_id}: {e}")
            raise DatabaseError(f"Failed to retrieve MyACG account: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting MyACG account {account_id}: {e}")
            return None

    def get_default_myacg_account(self) -> Optional[MyACGAccount]:
        """Get the default MyACG account."""
        try:
            with self.get_session() as session:
                account = session.query(MyACGAccount).filter(MyACGAccount.is_default == True).first()
                if account:
                    self._load_myacg_account_attributes([account])
                    session.expunge_all()
                return account
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting default MyACG account: {e}")
            raise DatabaseError(f"Failed to retrieve default MyACG account: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting default MyACG account: {e}")
            return None

    def update_myacg_account(self, account_id: int, data: Dict[str, Any]) -> Optional[MyACGAccount]:
        """Update a MyACG account."""
        try:
            with self.get_session() as session:
                account = session.query(MyACGAccount).filter(MyACGAccount.id == account_id).first()
                if not account:
                    self.logger.warning(f"MyACG account {account_id} not found")
                    return None
                
                # Handle password specially
                if 'password' in data:
                    setattr(account, 'encrypted_password', password_service.encrypt_data(data['password']))
                    del data['password']
                
                # Handle default flag specially
                if 'is_default' in data:
                    if data['is_default']:
                        # Setting this account as default - unset all others first
                        self._unset_default_myacg_accounts_in_session(session)
                        setattr(account, 'is_default', True)
                    else:
                        # Setting this account as NOT default
                        setattr(account, 'is_default', False)
                    del data['is_default']  # Remove from data to avoid duplicate setting
                
                # Update other fields
                for key, value in data.items():
                    if hasattr(account, key):
                        setattr(account, key, value)
                
                # Update timestamp
                setattr(account, 'updated_at', datetime.now())
                
                session.flush()  # Flush to ensure changes are persisted
                session.refresh(account)  # Refresh to get updated data
                
                self.logger.info(f"Updated MyACG account {account_id}")
                return account
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating MyACG account {account_id}: {e}")
            raise DatabaseError(f"Failed to update MyACG account: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error updating MyACG account {account_id}: {e}")
            return None

    def delete_myacg_account(self, account_id: int) -> bool:
        """Delete a MyACG account."""
        try:
            with self.get_session() as session:
                account = session.query(MyACGAccount).filter(MyACGAccount.id == account_id).first()
                if account:
                    session.delete(account)
                    self.logger.info(f"Deleted MyACG account {account_id}")
                    return True
                else:
                    self.logger.warning(f"MyACG account {account_id} not found for deletion")
                    return False
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Database error deleting MyACG account {account_id}: {e}")
            raise DatabaseError(f"Failed to delete MyACG account: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error deleting MyACG account {account_id}: {e}")
            return False

    def decrypt_myacg_password(self, account_id: int) -> Optional[str]:
        """Decrypt and return the password for a MyACG account."""
        try:
            with self.get_session() as session:
                account = session.query(MyACGAccount).filter(MyACGAccount.id == account_id).first()
                if account is not None and getattr(account, 'encrypted_password', None) is not None:
                    try:
                        return password_service.decrypt_data(getattr(account, 'encrypted_password'))
                    except Exception as decrypt_error:
                        self.logger.error(f"Failed to decrypt password for account {account_id}: {decrypt_error}")
                        return None
                else:
                    self.logger.warning(f"MyACG account {account_id} not found or has no password")
                    return None
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting MyACG account password {account_id}: {e}")
            raise DatabaseError(f"Failed to retrieve MyACG account password: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting MyACG account password {account_id}: {e}")
            return None

    def get_myacg_account_by_name(self, name: str) -> Optional[MyACGAccount]:
        """Get a MyACG account by name."""
        try:
            with self.get_session() as session:
                account = session.query(MyACGAccount).filter(MyACGAccount.name == name).first()
                if account:
                    self._load_myacg_account_attributes([account])
                    session.expunge_all()
                return account
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting MyACG account by name {name}: {e}")
            raise DatabaseError(f"Failed to retrieve MyACG account: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting MyACG account by name {name}: {e}")
            return None

    def cleanup(self):
        """Cleanup database resources on application shutdown."""
        try:
            # Close any remaining connections in the connection pool
            from packing_elf.models.database import engine
            engine.dispose()
            self.logger.info("Database cleanup completed successfully")
        except Exception as e:
            self.logger.error(f"Error during database cleanup: {e}")

    def execute_raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL and return results as list of dictionaries.
        
        Args:
            sql: SQL query string
            params: Optional parameters for the query
            
        Returns:
            List of dictionaries representing the query results
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(sql), params or {})
                
                # Convert result to list of dictionaries
                try:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in result.fetchall()]
                except Exception:
                    # If result doesn't have rows, return empty list
                    return []
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Database error executing raw SQL: {e}")
            raise DatabaseError(f"Failed to execute SQL: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error executing raw SQL: {e}")
            return []

    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information for debugging.
        
        Returns:
            Dictionary containing connection information
        """
        try:
            with self.get_session() as session:
                connection = session.connection()
                password = connection.engine.url.password
                safe_password = '***' if password else ''
                info = {
                    'database_url': str(connection.engine.url).replace(
                        password or '', safe_password
                    ),
                    'dialect': connection.dialect.name,
                    'driver': connection.dialect.driver,
                    'is_connected': True
                }
                return info
        except Exception as e:
            self.logger.error(f"Error getting connection info: {e}")
            return {
                'database_url': 'Unknown',
                'dialect': 'Unknown',
                'driver': 'Unknown',
                'is_connected': False,
                'error': str(e)
            }


class DatabaseConnectionManager:
    """Manages database connections with dynamic IP discovery and fallback modes."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_file = Path.home() / ".packing_elf" / "db_config.json"
        self.connection = None
        self.is_connected = False
        self.host_ip = None
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
    def load_saved_config(self) -> Optional[Dict[str, Any]]:
        """Load saved database configuration."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load saved config: {e}")
        return None
    
    def save_config(self, host_ip: str, port: int = 3306, 
                   user: str = "root", password: str = "Meridian0723",
                   database: str = "MyACG_data"):
        """Save database configuration for future use."""
        config = {
            "host": host_ip,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "last_updated": str(socket.gethostbyname(socket.gethostname()))
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Saved database config for host: {host_ip}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def test_connection(self, host_ip: str, **kwargs) -> bool:
        """Test if a database connection works with given host IP."""
        try:
            # Add timeout to prevent hanging
            connection_kwargs = kwargs.copy()
            connection_kwargs['connect_timeout'] = 3  # 3 second timeout
            
            if MYSQL_AVAILABLE:
                test_conn = mysql.connector.connect(
                    host=host_ip,
                    **connection_kwargs
                )
                test_conn.close()
            else:
                # Fallback to pymysql
                import pymysql
                test_conn = pymysql.connect(
                    host=host_ip,
                    **connection_kwargs
                )
                test_conn.close()
            return True
        except Exception as e:
            self.logger.warning(f"Connection test failed for {host_ip}: {e}")
            return False
    
    def discover_host_ip(self) -> Optional[str]:
        """Try to discover the host IP using multiple methods."""
        try:
            # Set default credentials for testing
            default_credentials = {
                "user": "root",
                "password": "Meridian0723",
                "database": "MyACG_data",
                "port": 3306
            }
            
            # Method 1: Try discovery service (if running on host)
            discovered_ip = self._try_discovery_service()
            if discovered_ip:
                self.logger.info(f"Discovered host via discovery service: {discovered_ip}")
                return discovered_ip
            
            # Method 2: Try common local network ranges
            common_ranges = [
                "192.168.1.100", "192.168.1.101", "192.168.1.102",
                "192.168.0.100", "192.168.0.101", "192.168.0.102",
                "10.0.0.100", "10.0.0.101", "10.0.0.102"
            ]
            
            for ip in common_ranges:
                if self.test_connection(ip, **default_credentials):
                    self.logger.info(f"Discovered host at: {ip}")
                    return ip
            
            # Method 3: Try saved config
            saved_config = self.load_saved_config()
            if saved_config and self.test_connection(saved_config["host"], **default_credentials):
                self.logger.info(f"Using saved host: {saved_config['host']}")
                return saved_config["host"]
            
            return None
        except Exception as e:
            self.logger.error(f"Error during host discovery: {e}")
            return None
    
    def _try_discovery_service(self) -> Optional[str]:
        """Try to discover host using the discovery service."""
        try:
            import urllib.request
            import json
            
            # Try common discovery service ports
            discovery_ports = [8080, 8081, 8082]
            
            # First try localhost (same machine)
            for port in discovery_ports:
                try:
                    url = f"http://localhost:{port}/discover"
                    with urllib.request.urlopen(url, timeout=2) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            server_ip = data.get('server_ip')
                            if server_ip:
                                self.logger.info(f"Found discovery service on localhost:{port}")
                                return server_ip
                except Exception:
                    continue
            
            # If localhost didn't work, try a limited set of common IPs
            # Only try a few common IPs to avoid long timeouts
            common_ips = [
                "192.168.1.100", "192.168.1.101", "192.168.1.102", "192.168.1.103",
                "192.168.0.100", "192.168.0.101", "192.168.0.102", "192.168.0.103",
                "10.0.0.100", "10.0.0.101", "10.0.0.102", "10.0.0.103"
            ]
            
            for ip in common_ips:
                for port in discovery_ports:
                    try:
                        url = f"http://{ip}:{port}/discover"
                        with urllib.request.urlopen(url, timeout=1) as response:
                            if response.status == 200:
                                data = json.loads(response.read().decode('utf-8'))
                                server_ip = data.get('server_ip')
                                if server_ip:
                                    self.logger.info(f"Found discovery service at {ip}:{port}")
                                    return server_ip
                    except Exception:
                        continue
                            
        except Exception as e:
            self.logger.debug(f"Discovery service not available: {e}")
        
        return None
    
    def connect(self, host_ip: Optional[str] = None, **kwargs) -> bool:
        """Connect to database with fallback options."""
        # Set default credentials if not provided
        default_credentials = {
            "user": "root",
            "password": "Meridian0723",
            "database": "MyACG_data",
            "port": 3306
        }
        
        # Update with provided kwargs, keeping defaults for missing values
        connection_params = default_credentials.copy()
        connection_params.update(kwargs)
        
        if host_ip:
            # User provided IP - test and use it
            if self.test_connection(host_ip, **connection_params):
                self.host_ip = host_ip
                self.save_config(host_ip, **connection_params)
                return self._establish_connection(host_ip, **connection_params)
            else:
                return False
        
        # Try to discover host IP
        discovered_ip = self.discover_host_ip()
        if discovered_ip:
            # Remove 'host' from kwargs if it exists to avoid duplicate parameter
            connection_params.pop('host', None)  # Remove host if present
            return self._establish_connection(discovered_ip, **connection_params)
        
        # No connection possible
        self.is_connected = False
        return False
    
    def _establish_connection(self, host_ip: str, **kwargs) -> bool:
        """Establish the actual database connection."""
        try:
            # Add timeout to prevent hanging
            connection_kwargs = kwargs.copy()
            connection_kwargs['connect_timeout'] = 10  # 10 second timeout for main connection
            
            if MYSQL_AVAILABLE:
                self.connection = mysql.connector.connect(
                    host=host_ip,
                    **connection_kwargs
                )
            else:
                # Fallback to pymysql
                import pymysql
                self.connection = pymysql.connect(
                    host=host_ip,
                    **connection_kwargs
                )
            
            self.is_connected = True
            self.host_ip = host_ip
            self.logger.info(f"Successfully connected to database at {host_ip}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            self.is_connected = False
            return False
    
    def get_connection(self):
        """Get the current database connection."""
        return self.connection
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.is_connected = False

# Global instance
db_connection_manager = DatabaseConnectionManager()

# Singleton instance for the application
db_service = DatabaseService()