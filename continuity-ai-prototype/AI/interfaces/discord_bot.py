"""Discord bot interface."""
import logging
import asyncio
from typing import Optional
import discord
from discord.ext import commands

from database.vector_db import VectorDB
from models.llm_manager import LLMManager
from rag.pipeline import RAGPipeline
from utils.context_manager import ContextManager
from config.settings import DISCORD_PREFIX

logger = logging.getLogger(__name__)


def create_bot(
    vector_db: VectorDB,
    llm_manager: LLMManager,
    context_manager: ContextManager,
) -> commands.Bot:
    """Create and configure Discord bot."""

    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix=DISCORD_PREFIX, intents=intents)

    # Initialize RAG pipeline
    rag_pipeline = RAGPipeline(vector_db, llm_manager)

    # Events

    @bot.event
    async def on_ready():
        """Bot ready event."""
        logger.info(f"Discord bot connected as {bot.user}")
        print(f"✓ Bot connected as {bot.user}")

    @bot.event
    async def on_message(message: discord.Message):
        """Handle incoming messages."""
        # Ignore bot's own messages
        if message.author == bot.user:
            return

        # Check for bot mention
        if bot.user not in message.mentions:
            return

        try:
            # Show typing indicator
            async with message.channel.typing():
                # Clean query (remove mention)
                query = message.content.replace(f"<@{bot.user.id}>", "").strip()
                
                if not query:
                    await message.reply("Please ask me something!")
                    return

                # Get user ID
                user_id = str(message.author.id)

                # Add to context
                context_manager.add_message(user_id, "user", query)
                chat_history = context_manager.get_history(user_id)

                # Get response
                response, sources = await rag_pipeline.query(
                    user_query=query,
                    chat_history=chat_history,
                    use_context=True,
                )

                # Add to history
                context_manager.add_message(user_id, "assistant", response)

                # Split response if too long (Discord limit: 2000 chars)
                if len(response) > 1900:
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(response)

                # Add sources as separate message if available
                if sources:
                    sources_text = "📚 **Sources:**\n"
                    for i, source in enumerate(sources[:3], 1):
                        score = 1 - source.get("distance", 1.0)
                        sources_text += f"{i}. (Relevance: {score:.1%})\n"
                    
                    if len(sources_text) < 1900:
                        await message.reply(sources_text)

        except Exception as e:
            logger.error(f"Error handling Discord message: {e}")
            await message.reply(f"Sorry, I encountered an error: {str(e)}")

    # Commands

    @bot.command(name="clear")
    async def clear_history(ctx: commands.Context):
        """Clear conversation history."""
        user_id = str(ctx.author.id)
        context_manager.clear_history(user_id)
        await ctx.send("✓ Your conversation history has been cleared.")

    @bot.command(name="bothelp")
    async def help_command(ctx: commands.Context):
        """Show help message."""
        embed = discord.Embed(
            title="AI Assistant Help",
            description="Ask me questions by mentioning me in a message.",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="Commands",
            value=f"{DISCORD_PREFIX}clear - Clear your conversation history\n"
                  f"{DISCORD_PREFIX}bothelp - Show this message",
            inline=False,
        )
        embed.add_field(
            name="Usage",
            value="Just mention me in any message to ask a question!\n"
                  f"Example: `@Bot What is this?`",
            inline=False,
        )
        await ctx.send(embed=embed)

    return bot
