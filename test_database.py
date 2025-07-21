#!/usr/bin/env python3
"""Test database connection and queries."""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from database_reader import db_reader
from query_handler import query_handler

def test_database_connection():
    """Test database connection."""
    print("🔍 測試資料庫連接...")
    
    if db_reader.connect():
        print("✅ 資料庫連接成功")
        
        # Test health check
        is_healthy, message = db_reader.health_check()
        print(f"健康檢查: {message}")
        
        return True
    else:
        print("❌ 資料庫連接失敗")
        return False

def test_order_queries():
    """Test order queries."""
    print("\n🔍 測試訂單查詢...")
    
    # Test specific order IDs
    test_orders = ["ORD002", "PG02612345", "12345", "1"]
    
    for order_id in test_orders:
        print(f"\n查詢訂單: {order_id}")
        
        # Test external ID first
        order = db_reader.get_order_by_external_id(order_id)
        if order:
            print(f"✅ 找到訂單 (external_id): {order}")
        else:
            # Test numeric ID
            try:
                order_id_int = int(order_id)
                order = db_reader.get_order_by_id(order_id_int)
                if order:
                    print(f"✅ 找到訂單 (numeric_id): {order}")
                else:
                    print(f"❌ 未找到訂單: {order_id}")
            except ValueError:
                print(f"❌ 未找到訂單: {order_id}")

def test_recent_orders():
    """Test recent orders query."""
    print("\n🔍 測試最近訂單查詢...")
    
    orders = db_reader.get_recent_orders(5)
    print(f"找到 {len(orders)} 個最近訂單:")
    
    for order in orders:
        print(f"  - {order.get('external_order_id', 'N/A')}: {order.get('customer_name', 'N/A')}")

def test_query_handler():
    """Test query handler."""
    print("\n🔍 測試查詢處理器...")
    
    test_queries = [
        "搜尋訂單號ORD002",
        "查找訂單PG02612345",
        "顯示最近10個訂單",
        "查詢訂單12345"
    ]
    
    for query in test_queries:
        print(f"\n處理查詢: {query}")
        result = query_handler.process_question(query)
        print(f"結果: {result}")

def main():
    """Main test function."""
    print("🚀 開始資料庫測試...")
    
    if not test_database_connection():
        print("❌ 無法繼續測試，資料庫未連接")
        return
    
    test_order_queries()
    test_recent_orders()
    test_query_handler()
    
    print("\n✅ 測試完成")

if __name__ == "__main__":
    main() 