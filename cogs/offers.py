import discord
from discord import app_commands
from discord.ext import commands
from database.db_manager import (
    set_trade_name, get_trade_name, has_trade_name,
    create_offer, get_pending_offer_for_trade, update_offer_status,
    complete_trade, get_trade_by_id
)

class OfferView(discord.ui.View):
    """View with Accept/Decline buttons for offers"""
    
    def __init__(self, offer_id: int, trade_id: int, seller_id: str, buyer_id: str, 
                 buyer_username: str, offer_amount: str):
        super().__init__(timeout=None)  # No timeout
        self.offer_id = offer_id
        self.trade_id = trade_id
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.buyer_username = buyer_username
        self.offer_amount = offer_amount
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, custom_id="accept_offer")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the person clicking is the seller
        if str(interaction.user.id) != self.seller_id:
            await interaction.response.send_message(
                "Only the seller can accept this offer!", 
                ephemeral=True
            )
            return
        
        # Update offer status
        update_offer_status(self.offer_id, "accepted")
        
        # Complete the trade
        success = complete_trade(
            self.trade_id,
            self.buyer_id,
            self.buyer_username,
            self.offer_amount,
            "offer_accepted"
        )
        
        if success:
            # Get trade names
            seller_tradename = get_trade_name(self.seller_id)
            buyer_tradename = get_trade_name(self.buyer_id)
            
            # Disable buttons
            for item in self.children:
                item.disabled = True
            
            # Update the message
            embed = discord.Embed(
                title="Trade Accepted!",
                description=f"<@{self.seller_id}> accepted the offer from <@{self.buyer_id}>",
                color=discord.Color.green()
            )
            embed.add_field(name="Final Price", value=self.offer_amount)
            embed.add_field(name="Seller In-Game", value=seller_tradename, inline=True)
            embed.add_field(name="Buyer In-Game", value=buyer_tradename, inline=True)
            embed.add_field(
                name="Next Steps", 
                value=f"<@{self.buyer_id}> contact <@{self.seller_id}> in-game to complete the trade!",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
            
            # Send DM to buyer
            try:
                buyer = await interaction.client.fetch_user(int(self.buyer_id))
                dm_embed = discord.Embed(
                    title="Your offer was accepted!",
                    description=f"Your offer of {self.offer_amount} was accepted!",
                    color=discord.Color.green()
                )
                dm_embed.add_field(name="Seller In-Game Name", value=seller_tradename)
                dm_embed.add_field(name="Your In-Game Name", value=buyer_tradename)
                dm_embed.add_field(
                    name="Next Steps",
                    value=f"Contact **{seller_tradename}** in-game to complete the trade!",
                    inline=False
                )
                await buyer.send(embed=dm_embed)
            except:
                pass  # DMs might be disabled
        else:
            await interaction.response.send_message(
                "Error completing trade. Please contact an admin.",
                ephemeral=True
            )
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, custom_id="decline_offer")
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the person clicking is the seller
        if str(interaction.user.id) != self.seller_id:
            await interaction.response.send_message(
                "Only the seller can decline this offer!",
                ephemeral=True
            )
            return
        
        # Update offer status
        update_offer_status(self.offer_id, "declined")
        
        # Disable buttons
        for item in self.children:
            item.disabled = True
        
        # Update the message
        embed = discord.Embed(
            title="Offer Declined",
            description=f"<@{self.seller_id}> declined the offer from <@{self.buyer_id}>",
            color=discord.Color.red()
        )
        embed.add_field(name="Declined Offer", value=self.offer_amount)
        embed.add_field(
            name="Status",
            value="The listing is still active. Others can now make offers.",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        # Notify buyer via DM
        try:
            buyer = await interaction.client.fetch_user(int(self.buyer_id))
            dm_embed = discord.Embed(
                title="Your offer was declined",
                description=f"Your offer of {self.offer_amount} was declined.",
                color=discord.Color.red()
            )
            dm_embed.add_field(
                name="Next Steps",
                value="You can try making a different offer when no other offers are pending.",
                inline=False
            )
            await buyer.send(embed=dm_embed)
        except:
            pass  # DMs might be disabled

class Offers(commands.Cog):
    """Commands for trade offers and trade names"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="settradename", description="Set your in-game trade name (one-time setup)")
    @app_commands.describe(name="Your in-game character/account name")
    async def settradename(self, interaction: discord.Interaction, name: str):
        """Set your trade name"""
        user_id = str(interaction.user.id)
        
        # Check if already set
        if has_trade_name(user_id):
            await interaction.response.send_message(
                f"You already have a trade name set. Contact an admin to change it.",
                ephemeral=True
            )
            return
        
        # Set the trade name
        success = set_trade_name(user_id, name)
        
        if success:
            embed = discord.Embed(
                title="Trade Name Set!",
                description=f"Your in-game trade name has been set to: **{name}**",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Note",
                value="This name will be shown to other traders. Contact an admin if you need to change it.",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                "Error setting trade name. Please try again.",
                ephemeral=True
            )
    
    @app_commands.command(name="changetradename", description="Change a user's trade name (Admin only)")
    @app_commands.describe(
        user="The user whose trade name to change",
        name="The new in-game trade name"
    )
    @app_commands.default_permissions(administrator=True)
    async def changetradename(self, interaction: discord.Interaction, user: discord.User, name: str):
        """Change a user's trade name (admin only)"""
        success = set_trade_name(str(user.id), name)
        
        if success:
            await interaction.response.send_message(
                f"Changed {user.mention}'s trade name to: **{name}**"
            )
        else:
            await interaction.response.send_message(
                "Error changing trade name.",
                ephemeral=True
            )
    
    @app_commands.command(name="accept", description="Accept a listing at the listed price")
    @app_commands.describe(trade_id="The ID of the trade to accept")
    async def accept(self, interaction: discord.Interaction, trade_id: int):
        """Accept a trade at the listed price"""
        buyer_id = str(interaction.user.id)
        
        # Check if buyer has trade name set
        if not has_trade_name(buyer_id):
            await interaction.response.send_message(
                "You must set your trade name first! Use `/settradename`",
                ephemeral=True
            )
            return
        
        # Get the trade
        trade = get_trade_by_id(trade_id)
        
        if not trade:
            await interaction.response.send_message(
                f"Trade ID `{trade_id}` not found.",
                ephemeral=True
            )
            return
        
        seller_id, seller_username, trade_type, item_name, quantity, price, notes, timestamp, active = trade
        
        # Check if trade is active
        if not active:
            await interaction.response.send_message(
                "This trade is no longer active.",
                ephemeral=True
            )
            return
        
        # Check if it's a WTS listing
        if trade_type != 'WTS':
            await interaction.response.send_message(
                "You can only accept WTS (sell) listings!",
                ephemeral=True
            )
            return
        
        # Check if price is set
        if not price:
            await interaction.response.send_message(
                "This listing doesn't have a set price. Use `/offer` to make an offer instead.",
                ephemeral=True
            )
            return
        
        # Check if buyer is the seller
        if buyer_id == seller_id:
            await interaction.response.send_message(
                "You can't accept your own listing!",
                ephemeral=True
            )
            return
        
        # Check if there's a pending offer
        pending_offer = get_pending_offer_for_trade(trade_id)
        if pending_offer:
            await interaction.response.send_message(
                "This trade has a pending offer. Wait for it to be resolved first.",
                ephemeral=True
            )
            return
        
        # Complete the trade
        success = complete_trade(
            trade_id,
            buyer_id,
            interaction.user.name,
            price,
            "direct_accept"
        )
        
        if success:
            seller_tradename = get_trade_name(seller_id)
            buyer_tradename = get_trade_name(buyer_id)
            
            embed = discord.Embed(
                title="Trade Accepted!",
                description=f"<@{buyer_id}> accepted the listing from <@{seller_id}>",
                color=discord.Color.green()
            )
            embed.add_field(name="Item", value=f"{quantity}x {item_name}", inline=True)
            embed.add_field(name="Price", value=price, inline=True)
            embed.add_field(name="Seller In-Game", value=seller_tradename, inline=True)
            embed.add_field(name="Buyer In-Game", value=buyer_tradename, inline=True)
            embed.add_field(
                name="Next Steps",
                value=f"<@{buyer_id}> contact <@{seller_id}> in-game to complete the trade!",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Send DM to seller
            try:
                seller = await self.bot.fetch_user(int(seller_id))
                dm_embed = discord.Embed(
                    title="Your listing was accepted!",
                    description=f"{interaction.user.name} accepted your listing at {price}!",
                    color=discord.Color.green()
                )
                dm_embed.add_field(name="Item", value=f"{quantity}x {item_name}")
                dm_embed.add_field(name="Buyer In-Game Name", value=buyer_tradename)
                dm_embed.add_field(name="Your In-Game Name", value=seller_tradename)
                dm_embed.add_field(
                    name="Next Steps",
                    value=f"**{buyer_tradename}** will contact you in-game!",
                    inline=False
                )
                await seller.send(embed=dm_embed)
            except:
                pass  # DMs might be disabled
        else:
            await interaction.response.send_message(
                "Error completing trade. Please try again.",
                ephemeral=True
            )
    
    @app_commands.command(name="offer", description="Make an offer on a listing")
    @app_commands.describe(
        trade_id="The ID of the trade to make an offer on",
        offer="Your offer amount (e.g., 90g, 1.5mg)",
        message="Optional message to the seller"
    )
    async def offer(self, interaction: discord.Interaction, trade_id: int, offer: str, message: str = None):
        """Make an offer on a trade"""
        buyer_id = str(interaction.user.id)
        
        # Check if buyer has trade name set
        if not has_trade_name(buyer_id):
            await interaction.response.send_message(
                "You must set your trade name first! Use `/settradename`",
                ephemeral=True
            )
            return
        
        # Get the trade
        trade = get_trade_by_id(trade_id)
        
        if not trade:
            await interaction.response.send_message(
                f"Trade ID `{trade_id}` not found.",
                ephemeral=True
            )
            return
        
        seller_id, seller_username, trade_type, item_name, quantity, price, notes, timestamp, active = trade
        
        # Check if trade is active
        if not active:
            await interaction.response.send_message(
                "This trade is no longer active.",
                ephemeral=True
            )
            return
        
        # Check if it's a WTS listing
        if trade_type != 'WTS':
            await interaction.response.send_message(
                "You can only make offers on WTS (sell) listings!",
                ephemeral=True
            )
            return
        
        # Check if buyer is the seller
        if buyer_id == seller_id:
            await interaction.response.send_message(
                "You can't make an offer on your own listing!",
                ephemeral=True
            )
            return
        
        # Check if there's already a pending offer
        pending_offer = get_pending_offer_for_trade(trade_id)
        if pending_offer:
            await interaction.response.send_message(
                "This trade already has a pending offer. Wait for it to be resolved first.",
                ephemeral=True
            )
            return
        
        # Create the offer
        offer_id = create_offer(
            trade_id,
            buyer_id,
            interaction.user.name,
            offer,
            message
        )
        
        # Create embed for the offer
        embed = discord.Embed(
            title="New Trade Offer!",
            description=f"<@{buyer_id}> made an offer on trade `#{trade_id}`",
            color=discord.Color.blue()
        )
        embed.add_field(name="Item", value=f"{quantity}x {item_name}", inline=True)
        if price:
            embed.add_field(name="Listed Price", value=price, inline=True)
        embed.add_field(name="Offer Amount", value=offer, inline=True)
        if message:
            embed.add_field(name="Message", value=message, inline=False)
        embed.add_field(
            name="Seller",
            value=f"<@{seller_id}> - Use the buttons below to accept or decline",
            inline=False
        )
        
        # Create the view with buttons
        view = OfferView(
            offer_id,
            trade_id,
            seller_id,
            buyer_id,
            interaction.user.name,
            offer
        )
        
        await interaction.response.send_message(embed=embed, view=view)
        
        # Send DM to seller
        try:
            seller = await self.bot.fetch_user(int(seller_id))
            dm_embed = discord.Embed(
                title="You received a trade offer!",
                description=f"{interaction.user.name} made an offer on your listing!",
                color=discord.Color.blue()
            )
            dm_embed.add_field(name="Item", value=f"{quantity}x {item_name}")
            dm_embed.add_field(name="Your Listed Price", value=price or "No price set")
            dm_embed.add_field(name="Their Offer", value=offer)
            if message:
                dm_embed.add_field(name="Message", value=message, inline=False)
            dm_embed.add_field(
                name="Action Required",
                value="Check the channel to accept or decline this offer!",
                inline=False
            )
            await seller.send(embed=dm_embed)
        except:
            pass  # DMs might be disabled

# Setup function for cog
async def setup(bot):
    await bot.add_cog(Offers(bot))