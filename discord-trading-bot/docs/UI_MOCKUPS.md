# Trading Bot - UI Mockups

## Discord Embed Examples

This document shows exactly how the Discord bot interface should look for all interactions.

---

## Table of Contents
1. [Command Inputs](#command-inputs)
2. [Listing Displays](#listing-displays)
3. [Market Browsing](#market-browsing)
4. [Trade Notifications](#trade-notifications)
5. [Offer System](#offer-system)
6. [Confirmation Status](#confirmation-status)
7. [Trade Completion](#trade-completion)
8. [User Listings](#user-listings)

---

## 1. Command Inputs

### UI-001: Sell Listing Creation

**Command Input:**
```
User types: /sell
Discord shows autocomplete with fields:
┌──────────────────────────────────────┐
│ /sell                                │
├──────────────────────────────────────┤
│ item*        [Dropdown/Autocomplete] │
│              Type to search...       │
├──────────────────────────────────────┤
│ quantity*    [Number field]          │
│              1                       │
├──────────────────────────────────────┤
│ price_per_unit [Text field]          │
│              e.g., 100g              │
├──────────────────────────────────────┤
│ notes        [Text field]            │
│              Optional                │
├──────────────────────────────────────┤
│          [Submit] [Cancel]           │
└──────────────────────────────────────┘
```

**Bot Response (Success):**
```
┌─────────────────────────────────────────────────┐
│ ✅ Trade Listed                                 │
├─────────────────────────────────────────────────┤
│ Seller:    @Alice                               │
│ IGN:       AliceTheWarrior                      │
│                                                 │
│ Item:      Sword of Fire                        │
│ Quantity:  5 available                          │
│ Price:     100g per unit (500g total)           │
│ Notes:     Perfect condition, max stats         │
│                                                 │
│ Trade ID:  #42                                  │
│                                                 │
│ Use /accept 42 <quantity> to buy this item     │
│ Or /offer 42 <quantity> <price> to make offer  │
├─────────────────────────────────────────────────┤
│ Listed 2 minutes ago                            │
└─────────────────────────────────────────────────┘
```

---

## 2. Listing Displays

### UI-002: Item Listing (With Price)

```
┌─────────────────────────────────────────────────┐
│ 🏪 WTS - For Sale                               │
├─────────────────────────────────────────────────┤
│ Seller:    @Alice (AliceTheWarrior)             │
│                                                 │
│ 📦 Sword of Fire                                │
│    5x available @ 100g each                     │
│    Total: 500g for all                          │
│                                                 │
│ 📝 Notes: Perfect condition, max stats          │
│                                                 │
│ Trade ID: #42                                   │
├─────────────────────────────────────────────────┤
│ Listed 2 minutes ago                            │
└─────────────────────────────────────────────────┘
```

### UI-003: Item Listing (No Price - Offers Only)

```
┌─────────────────────────────────────────────────┐
│ 🏪 WTS - For Sale (Offers Only)                 │
├─────────────────────────────────────────────────┤
│ Seller:    @Alice (AliceTheWarrior)             │
│                                                 │
│ 📦 Rare Shield                                  │
│    1x available                                 │
│    💰 Price: Make an offer!                     │
│                                                 │
│ 📝 Notes: Ultra rare, best offer takes it       │
│                                                 │
│ Trade ID: #44                                   │
├─────────────────────────────────────────────────┤
│ Use /offer 44 <quantity> <price> to make offer │
│ Listed 10 minutes ago                           │
└─────────────────────────────────────────────────┘
```

### UI-004: Buy Order Listing

```
┌─────────────────────────────────────────────────┐
│ 💰 WTB - Buying                                 │
├─────────────────────────────────────────────────┤
│ Buyer:     @Bob (BobTheTrader)                  │
│                                                 │
│ 📦 Legendary Armor                              │
│    Looking for: 1x                              │
│    Offering:    5000g                           │
│                                                 │
│ 📝 Notes: Must have perfect stats               │
│                                                 │
│ Trade ID: #55                                   │
├─────────────────────────────────────────────────┤
│ Posted 3 hours ago                              │
└─────────────────────────────────────────────────┘
```

---

## 3. Market Browsing

### UI-005: Market Overview

**Command:** `/market filter:WTS`

**Bot Response:**
```
┌─────────────────────────────────────────────────┐
│ 🏪 Trading Market - Items For Sale              │
├─────────────────────────────────────────────────┤
│ [42] Sword of Fire                              │
│      5x @ 100g each | by AliceTheWarrior        │
│      "Perfect condition, max stats"             │
│                                                 │
│ [43] Health Potion                              │
│      20x @ 10g each | by BobTheHealer           │
│                                                 │
│ [44] Rare Shield                                │
│      1x @ Price not set | by CharlieTheDefender │
│      "Make an offer!"                           │
│                                                 │
│ [45] Magic Scroll                               │
│      3x @ 50g each | by DaveTheMage             │
│                                                 │
│ [46] Iron Ore                                   │
│      100x @ 5g each | by MinerSteve             │
│                                                 │
│ ... 15 more listings                            │
├─────────────────────────────────────────────────┤
│ Showing 20 most recent WTS listings             │
│ Use /search <item> to find specific items      │
│ Use /tradeinfo <id> for details                │
└─────────────────────────────────────────────────┘
```

### UI-006: Search Results

**Command:** `/search item:Sword type:WTS`

**Bot Response:**
```
┌─────────────────────────────────────────────────┐
│ 🔍 Search Results: Sword (WTS)                  │
├─────────────────────────────────────────────────┤
│ 🏪 For Sale                                     │
│                                                 │
│ [42] Sword of Fire                              │
│      5x @ 100g each (500g total)                │
│      Seller: AliceTheWarrior                    │
│      Notes: Perfect condition, max stats        │
│      Listed: 5 minutes ago                      │
│                                                 │
│ [48] Sword of Ice                               │
│      2x @ 150g each (300g total)                │
│      Seller: FrostKnight                        │
│      Listed: 1 hour ago                         │
│                                                 │
│ [51] Legendary Sword                            │
│      1x @ Price not set (offers only)           │
│      Seller: EpicWarrior                        │
│      Notes: Ultra rare, best offer              │
│      Listed: 3 hours ago                        │
├─────────────────────────────────────────────────┤
│ 3 result(s) found                               │
│ Use /tradeinfo <id> for more details           │
└─────────────────────────────────────────────────┘
```

### UI-007: Trade Info Detail

**Command:** `/tradeinfo 42`

**Bot Response:**
```
┌─────────────────────────────────────────────────┐
│ 📊 Trade Details - ID: #42                      │
├─────────────────────────────────────────────────┤
│ Type:         WTS (For Sale)                    │
│ Status:       🟢 Active                         │
│                                                 │
│ 📦 Item Details                                 │
│ Item:         Sword of Fire                     │
│ Category:     Weapons > Swords                  │
│ Rarity:       Epic                              │
│ Quantity:     2 of 5 remaining                  │
│ Sold:         3 units                           │
│                                                 │
│ 💰 Pricing                                      │
│ Price:        100g per unit                     │
│ Total Value:  200g (for remaining)              │
│ Avg Market:   95g per unit                      │
│ Status:       Priced above average (+5%)        │
│                                                 │
│ 👤 Seller                                       │
│ Discord:      @AliceTheWarrior                  │
│ IGN:          AliceTheWarrior                   │
│ Trades:       47 completed                      │
│                                                 │
│ 📝 Notes                                        │
│ "Perfect condition, max stats"                  │
│                                                 │
│ 🕐 Timeline                                     │
│ Listed:       2 hours ago                       │
│ Updated:      30 minutes ago (qty reduced)      │
│                                                 │
│ 🔒 Trade Status                                 │
│ Pending Offer: None                             │
│ Can Accept:    Yes                              │
│ Can Offer:     Yes                              │
├─────────────────────────────────────────────────┤
│ /accept 42 <qty>  |  /offer 42 <qty> <price>   │
└─────────────────────────────────────────────────┘
```

---

## 4. Trade Notifications

### UI-008: Trade Accepted (Public Channel)

**After buyer uses:** `/accept 42 3`

**Bot Response:**
```
┌─────────────────────────────────────────────────┐
│ ✅ Trade Accepted!                              │
├─────────────────────────────────────────────────┤
│ @BobTheTrader accepted listing #42              │
│                                                 │
│ Item:         Sword of Fire                     │
│ Quantity:     3 units                           │
│ Price:        100g per unit                     │
│ Total:        300g                              │
│                                                 │
│ 👤 Seller IGN: AliceTheWarrior                  │
│ 👤 Buyer IGN:  BobTheTrader                     │
│                                                 │
│ ⏱️ Both parties must confirm within 24 hours    │
│                                                 │
│ 📌 Next Steps:                                  │
│ 1. Complete the trade in-game                   │
│ 2. Use /confirm 42 after transfer is complete  │
│                                                 │
│ Trade ID: #42-pending                           │
├─────────────────────────────────────────────────┤
│ Created just now                                │
└─────────────────────────────────────────────────┘
```

---

## 5. Offer System

### UI-009: Offer Posted (with Buttons)

**After buyer uses:** `/offer 42 3 80g Would you take 80g each for 3?`

**Bot Response:**
```
┌─────────────────────────────────────────────────┐
│ 💬 New Trade Offer!                             │
├─────────────────────────────────────────────────┤
│ @BobTheTrader made an offer on listing #42      │
│                                                 │
│ Item:          Sword of Fire                    │
│ Quantity:      3 units                          │
│ Listed Price:  100g per unit                    │
│ Offer:         80g per unit (240g total)        │
│                                                 │
│ Message: "Would you take 80g each for 3?"      │
│                                                 │
│ 👤 Seller: @AliceTheWarrior (AliceTheWarrior)   │
│ 👤 Buyer:  @BobTheTrader (BobTheTrader)         │
│                                                 │
│ ⚠️ @AliceTheWarrior - You must respond to this  │
│    offer using the buttons below               │
├─────────────────────────────────────────────────┤
│    [✅ Accept Offer]    [❌ Decline Offer]      │
├─────────────────────────────────────────────────┤
│ Offer expires in 7 days                         │
└─────────────────────────────────────────────────┘
```

### UI-010: Offer Accepted (Buttons Disabled)

**After seller clicks Accept:**
```
┌─────────────────────────────────────────────────┐
│ ✅ Offer Accepted!                              │
├─────────────────────────────────────────────────┤
│ @AliceTheWarrior accepted the offer from        │
│ @BobTheTrader                                   │
│                                                 │
│ Item:         Sword of Fire                     │
│ Quantity:     3 units                           │
│ Final Price:  80g per unit (240g total)         │
│                                                 │
│ 👤 Seller IGN: AliceTheWarrior                  │
│ 👤 Buyer IGN:  BobTheTrader                     │
│                                                 │
│ ⏱️ Both parties must confirm within 24 hours    │
│                                                 │
│ 📌 Next Steps:                                  │
│ 1. Complete the trade in-game                   │
│ 2. Use /confirm 42 after transfer is complete  │
├─────────────────────────────────────────────────┤
│    [  Accepted  ]    [  Declined  ]             │
│      (disabled)        (disabled)               │
├─────────────────────────────────────────────────┤
│ Accepted just now                               │
└─────────────────────────────────────────────────┘
```

### UI-011: Offer Declined (Buttons Disabled)

**After seller clicks Decline:**
```
┌─────────────────────────────────────────────────┐
│ ❌ Offer Declined                               │
├─────────────────────────────────────────────────┤
│ @AliceTheWarrior declined the offer from        │
│ @BobTheTrader                                   │
│                                                 │
│ Item:         Sword of Fire                     │
│ Declined:     80g per unit (240g total)         │
│                                                 │
│ The listing remains active at the original      │
│ price of 100g per unit.                         │
│                                                 │
│ Other buyers can now make offers.               │
├─────────────────────────────────────────────────┤
│    [  Accepted  ]    [  Declined  ]             │
│      (disabled)        (disabled)               │
├─────────────────────────────────────────────────┤
│ Declined just now                               │
└─────────────────────────────────────────────────┘
```

---

## 6. Confirmation Status

### UI-012: My Pending Trades

**Command:** `/mytrades`

**Bot Response:**
```
┌─────────────────────────────────────────────────┐
│ 📋 Your Pending Trades                          │
├─────────────────────────────────────────────────┤
│ Trade #42-pending                               │
│ ├─ Item: 3x Sword of Fire @ 80g each           │
│ ├─ With: AliceTheWarrior                        │
│ ├─ Status: ⏳ Awaiting YOUR confirmation       │
│ └─ Expires: in 22 hours                         │
│                                                 │
│ Trade #38-pending                               │
│ ├─ Item: 10x Health Potion @ 10g each          │
│ ├─ With: CharlieTheHealer                       │
│ ├─ Status: ✅ You confirmed | ⏳ Waiting other  │
│ └─ Expires: in 18 hours                         │
├─────────────────────────────────────────────────┤
│ Use /confirm <id> to confirm a trade           │
└─────────────────────────────────────────────────┘
```

### UI-013: Confirmation Recorded (One Party)

**After first confirmation:**
```
┌─────────────────────────────────────────────────┐
│ ✅ Your Confirmation Recorded                   │
├─────────────────────────────────────────────────┤
│ Trade #42-pending                               │
│                                                 │
│ You have confirmed receipt of:                  │
│ 3x Sword of Fire                                │
│                                                 │
│ ⏳ Waiting for @AliceTheWarrior to confirm      │
│                                                 │
│ The trade will be completed once both parties   │
│ have confirmed.                                 │
│                                                 │
│ Confirmation expires in: 22 hours               │
├─────────────────────────────────────────────────┤
│ Confirmed just now                              │
└─────────────────────────────────────────────────┘
```

---

## 7. Trade Completion

### UI-014: Trade Completed Successfully

**After both parties confirm:**
```
┌─────────────────────────────────────────────────┐
│ 🎉 Trade Completed Successfully!                │
├─────────────────────────────────────────────────┤
│ Trade #42 has been finalized                    │
│                                                 │
│ Item:       3x Sword of Fire                    │
│ Price:      80g per unit (240g total)           │
│                                                 │
│ Seller:     @AliceTheWarrior (AliceTheWarrior)  │
│ Buyer:      @BobTheTrader (BobTheTrader)        │
│                                                 │
│ ✅ Both parties confirmed the trade             │
│                                                 │
│ This trade has been saved to history and will   │
│ be used for market analytics.                   │
├─────────────────────────────────────────────────┤
│ Completed just now                              │
└─────────────────────────────────────────────────┘
```

### UI-015: Trade Disputed (Timeout)

**After confirmation timeout:**
```
┌─────────────────────────────────────────────────┐
│ ⚠️ Trade Confirmation Timeout                   │
├─────────────────────────────────────────────────┤
│ Trade #42 has been marked as DISPUTED           │
│                                                 │
│ Item:       3x Sword of Fire                    │
│ Price:      80g per unit (240g total)           │
│                                                 │
│ Seller:     @AliceTheWarrior                    │
│ Buyer:      @BobTheTrader                       │
│                                                 │
│ Status:                                         │
│ ✅ Buyer confirmed                              │
│ ❌ Seller did NOT confirm within 24 hours       │
│                                                 │
│ The listing quantity has been restored.         │
│ Admins have been notified for review.           │
│                                                 │
│ If you completed this trade in-game, please     │
│ contact an admin for manual resolution.         │
├─────────────────────────────────────────────────┤
│ Expired 5 minutes ago                           │
└─────────────────────────────────────────────────┘
```

---

## 8. User Listings

### UI-016: My Active Listings

**Command:** `/mylistings`

**Bot Response:**
```
┌─────────────────────────────────────────────────┐
│ 📋 AliceTheWarrior's Active Listings            │
├─────────────────────────────────────────────────┤
│ 🏪 Selling                                      │
│                                                 │
│ [42] Sword of Fire                              │
│      2 remaining (3 sold) @ 100g each           │
│      Notes: Perfect condition, max stats        │
│      Listed: 2 hours ago                        │
│                                                 │
│ [50] Magic Potion                               │
│      15x @ 20g each                             │
│      Listed: 1 day ago                          │
│                                                 │
│ 💰 Buying                                       │
│                                                 │
│ [55] Legendary Armor                            │
│      1x @ Offering 5000g                        │
│      Notes: Looking for perfect stats           │
│      Listed: 3 hours ago                        │
├─────────────────────────────────────────────────┤
│ Total: 2 sell listings, 1 buy order             │
│ Use /remove <id> to cancel a listing           │
└─────────────────────────────────────────────────┘
```

### UI-017: Listing Removed

**After:** `/remove 42`

**Bot Response:**
```
┌─────────────────────────────────────────────────┐
│ ✅ Listing Removed                              │
├─────────────────────────────────────────────────┤
│ Your listing has been cancelled:                │
│                                                 │
│ Trade ID:  #42                                  │
│ Item:      Sword of Fire                        │
│ Quantity:  2 remaining                          │
│                                                 │
│ This listing is no longer visible in the market.│
├─────────────────────────────────────────────────┤
│ Removed just now                                │
└─────────────────────────────────────────────────┘
```

---

## Color Scheme Guide

For consistency across all embeds:

- **Success Messages**: Green (#57F287)
  - Trade accepted, offer accepted, confirmations, completions

- **Info Messages**: Blue (#5865F2)
  - Listings, market views, searches, trade info

- **Warning Messages**: Yellow (#FEE75C)
  - Pending confirmations, timeouts approaching

- **Error Messages**: Red (#ED4245)
  - Declined offers, disputes, errors

- **Buying Messages**: Purple (#EB459E)
  - WTB listings

- **Selling Messages**: Orange (#F26522)
  - WTS listings

---

## Emoji Guide

Consistent emoji use across all messages:

- ✅ Success, confirmation, active
- ❌ Error, declined, cancelled
- ⚠️ Warning, attention needed
- 🏪 Market, selling
- 💰 Buying, money
- 📦 Item, package
- 👤 User, player
- 🔍 Search
- 📋 List, inventory
- 💬 Offer, message
- ⏱️ Time, countdown
- 🎉 Celebration, completion
- 📊 Details, info
- 📝 Notes
- 🕐 Time/history

---

## Mobile Considerations

All embeds are designed to be:
- Maximum 6000 characters
- Readable on mobile devices
- Use minimal line breaks
- Clear visual hierarchy
- Important info at top
- Actions/buttons clearly visible
