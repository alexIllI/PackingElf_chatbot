"""Discord bot for Chinese to SQL query conversion using ChatGLM3."""
import discord
from discord.ext import commands
import logging
import asyncio
import os
from typing import Optional
import json

from ai_model import AIModelManager
from database_reader import db_reader
from function_selector import function_selector
from query_handler import query_handler  # Keep as fallback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseBot(commands.Bot):
    """Discord bot for database queries using ChatGLM3."""
    
    def __init__(self):
        """Initialize the bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.ai_model = None
        self.is_ai_ready = False
        
    async def setup_hook(self):
        """Setup hook called when bot is starting."""
        logger.info("Setting up bot...")
        
        # Initialize AI model
        try:
            self.ai_model = AIModelManager()
            self.is_ai_ready = self.ai_model.is_model_available()
            if self.is_ai_ready:
                logger.info("AI model initialized successfully")
            else:
                logger.error("AI model not available")
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {e}")
            self.is_ai_ready = False
        
        # Try to connect to database
        try:
            if db_reader.connect():
                logger.info("Database connected successfully")
            else:
                logger.warning("Failed to connect to database - will prompt user for connection")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
        
        # Add commands
        await self.add_cog(DatabaseCommands(self))
        
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'Bot is ready! Logged in as {self.user}')
        
        # Set bot status
        if self.is_ai_ready and db_reader.is_connected:
            await self.change_presence(activity=discord.Game(name="新架構查詢助手 | !help"))
        elif self.is_ai_ready:
            await self.change_presence(activity=discord.Game(name="AI就緒 | 需要連接資料庫"))
        else:
            await self.change_presence(activity=discord.Game(name="初始化中..."))

class DatabaseCommands(commands.Cog):
    """Database-related commands."""
    
    def __init__(self, bot: DatabaseBot):
        """Initialize the commands cog."""
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information."""
        embed = discord.Embed(
            title="新架構資料庫查詢助手 - 幫助",
            description="這是一個使用函數選擇器架構的智能資料庫助手機器人",
            color=0x00ff00
        )
        
        embed.add_field(
            name="基本命令",
            value="""
            `!help` - 顯示此幫助資訊
            `!connect <資料庫IP>` - 連接到資料庫
            `!status` - 檢查系統狀態
            `!health` - 檢查資料庫健康狀態
            """,
            inline=False
        )
        
        embed.add_field(
            name="查詢範例",
            value="""
            • "幫我查 PG12345678" (新訂單格式)
            • "查找客戶張三的訂單"
            • "顯示最近10個訂單"
            • "查詢已發貨狀態的訂單"
            • "搜尋產品HIB001"
            • "顯示mizuki分類的產品"
            • "查看訂單統計資訊"
            • "顯示產品庫存統計"
            """,
            inline=False
        )
        
        embed.add_field(
            name="訂單狀態查詢",
            value="""
            • "查詢處理中的訂單" (processing)
            • "已發貨的訂單" (shipped)
            • "待處理訂單" (pending)
            • "已取消訂單" (cancelled)
            • "已送達訂單" (delivered)
            • "查詢pending的訂單" (英文狀態)
            • "shipped orders" (英文查詢)
            """,
            inline=False
        )
        
        embed.add_field(
            name="支援的查詢類型",
            value="""
            • 訂單查詢 (PG格式: PG + 8位數字)
            • 客戶搜尋 (按客戶名稱)
            • 訂單狀態查詢 (處理中/已發貨/待處理/已取消/已送達)
            • 產品查詢 (按SKU、名稱、分類)
            • 統計資訊 (訂單統計、產品統計)
            • 最近記錄查詢
            """,
            inline=False
        )
        
        embed.add_field(
            name="新架構特色",
            value="""
            ✨ 使用LLM函數選擇器
            🎯 預定義SQL函數，更穩定可靠
            🚀 更快的查詢響應時間
            🔧 調試資訊顯示
            """,
            inline=False
        )
        
        embed.set_footer(text="直接發送中文問題即可查詢資料庫 | 訂單格式: PG00000000")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='connect')
    async def connect_database(self, ctx, host_ip: Optional[str] = None):
        """Connect to the database."""
        try:
            if db_reader.connect(host_ip):
                await ctx.send(f"✅ 成功連接到資料庫")
                await self.bot.change_presence(activity=discord.Game(name="資料庫查詢助手 | !help"))
            else:
                await ctx.send("❌ 連接資料庫失敗。請檢查資料庫是否運行，或提供正確的IP地址。")
        except Exception as e:
            await ctx.send(f"❌ 連接資料庫時發生錯誤: {str(e)}")
    
    @commands.command(name='status')
    async def check_status(self, ctx):
        """Check system status."""
        embed = discord.Embed(title="系統狀態", color=0x00ff00)
        
        # AI Model status
        ai_status = "✅ 就緒" if self.bot.is_ai_ready else "❌ 未就緒"
        embed.add_field(name="AI模型", value=ai_status, inline=True)
        
        # Database status
        db_status = "✅ 已連接" if db_reader.is_connected else "❌ 未連接"
        embed.add_field(name="資料庫", value=db_status, inline=True)
        
        # Overall status
        if self.bot.is_ai_ready and db_reader.is_connected:
            overall_status = "✅ 系統正常運行"
            embed.color = 0x00ff00
        elif self.bot.is_ai_ready:
            overall_status = "⚠️ AI就緒，需要連接資料庫"
            embed.color = 0xffff00
        else:
            overall_status = "❌ 系統未完全就緒"
            embed.color = 0xff0000
        
        embed.add_field(name="總體狀態", value=overall_status, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='health')
    async def health_check(self, ctx):
        """Check database health."""
        try:
            is_healthy, message = db_reader.health_check()
            
            if is_healthy:
                embed = discord.Embed(
                    title="資料庫健康檢查",
                    description=f"✅ {message}",
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="資料庫健康檢查",
                    description=f"❌ {message}",
                    color=0xff0000
                )
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ 健康檢查失敗: {str(e)}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages."""
        # Ignore bot's own messages
        if message.author == self.bot.user:
            return
        
        # Process commands first
        if message.content.startswith('!'):
            await self.bot.process_commands(message)
            return
        
        # Check if database is connected
        if not db_reader.is_connected:
            await message.channel.send(
                "❌ 資料庫未連接。請使用 `!connect <資料庫IP>` 命令連接資料庫。"
            )
            return
        
        # Process the message using new function selector architecture
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Use new function selector for query processing
                result = function_selector.process_query(message.content)
                
                # If function selector fails, fall back to old query handler
                if not result['success']:
                    self.logger.warning("Function selector failed, using fallback query handler")
                    result = query_handler.process_question(message.content)
                
                # Format the response
                response = query_handler.format_response(result)
                
                # Add function selector info for debugging (only if AI is available)
                if self.bot.is_ai_ready:
                    # Get function selection info for debugging
                    try:
                        selection = function_selector.select_function_and_params(message.content)
                        if selection.get('success'):
                            func_name = selection.get('function', 'unknown')
                            params = selection.get('parameters', {})
                            debug_info = f"\n🔧 已選用函數: `{func_name}` 參數: `{params}`"
                            response += debug_info
                    except Exception as e:
                        self.logger.error(f"Error getting debug info: {e}")
                
                # Send the response
                if len(response) > 2000:
                    # Split long responses
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            await message.channel.send(chunk)
                        else:
                            await message.channel.send(f"```\n{chunk}\n```")
                else:
                    await message.channel.send(response)
                    
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            await message.channel.send(f"❌ 處理您的問題時發生錯誤: {str(e)}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            # Ignore command not found errors for non-command messages
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ 缺少必要參數: {error.param}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ 參數格式錯誤: {error}")
        else:
            await ctx.send(f"❌ 命令執行錯誤: {str(error)}")

def create_bot() -> DatabaseBot:
    """Create and return a configured bot instance."""
    return DatabaseBot()

async def main():
    """Main function to run the bot."""
    # Load configuration
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return
    
    # Create and run bot
    bot = create_bot()
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        # Cleanup
        if db_reader:
            db_reader.close()
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main()) 