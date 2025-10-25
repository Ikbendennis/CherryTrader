# Trading Bot - Use Cases Documentation

## Table of Contents
- [Actors](#actors)
- [UC-001: Set Trade Name](#uc-001-set-trade-name)
- [UC-002: Change Trade Name (Admin)](#uc-002-change-trade-name-admin)
- [UC-003: Create Sell Listing](#uc-003-create-sell-listing)
- [UC-004: Create Buy Order](#uc-004-create-buy-order)
- [UC-005: Accept Listing at Listed Price](#uc-005-accept-listing-at-listed-price)
- [UC-006: Make Offer on Listing](#uc-006-make-offer-on-listing)
- [UC-007: Accept Offer](#uc-007-accept-offer)
- [UC-008: Decline Offer](#uc-008-decline-offer)
- [UC-009: Confirm Trade Completion](#uc-009-confirm-trade-completion)
- [UC-010: Search Market](#uc-010-search-market)
- [UC-011: View Market](#uc-011-view-market)
- [UC-012: View My Listings](#uc-012-view-my-listings)
- [UC-013: View My Pending Trades](#uc-013-view-my-pending-trades)
- [UC-014: Remove Listing](#uc-014-remove-listing)
- [UC-015: Clear Market (Admin)](#uc-015-clear-market-admin)
- [UC-016: View Trade Info](#uc-016-view-trade-info)

---

## Actors
- **Trader**: Any user who wants to buy or sell items
- **Admin**: Server administrator with elevated permissions
- **System**: The Discord bot

---

## UC-001: Set Trade Name

**Primary Actor**: Trader  
**Scope**: User Profile Management  
**Level**: User Goal  

**Preconditions**:
- User is a member of the Discord server
- User has not previously set a trade name

**Main Success Scenario**:
1. Trader invokes `/settradename` command with their in-game name
2. System validates that trade name is not already set
3. System saves the trade name to database
4. System confirms successful registration
5. Trader can now create listings and make offers

**Extensions (Alternate Flows)**:
- 2a. Trade name already exists for this user
  - 2a1. System displays error message
  - 2a2. System instructs user to contact admin to change name
  - Use case ends

**Postconditions**:
- Trade name is stored in database associated with user ID
- User can participate in trading activities

---

## UC-002: Change Trade Name (Admin)

**Primary Actor**: Admin  
**Scope**: User Profile Management  
**Level**: User Goal  

**Preconditions**:
- Actor has administrator permissions
- Target user exists in the system

**Main Success Scenario**:
1. Admin invokes `/changetradename` with target user and new name
2. System validates admin permissions
3. System updates user's trade name in database
4. System confirms change to admin
5. System notifies target user of name change

**Extensions**:
- 2a. User lacks admin permissions
  - 2a1. System displays permission denied error
  - Use case ends

**Postconditions**:
- User's trade name is updated in database
- All future trades display new name

---

## UC-003: Create Sell Listing

**Primary Actor**: Trader (Seller)  
**Scope**: Listing Management  
**Level**: User Goal  

**Preconditions**:
- Seller has set their trade name (UC-001)
- Item exists in valid items database

**Main Success Scenario**:
1. Seller invokes `/sell` command with item, quantity, and optional price per unit
2. System validates seller has trade name
3. System validates item exists in items database
4. System validates quantity is positive integer
5. System creates listing with unique trade ID
6. System posts listing in channel
7. Listing is now visible in market search

**Extensions**:
- 2a. Seller has no trade name
  - 2a1. System prompts to set trade name first
  - Use case ends
- 3a. Item not in valid items list
  - 3a1. System displays error with similar item suggestions
  - Use case ends
- 4a. Invalid quantity
  - 4a1. System displays validation error
  - Use case ends

**Postconditions**:
- New listing exists with status "active"
- Listing is searchable in market
- Seller can manage this listing

**Special Requirements**:
- Item selection should use autocomplete/dropdown to prevent typos
- Quantity must be greater than 0
- Price per unit is optional (offers only if not specified)

---

## UC-004: Create Buy Order

**Primary Actor**: Trader (Buyer)  
**Scope**: Listing Management  
**Level**: User Goal  

**Preconditions**:
- Buyer has set their trade name (UC-001)
- Item exists in valid items database

**Main Success Scenario**:
1. Buyer invokes `/buy` command with item, quantity, and optional offer per unit
2. System validates buyer has trade name
3. System validates item exists in items database
4. System validates quantity is positive integer
5. System creates buy order with unique trade ID
6. System posts buy order in channel
7. Buy order is now visible in market search

**Extensions**:
- Similar to UC-003

**Postconditions**:
- New buy order exists with status "active"
- Buy order is searchable in market
- Buyer can manage this order

**Business Rules**:
- Buy orders help sellers gauge market demand and pricing

---

## UC-005: Accept Listing at Listed Price

**Primary Actor**: Trader (Buyer)  
**Scope**: Trade Execution  
**Level**: User Goal  

**Preconditions**:
- Buyer has set their trade name (UC-001)
- Target listing exists and is active
- Listing has price per unit specified
- No pending offers on the listing

**Main Success Scenario**:
1. Buyer invokes `/accept` with trade ID and desired quantity
2. System validates listing exists and is active
3. System validates listing has price set
4. System validates no pending offers exist
5. System validates requested quantity ≤ available quantity
6. System calculates total price (quantity × price_per_unit)
7. System creates pending trade record
8. System notifies both parties with trade details and in-game names
9. Both parties must confirm trade completion (UC-009)

**Extensions**:
- 2a. Listing not found or inactive
  - 2a1. System displays error
  - Use case ends
- 3a. Listing has no price set
  - 3a1. System prompts buyer to use `/offer` instead
  - Use case ends
- 4a. Pending offer exists
  - 4a1. System informs buyer to wait for offer resolution
  - Use case ends
- 5a. Requested quantity exceeds available
  - 5a1. System displays available quantity
  - Use case ends
- 5b. Buyer is the seller
  - 5b1. System displays error (cannot trade with self)
  - Use case ends

**Postconditions**:
- If quantity < total listed:
  - Listing quantity reduced by accepted amount
  - Listing remains active with reduced quantity
- If quantity = total listed:
  - Listing marked as pending (not visible in market during confirmation period)
- Pending trade created awaiting confirmation
- Both parties notified

---

## UC-006: Make Offer on Listing

**Primary Actor**: Trader (Buyer)  
**Scope**: Trade Negotiation  
**Level**: User Goal  

**Preconditions**:
- Buyer has set their trade name (UC-001)
- Target listing exists and is active
- No other pending offers on the listing

**Main Success Scenario**:
1. Buyer invokes `/offer` with trade ID, quantity, offer per unit, and optional message
2. System validates listing exists and is active
3. System validates no pending offers exist on this listing
4. System validates requested quantity ≤ available quantity
5. System validates buyer is not the seller
6. System creates offer record with status "pending"
7. System posts offer in channel with Accept/Decline buttons
8. System notifies seller via channel
9. Seller responds via buttons (UC-007 or UC-008)

**Extensions**:
- 2a. Listing not found or inactive
  - Use case ends
- 3a. Another offer is pending
  - 3a1. System informs buyer to wait
  - Use case ends
- 4a. Quantity exceeds available
  - Use case ends
- 5a. Buyer is the seller
  - Use case ends

**Postconditions**:
- Offer record created with status "pending"
- Listing temporarily locked (no other offers possible)
- Seller can accept or decline

**Business Rules**:
- Only one pending offer per listing at a time
- Offers expire after configured period (7-30 days)

---

## UC-007: Accept Offer

**Primary Actor**: Trader (Seller)  
**Scope**: Trade Negotiation  
**Level**: User Goal  

**Preconditions**:
- Seller has pending offer on their listing (UC-006)
- Offer has not expired

**Main Success Scenario**:
1. Seller clicks "Accept" button on offer
2. System validates seller is the listing owner
3. System validates offer is still pending
4. System calculates total price (quantity × offer_per_unit)
5. System updates offer status to "accepted"
6. System creates pending trade record
7. System updates listing quantity (reduce by offered amount)
8. System notifies both parties with trade details and in-game names
9. Both parties must confirm trade completion (UC-009)

**Extensions**:
- 2a. User is not the seller
  - 2a1. System displays permission error
  - Use case ends
- 3a. Offer expired or already resolved
  - Use case ends

**Postconditions**:
- Same as UC-005 postconditions
- Offer marked as "accepted"

---

## UC-008: Decline Offer

**Primary Actor**: Trader (Seller)  
**Scope**: Trade Negotiation  
**Level**: User Goal  

**Preconditions**:
- Seller has pending offer on their listing (UC-006)

**Main Success Scenario**:
1. Seller clicks "Decline" button on offer
2. System validates seller is the listing owner
3. System updates offer status to "declined"
4. System notifies buyer of declination
5. Listing unlocked (others can now make offers)
6. Listing remains active with original quantity

**Extensions**:
- 2a. User is not the seller
  - Use case ends

**Postconditions**:
- Offer marked as "declined"
- Listing unlocked for new offers
- Listing remains active

---

## UC-009: Confirm Trade Completion

**Primary Actor**: Trader (Buyer or Seller)  
**Scope**: Trade Execution  
**Level**: User Goal  

**Preconditions**:
- Trade has been accepted (UC-005 or UC-007)
- Trade status is "pending_confirmation"
- In-game item transfer has occurred
- Confirmation period has not expired (24 hours)

**Main Success Scenario**:
1. Trader invokes `/confirm` with trade ID
2. System validates trader is party to this trade
3. System validates trade is in pending_confirmation status
4. System marks trader's confirmation
5. System checks if both parties have confirmed
6. If both confirmed:
   - 6a. System finalizes trade
   - 6b. System saves to completed trades history
   - 6c. System removes listing (if fully sold) or updates quantity
   - 6d. System notifies both parties of successful completion
7. If only one confirmed:
   - 7a. System notifies other party to confirm
   - 7b. Trade remains in pending status

**Extensions**:
- 1a. Confirmation period expired
  - 1a1. System marks trade as "disputed"
  - 1a2. System notifies admins for review
  - Use case ends
- 2a. User not party to trade
  - 2a1. System displays permission error
  - Use case ends
- 3a. Trade already confirmed or cancelled
  - Use case ends

**Postconditions (both confirmed)**:
- Trade marked as "completed"
- Trade saved to completed_trades table with timestamp
- Listing removed or quantity reduced
- Trade history updated for metrics

**Business Rules**:
- Both parties must confirm within 24 hours
- In-game transfer happens outside system (no items in bot)
- Failed confirmations escalate to admin review

---

## UC-010: Search Market

**Primary Actor**: Trader  
**Scope**: Market Browsing  
**Level**: User Goal  

**Preconditions**:
- User is member of Discord server

**Main Success Scenario**:
1. Trader invokes `/search` with item name and optional type filter (WTS/WTB)
2. System queries database for active listings matching criteria
3. System formats results with trade IDs, quantities, prices, sellers
4. System displays results to trader (up to 20 results)
5. Trader can view details or take action on listings

**Extensions**:
- 2a. No results found
  - 2a1. System displays "no results" message
  - Use case ends
- 2b. More than 20 results
  - 2b1. System displays first 20 with pagination info
  - 2b2. System suggests narrowing search

**Postconditions**:
- Trader has visibility of relevant market listings

---

## UC-011: View Market

**Primary Actor**: Trader  
**Scope**: Market Browsing  
**Level**: User Goal  

**Preconditions**:
- Active listings exist in database

**Main Success Scenario**:
1. Trader invokes `/market` with optional filter (WTS/WTB/ALL)
2. System retrieves most recent 20 active listings matching filter
3. System formats and displays listings grouped by type
4. Trader can view details or take action

**Extensions**:
- Similar to UC-010

**Postconditions**:
- Trader has overview of market activity

---

## UC-012: View My Listings

**Primary Actor**: Trader  
**Scope**: Listing Management  
**Level**: User Goal  

**Preconditions**:
- Trader has created listings

**Main Success Scenario**:
1. Trader invokes `/mylistings`
2. System retrieves all active listings owned by trader
3. System displays listings with trade IDs, items, quantities, prices
4. Trader can manage their listings

**Extensions**:
- 1a. Trader has no active listings
  - 1a1. System displays "no listings" message

**Postconditions**:
- Trader has visibility of their active listings

---

## UC-013: View My Pending Trades

**Primary Actor**: Trader  
**Scope**: Trade Management  
**Level**: User Goal  

**Preconditions**:
- Trader has trades awaiting confirmation

**Main Success Scenario**:
1. Trader invokes `/mytrades`
2. System retrieves all pending trades involving trader
3. System displays trades with confirmation status
4. System highlights trades needing trader's confirmation
5. Trader can confirm pending trades

**Extensions**:
- 1a. No pending trades
  - 1a1. System displays "no pending trades" message

**Postconditions**:
- Trader aware of trades requiring action

---

## UC-014: Remove Listing

**Primary Actor**: Trader  
**Scope**: Listing Management  
**Level**: User Goal  

**Preconditions**:
- Trader owns the target listing
- Listing is active
- No pending offers or trades on listing

**Main Success Scenario**:
1. Trader invokes `/remove` with trade ID
2. System validates trader owns the listing
3. System validates listing is active
4. System validates no pending offers/trades
5. System marks listing as inactive
6. System confirms removal to trader

**Extensions**:
- 2a. Trader doesn't own listing
  - 2a1. System displays permission error
  - Use case ends
- 3a. Listing already inactive
  - Use case ends
- 4a. Pending offers/trades exist
  - 4a1. System displays error
  - 4a2. System instructs to resolve pending items first
  - Use case ends

**Postconditions**:
- Listing marked as inactive
- Listing no longer visible in market
- Listing data retained for history

---

## UC-015: Clear Market (Admin)

**Primary Actor**: Admin  
**Scope**: Market Management  
**Level**: User Goal  

**Preconditions**:
- Actor has administrator permissions

**Main Success Scenario**:
1. Admin invokes `/clearmarket`
2. System validates admin permissions
3. System prompts for confirmation
4. Admin confirms action
5. System marks all active listings as inactive
6. System reports number of listings cleared

**Extensions**:
- 2a. Insufficient permissions
  - Use case ends
- 4a. Admin cancels
  - Use case ends

**Postconditions**:
- All active listings marked inactive
- Market appears empty
- Historical data retained

**Business Rules**:
- Use for market resets or testing
- Does not affect completed trade history

---

## UC-016: View Trade Info

**Primary Actor**: Trader  
**Scope**: Information Retrieval  
**Level**: User Goal  

**Preconditions**:
- Trade ID exists in system

**Main Success Scenario**:
1. Trader invokes `/tradeinfo` with trade ID
2. System retrieves trade details
3. System displays:
   - Trader name and in-game name
   - Item, quantity, price
   - Status (active/pending/completed)
   - Timestamps
   - Notes
4. Trader can take appropriate action based on info

**Extensions**:
- 2a. Trade ID not found
  - 2a1. System displays error
  - Use case ends

**Postconditions**:
- Trader has detailed information about trade

---

## Non-Functional Requirements

### Performance
- Commands respond within 2 seconds
- Market searches return within 3 seconds
- Support up to 10,000 active listings
- Handle 100 concurrent users

### Usability
- Slash commands with autocomplete for items
- Clear error messages with suggested actions
- Visual feedback (embeds, buttons)
- Mobile-friendly interface

### Reliability
- Database transactions ensure data consistency
- Graceful error handling
- Automatic offer expiration cleanup
- Trade confirmation timeout handling

### Security
- Admin commands require proper permissions
- Users can only modify own listings
- Trade names unchangeable except by admin
- Audit log for admin actions

---

## Future Enhancements (Phase 2+)

- **UC-017**: View Price History
- **UC-018**: Set Price Alerts
- **UC-019**: Generate Market Reports
- **UC-020**: Bulk Import Items
- **UC-021**: Trade Reputation System
- **UC-022**: Dispute Resolution
