"""
ChatGLM3 Discord Bot - Main Bot Module
"""

import discord
from discord.ext import commands
import logging
import os
import json
from typing import Optional, Tuple, Any
from .database import DatabaseManager
from .ai_model import AIModelManager
from .config import ConfigManager

logger = logging.getLogger(__name__)


class ChatGLM3Bot:
    """Main Discord bot class"""

    def __init__(self):
        """Initialize the bot"""
        self.config = ConfigManager()
        self.db_manager = DatabaseManager()
        self.ai_manager = AIModelManager()
        
        # Setup Discord bot
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(
            command_prefix=self.config.get('COMMAND_PREFIX', '!'),
            intents=intents
        )
        
        self._setup_events()
        self._setup_commands()

    def _setup_events(self):
        """Setup bot events"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f"Bot logged in as {self.bot.user.name}")
            print(f"🤖 {self.bot.user.name} is ready!")
            print(f"📊 Database: {self.config.get('MYSQL_DATABASE')}")
            print(f"🧠 AI Model: {'Loaded' if self.ai_manager.is_loaded else 'Not available'}")

    def _setup_commands(self):
        """Setup bot commands"""
        
        @self.bot.command(name='query')
        async def query_database(ctx, *, question: str):
            """Query database using natural language"""
            try:
                # Generate SQL from question
                sql_query, error = self.ai_manager.generate_sql(question)
                if error:
                    await ctx.send(f"❌ AI Error: {error}")
                    return
                
                if not sql_query:
                    await ctx.send("❌ Could not generate SQL query")
                    return
                
                # Execute query
                results, error = self.db_manager.execute_query(
                    sql_query, 
                    max_results=int(self.config.get('MAX_RESULTS', 100))
                )
                if error:
                    await ctx.send(f"❌ Database Error: {error}")
                    return
                
                # Format and send response
                response = self._format_query_response(question, sql_query, results)
                await ctx.send(response)
                
            except Exception as e:
                logger.error(f"Error in query command: {e}")
                await ctx.send(f"❌ Unexpected error occurred")

        @self.bot.command(name='status')
        async def status_command(ctx):
            """Check bot and system status"""
            status_info = self._get_status_info()
            await ctx.send(status_info)

        @self.bot.command(name='help')
        async def help_command(ctx):
            """Show help information"""
            help_text = self._get_help_text()
            await ctx.send(help_text)

    def _format_query_response(self, question: str, sql_query: str, results: Any) -> str:
        """Format query results for Discord response"""
        response = f"**Question:** {question}\n\n"
        response += f"**Generated SQL:**\n```sql\n{sql_query}\n```\n\n"
        
        if isinstance(results, str):
            response += f"**Result:** {results}"
        else:
            response += f"**Results:** ({len(results)} rows)\n"
            if results:
                # Show first few rows
                sample_data = results[:5]
                response += "```json\n"
                response += json.dumps(sample_data, indent=2, ensure_ascii=False)
                if len(results) > 5:
                    response += f"\n... and {len(results) - 5} more rows"
                response += "\n```"
            else:
                response += "No data returned"
        
        return response

    def _get_status_info(self) -> str:
        """Get bot status information"""
        status = "**🤖 Bot Status**\n"
        status += "✅ Bot: Online\n"
        status += f"🧠 AI Model: {'✅ Loaded' if self.ai_manager.is_loaded else '❌ Not available'}\n"
        
        # Test database connection
        is_connected = self.db_manager.test_connection()
        status += f"🗄️ Database: {'✅ Connected' if is_connected else '❌ Connection failed'}\n"
        
        return status

    def _get_help_text(self) -> str:
        """Get help text"""
        return """
**🤖 ChatGLM3 Discord SQL Bot**

**Commands:**
- `!query <question>` - Ask a question in Chinese about your database
- `!status` - Check bot and system status
- `!help` - Show this help message

**Examples:**
- `!query 过去七天有多少笔订单？`
- `!query 显示所有用户信息`
- `!query 统计每个部门的员工数量`

**Features:**
- AI-powered Chinese to SQL conversion
- Direct MySQL database access
- Local processing for privacy
        """

    async def start(self):
        """Start the bot"""
        try:
            token = self.config.get('DISCORD_TOKEN')
            if not token:
                raise ValueError("Discord token not found in configuration")
            
            await self.bot.start(token)
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise

    def run(self):
        """Run the bot (blocking)"""
        try:
            token = self.config.get('DISCORD_TOKEN')
            if not token:
                raise ValueError("Discord token not found in configuration")
            
            self.bot.run(token)
        except Exception as e:
            logger.error(f"Failed to run bot: {e}")
            raise 