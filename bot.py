import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import sys
from database.db_manager import init_database
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up bot with command prefix (kept for backward compatibility)
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!', flush=True)
    print(f'Bot is in {len(bot.guilds)} server(s)', flush=True)
    
    # Debug: Check what commands we have before syncing
    print(f'Commands in tree before sync: {len(bot.tree.get_commands())}', flush=True)
    for cmd in bot.tree.get_commands():
        print(f'  - {cmd.name}', flush=True)
    
    # Sync slash commands
    try:
        # Try syncing without clearing first
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash command(s)', flush=True)
        
        # List all synced commands
        if synced:
            for cmd in synced:
                print(f'  - /{cmd.name}', flush=True)
        else:
            print('WARNING: 0 commands synced!', flush=True)
            print('This might be a Discord API rate limit or permission issue.', flush=True)
            print('Commands should appear in 1-2 minutes, or try:', flush=True)
            print('  1. Kick and re-invite the bot', flush=True)
            print('  2. Make sure bot has applications.commands scope', flush=True)
    except Exception as e:
        print(f'Failed to sync commands: {e}', flush=True)
        import traceback
        traceback.print_exc()
    
    print('Trading system initialized!', flush=True)
    print('=' * 50, flush=True)

# Event: When a message is sent
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# Load all cogs (command modules)
async def load_cogs():
    cogs = ['cogs.trading', 'cogs.market', 'cogs.admin', 'cogs.offers']
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'[OK] Loaded: {cog}', flush=True)
        except Exception as e:
            print(f'[ERROR] Failed to load {cog}:', flush=True)
            print(f'  Error: {type(e).__name__}: {e}', flush=True)
            import traceback
            traceback.print_exc()

# Main function
async def main():
    # Initialize database
    print('Initializing database...', flush=True)
    init_database()
    print('[OK] Database ready!', flush=True)
    
    # Load command modules
    print('Loading command modules...', flush=True)
    await load_cogs()
    print('', flush=True)
    print('Starting bot...', flush=True)
    print('Connecting to Discord...', flush=True)
    
    # Get token and start bot
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found!", flush=True)
        print("Please set your bot token as an environment variable.", flush=True)
        return
    
    # Start the bot
    await bot.start(TOKEN)

# Run the bot
if __name__ == '__main__':
    print('=' * 50, flush=True)
    print('Discord Trading Bot', flush=True)
    print('=' * 50, flush=True)
    asyncio.run(main())
