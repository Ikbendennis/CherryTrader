# Discord Trading Bot

A modular trading system for Discord with **Slash Commands** for easy use!

## 📁 Project Structure

```
discord-trading-bot/
├── bot.py                      # Main bot launcher
├── .env                        # Your bot token (create this)
├── requirements.txt            # Python dependencies
├── trades.db                   # Database (auto-created)
│
├── cogs/                       # Command modules (plugins)
│   ├── __init__.py
│   ├── trading.py              # /sell, /buy commands
│   ├── market.py               # /search, /market, /mylistings, /remove
│   ├── offers.py               # /accept, /offer, /settradename (Phase 2)
│   └── admin.py                # /clearmarket, /ping
│
├── database/                   # Database layer
│   ├── __init__.py
│   └── db_manager.py           # All database operations
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   └── parsers.py              # Parse item listings
│
└── config/                     # Configuration (for future use)
    └── (item validation files will go here in Phase 3)
```

## ✨ Phase 1 & 2 Features - NOW WITH SLASH COMMANDS!

### Trade Names (Phase 2 - NEW!)
- `/settradename` - Set your in-game name (required before trading)
  - `name`: Your in-game character/account name
  
- `/changetradename` - Change a user's trade name (Admin only)
  - `user`: The user to change
  - `name`: New trade name

### Listing Commands (Phase 1)
- `/sell` - List an item for sale
  - `item`: The item you want to sell (e.g., "2x gloves of Feroxi")
  - `price`: Your asking price (optional)
  - `notes`: Additional notes (optional)

- `/buy` - Post a buy order
  - `item`: The item you want to buy
  - `offer`: Your offer price (optional)
  - `notes`: Additional notes (optional)

### Trading Commands (Phase 2 - NEW!)
- `/accept` - Accept a listing at the listed price
  - `trade_id`: The ID of the trade to accept
  - Only works on listings WITH a price set
  - Both parties notified, trade completed automatically

- `/offer` - Make an offer on any listing
  - `trade_id`: The ID of the trade
  - `offer`: Your offer amount (e.g., "90g")
  - `message`: Optional message to seller
  - Only one pending offer per trade at a time
  - Seller gets Accept/Decline buttons

### Search & Browse (Phase 1)
- `/search` - Search for specific items
  - `query`: Item name to search for

- `/market` - View all active trades
  - `filter`: Filter by WTS or WTB (optional)

- `/mylistings` - View your active trades (private response)

**Management:**
- `/tradeinfo` - Get detailed info about a trade
  - `trade_id`: The ID of the trade

- `/remove` - Remove your listing
  - `trade_id`: The ID of the trade to remove

**Admin:**
- `/clearmarket` - Clear all trades (Admin only)
- `/ping` - Check bot responsiveness

## 🚀 How to Run the Bot

### First Time Setup

1. **Make sure you're in the bot directory:**
   ```bash
   cd discord-trading-bot
   ```

2. **Copy your .env file:**
   ```bash
   cp env.example .env
   ```
   Then edit `.env` and add your bot token

3. **Install dependencies (if needed):**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Bot

**Simple method:**
```bash
python bot.py
```

**If you have an old bot still running:**
1. Stop the old bot first (Ctrl+C in its terminal)
2. Then run the new one:
   ```bash
   python bot.py
   ```

You should see:
```
Initializing database...
[OK] Database ready!
Loading command modules...
[OK] Loaded: cogs.trading
[OK] Loaded: cogs.market
[OK] Loaded: cogs.admin
Synced X slash command(s)
==================================================
BotName has connected to Discord!
Bot is in 1 server(s)
Trading system initialized!
==================================================
```

### Restarting After Changes

If you modify any code:
1. Stop the bot (Ctrl+C)
2. Run `python bot.py` again

## 📝 Using Slash Commands

Slash commands are super easy! Just type `/` in Discord and:

1. **Discord will show you all available commands**
2. **Click on a command to see required and optional parameters**
3. **Autocomplete will help you fill in the fields**
4. **Press Enter to submit**

**Examples:**
```
# First time setup - set your in-game name
/settradename name:MyGameName

# List items
/sell item:gloves of Feroxi price:1.5mg notes:perfect stats
/sell item:2x rare sword price:500g
/buy item:shield of valor offer:2mg notes:willing to negotiate

# Trading
/accept trade_id:42                          # Accept at listed price
/offer trade_id:42 offer:90g message:Can you do 90g?  # Make an offer

# Browsing
/search query:gloves
/market filter:WTS
/mylistings
/tradeinfo trade_id:42
/remove trade_id:42
```

## 🎯 Why Slash Commands?

**Benefits:**
- ✅ **User-friendly**: Discord shows you what to fill in
- ✅ **Autocomplete**: No need to remember syntax
- ✅ **Clean**: No more `!command | field | field` parsing
- ✅ **Mobile-friendly**: Easier to use on phones
- ✅ **Modern**: The new Discord standard

## 🎯 Why This Structure?

**Benefits:**
- ✅ **Modular**: Each feature in its own file
- ✅ **Scalable**: Easy to add Phase 2 & 3 features
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Organized**: Database, commands, and utils separated

**Where to add new features:**
- New commands → Create a new cog in `cogs/`
- Database functions → Add to `database/db_manager.py`
- Utility functions → Add to `utils/`
- Config files → Put in `config/`

## 🔜 Next Phases

**Phase 2 - Trade Offers:**
- Create `cogs/offers.py`
- `/offer` command to propose trades
- Buttons to accept/decline offers
- Direct messaging between traders

**Phase 3 - Validation & Price History:**
- Create `utils/validators.py`
- Add `config/items.json` for valid items
- Create `utils/price_history.py` for price tracking
- Price suggestions based on history

## ❓ Troubleshooting

**"ModuleNotFoundError: No module named 'cogs'"**
- Make sure you're running `python bot.py` from inside the `discord-trading-bot/` folder

**"DISCORD_BOT_TOKEN not found"**
- Make sure you have a `.env` file in the `discord-trading-bot/` folder with your token

**Slash commands not showing up**
- Wait a few minutes after starting the bot (Discord needs to sync)
- If still not working, kick and re-invite the bot to your server
- Make sure the bot has `applications.commands` scope when inviting

**Old trades not showing up**
- Copy your old `trades.db` file into the `discord-trading-bot/` folder

**Commands not working**
- Make sure all the cogs loaded successfully (check the startup messages)
- Check that you see "Synced X slash command(s)" in the startup output

**Encoding errors on Windows**
- The bot now handles this automatically, but if you still see issues, run:
  ```bash
  chcp 65001
  ```
  before running the bot
