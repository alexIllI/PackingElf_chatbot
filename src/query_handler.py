"""Query handler for processing Chinese questions and converting them to database queries."""
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from database_reader import db_reader

logger = logging.getLogger(__name__)


class QueryHandler:
    """Handles Chinese question processing and database queries."""
    
    def __init__(self):
        """Initialize the query handler."""
        self.logger = logging.getLogger(__name__)
        
        # Status translation mapping
        self.status_names = {
            'processing': '處理中',
            'delivered': '已送達',
            'pending': '待處理',
            'cancelled': '已取消',
            'shipped': '已發貨',
            'closed': '關轉',
            'returned': '已退貨'
        }
        
        # Chinese keywords mapping (Traditional Chinese only)
        self.keywords = {
            'order': ['訂單', 'order', '訂單號', 'order_id', '訂單編號'],
            'product': ['產品', 'product', '商品', 'sku', '產品編號'],
            'user': ['使用者', '用戶', 'user'],
            'status': ['狀態', 'status', '狀況'],
            'customer': ['客戶', 'customer', '顧客'],
            'recent': ['最近', 'recent', '最新', 'latest'],
            'statistics': ['統計', 'statistics', '數據', 'data'],
            'search': ['搜尋', 'search', '查找', 'find'],
            'count': ['數量', 'count', '個數', 'number'],
            'total': ['總計', 'total', '總額', 'sum'],
            'revenue': ['營收', 'revenue', '收益'],
            'stock': ['庫存', 'stock', '存貨'],
            'category': ['分類', 'category', '類別'],
            'date': ['日期', 'date', '時間', 'time'],
            'price': ['價格', 'price', '價錢'],
            'cost': ['成本', 'cost', '費用'],
            'shipping': ['運費', 'shipping', '運送'],
            'payment': ['付款', 'payment', '支付'],
            'invoice': ['發票', 'invoice', '收據'],
            'coupon': ['優惠券', 'coupon', '折扣'],
            'myacg': ['myacg', '帳號', 'account'],
            'default': ['預設', 'default', '預設值']
        }
        
        # Status mappings (Traditional Chinese only)
        self.status_mappings = {
            'processing': ['處理中', 'processing', '待列印'],
            'pending': ['待處理', 'pending', '等待'],
            'shipped': ['已發貨', 'shipped', '已列印'],
            'delivered': ['已送達', 'delivered', '已出貨'],
            'cancelled': ['已取消', 'cancelled', '取消'],
            'closed': ['關閉', 'closed', '關轉'],
            'returned': ['已退貨', 'returned', '退貨']
        }
    
    def _translate_status(self, status: str) -> str:
        """Translate status to Chinese display name."""
        return self.status_names.get(status, status.upper())
        
        # Category mappings (Traditional Chinese preferred)
        self.category_mappings = {
            'mizuki': ['mizuki', '水木'],
            'seki': ['seki', '關'],
            'hibiki': ['hibiki', '響'],
            'ksp': ['ksp'],
            'rei': ['rei', '零'],
            'kirali': ['kirali', '基拉利'],
            'yuzumi': ['yuzumi', '柚子'],
            'meridian': ['meridian', '子午線'],
            'sakuro': ['sakuro', '櫻郎'],
            'oboro': ['oboro', '朧'],
            'yoruno': ['yoruno', '夜野'],
            'iruni': ['iruni', '伊魯尼'],
            'itsuki': ['itsuki', '一樹'],
            'other': ['other', '其他', '其它']
        }
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """Process a Chinese question and return database query results."""
        try:
            question_lower = question.lower()
            
            # Check database connection first
            if not db_reader.is_connected:
                            return {
                'success': False,
                'error': '資料庫未連接，請先連接資料庫',
                'data': None
            }
            
            # Determine query type based on keywords
            query_type = self._determine_query_type(question_lower)
            
            if query_type == 'order_search':
                return self._handle_order_search(question)
            elif query_type == 'order_by_id':
                return self._handle_order_by_id(question)
            elif query_type == 'order_by_status':
                return self._handle_order_by_status(question)
            elif query_type == 'recent_orders':
                return self._handle_recent_orders(question)
            elif query_type == 'product_search':
                return self._handle_product_search(question)
            elif query_type == 'product_by_sku':
                return self._handle_product_by_sku(question)
            elif query_type == 'products_by_category':
                return self._handle_products_by_category(question)
            elif query_type == 'user_search':
                return self._handle_user_search(question)
            elif query_type == 'order_statistics':
                return self._handle_order_statistics(question)
            elif query_type == 'product_statistics':
                return self._handle_product_statistics(question)
            elif query_type == 'myacg_accounts':
                return self._handle_myacg_accounts(question)
            elif query_type == 'health_check':
                return self._handle_health_check(question)
            else:
                            return {
                'success': False,
                'error': '無法理解您的問題，請嘗試更具體的查詢',
                'data': None
            }
                
        except Exception as e:
            self.logger.error(f"Error processing question: {e}")
            return {
                'success': False,
                'error': f'處理問題時發生錯誤: {str(e)}',
                'data': None
            }
    
    def _determine_query_type(self, question: str) -> str:
        """Determine the type of query based on keywords in the question."""
        question_lower = question.lower()
        
        # Check for specific patterns first (improved order number detection)
        if any(word in question for word in ['訂單號', '訂單編號', 'order_id', 'order number']):
            return 'order_by_id'
        elif any(word in question for word in ['sku', '產品編號', 'product number']):
            return 'product_by_sku'
        elif any(word in question for word in ['最近', 'recent', '最新', 'latest']):
            return 'recent_orders'
        elif any(word in question for word in ['統計', 'statistics', '數據', 'data']):
            if any(word in question for word in ['產品', 'product', '商品']):
                return 'product_statistics'
            else:
                return 'order_statistics'
        elif any(word in question for word in ['狀態', 'status']):
            return 'order_by_status'
        elif any(word in question for word in ['分類', 'category', '類別']):
            return 'products_by_category'
        elif any(word in question for word in ['myacg', '帳號', 'account']):
            return 'myacg_accounts'
        elif any(word in question for word in ['健康', 'health', '連接']):
            return 'health_check'
        elif any(word in question for word in ['搜尋', 'search', '查找', 'find']):
            if any(word in question for word in ['產品', 'product', '商品']):
                return 'product_search'
            elif any(word in question for word in ['使用者', '用戶', 'user']):
                return 'user_search'
            else:
                return 'order_search'
        elif any(word in question for word in ['客戶', 'customer']):
            return 'order_search'
        elif any(word in question for word in ['顯示', 'show', '列出', 'list']):
            if any(word in question for word in ['產品', 'product', '商品']):
                return 'product_search'
            elif any(word in question for word in ['訂單', 'order']):
                return 'recent_orders'
            else:
                return 'order_search'
        elif any(word in question for word in ['查詢', 'query', '查']):
            # Check if it contains order-like patterns
            if re.search(r'[A-Z]{2,4}\d{2,8}', question, re.IGNORECASE) or re.search(r'\d{2,10}', question):
                return 'order_by_id'
            elif any(word in question for word in ['產品', 'product', '商品']):
                return 'product_search'
            elif any(word in question for word in ['訂單', 'order']):
                return 'order_search'
            else:
                return 'order_search'
        else:
            # Default to order search if no specific pattern is found
            return 'order_search'
    
    def _extract_order_id(self, question: str) -> Optional[str]:
        """Extract order ID from question."""
        # Look for patterns like "訂單號12345" or "order_id 12345" or "ORD002" or "PG02612345"
        patterns = [
            r'訂單號\s*([A-Z0-9]+)',  # 訂單號PG02612345
            r'訂單編號\s*([A-Z0-9]+)',  # 訂單編號ORD002
            r'order_id\s*([A-Z0-9]+)',  # order_id PG02612345
            r'order\s*number\s*([A-Z0-9]+)',  # order number ORD002
            r'order\s*([A-Z0-9]+)',  # order PG02612345
            r'([A-Z]{2,4}\d{2,8})',  # Pattern for ORD002, PG02612345, etc.
            r'(\d{5,10})',  # General pattern for numeric order IDs
            r'(\d{2,6})'  # Shorter numeric patterns
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                order_id = match.group(1)
                # Clean up the order ID
                order_id = order_id.strip()
                if order_id:
                    return order_id
        return None
    
    def _extract_sku(self, question: str) -> Optional[str]:
        """Extract SKU from question."""
        # Look for SKU patterns
        patterns = [
            r'sku\s*([A-Za-z0-9\-_]+)',
            r'产品编号\s*([A-Za-z0-9\-_]+)',
            r'產品編號\s*([A-Za-z0-9\-_]+)',
            r'([A-Z]{2,5}\d{3,6})'  # Common SKU pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_status(self, question: str) -> Optional[str]:
        """Extract order status from question."""
        question_lower = question.lower()
        
        for status, keywords in self.status_mappings.items():
            if any(keyword in question_lower for keyword in keywords):
                return status
        return None
    
    def _extract_category(self, question: str) -> Optional[str]:
        """Extract product category from question."""
        question_lower = question.lower()
        
        for category, keywords in self.category_mappings.items():
            if any(keyword in question_lower for keyword in keywords):
                return category
        return None
    
    def _extract_search_term(self, question: str) -> str:
        """Extract search term from question."""
        # Remove common question words and extract the main search term
        question_words = ['搜尋', 'search', '查找', 'find', '查詢', 'query', '顯示', 'show']
        search_term = question
        
        for word in question_words:
            search_term = search_term.replace(word, '').strip()
        
        # Remove common prefixes
        prefixes = ['客戶', 'customer', '產品', 'product']
        for prefix in prefixes:
            if search_term.startswith(prefix):
                search_term = search_term[len(prefix):].strip()
        
        # Remove common suffixes
        suffixes = ['的訂單', '的產品', '的使用者', '客戶', 'customer']
        for suffix in suffixes:
            if search_term.endswith(suffix):
                search_term = search_term[:-len(suffix)].strip()
        
        # Clean up the search term
        search_term = search_term.strip()
        
        # If search term is empty, return the original question
        return search_term if search_term else question
    
    def _handle_order_search(self, question: str) -> Dict[str, Any]:
        """Handle order search queries."""
        search_term = self._extract_search_term(question)
        
        # If the search term looks like an order ID, try direct order lookup first
        if re.search(r'[A-Z]{2,4}\d{2,8}', search_term, re.IGNORECASE) or re.search(r'\d{2,10}', search_term):
            # Try to get order by external ID first
            order = db_reader.get_order_by_external_id(search_term)
            if order:
                return {
                    'success': True,
                    'message': f'找到訂單 {search_term}',
                    'data': order
                }
        
        # Fallback to general search
        orders = db_reader.search_orders(search_term)
        
        if not orders:
            return {
                'success': True,
                'message': f'未找到包含 "{search_term}" 的訂單',
                'data': []
            }
        
        return {
            'success': True,
            'message': f'找到 {len(orders)} 個相關訂單',
            'data': orders
        }
    
    def _handle_order_by_id(self, question: str) -> Dict[str, Any]:
        """Handle order by ID queries."""
        order_id = self._extract_order_id(question)
        
        if not order_id:
            return {
                'success': False,
                'error': '無法從問題中提取訂單號',
                'data': None
            }
        
        try:
            # Try to get order by external ID first (for ORD002, PG02612345, etc.)
            order = db_reader.get_order_by_external_id(order_id)
            
            if not order:
                # If not found by external ID, try by numeric ID
                try:
                    order_id_int = int(order_id)
                    order = db_reader.get_order_by_id(order_id_int)
                except ValueError:
                    # If order_id is not numeric, just return not found
                    pass
            
            if not order:
                return {
                    'success': True,
                    'message': f'未找到訂單號 {order_id}',
                    'data': None
                }
            
            return {
                'success': True,
                'message': f'找到訂單 {order_id}',
                'data': order
            }
        except Exception as e:
            self.logger.error(f"Error querying order {order_id}: {e}")
            return {
                'success': False,
                'error': f'查詢訂單時發生錯誤: {str(e)}',
                'data': None
            }
    
    def _handle_order_by_status(self, question: str) -> Dict[str, Any]:
        """Handle order by status queries."""
        status = self._extract_status(question)
        
        if not status:
            return {
                'success': False,
                'error': '無法識別訂單狀態，請使用以下狀態之一：處理中、待處理、已發貨、已送達、已取消、已關閉、已退貨',
                'data': None
            }
        
        orders = db_reader.get_orders_by_status(status)
        
        return {
            'success': True,
            'message': f'找到 {len(orders)} 個 {status} 狀態的訂單',
            'data': orders
        }
    
    def _handle_recent_orders(self, question: str) -> Dict[str, Any]:
        """Handle recent orders queries."""
        # Extract limit from question if specified
        limit = 10
        limit_match = re.search(r'(\d+)', question)
        if limit_match:
            try:
                limit = int(limit_match.group(1))
                limit = min(limit, 50)  # Cap at 50
            except ValueError:
                pass
        
        orders = db_reader.get_recent_orders(limit)
        
        return {
            'success': True,
            'message': f'最近 {len(orders)} 個訂單',
            'data': orders
        }
    
    def _handle_product_search(self, question: str) -> Dict[str, Any]:
        """Handle product search queries."""
        search_term = self._extract_search_term(question)
        products = db_reader.get_all_products()
        
        # Filter products by search term
        filtered_products = []
        for product in products:
            if (search_term.lower() in product['name'].lower() or 
                search_term.lower() in product['sku'].lower() or
                (product['description'] and search_term.lower() in product['description'].lower())):
                filtered_products.append(product)
        
        if not filtered_products:
            return {
                'success': True,
                'message': f'未找到包含 "{search_term}" 的產品',
                'data': []
            }
        
        return {
            'success': True,
            'message': f'找到 {len(filtered_products)} 個相關產品',
            'data': filtered_products
        }
    
    def _handle_product_by_sku(self, question: str) -> Dict[str, Any]:
        """Handle product by SKU queries."""
        sku = self._extract_sku(question)
        
        if not sku:
            return {
                'success': False,
                'error': '無法從問題中提取產品SKU',
                'data': None
            }
        
        product = db_reader.get_product_by_sku(sku)
        
        if not product:
            return {
                'success': True,
                'message': f'未找到SKU為 {sku} 的產品',
                'data': None
            }
        
        return {
            'success': True,
            'message': f'找到產品 {sku}',
            'data': product
        }
    
    def _handle_products_by_category(self, question: str) -> Dict[str, Any]:
        """Handle products by category queries."""
        category = self._extract_category(question)
        
        if not category:
            return {
                'success': False,
                'error': '無法識別產品分類，請使用以下分類之一：mizuki, seki, hibiki, ksp, rei, kirali, yuzumi, meridian, sakuro, oboro, yoruno, iruni, itsuki, other',
                'data': None
            }
        
        products = db_reader.get_products_by_category(category)
        
        return {
            'success': True,
            'message': f'找到 {len(products)} 個 {category} 分類的產品',
            'data': products
        }
    
    def _handle_user_search(self, question: str) -> Dict[str, Any]:
        """Handle user search queries."""
        search_term = self._extract_search_term(question)
        users = db_reader.get_all_users()
        
        # Filter users by search term
        filtered_users = []
        for user in users:
            if (search_term.lower() in user['name'].lower() or 
                search_term.lower() in user['username'].lower()):
                filtered_users.append(user)
        
        if not filtered_users:
            return {
                'success': True,
                'message': f'未找到包含 "{search_term}" 的使用者',
                'data': []
            }
        
        return {
            'success': True,
            'message': f'找到 {len(filtered_users)} 個相關使用者',
            'data': filtered_users
        }
    
    def _handle_order_statistics(self, question: str) -> Dict[str, Any]:
        """Handle order statistics queries."""
        stats = db_reader.get_order_statistics()
        
        return {
            'success': True,
            'message': '訂單統計資訊',
            'data': stats
        }
    
    def _handle_product_statistics(self, question: str) -> Dict[str, Any]:
        """Handle product statistics queries."""
        stats = db_reader.get_product_statistics()
        
        return {
            'success': True,
            'message': '產品統計資訊',
            'data': stats
        }
    
    def _handle_myacg_accounts(self, question: str) -> Dict[str, Any]:
        """Handle MyACG accounts queries."""
        accounts = db_reader.get_myacg_accounts()
        
        return {
            'success': True,
            'message': f'找到 {len(accounts)} 個MyACG帳戶',
            'data': accounts
        }
    
    def _handle_health_check(self, question: str) -> Dict[str, Any]:
        """Handle database health check queries."""
        is_healthy, message = db_reader.health_check()
        
        return {
            'success': True,
            'message': f'資料庫健康檢查: {message}',
            'data': {
                'is_healthy': is_healthy,
                'message': message
            }
        }
    
    def format_response(self, result: Dict[str, Any]) -> str:
        """Format the query result into a readable response."""
        if not result['success']:
            return f"❌ 錯誤: {result['error']}"
        
        # Handle None data or empty data
        if result['data'] is None or (isinstance(result['data'], list) and len(result['data']) == 0):
            return f"ℹ️ {result['message']}"
        
        # Format based on data type
        if isinstance(result['data'], list):
            if not result['data']:
                return f"ℹ️ {result['message']}"
            
            # Format list data
            if len(result['data']) == 1:
                return self._format_single_item(result['data'][0], result['message'])
            else:
                return self._format_list_summary(result['data'], result['message'])
        
        elif isinstance(result['data'], dict):
            return self._format_dict_data(result['data'], result['message'])
        
        else:
            return f"✅ {result['message']}\n{result['data']}"
    
    def _format_single_item(self, item: Dict[str, Any], message: str) -> str:
        """Format a single item response."""
        if 'external_order_id' in item:  # Order
            # Format datetime objects
            order_date = item['order_date']
            if hasattr(order_date, 'strftime'):
                order_date_str = order_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                order_date_str = str(order_date)
            
            # Translate status to Chinese
            status_display = self._translate_status(item['status'])
            
            return f"✅ {message}\n" + \
                   f"訂單號: {item['external_order_id']}\n" + \
                   f"客戶: {item['customer_name']}\n" + \
                   f"狀態: {status_display}\n" + \
                   f"總金額: ${item['total']:.2f}\n" + \
                   f"訂單日期: {order_date_str}"
        
        elif 'sku' in item:  # Product
            return f"✅ {message}\n" + \
                   f"SKU: {item['sku']}\n" + \
                   f"名稱: {item['name']}\n" + \
                   f"價格: ${item['price']:.2f}\n" + \
                   f"庫存: {item['stock_quantity']}\n" + \
                   f"分類: {item['category']}"
        
        elif 'username' in item and 'api_key' in item:  # MyACG Account
            return f"✅ {message}\n" + \
                   f"名稱: {item['name']}\n" + \
                   f"使用者名: {item['username']}\n" + \
                   f"預設帳戶: {'是' if item['is_default'] else '否'}"
        
        else:  # Generic
            return f"✅ {message}\n{str(item)}"
    
    def _format_list_summary(self, items: List[Dict[str, Any]], message: str) -> str:
        """Format a list summary response."""
        if not items:
            return f"ℹ️ {message}"
        
        # Show first few items and total count
        display_count = min(5, len(items))
        summary = f"✅ {message}\n\n"
        
        for i, item in enumerate(items[:display_count]):
            if 'external_order_id' in item:  # Order
                # Format datetime for order date
                order_date = item.get('order_date')
                if order_date and hasattr(order_date, 'strftime'):
                    date_str = order_date.strftime('%m-%d')
                else:
                    date_str = 'N/A'
                
                # Translate status to Chinese
                status_display = self._translate_status(item['status'])
                
                summary += f"{i+1}. 訂單 {item['external_order_id']} - {item['customer_name']} (${item['total']:.2f}) [{status_display}] {date_str}\n"
            elif 'sku' in item:  # Product
                summary += f"{i+1}. {item['sku']} - {item['name']} (${item['price']:.2f})\n"
            elif 'username' in item:  # User
                summary += f"{i+1}. {item['name']} ({item['username']})\n"
            else:
                summary += f"{i+1}. {str(item)}\n"
        
        if len(items) > display_count:
            summary += f"\n... 還有 {len(items) - display_count} 項"
        
        return summary
    
    def _format_dict_data(self, data: Dict[str, Any], message: str) -> str:
        """Format dictionary data response."""
        if 'total_orders' in data:  # Order statistics
            # Format status counts more nicely
            status_display = []
            for status, count in data['status_counts'].items():
                status_name = self._translate_status(status)
                status_display.append(f"{status_name}: {count}")
            
            return f"✅ {message}\n" + \
                   f"總訂單數: {data['total_orders']}\n" + \
                   f"總收入: ${data['total_revenue']:.2f}\n" + \
                   f"平均訂單價值: ${data['average_order_value']:.2f}\n" + \
                   f"狀態分佈: {', '.join(status_display)}"
        
        elif 'total_products' in data:  # Product statistics
            return f"✅ {message}\n" + \
                   f"總產品數: {data['total_products']}\n" + \
                   f"庫存不足產品: {data['low_stock_products']}\n" + \
                   f"總庫存價值: ${data['total_stock_value']:.2f}\n" + \
                   f"分類分佈: {', '. join([f'{k}: {v}' for k, v in data['category_counts'].items()])}"
        
        elif 'is_healthy' in data:  # Health check
            status = "🟢 正常" if data['is_healthy'] else "🔴 異常"
            return f"{status} {message}"
        
        else:
            return f"✅ {message}\n{str(data)}"


# Global instance
query_handler = QueryHandler() 