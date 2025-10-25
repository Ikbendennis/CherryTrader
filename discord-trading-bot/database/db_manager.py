import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

DB_PATH = 'trades.db'

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize the database with required tables"""
    conn = get_connection()
    c = conn.cursor()
    
    # Trades table
    c.execute('''CREATE TABLE IF NOT EXISTS trades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT NOT NULL,
                  username TEXT NOT NULL,
                  trade_type TEXT NOT NULL,
                  item_name TEXT NOT NULL,
                  quantity INTEGER DEFAULT 1,
                  price TEXT,
                  notes TEXT,
                  timestamp TEXT NOT NULL,
                  active INTEGER DEFAULT 1)''')
    
    # Trade names table
    c.execute('''CREATE TABLE IF NOT EXISTS trade_names
                 (user_id TEXT PRIMARY KEY,
                  trade_name TEXT NOT NULL,
                  set_at TEXT NOT NULL)''')
    
    # Offers table
    c.execute('''CREATE TABLE IF NOT EXISTS offers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  trade_id INTEGER NOT NULL,
                  buyer_id TEXT NOT NULL,
                  buyer_username TEXT NOT NULL,
                  offer_amount TEXT NOT NULL,
                  message TEXT,
                  status TEXT DEFAULT 'pending',
                  timestamp TEXT NOT NULL,
                  FOREIGN KEY (trade_id) REFERENCES trades (id))''')
    
    # Completed trades table
    c.execute('''CREATE TABLE IF NOT EXISTS completed_trades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original_trade_id INTEGER,
                  seller_id TEXT NOT NULL,
                  seller_username TEXT NOT NULL,
                  seller_tradename TEXT NOT NULL,
                  buyer_id TEXT NOT NULL,
                  buyer_username TEXT NOT NULL,
                  buyer_tradename TEXT NOT NULL,
                  item_name TEXT NOT NULL,
                  quantity INTEGER,
                  final_price TEXT,
                  completion_type TEXT,
                  completed_at TEXT NOT NULL)''')
    
    conn.commit()
    conn.close()

def add_trade(user_id: str, username: str, trade_type: str, item_name: str, 
              quantity: int, price: Optional[str], notes: Optional[str]) -> int:
    """Add a new trade to the database"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''INSERT INTO trades (user_id, username, trade_type, item_name, quantity, price, notes, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, username, trade_type, item_name, quantity, price, notes, datetime.now().isoformat()))
    
    trade_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return trade_id

def search_trades(query: str) -> List[Tuple]:
    """Search for trades by item name"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''SELECT id, user_id, username, trade_type, item_name, quantity, price, notes
                 FROM trades 
                 WHERE active = 1 AND item_name LIKE ?
                 ORDER BY timestamp DESC''',
              (f'%{query}%',))
    
    results = c.fetchall()
    conn.close()
    
    return results

def get_all_trades(trade_type: Optional[str] = None, limit: int = 20) -> List[Tuple]:
    """Get all active trades, optionally filtered by type"""
    conn = get_connection()
    c = conn.cursor()
    
    if trade_type and trade_type.upper() in ['WTS', 'WTB']:
        c.execute('''SELECT id, username, trade_type, item_name, quantity, price, timestamp
                     FROM trades 
                     WHERE active = 1 AND trade_type = ?
                     ORDER BY timestamp DESC
                     LIMIT ?''',
                  (trade_type.upper(), limit))
    else:
        c.execute('''SELECT id, username, trade_type, item_name, quantity, price, timestamp
                     FROM trades 
                     WHERE active = 1
                     ORDER BY timestamp DESC
                     LIMIT ?''',
                  (limit,))
    
    results = c.fetchall()
    conn.close()
    
    return results

def get_user_trades(user_id: str) -> List[Tuple]:
    """Get all active trades for a specific user"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''SELECT id, trade_type, item_name, quantity, price, notes
                 FROM trades 
                 WHERE active = 1 AND user_id = ?
                 ORDER BY timestamp DESC''',
              (user_id,))
    
    results = c.fetchall()
    conn.close()
    
    return results

def get_trade_by_id(trade_id: int) -> Optional[Tuple]:
    """Get a specific trade by ID"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''SELECT user_id, username, trade_type, item_name, quantity, price, notes, timestamp, active
                 FROM trades 
                 WHERE id = ?''',
              (trade_id,))
    
    result = c.fetchone()
    conn.close()
    
    return result

def remove_trade(trade_id: int, user_id: str) -> Tuple[bool, str]:
    """Remove a trade (mark as inactive)"""
    conn = get_connection()
    c = conn.cursor()
    
    # Check if trade exists and belongs to user
    c.execute('SELECT user_id, active FROM trades WHERE id = ?', (trade_id,))
    result = c.fetchone()
    
    if not result:
        conn.close()
        return False, "Trade not found"
    
    owner_id, active = result
    
    if owner_id != user_id:
        conn.close()
        return False, "You can only remove your own trades"
    
    if not active:
        conn.close()
        return False, "Trade is already closed"
    
    # Mark as inactive
    c.execute('UPDATE trades SET active = 0 WHERE id = ?', (trade_id,))
    conn.commit()
    conn.close()
    
    return True, "Trade removed successfully"

def clear_all_trades() -> int:
    """Clear all active trades (admin function)"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('UPDATE trades SET active = 0 WHERE active = 1')
    rows_affected = c.rowcount
    
    conn.commit()
    conn.close()
    
    return rows_affected

# Trade Name Functions
def set_trade_name(user_id: str, trade_name: str) -> bool:
    """Set a user's trade name"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute('''INSERT OR REPLACE INTO trade_names (user_id, trade_name, set_at)
                     VALUES (?, ?, ?)''',
                  (user_id, trade_name, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def get_trade_name(user_id: str) -> Optional[str]:
    """Get a user's trade name"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('SELECT trade_name FROM trade_names WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else None

def has_trade_name(user_id: str) -> bool:
    """Check if a user has set their trade name"""
    return get_trade_name(user_id) is not None

# Offer Functions
def create_offer(trade_id: int, buyer_id: str, buyer_username: str, 
                offer_amount: str, message: Optional[str]) -> int:
    """Create a new offer on a trade"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''INSERT INTO offers (trade_id, buyer_id, buyer_username, offer_amount, message, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (trade_id, buyer_id, buyer_username, offer_amount, message, datetime.now().isoformat()))
    
    offer_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return offer_id

def get_pending_offer_for_trade(trade_id: int) -> Optional[Tuple]:
    """Get the pending offer for a trade (if any)"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''SELECT id, buyer_id, buyer_username, offer_amount, message, timestamp
                 FROM offers
                 WHERE trade_id = ? AND status = 'pending'
                 LIMIT 1''',
              (trade_id,))
    
    result = c.fetchone()
    conn.close()
    
    return result

def update_offer_status(offer_id: int, status: str) -> bool:
    """Update an offer's status (accepted/declined)"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute('UPDATE offers SET status = ? WHERE id = ?', (status, offer_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def complete_trade(trade_id: int, buyer_id: str, buyer_username: str, 
                  final_price: str, completion_type: str) -> bool:
    """Mark a trade as completed and save to history"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # Get the original trade details
        c.execute('''SELECT user_id, username, item_name, quantity
                     FROM trades WHERE id = ?''', (trade_id,))
        trade = c.fetchone()
        
        if not trade:
            conn.close()
            return False
        
        seller_id, seller_username, item_name, quantity = trade
        
        # Get trade names
        seller_tradename = get_trade_name(seller_id) or "Unknown"
        buyer_tradename = get_trade_name(buyer_id) or "Unknown"
        
        # Insert into completed trades
        c.execute('''INSERT INTO completed_trades 
                     (original_trade_id, seller_id, seller_username, seller_tradename,
                      buyer_id, buyer_username, buyer_tradename, item_name, quantity,
                      final_price, completion_type, completed_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (trade_id, seller_id, seller_username, seller_tradename,
                   buyer_id, buyer_username, buyer_tradename, item_name, quantity,
                   final_price, completion_type, datetime.now().isoformat()))
        
        # Mark original trade as inactive
        c.execute('UPDATE trades SET active = 0 WHERE id = ?', (trade_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False
