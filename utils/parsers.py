import re
from typing import Tuple, Optional

def parse_listing(text: str) -> Tuple[Optional[str], int, Optional[str], Optional[str]]:
    """
    Parse listing format: item | price | notes
    
    Returns:
        (item_name, quantity, price, notes)
    
    Examples:
        "gloves of Feroxi | 1.5mg | perfect stats" 
            -> ("gloves of Feroxi", 1, "1.5mg", "perfect stats")
        
        "2x rare sword | 500g"
            -> ("rare sword", 2, "500g", None)
        
        "shield of valor"
            -> ("shield of valor", 1, None, None)
    """
    parts = [p.strip() for p in text.split('|')]
    
    item_name = parts[0] if len(parts) > 0 else None
    price = parts[1] if len(parts) > 1 else None
    notes = parts[2] if len(parts) > 2 else None
    
    # Extract quantity from item name (e.g., "2x gloves" or "2 gloves")
    quantity = 1
    if item_name:
        match = re.match(r'(\d+)\s*[xX×]?\s*(.+)', item_name)
        if match:
            quantity = int(match.group(1))
            item_name = match.group(2).strip()
    
    return item_name, quantity, price, notes
