import discord
from discord import app_commands
from discord.ext import commands
from database.db_manager import clear_all_trades

class Admin(commands.Cog):
    """Administrative commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="clearmarket", description="Clear all trades from the market (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def clearmarket(self, interaction: discord.Interaction):
        """Clear all trades from the market (admin only)"""
        try:
            rows_affected = clear_all_trades()
            await interaction.response.send_message(f"✅ Market cleared! {rows_affected} trade(s) removed.")
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error clearing market: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="ping", description="Check if the bot is responsive")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f'🏓 Pong! Latency: {latency}ms')

# Setup function for cog
async def setup(bot):
    await bot.add_cog(Admin(bot))
