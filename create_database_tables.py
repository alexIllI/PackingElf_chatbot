#!/usr/bin/env python3
"""
Simple Database Table Creation Script for Packing Elf Bot
Creates the necessary tables for the Discord bot to work with.
"""

import mysql.connector
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_tables():
    """Create all necessary database tables for the bot."""
    
    # Database connection parameters
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'Meridian0723',
        'database': 'MyACG_data',
        'charset': 'utf8mb4'
    }
    
    try:
        # Connect to database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        logger.info("Connected to database successfully")
        
        # Create tables
        tables = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                profile_picture VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            
            # Roles table
            """
            CREATE TABLE IF NOT EXISTS roles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                description VARCHAR(255)
            )
            """,
            
            # User roles association table
            """
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INT,
                role_id INT,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
            )
            """,
            
            # MyACG accounts table
            """
            CREATE TABLE IF NOT EXISTS myacg_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                username VARCHAR(50) NOT NULL,
                encrypted_password VARCHAR(255) NOT NULL,
                api_key VARCHAR(255),
                is_default BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            
            # Products table
            """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(50) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                cost DECIMAL(10,2),
                stock_quantity INT DEFAULT 0,
                low_stock_threshold INT DEFAULT 5,
                is_active BOOLEAN DEFAULT TRUE,
                category ENUM('mizuki', 'seki', 'hibiki', 'ksp', 'rei', 'kirali', 'yuzumi', 'meridian', 'sakuro', 'oboro', 'yoruno', 'iruni', 'itsuki', 'other') DEFAULT 'other',
                image_path VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            
            # Orders table
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                external_order_id VARCHAR(10) UNIQUE,
                invoice VARCHAR(10) UNIQUE,
                coupon VARCHAR(30) DEFAULT 'none',
                status ENUM('processing', 'pending', 'shipped', 'delivered', 'cancelled', 'closed', 'returned') DEFAULT 'processing',
                customer_name VARCHAR(30),
                payment_method VARCHAR(20),
                shipping_cost DECIMAL(10,2) DEFAULT 0.0,
                total DECIMAL(10,2) NOT NULL,
                order_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_by_id INT,
                myacg_account_id INT,
                notes TEXT,
                export_to_excel BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (created_by_id) REFERENCES users(id),
                FOREIGN KEY (myacg_account_id) REFERENCES myacg_accounts(id)
            )
            """,
            
            # Order products association table
            """
            CREATE TABLE IF NOT EXISTS order_products (
                order_id INT,
                product_id INT,
                quantity INT DEFAULT 1,
                unit_price DECIMAL(10,2),
                PRIMARY KEY (order_id, product_id),
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
            """,
            
            # Shipping labels table
            """
            CREATE TABLE IF NOT EXISTS shipping_labels (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                label_data TEXT NOT NULL,
                tracking_number VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )
            """,
            
            # Packing slips table
            """
            CREATE TABLE IF NOT EXISTS packing_slips (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                slip_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )
            """
        ]
        
        # Execute table creation
        for i, table_sql in enumerate(tables, 1):
            try:
                cursor.execute(table_sql)
                logger.info(f"Created table {i}/{len(tables)}")
            except mysql.connector.Error as e:
                if e.errno == 1050:  # Table already exists
                    logger.info(f"Table {i}/{len(tables)} already exists")
                else:
                    logger.error(f"Error creating table {i}: {e}")
                    raise
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_orders_external_id ON orders(external_order_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_invoice ON orders(invoice)",
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
            "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_name)",
            "CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)",
            "CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_myacg_name ON myacg_accounts(name)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except mysql.connector.Error as e:
                if e.errno != 1061:  # Index already exists
                    logger.warning(f"Index creation warning: {e}")
        
        # Insert initial data
        insert_initial_data(cursor)
        
        connection.commit()
        logger.info("Database tables created successfully!")
        
        cursor.close()
        connection.close()
        
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def insert_initial_data(cursor):
    """Insert initial data into the database."""
    
    # Insert default roles
    roles = [
        ("Administrator", "Full system access"),
        ("Manager", "Manage orders and accounts"),
        ("StaffUser", "Basic order operations")
    ]
    
    for role_name, description in roles:
        try:
            cursor.execute(
                "INSERT IGNORE INTO roles (name, description) VALUES (%s, %s)",
                (role_name, description)
            )
        except mysql.connector.Error as e:
            logger.warning(f"Role insertion warning: {e}")
    
    # Insert admin user if no users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        try:
            # Simple password hash for demo (in production, use proper hashing)
            admin_password = "PackingElf2023"
            cursor.execute(
                "INSERT INTO users (name, username, hashed_password, is_active) VALUES (%s, %s, %s, %s)",
                ("Administrator", "admin", admin_password, True)
            )
            
            # Assign administrator role
            cursor.execute("SELECT id FROM roles WHERE name = 'Administrator'")
            admin_role_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin_user_id = cursor.fetchone()[0]
            
            cursor.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                (admin_user_id, admin_role_id)
            )
            
            logger.info("Created admin user: admin/PackingElf2023")
            
        except mysql.connector.Error as e:
            logger.warning(f"Admin user creation warning: {e}")
    
    # Insert sample products
    sample_products = [
        ("MIZ001", "Mizuki Sample Product 1", "Sample product for Mizuki category", 29.99, 15.00, 100, "mizuki"),
        ("SEK001", "Seki Sample Product 1", "Sample product for Seki category", 39.99, 20.00, 50, "seki"),
        ("HIB001", "Hibiki Sample Product 1", "Sample product for Hibiki category", 49.99, 25.00, 75, "hibiki"),
        ("KSP001", "KSP Sample Product 1", "Sample product for KSP category", 19.99, 10.00, 200, "ksp"),
        ("REI001", "Rei Sample Product 1", "Sample product for Rei category", 34.99, 18.00, 60, "rei")
    ]
    
    for sku, name, description, price, cost, stock, category in sample_products:
        try:
            cursor.execute(
                "INSERT IGNORE INTO products (sku, name, description, price, cost, stock_quantity, category) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (sku, name, description, price, cost, stock, category)
            )
        except mysql.connector.Error as e:
            logger.warning(f"Product insertion warning: {e}")
    
    # Insert sample orders
    sample_orders = [
        ("ORD001", "INV001", "processing", "張三", "credit_card", 5.00, 34.99, "2024-01-15 10:30:00"),
        ("ORD002", "INV002", "shipped", "李四", "paypal", 5.00, 44.99, "2024-01-16 14:20:00"),
        ("ORD003", "INV003", "pending", "王五", "credit_card", 0.00, 19.99, "2024-01-17 09:15:00")
    ]
    
    for ext_id, invoice, status, customer, payment, shipping, total, order_date in sample_orders:
        try:
            cursor.execute(
                "INSERT IGNORE INTO orders (external_order_id, invoice, status, customer_name, payment_method, shipping_cost, total, order_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (ext_id, invoice, status, customer, payment, shipping, total, order_date)
            )
        except mysql.connector.Error as e:
            logger.warning(f"Order insertion warning: {e}")

def main():
    """Main function."""
    print("=" * 60)
    print("Packing Elf Bot Database Setup")
    print("=" * 60)
    
    success = create_database_tables()
    
    if success:
        print("✓ Database setup completed successfully!")
        print("\nDefault admin credentials:")
        print("  Username: admin")
        print("  Password: PackingElf2023")
        print("\nSample data has been created for testing.")
    else:
        print("✗ Database setup failed. Please check the logs.")
    
    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 