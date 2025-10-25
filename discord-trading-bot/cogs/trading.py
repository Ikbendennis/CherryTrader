import discord
from discord import app_commands
from discord.ext import commands
from database.db_manager import add_trade
from utils.parsers import parse_listing

class Trading(commands.Cog):
    """Commands for listing items to sell or buy"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="sell", description="List an item for sale")
    @app_commands.describe(
        item="The item you want to sell (e.g., 2x gloves of Feroxi)",
        price="The price you're asking (optional)",
        notes="Additional notes about the item (optional)"
    )
    async def sell(self, interaction: discord.Interaction, item: str, price: str = None, notes: str = None):
        """List an item for sale"""
        try:
            # Parse quantity from item name
            item_name, quantity, _, _ = parse_listing(item)
            
            if not item_name:
                await interaction.response.send_message("❌ Please provide an item name!", ephemeral=True)
                return
            
            # Add to database
            trade_id = add_trade(
                str(interaction.user.id),
                interaction.user.name,
                'WTS',
                item_name,
                quantity,
                price,
                notes
            )
            
            # Create embed
            embed = discord.Embed(title="✅ Trade Listed", color=discord.Color.green())
            embed.add_field(name="Seller", value=interaction.user.mention, inline=False)
            embed.add_field(name="Item", value=f"{quantity}x {item_name}", inline=True)
            if price:
                embed.add_field(name="Price", value=price, inline=True)
            if notes:
                embed.add_field(name="Notes", value=notes, inline=False)
            embed.add_field(name="Trade ID", value=f"`{trade_id}`", inline=False)
            embed.set_footer(text=f"Listed by {interaction.user.name}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating listing: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="buy", description="Post a buy order for an item")
    @app_commands.describe(
        item="The item you want to buy (e.g., shield of valor)",
        offer="Your offer price (optional)",
        notes="Additional notes (optional)"
    )
    async def buy(self, interaction: discord.Interaction, item: str, offer: str = None, notes: str = None):
        """Post a buy order"""
        try:
            # Parse quantity from item name
            item_name, quantity, _, _ = parse_listing(item)
            
            if not item_name:
                await interaction.response.send_message("❌ Please provide an item name!", ephemeral=True)
                return
            
            # Add to database
            trade_id = add_trade(
                str(interaction.user.id),
                interaction.user.name,
                'WTB',
                item_name,
                quantity,
                offer,
                notes
            )
            
            # Create embed
            embed = discord.Embed(title="✅ Buy Order Posted", color=discord.Color.blue())
            embed.add_field(name="Buyer", value=interaction.user.mention, inline=False)
            embed.add_field(name="Item", value=f"{quantity}x {item_name}", inline=True)
            if offer:
                embed.add_field(name="Offer", value=offer, inline=True)
            if notes:
                embed.add_field(name="Notes", value=notes, inline=False)
            embed.add_field(name="Trade ID", value=f"`{trade_id}`", inline=False)
            embed.set_footer(text=f"Posted by {interaction.user.name}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating buy order: {str(e)}", ephemeral=True)

# Setup function for cog
async def setup(bot):
    await bot.add_cog(Trading(bot))
