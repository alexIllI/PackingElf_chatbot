#!/usr/bin/env python3
"""
Packing Elf Database Setup Script
Complete database setup solution for non-technical users.

This script will:
1. Check MySQL installation and configuration
2. Create the database and user
3. Set up all tables and initial data
4. Configure MySQL for remote access
5. Test the connection

Usage: python setup_database.py
"""

import os
import sys
import subprocess
import sqlite3
import json
import logging
import time
from pathlib import Path

# Try to import required packages
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("✗ mysql-connector-python not installed")
    print("  Please run: install_dependencies.bat")
    print("  Or run: troubleshoot_mysql.bat")

try:
    import cryptography
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    print("✗ cryptography not installed")
    print("  Please run: install_dependencies.bat")
    print("  Or run: troubleshoot_mysql.bat")

try:
    import appdirs
    APPDIRS_AVAILABLE = True
except ImportError:
    APPDIRS_AVAILABLE = False
    print("✗ appdirs not installed")
    print("  Please run: install_dependencies.bat")
    print("  Or run: troubleshoot_mysql.bat")

# Configure logging
log_dir = Path.home() / ".packing_elf" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / "database_setup.log")
    ]
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self):
        self.db_name = "MyACG_data"
        self.db_user = "root"
        self.db_password = "Meridian0723"
        self.db_host = "localhost"
        self.db_port = 3306
        
        # Configuration file
        self.config_file = Path.home() / ".packing_elf" / "db_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
    def print_banner(self):
        """Print setup banner."""
        print("=" * 60)
        print("Packing Elf Database Setup")
        print("=" * 60)
        print("This script will set up your database for Packing Elf.")
        print("Make sure MySQL is installed and running.")
        print("=" * 60)
        print()
        
    def try_mysql_connection(self, host, user, password, database=None, auth_plugin=None):
        """Try to connect to MySQL with different parameters."""
        try:
            connection_params = {
                "host": host,
                "port": self.db_port,
                "user": user,
                "password": password,
                "connect_timeout": 10
            }
            
            if database:
                connection_params["database"] = database
                
            if auth_plugin:
                connection_params["auth_plugin"] = auth_plugin
                
            connection = mysql.connector.connect(**connection_params)
            connection.close()
            return True, None
        except mysql.connector.Error as e:
            return False, e
            
    def fix_mysql_authentication(self):
        """Try to fix MySQL authentication issues."""
        logger.info("Attempting to fix MySQL authentication...")
        print("Attempting to fix MySQL authentication...")
        
        # Try different connection methods
        connection_methods = [
            ("localhost", "root", "Meridian0723"),
            ("127.0.0.1", "root", "Meridian0723"),
            ("localhost", "root", ""),  # Try empty password
        ]
        
        working_connection = None
        
        for host, user, password in connection_methods:
            success, error = self.try_mysql_connection(host, user, password)
            if success:
                working_connection = (host, user, password)
                logger.info(f"Found working connection: {user}@{host}")
                break
                
        if not working_connection:
            logger.error("No working MySQL connection found")
            print("✗ No working MySQL connection found")
            return False
            
        # Try to fix authentication for the root user
        try:
            host, user, password = working_connection
            connection = mysql.connector.connect(
                host=host,
                port=self.db_port,
                user=user,
                password=password
            )
            cursor = connection.cursor()
            
            # Update root user authentication
            try:
                cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Meridian0723'")
                logger.info("Updated root@localhost authentication")
            except:
                pass
                
            try:
                cursor.execute("ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Meridian0723'")
                logger.info("Updated root@% authentication")
            except:
                pass
                
            # Create root user for % if it doesn't exist
            try:
                cursor.execute("CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Meridian0723'")
                logger.info("Created root@% user")
            except:
                pass
                
            # Grant privileges
            try:
                cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost'")
                cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'root'@'%'")
                cursor.execute("FLUSH PRIVILEGES")
                logger.info("Granted privileges to root users")
            except:
                pass
                
            cursor.close()
            connection.close()
            
            logger.info("MySQL authentication fixed")
            print("✓ MySQL authentication fixed")
            return True
            
        except Exception as e:
            logger.error(f"Error fixing authentication: {e}")
            print(f"✗ Error fixing authentication: {e}")
            return False
        
    def check_mysql_installation(self):
        """Check if MySQL is installed and accessible."""
        logger.info("Checking MySQL installation...")
        print("Checking MySQL installation...")
        
        # First, try the standard connection
        success, error = self.try_mysql_connection(
            self.db_host, 
            self.db_user, 
            self.db_password
        )
        
        if success:
            logger.info("MySQL connection successful")
            print("✓ MySQL is installed and accessible")
            return True
            
        # If standard connection fails, try to fix authentication
        if error and error.errno == 1045:  # Access denied
            logger.info("MySQL access denied, attempting to fix authentication...")
            print("MySQL access denied, attempting to fix authentication...")
            
            if self.fix_mysql_authentication():
                # Try connection again after fixing
                success, error = self.try_mysql_connection(
                    self.db_host, 
                    self.db_user, 
                    self.db_password
                )
                if success:
                    logger.info("MySQL connection successful after authentication fix")
                    print("✓ MySQL is installed and accessible")
                    return True
                    
        # If still failing, provide detailed error information
        if error:
            if error.errno == 1045:  # Access denied
                logger.error("MySQL access denied. Please check username/password.")
                print("✗ MySQL access denied. Please check username/password.")
                print("  Default: username=root, password=Meridian0723")
                print("  Try running: mysql -u root -p")
            elif error.errno == 2003:  # Can't connect
                logger.error("Cannot connect to MySQL. Is it running?")
                print("✗ Cannot connect to MySQL. Please ensure MySQL is running.")
                print("  Try starting MySQL service or check if MySQL is installed.")
            else:
                logger.error(f"MySQL error: {error}")
                print(f"✗ MySQL error: {error}")
                
        return False
                
    def create_database(self):
        """Create the database if it doesn't exist."""
        logger.info("Creating database...")
        print("Creating database...")
        
        try:
            # Connect without specifying database
            connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password
            )
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            logger.info(f"Database '{self.db_name}' created/verified")
            print(f"✓ Database '{self.db_name}' created/verified")
            
            cursor.close()
            connection.close()
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Error creating database: {e}")
            print(f"✗ Error creating database: {e}")
            return False
            
    def setup_remote_access(self):
        """Configure MySQL for remote access."""
        logger.info("Setting up remote access...")
        print("Setting up remote access...")
        
        try:
            connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            cursor = connection.cursor()
            
            # Create user for remote access
            cursor.execute(f"CREATE USER IF NOT EXISTS '{self.db_user}'@'%' IDENTIFIED BY '{self.db_password}'")
            cursor.execute(f"GRANT ALL PRIVILEGES ON {self.db_name}.* TO '{self.db_user}'@'%'")
            cursor.execute("FLUSH PRIVILEGES")
            
            logger.info("Remote access configured")
            print("✓ Remote access configured")
            
            cursor.close()
            connection.close()
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Error setting up remote access: {e}")
            print(f"✗ Error setting up remote access: {e}")
            return False
            
    def create_tables(self):
        """Create all database tables."""
        logger.info("Creating database tables...")
        print("Creating database tables...")
        
        try:
            # Import SQLAlchemy components
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from packing_elf.models.database import engine, SessionLocal
            from packing_elf.models import Base
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            
            logger.info("Database tables created successfully")
            print("✓ Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            print(f"✗ Error creating tables: {e}")
            return False
            
    def create_initial_data(self):
        """Create initial roles and admin user."""
        logger.info("Creating initial data...")
        print("Creating initial data...")
        
        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from packing_elf.models.database import SessionLocal
            from packing_elf.models import User, Role
            from packing_elf.services.password_service import password_service
            
            session = SessionLocal()
            
            # Create roles
            roles = [
                {"name": "Administrator", "description": "Full system access"},
                {"name": "Manager", "description": "Manage orders and accounts"},
                {"name": "StaffUser", "description": "Basic order operations"}
            ]
            
            for role_data in roles:
                existing_role = session.query(Role).filter(Role.name == role_data["name"]).first()
                if not existing_role:
                    role = Role(**role_data)
                    session.add(role)
                    logger.info(f"Created role: {role_data['name']}")
            
            session.commit()
            
            # Create admin user if no users exist
            users = session.query(User).all()
            if not users:
                admin_user = User(
                    name="Administrator",
                    username="admin",
                    hashed_password=password_service.hash_password("PackingElf2023"),
                    is_active=True
                )
                session.add(admin_user)
                session.commit()
                
                # Assign administrator role
                admin_role = session.query(Role).filter(Role.name == "Administrator").first()
                if admin_role:
                    admin_user.roles.append(admin_role)
                    session.commit()
                
                logger.info("Created admin user: admin/PackingElf2023")
                print("✓ Created admin user: admin/PackingElf2023")
            
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating initial data: {e}")
            print(f"✗ Error creating initial data: {e}")
            return False
            
    def save_configuration(self):
        """Save database configuration for the application."""
        logger.info("Saving configuration...")
        print("Saving configuration...")
        
        try:
            config = {
                "host": self.db_host,
                "port": self.db_port,
                "user": self.db_user,
                "password": self.db_password,
                "database": self.db_name
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Configuration saved")
            print("✓ Configuration saved")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            print(f"✗ Error saving configuration: {e}")
            return False
            
    def test_connection(self):
        """Test the final database connection."""
        logger.info("Testing final connection...")
        print("Testing final connection...")
        
        try:
            connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            connection.close()
            
            logger.info("Final connection test successful")
            print("✓ Final connection test successful")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Final connection test failed: {e}")
            print(f"✗ Final connection test failed: {e}")
            return False
            
    def check_dependencies(self):
        """Check if all required dependencies are installed."""
        if not MYSQL_AVAILABLE or not CRYPTOGRAPHY_AVAILABLE or not APPDIRS_AVAILABLE:
            print("✗ Missing required dependencies")
            print("Please run: install_dependencies.bat")
            print("Or run: troubleshoot_mysql.bat")
            return False
        return True
        
    def run_setup(self):
        """Run the complete setup process."""
        self.print_banner()
        
        # Check dependencies first
        if not self.check_dependencies():
            return False
        
        steps = [
            ("Checking MySQL installation", self.check_mysql_installation),
            ("Creating database", self.create_database),
            ("Setting up remote access", self.setup_remote_access),
            ("Creating tables", self.create_tables),
            ("Creating initial data", self.create_initial_data),
            ("Saving configuration", self.save_configuration),
            ("Testing connection", self.test_connection)
        ]
        
        success = True
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                success = False
                break
            time.sleep(0.5)  # Small delay for better UX
            
        print("\n" + "=" * 60)
        if success:
            print("✓ Database setup completed successfully!")
            print("\nYour database is ready to use.")
            print("Default admin credentials:")
            print("  Username: admin")
            print("  Password: PackingElf2023")
            print("\nYou can now start the Packing Elf application.")
        else:
            print("✗ Database setup failed. Please check the logs.")
            print("Log file: " + str(log_dir / "database_setup.log"))
            
        print("=" * 60)
        return success

def main():
    """Main function."""
    setup = DatabaseSetup()
    success = setup.run_setup()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 