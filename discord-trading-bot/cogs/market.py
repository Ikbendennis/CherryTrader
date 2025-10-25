import discord
from discord import app_commands
from discord.ext import commands
from database.db_manager import search_trades, get_all_trades, get_user_trades, get_trade_by_id, remove_trade
from datetime import datetime
from typing import Literal

class Market(commands.Cog):
    """Commands for searching and viewing the market"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="search", description="Search for items in the market")
    @app_commands.describe(query="The item name to search for")
    async def search(self, interaction: discord.Interaction, query: str):
        """Search for items in the market"""
        try:
            results = search_trades(query)
            
            if not results:
                await interaction.response.send_message(f"🔍 No results found for '{query}'", ephemeral=True)
                return
            
            # Separate WTS and WTB
            wts_items = [r for r in results if r[3] == 'WTS']
            wtb_items = [r for r in results if r[3] == 'WTB']
            
            embed = discord.Embed(title=f"🔍 Search Results: {query}", color=discord.Color.gold())
            
            # Add WTS items
            if wts_items:
                wts_text = ""
                for item in wts_items[:10]:  # Limit to 10 results
                    trade_id, user_id, username, _, item_name, quantity, price, notes = item
                    price_str = f" - {price}" if price else ""
                    wts_text += f"`[{trade_id}]` {quantity}x {item_name}{price_str} (by {username})\n"
                embed.add_field(name="🏪 For Sale", value=wts_text, inline=False)
            
            # Add WTB items
            if wtb_items:
                wtb_text = ""
                for item in wtb_items[:10]:
                    trade_id, user_id, username, _, item_name, quantity, offer, notes = item
                    offer_str = f" - {offer}" if offer else ""
                    wtb_text += f"`[{trade_id}]` {quantity}x {item_name}{offer_str} (by {username})\n"
                embed.add_field(name="💰 Wanted", value=wtb_text, inline=False)
            
            total = len(results)
            if total > 20:
                embed.set_footer(text=f"Showing 20 of {total} results")
            else:
                embed.set_footer(text=f"{total} result(s) found")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error searching: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="market", description="View all active trades in the market")
    @app_commands.describe(filter="Filter by trade type (optional)")
    async def market(self, interaction: discord.Interaction, filter: Literal["WTS", "WTB"] = None):
        """View all active trades in the market"""
        try:
            results = get_all_trades(filter, limit=20)
            
            if not results:
                await interaction.response.send_message("🏪 The market is empty!", ephemeral=True)
                return
            
            # Separate WTS and WTB
            wts_items = [r for r in results if r[2] == 'WTS']
            wtb_items = [r for r in results if r[2] == 'WTB']
            
            embed = discord.Embed(title="🏪 Trading Market", color=discord.Color.purple())
            
            # Add WTS items
            if wts_items and (not filter or filter == 'WTS'):
                wts_text = ""
                for item in wts_items:
                    trade_id, username, _, item_name, quantity, price, _ = item
                    price_str = f" - {price}" if price else ""
                    wts_text += f"`[{trade_id}]` {quantity}x {item_name}{price_str} (by {username})\n"
                embed.add_field(name="🏪 For Sale", value=wts_text or "None", inline=False)
            
            # Add WTB items
            if wtb_items and (not filter or filter == 'WTB'):
                wtb_text = ""
                for item in wtb_items:
                    trade_id, username, _, item_name, quantity, offer, _ = item
                    offer_str = f" - {offer}" if offer else ""
                    wtb_text += f"`[{trade_id}]` {quantity}x {item_name}{offer_str} (by {username})\n"
                embed.add_field(name="💰 Wanted", value=wtb_text or "None", inline=False)
            
            embed.set_footer(text="Showing most recent 20 trades")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error loading market: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="mylistings", description="View your active trades")
    async def mylistings(self, interaction: discord.Interaction):
        """View your own active trades"""
        try:
            results = get_user_trades(str(interaction.user.id))
            
            if not results:
                await interaction.response.send_message("📋 You don't have any active trades.", ephemeral=True)
                return
            
            embed = discord.Embed(title=f"📋 {interaction.user.name}'s Active Trades", color=discord.Color.blue())
            
            # Separate WTS and WTB
            wts_items = [r for r in results if r[1] == 'WTS']
            wtb_items = [r for r in results if r[1] == 'WTB']
            
            if wts_items:
                wts_text = ""
                for item in wts_items:
                    trade_id, _, item_name, quantity, price, notes = item
                    price_str = f" - {price}" if price else ""
                    notes_str = f"\n  _{notes}_" if notes else ""
                    wts_text += f"`[{trade_id}]` {quantity}x {item_name}{price_str}{notes_str}\n"
                embed.add_field(name="🏪 Selling", value=wts_text, inline=False)
            
            if wtb_items:
                wtb_text = ""
                for item in wtb_items:
                    trade_id, _, item_name, quantity, offer, notes = item
                    offer_str = f" - {offer}" if offer else ""
                    notes_str = f"\n  _{notes}_" if notes else ""
                    wtb_text += f"`[{trade_id}]` {quantity}x {item_name}{offer_str}{notes_str}\n"
                embed.add_field(name="💰 Buying", value=wtb_text, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error loading listings: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="tradeinfo", description="Get detailed information about a specific trade")
    @app_commands.describe(trade_id="The ID of the trade")
    async def tradeinfo(self, interaction: discord.Interaction, trade_id: int):
        """Get detailed information about a specific trade"""
        try:
            result = get_trade_by_id(trade_id)
            
            if not result:
                await interaction.response.send_message(f"❌ Trade ID `{trade_id}` not found.", ephemeral=True)
                return
            
            user_id, username, trade_type, item_name, quantity, price, notes, timestamp, active = result
            
            color = discord.Color.green() if trade_type == 'WTS' else discord.Color.blue()
            status = "✅ Active" if active else "❌ Closed"
            
            embed = discord.Embed(title=f"Trade Details - ID: {trade_id}", color=color)
            embed.add_field(name="Status", value=status, inline=True)
            embed.add_field(name="Type", value=trade_type, inline=True)
            embed.add_field(name="Trader", value=f"<@{user_id}>", inline=True)
            embed.add_field(name="Item", value=f"{quantity}x {item_name}", inline=True)
            
            if price:
                embed.add_field(name="Price/Offer", value=price, inline=True)
            
            if notes:
                embed.add_field(name="Notes", value=notes, inline=False)
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                embed.add_field(name="Listed", value=dt.strftime("%Y-%m-%d %H:%M"), inline=False)
            except:
                pass
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error loading trade info: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="remove", description="Remove one of your trades from the market")
    @app_commands.describe(trade_id="The ID of the trade to remove")
    async def remove(self, interaction: discord.Interaction, trade_id: int):
        """Remove one of your trades from the market"""
        try:
            success, message = remove_trade(trade_id, str(interaction.user.id))
            
            if success:
                await interaction.response.send_message(f"✅ Trade `{trade_id}` has been removed from the market.")
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error removing trade: {str(e)}", ephemeral=True)

# Setup function for cog
async def setup(bot):
    await bot.add_cog(Market(bot))
