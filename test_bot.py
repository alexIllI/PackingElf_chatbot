#!/usr/bin/env python3
"""
Test script for bot query processing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from query_handler import query_handler
from database_reader import db_reader

def test_queries():
    """Test various queries to ensure they work correctly."""
    
    # Test queries
    test_cases = [
        "搜尋訂單號12345",
        "查找客戶張三的訂單", 
        "顯示最近10個訂單",
        "搜尋產品SKU MIZ001",
        "顯示mizuki分類的產品"
    ]
    
    print("Testing bot query processing...")
    print("=" * 50)
    
    for query in test_cases:
        print(f"\nQuery: {query}")
        try:
            result = query_handler.process_question(query)
            response = query_handler.format_response(result)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_queries() 