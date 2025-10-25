# Trading Bot - System Diagrams

## Table of Contents
1. [Sequence Diagrams](#sequence-diagrams)
2. [State Diagrams](#state-diagrams)
3. [Entity Relationship Diagram](#entity-relationship-diagram)
4. [Activity Diagram](#activity-diagram)
5. [Component Diagram](#component-diagram)
6. [Deployment Diagram](#deployment-diagram)
7. [Class Diagrams](#class-diagrams)

---

## 1. Sequence Diagrams

### SD-001: Complete Trade Flow (Accept at Listed Price)

```
Actor: Buyer
Actor: Seller
Participant: Discord
Participant: Bot
Database: DB

Note over Buyer,DB: Prerequisites: Both users have trade names set

Seller->Discord: /sell item:Sword quantity:5 price_per_unit:100g
Discord->Bot: Command received
Bot->DB: Validate seller has trade name
DB-->Bot: Valid
Bot->DB: Create listing (ID: 42, qty: 5)
DB-->Bot: Success
Bot->Discord: Post listing embed
Discord->Seller: Confirmation message

Note over Buyer,Seller: Time passes, Buyer finds listing

Buyer->Discord: /accept trade_id:42 quantity:3
Discord->Bot: Command received
Bot->DB: Get listing (ID: 42)
DB-->Bot: Listing data (qty: 5, price: 100g)
Bot->DB: Validate buyer has trade name
DB-->Bot: Valid
Bot->Bot: Calculate total (3 × 100g = 300g)
Bot->DB: Create pending_trade (qty: 3, total: 300g)
Bot->DB: Update listing (qty: 5 → 2)
DB-->Bot: Success
Bot->Discord: Post trade notification
Discord->Buyer: Trade details + seller IGN
Discord->Seller: Trade details + buyer IGN

Note over Buyer,Seller: In-game item transfer happens

Buyer->Discord: /confirm trade_id:42
Discord->Bot: Confirm command
Bot->DB: Mark buyer_confirmed = true
DB-->Bot: Success (1 of 2 confirmed)
Bot->Discord: "Waiting for seller confirmation"
Discord->Buyer: Confirmation recorded

Seller->Discord: /confirm trade_id:42
Discord->Bot: Confirm command
Bot->DB: Mark seller_confirmed = true
DB-->Bot: Success (2 of 2 confirmed)
Bot->DB: Move to completed_trades
Bot->DB: Check listing qty (2 remaining)
DB-->Bot: Listing still has qty
Bot->Discord: Trade completed notification
Discord->Buyer: Trade complete!
Discord->Seller: Trade complete!

Note over Bot,DB: Listing ID:42 remains active with qty:2
```

---

### SD-002: Offer Negotiation Flow

```
Actor: Buyer
Actor: Seller
Participant: Discord
Participant: Bot
Database: DB

Note over Buyer,DB: Listing exists (ID: 42, qty: 10, price: 50g)

Buyer->Discord: /offer trade_id:42 quantity:5 offer_per_unit:40g
Discord->Bot: Offer command
Bot->DB: Get listing
DB-->Bot: Listing data
Bot->DB: Check pending offers
DB-->Bot: None found
Bot->DB: Create offer (status: pending)
Bot->DB: Lock listing (has_pending_offer: true)
DB-->Bot: Success
Bot->Discord: Post offer with Accept/Decline buttons
Discord->Seller: Offer notification

Note over Seller: Seller considers offer

Seller->Discord: [Clicks Accept button]
Discord->Bot: Button interaction
Bot->DB: Validate seller owns listing
DB-->Bot: Valid
Bot->DB: Update offer (status: accepted)
Bot->DB: Create pending_trade
Bot->DB: Update listing (qty: 10 → 5, unlock)
DB-->Bot: Success
Bot->Discord: Update message (buttons disabled)
Bot->Discord: Post trade notification
Discord->Buyer: Trade accepted! Confirm when complete
Discord->Seller: Trade accepted! Confirm when complete

Note over Buyer,Seller: Confirmation flow same as SD-001
```

---

### SD-003: Offer Declined Flow

```
Actor: Buyer
Actor: Seller
Participant: Discord
Participant: Bot
Database: DB

Note over Buyer,DB: Offer exists (status: pending)

Seller->Discord: [Clicks Decline button]
Discord->Bot: Button interaction
Bot->DB: Validate seller owns listing
DB-->Bot: Valid
Bot->DB: Update offer (status: declined)
Bot->DB: Unlock listing (has_pending_offer: false)
DB-->Bot: Success
Bot->Discord: Update offer message (buttons disabled)
Discord->Buyer: "Your offer was declined"
Discord->Seller: Confirmation
Bot->Discord: Update listing status
Discord->Discord: Listing visible again for new offers

Note over Bot: Listing remains active, others can offer
```

---

### SD-004: Offer Expiration (Automated)

```
Participant: Scheduler
Participant: Bot
Database: DB
Participant: Discord
Actor: Buyer
Actor: Seller

Note over Scheduler: Daily cleanup job runs

Scheduler->Bot: Check expired offers
Bot->DB: SELECT offers WHERE status=pending AND created_at < 7 days ago
DB-->Bot: List of expired offers
loop For each expired offer
    Bot->DB: Update offer (status: expired)
    Bot->DB: Unlock listing
    Bot->DB: Get buyer and seller IDs
    DB-->Bot: User data
    Bot->Discord: Notify buyer (offer expired)
    Bot->Discord: Notify seller (offer expired)
    Discord->Buyer: Your offer on listing X expired
    Discord->Seller: Offer on your listing X expired
end
```

---

### SD-005: Failed Trade Confirmation (Timeout)

```
Participant: Scheduler
Participant: Bot
Database: DB
Participant: Discord
Actor: Buyer
Actor: Seller
Actor: Admin

Note over Scheduler: Daily cleanup job runs

Scheduler->Bot: Check pending confirmations
Bot->DB: SELECT pending_trades WHERE created_at < 24 hours ago
DB-->Bot: List of expired confirmations

loop For each expired trade
    Bot->DB: Check confirmation status
    DB-->Bot: buyer_confirmed=true, seller_confirmed=false
    Bot->DB: Update trade (status: disputed)
    Bot->DB: Restore listing quantity
    DB-->Bot: Success
    Bot->Discord: Notify both parties
    Discord->Buyer: Trade confirmation failed
    Discord->Seller: Trade confirmation failed
    Bot->Discord: Notify admin channel
    Discord->Admin: Trade ID X needs review
end

Note over Admin: Admin investigates and resolves manually
```

---

## 2. State Diagrams

### STD-001: Listing State Diagram

```
[*] --> Created

Created --> Active : Validation passed
Created --> [*] : Validation failed

Active --> HasPendingOffer : Offer received
Active --> PendingConfirmation : Accepted (partial qty)
Active --> Completed : Accepted (full qty)
Active --> Cancelled : Owner cancelled

HasPendingOffer --> Active : Offer declined/expired
HasPendingOffer --> PendingConfirmation : Offer accepted (partial)
HasPendingOffer --> Completed : Offer accepted (full qty)

PendingConfirmation --> Active : Confirmation timeout, qty restored
PendingConfirmation --> Completed : Both parties confirmed (full qty)
PendingConfirmation --> Active : Both confirmed (partial qty, qty reduced)

Cancelled --> [*]
Completed --> [*]

state Active {
    [*] --> Visible
    Visible : Searchable in market
    Visible : Can receive offers
    Visible : Can be accepted
}

state HasPendingOffer {
    [*] --> Locked
    Locked : Not visible for new offers
    Locked : Cannot be directly accepted
    Locked : Awaiting seller response
}

state PendingConfirmation {
    [*] --> AwaitingBoth
    AwaitingBoth --> AwaitingSeller : Buyer confirmed
    AwaitingBoth --> AwaitingBuyer : Seller confirmed
    AwaitingSeller --> ReadyToComplete : Seller confirmed
    AwaitingBuyer --> ReadyToComplete : Buyer confirmed
    ReadyToComplete --> [*] : Trade finalized
}
```

---

### STD-002: Offer State Diagram

```
[*] --> Created

Created --> Pending : Validation passed
Created --> [*] : Validation failed

Pending --> Accepted : Seller accepts
Pending --> Declined : Seller declines
Pending --> Expired : Time limit reached
Pending --> Cancelled : Buyer cancels (optional feature)

Accepted --> [*] : Trade confirmation flow begins
Declined --> [*]
Expired --> [*]
Cancelled --> [*]

state Pending {
    [*] --> AwaitingResponse
    AwaitingResponse : Listing locked
    AwaitingResponse : Timer running
    AwaitingResponse : Buttons visible to seller
}
```

---

### STD-003: Trade State Diagram

```
[*] --> Created

Created --> PendingConfirmation : Trade accepted
Created --> [*] : Creation failed

PendingConfirmation --> PartiallyConfirmed : One party confirms
PartiallyConfirmed --> Completed : Both parties confirm
PartiallyConfirmed --> Disputed : Timeout reached
PendingConfirmation --> Disputed : Timeout before any confirmation

Completed --> [*]
Disputed --> UnderReview : Admin notified
UnderReview --> Completed : Admin resolves as complete
UnderReview --> Cancelled : Admin cancels trade

Cancelled --> [*]

state PendingConfirmation {
    [*] --> AwaitingBoth
    AwaitingBoth : Timer: 24 hours
    AwaitingBoth : Both can confirm
}

state PartiallyConfirmed {
    [*] --> OneConfirmed
    OneConfirmed : Timer: remaining time
    OneConfirmed : Reminder sent to other party
}

state Disputed {
    [*] --> FlaggedForReview
    FlaggedForReview : Admin notified
    FlaggedForReview : Parties notified
    FlaggedForReview : Listing qty restored
}
```

---

### STD-004: User State Diagram

```
[*] --> Unregistered

Unregistered --> Registered : Sets trade name
Registered --> Active : Can create listings
Active --> Suspended : Admin action (future)
Suspended --> Active : Admin reinstates
Active --> [*] : Leaves server

state Active {
    [*] --> CanTrade
    CanTrade --> Trading : Has active listings
    CanTrade --> Trading : Has pending trades
    Trading --> CanTrade : All trades resolved
}
```

---

## 3. Entity Relationship Diagram (ERD)

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ user_id (PK)    │
│ trade_name      │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────────┐
│      Listings           │
├─────────────────────────┤
│ id (PK)                 │
│ user_id (FK)            │
│ trade_type (WTS/WTB)    │
│ item_id (FK)            │
│ quantity_listed         │
│ quantity_remaining      │
│ price_per_unit          │
│ notes                   │
│ has_pending_offer       │
│ status                  │
│ created_at              │
│ updated_at              │
└────────┬────────────────┘
         │
         │ 1:N
         │
┌────────▼────────────────┐         ┌─────────────────┐
│       Offers            │         │     Items       │
├─────────────────────────┤         ├─────────────────┤
│ id (PK)                 │         │ id (PK)         │
│ listing_id (FK)         │◄────────┤ name            │
│ buyer_id (FK)           │         │ category        │
│ quantity                │         │ rarity          │
│ offer_per_unit          │         │ icon_url        │
│ message                 │         └─────────────────┘
│ status                  │
│ created_at              │
│ expires_at              │
└────────┬────────────────┘
         │
         │ 1:1
         │
┌────────▼────────────────┐
│   Pending_Trades        │
├─────────────────────────┤
│ id (PK)                 │
│ listing_id (FK)         │
│ offer_id (FK, nullable) │
│ seller_id (FK)          │
│ buyer_id (FK)           │
│ item_id (FK)            │
│ quantity                │
│ price_per_unit          │
│ total_price             │
│ buyer_confirmed         │
│ seller_confirmed        │
│ status                  │
│ created_at              │
│ confirmed_at            │
│ expires_at              │
└────────┬────────────────┘
         │
         │ 1:1 (when confirmed)
         │
┌────────▼────────────────┐
│  Completed_Trades       │
├─────────────────────────┤
│ id (PK)                 │
│ original_listing_id     │
│ original_offer_id       │
│ seller_id (FK)          │
│ seller_trade_name       │
│ buyer_id (FK)           │
│ buyer_trade_name        │
│ item_id (FK)            │
│ quantity                │
│ price_per_unit          │
│ total_price             │
│ completion_type         │
│ completed_at            │
└─────────────────────────┘
```

---

## 4. Activity Diagram: Complete Trading Flow

```
(Start)
   │
   ▼
[Seller creates listing]
   │
   ▼
<Has price?>
   │
   ├─Yes──► [Listed with price] ──► [Visible in market]
   │                                      │
   └─No───► [Listed without price]       │
                  │                       │
                  └───────────────────────┘
                                          │
                                          ▼
                            ┌──────────────────────┐
                            │  Listing is Active   │
                            └──────────────────────┘
                                     │   │
                    ┌────────────────┘   └────────────────┐
                    │                                      │
                    ▼                                      ▼
            [Buyer makes offer]                   [Buyer accepts price]
                    │                                      │
                    ▼                                      │
         [Offer posted with buttons]                      │
                    │                                      │
              ┌─────┴─────┐                               │
              │           │                               │
              ▼           ▼                               │
        [Decline]    [Accept]                             │
              │           │                               │
              │           └───────────────────┬───────────┘
              │                               │
              ▼                               ▼
      [Offer declined]              [Create pending trade]
              │                               │
              ▼                               ▼
      [Listing unlocked]          [Notify both parties with IGN]
              │                               │
              ▼                               ▼
      [Can receive new offers]      [24 hour timer starts]
              │                               │
              └───────────┐                   ▼
                          │         [In-game transfer happens]
                          │                   │
                          │                   ▼
                          │         ┌─────────────────┐
                          │         │ Confirmations?  │
                          │         └─────────────────┘
                          │              │     │
                          │    ┌─────────┘     └──────────┐
                          │    │                          │
                          │    ▼                          ▼
                          │  [Both      [Timeout]    [Partial]
                          │  confirm]       │            │
                          │    │            ▼            ▼
                          │    │      [Mark disputed] [Waiting]
                          │    │            │            │
                          │    │            ▼            │
                          │    │      [Admin review]     │
                          │    │                         │
                          │    └─────────────┬───────────┘
                          │                  │
                          │                  ▼
                          │        [Save to completed trades]
                          │                  │
                          │                  ▼
                          │        <Sold all quantity?>
                          │                  │
                          │        ┌─────────┴─────────┐
                          │        │                   │
                          │        ▼                   ▼
                          │      [Yes]               [No]
                          │        │                   │
                          │        ▼                   ▼
                          │  [Remove listing]  [Reduce quantity]
                          │        │                   │
                          │        │                   └────────┐
                          │        │                            │
                          └────────┴────────────────────────────┘
                                   │
                                   ▼
                                 (End)
```

---

## 5. Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Discord Client                       │
│  (User Interface - Slash Commands & Interactions)      │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ HTTPS/WebSocket
                 │
┌────────────────▼────────────────────────────────────────┐
│                   Discord Bot                           │
│  ┌───────────────────────────────────────────────────┐ │
│  │           Command Handler                          │ │
│  │  ┌──────────┬──────────┬──────────┬─────────────┐ │ │
│  │  │Trading   │Market    │Offers    │Admin        │ │ │
│  │  │Commands  │Commands  │Commands  │Commands     │ │ │
│  │  └──────────┴──────────┴──────────┴─────────────┘ │ │
│  └───────────────────────┬───────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐ │
│  │          Business Logic Layer                      │ │
│  │  ┌─────────────────┬─────────────────┬──────────┐ │ │
│  │  │Listing Manager  │Trade Manager    │Offer Mgr │ │ │
│  │  └─────────────────┴─────────────────┴──────────┘ │ │
│  └───────────────────────┬───────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐ │
│  │         Validation & Utils                         │ │
│  │  ┌────────────┬──────────────┬─────────────────┐  │ │
│  │  │Item        │Price         │Confirmation     │  │ │
│  │  │Validator   │Calculator    │Manager          │  │ │
│  │  └────────────┴──────────────┴─────────────────┘  │ │
│  └───────────────────────┬───────────────────────────┘ │
└──────────────────────────┼──────────────────────────────┘
                           │
                           │ SQL
                           │
┌──────────────────────────▼──────────────────────────────┐
│                   Database Layer                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │             PostgreSQL / SQLite                    │  │
│  │  ┌──────┬─────────┬────────┬────────────────────┐ │  │
│  │  │Users │Listings │Offers  │Completed_Trades    │ │  │
│  │  └──────┴─────────┴────────┴────────────────────┘ │  │
│  │  ┌──────┬──────────────────┬────────────────────┐ │  │
│  │  │Items │Pending_Trades    │Admin_Logs          │ │  │
│  │  └──────┴──────────────────┴────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Background Services                         │
│  ┌────────────────┬──────────────────────────────────┐  │
│  │Offer Expiry    │Trade Confirmation Timeout        │  │
│  │Cleanup Job     │Cleanup Job                       │  │
│  │(Daily)         │(Daily)                           │  │
│  └────────────────┴──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Deployment Diagram (Proposed Architecture)

```
┌──────────────────────────────────────────────────┐
│              Discord Platform                     │
│  (Cloud - Managed by Discord)                   │
└────────────────┬─────────────────────────────────┘
                 │
                 │ API Calls
                 │
┌────────────────▼─────────────────────────────────┐
│           VPS / Cloud Server                     │
│  (DigitalOcean, AWS, Heroku, etc.)              │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │       Node.js Runtime Environment          │  │
│  │                                            │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │      Discord Bot Application         │ │  │
│  │  │      (discord.js)                    │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  │                                            │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │     Database (PostgreSQL/SQLite)     │ │  │
│  │  │     - Persistent storage             │ │  │
│  │  │     - Backup enabled                 │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  │                                            │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │     Scheduler (node-cron)            │ │  │
│  │  │     - Offer expiry cleanup           │ │  │
│  │  │     - Trade timeout handling         │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  │                                            │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │     Logging & Monitoring             │ │  │
│  │  │     - Winston logs                   │ │  │
│  │  │     - Error tracking                 │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────┘  │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │        Configuration Files                 │  │
│  │  - .env (bot token, DB credentials)       │  │
│  │  - items.json (valid items list)          │  │
│  │  - config.js (expiry times, limits)       │  │
│  └────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
```

---

## 7. Class Diagrams

### CD-001: Core Domain Models

```
┌─────────────────────────────────┐
│         User                     │
├─────────────────────────────────┤
│ - userId: String                │
│ - discordUsername: String       │
│ - tradeName: String             │
│ - createdAt: Date               │
│ - updatedAt: Date               │
├─────────────────────────────────┤
│ + setTradeName(name: String)    │
│ + getTradeName(): String        │
│ + hasActiveListing(): Boolean   │
│ + canTrade(): Boolean           │
└─────────────────────────────────┘
              │
              │ 1:N
              ▼
┌─────────────────────────────────┐
│         Listing                  │
├─────────────────────────────────┤
│ - id: Integer                   │
│ - userId: String                │
│ - tradeType: TradeType          │
│ - itemId: Integer               │
│ - quantityListed: Integer       │
│ - quantityRemaining: Integer    │
│ - pricePerUnit: Decimal         │
│ - notes: String                 │
│ - hasPendingOffer: Boolean      │
│ - status: ListingStatus         │
│ - createdAt: Date               │
│ - updatedAt: Date               │
├─────────────────────────────────┤
│ + create(): Listing             │
│ + cancel(): void                │
│ + reduceQuantity(qty: Int): void│
│ + lockForOffer(): void          │
│ + unlockFromOffer(): void       │
│ + hasPrice(): Boolean           │
│ + canAcceptOffer(): Boolean     │
│ + isFullySold(): Boolean        │
└─────────────────────────────────┘
              │
              │ 1:N
              ▼
┌─────────────────────────────────┐
│         Offer                    │
├─────────────────────────────────┤
│ - id: Integer                   │
│ - listingId: Integer            │
│ - buyerId: String               │
│ - quantity: Integer             │
│ - offerPerUnit: Decimal         │
│ - message: String               │
│ - status: OfferStatus           │
│ - createdAt: Date               │
│ - expiresAt: Date               │
├─────────────────────────────────┤
│ + create(): Offer               │
│ + accept(): PendingTrade        │
│ + decline(): void               │
│ + expire(): void                │
│ + isExpired(): Boolean          │
│ + calculateTotal(): Decimal     │
└─────────────────────────────────┘
              │
              │ 1:1
              ▼
┌─────────────────────────────────┐
│       PendingTrade               │
├─────────────────────────────────┤
│ - id: Integer                   │
│ - listingId: Integer            │
│ - offerId: Integer (nullable)   │
│ - sellerId: String              │
│ - buyerId: String               │
│ - itemId: Integer               │
│ - quantity: Integer             │
│ - pricePerUnit: Decimal         │
│ - totalPrice: Decimal           │
│ - buyerConfirmed: Boolean       │
│ - sellerConfirmed: Boolean      │
│ - status: TradeStatus           │
│ - createdAt: Date               │
│ - confirmedAt: Date             │
│ - expiresAt: Date               │
├─────────────────────────────────┤
│ + confirmBuyer(): void          │
│ + confirmSeller(): void         │
│ + bothConfirmed(): Boolean      │
│ + complete(): CompletedTrade    │
│ + markDisputed(): void          │
│ + isExpired(): Boolean          │
└─────────────────────────────────┘
              │
              │ 1:1 (when confirmed)
              ▼
┌─────────────────────────────────┐
│      CompletedTrade              │
├─────────────────────────────────┤
│ - id: Integer                   │
│ - originalListingId: Integer    │
│ - originalOfferId: Integer      │
│ - sellerId: String              │
│ - sellerTradeName: String       │
│ - buyerId: String               │
│ - buyerTradeName: String        │
│ - itemId: Integer               │
│ - quantity: Integer             │
│ - pricePerUnit: Decimal         │
│ - totalPrice: Decimal           │
│ - completionType: String        │
│ - completedAt: Date             │
├─────────────────────────────────┤
│ + save(): void                  │
│ + getAveragePrice(): Decimal    │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│           Item                   │
├─────────────────────────────────┤
│ - id: Integer                   │
│ - name: String                  │
│ - category: ItemCategory        │
│ - rarity: ItemRarity            │
│ - iconUrl: String               │
├─────────────────────────────────┤
│ + search(query: String): Item[] │
│ + getByCategory(cat): Item[]    │
│ + exists(name: String): Boolean │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│     <<enumeration>>              │
│       TradeType                  │
├─────────────────────────────────┤
│ WTS                             │
│ WTB                             │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│     <<enumeration>>              │
│     ListingStatus                │
├─────────────────────────────────┤
│ ACTIVE                          │
│ PENDING_CONFIRMATION            │
│ COMPLETED                       │
│ CANCELLED                       │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│     <<enumeration>>              │
│      OfferStatus                 │
├─────────────────────────────────┤
│ PENDING                         │
│ ACCEPTED                        │
│ DECLINED                        │
│ EXPIRED                         │
│ CANCELLED                       │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│     <<enumeration>>              │
│      TradeStatus                 │
├─────────────────────────────────┤
│ PENDING_CONFIRMATION            │
│ PARTIALLY_CONFIRMED             │
│ COMPLETED                       │
│ DISPUTED                        │
│ CANCELLED                       │
└─────────────────────────────────┘
```

---

### CD-002: Command Handlers

```
┌──────────────────────────────────┐
│    <<interface>>                 │
│    CommandHandler                │
├──────────────────────────────────┤
│ + execute(interaction): Promise  │
│ + validate(params): Boolean      │
│ + handleError(error): void       │
└──────────────────────────────────┘
              △
              │ implements
    ┌─────────┼─────────────┐
    │         │             │
┌───▼──────┐ ┌▼──────────┐ ┌▼──────────┐
│Trading   │ │Market     │ │Offers     │
│Commands  │ │Commands   │ │Commands   │
├──────────┤ ├───────────┤ ├───────────┤
│+sellCmd  │ │+searchCmd │ │+offerCmd  │
│+buyCmd   │ │+marketCmd │ │+acceptCmd │
└──────────┘ │+mylistings│ │+confirmCmd│
             │+removeCmd │ └───────────┘
             └───────────┘

┌──────────────────────────────────┐
│      ListingManager              │
├──────────────────────────────────┤
│ - db: Database                   │
│ - validator: ItemValidator       │
├──────────────────────────────────┤
│ + createListing(params): Listing│
│ + updateQuantity(id, qty): void  │
│ + cancelListing(id, userId): void│
│ + getActiveListing(id): Listing  │
│ + getUserListings(userId): List  │
│ + searchListings(query): List    │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│       TradeManager               │
├──────────────────────────────────┤
│ - db: Database                   │
│ - notifier: NotificationService  │
├──────────────────────────────────┤
│ + createPendingTrade(params)     │
│ + confirmTrade(id, userId): void │
│ + completeTrade(id): void        │
│ + handleTimeout(id): void        │
│ + getPendingTrades(userId): List │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│        OfferManager              │
├──────────────────────────────────┤
│ - db: Database                   │
│ - listingManager: ListingManager │
├──────────────────────────────────┤
│ + createOffer(params): Offer     │
│ + acceptOffer(id, userId): void  │
│ + declineOffer(id, userId): void │
│ + expireOffers(): void           │
│ + getPendingOffer(listingId)     │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│       ItemValidator              │
├──────────────────────────────────┤
│ - items: Item[]                  │
├──────────────────────────────────┤
│ + validateItem(name): Boolean    │
│ + searchItems(query): Item[]     │
│ + getItemById(id): Item          │
│ + getAllItems(): Item[]          │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│    NotificationService           │
├──────────────────────────────────┤
│ - bot: DiscordClient             │
├──────────────────────────────────┤
│ + notifyTradeCreated(trade)      │
│ + notifyOfferReceived(offer)     │
│ + notifyConfirmationNeeded(trade)│
│ + notifyTradeCompleted(trade)    │
│ + notifyOfferExpired(offer)      │
│ + notifyTradeDisputed(trade)     │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│        PriceCalculator           │
├──────────────────────────────────┤
│ + calculateTotal(qty, price): Dec│
│ + getAveragePrice(itemId): Dec   │
│ + getPriceRange(itemId): Range   │
│ + suggestPrice(itemId): Dec      │
└──────────────────────────────────┘
```

---

### CD-003: Services Layer

```
┌──────────────────────────────────┐
│      DatabaseService             │
├──────────────────────────────────┤
│ - connection: DBConnection       │
├──────────────────────────────────┤
│ + query(sql, params): Result     │
│ + transaction(callback): void    │
│ + connect(): void                │
│ + disconnect(): void             │
└──────────────────────────────────┘
              △
              │ uses
┌─────────────┴──────────────┐
│                             │
┌▼──────────────┐  ┌─────────▼──────┐
│UserRepository │  │ListingRepository│
├───────────────┤  ├─────────────────┤
│+findById()    │  │+findById()      │
│+findByName()  │  │+findByUser()    │
│+create()      │  │+findActive()    │
│+update()      │  │+create()        │
└───────────────┘  │+update()        │
                   │+search()        │
                   └─────────────────┘

┌──────────────────────────────────┐
│      SchedulerService            │
├──────────────────────────────────┤
│ - jobs: Job[]                    │
├──────────────────────────────────┤
│ + scheduleOfferExpiry()          │
│ + scheduleTradeTimeout()         │
│ + scheduleDailyCleanup()         │
│ + start(): void                  │
│ + stop(): void                   │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│       LoggingService             │
├──────────────────────────────────┤
│ + logInfo(message): void         │
│ + logError(error): void          │
│ + logCommand(cmd, user): void    │
│ + logTrade(trade): void          │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     ConfigurationService         │
├──────────────────────────────────┤
│ - config: Config                 │
├──────────────────────────────────┤
│ + getOfferExpiryDays(): Integer  │
│ + getTradeTimeoutHours(): Integer│
│ + getMaxListingsPerUser(): Int   │
│ + loadItemsConfig(): Item[]      │
└──────────────────────────────────┘
```
