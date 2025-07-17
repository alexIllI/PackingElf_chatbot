"""
Configuration validator for ChatGLM3 Discord Bot
Validates environment, dependencies, and configuration before startup
"""

import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import mysql.connector
from dotenv import load_dotenv

class ConfigValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.load_dotenv()
        
    def load_dotenv(self):
        """Load environment variables"""
        load_dotenv()
        
    def validate_python_version(self) -> bool:
        """Validate Python version"""
        if sys.version_info < (3, 10):
            self.errors.append("Python 3.10+ is required")
            return False
        return True
    
    def validate_dependencies(self) -> bool:
        """Validate required Python packages"""
        required_packages = [
            'discord',
            'mysql.connector',
            'gpt4all',
            'dotenv',
            'psutil'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.errors.append(f"Missing required packages: {', '.join(missing_packages)}")
            return False
        return True
    
    def validate_env_variables(self) -> bool:
        """Validate required environment variables"""
        required_vars = [
            'DISCORD_TOKEN',
            'MYSQL_HOST',
            'MYSQL_USER',
            'MYSQL_PASSWORD',
            'MYSQL_DATABASE',
            'MODEL_PATH'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.errors.append(f"Missing environment variables: {', '.join(missing_vars)}")
            return False
        return True
    
    def validate_database_connection(self) -> bool:
        """Test database connection"""
        try:
            connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST'),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                database=os.getenv('MYSQL_DATABASE'),
                port=int(os.getenv('MYSQL_PORT', 3306))
            )
            connection.close()
            return True
        except Exception as e:
            self.errors.append(f"Database connection failed: {e}")
            return False
    
    def validate_model_file(self) -> bool:
        """Validate AI model file exists"""
        model_path = os.getenv('MODEL_PATH')
        if not model_path:
            self.errors.append("MODEL_PATH not set")
            return False
        
        if not os.path.exists(model_path):
            self.errors.append(f"Model file not found: {model_path}")
            return False
        
        # Check file size (should be several GB)
        file_size = os.path.getsize(model_path) / (1024**3)  # GB
        if file_size < 1:
            self.warnings.append(f"Model file seems small ({file_size:.2f} GB), may be corrupted")
        
        return True
    
    def validate_directories(self) -> bool:
        """Validate and create necessary directories"""
        directories = ['logs', 'models', 'startup']
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        return True
    
    def validate_discord_token(self) -> bool:
        """Basic Discord token validation"""
        token = os.getenv('DISCORD_TOKEN')
        if not token or token == 'your_discord_bot_token_here':
            self.errors.append("Invalid Discord token")
            return False
        return True
    
    def validate_permissions(self) -> bool:
        """Validate file and directory permissions"""
        try:
            # Test write permissions for logs
            log_file = Path('logs/test.log')
            log_file.write_text('test')
            log_file.unlink()
        except Exception as e:
            self.errors.append(f"Permission error: {e}")
            return False
        return True
    
    def get_system_info(self) -> Dict:
        """Get system information for debugging"""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_free_gb': round(psutil.disk_usage('.').free / (1024**3), 2)
        }
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validations"""
        print("🔍 Validating configuration...")
        
        # System checks
        self.validate_python_version()
        self.validate_dependencies()
        self.validate_permissions()
        
        # Configuration checks
        self.validate_env_variables()
        self.validate_discord_token()
        
        # Resource checks
        self.validate_directories()
        self.validate_model_file()
        self.validate_database_connection()
        
        # System info
        system_info = self.get_system_info()
        print(f"💻 System: {system_info['platform']}")
        print(f"🐍 Python: {system_info['python_version']}")
        print(f"🖥️  CPU: {system_info['cpu_count']} cores")
        print(f"💾 Memory: {system_info['memory_gb']} GB")
        print(f"💿 Free disk: {system_info['disk_free_gb']} GB")
        
        return len(self.errors) == 0, self.errors, self.warnings

def main():
    """Main validation function"""
    validator = ConfigValidator()
    is_valid, errors, warnings = validator.validate_all()
    
    print("\n" + "="*50)
    
    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
        print()
    
    if errors:
        print("❌ Errors found:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease fix the errors above before starting the bot.")
        return False
    else:
        print("✅ All validations passed!")
        print("🚀 Bot is ready to start!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 