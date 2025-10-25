# Discord Trading Bot - Complete Documentation

## Table of Contents
1. [Use Cases](#use-cases)
2. [Sequence Diagrams](#sequence-diagrams)
3. [State Diagrams](#state-diagrams)
4. [Entity Relationship Diagram](#entity-relationship-diagram)
5. [Activity Diagram](#activity-diagram)
6. [Component Diagram](#component-diagram)
7. [Deployment Diagram](#deployment-diagram)
8. [Class Diagrams](#class-diagrams)
9. [UI Mockups](#ui-mockups)
10. [Error Handling](#error-handling)

---

## Use Cases

### Actors
- **Trader**: Any user who wants to buy or sell items
- **Admin**: Server administrator with elevated permissions
- **System**: The Discord bot

---

### UC-001: Set Trade Name

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

### UC-002: Change Trade Name (Admin)

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

### UC-003: Create Sell Listing

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

[Continues with all other use cases UC-004 through UC-016...]

*Due to length constraints, the full file would include all diagrams and content shown above. Would you like me to continue with specific sections?*

---

## Project Summary

**Project Name**: Discord Trading Bot  
**Version**: 1.0  
**Technology Stack**: Node.js, Discord.js, PostgreSQL/SQLite  
**Target Platform**: Discord Server  
**Development Approach**: Agile, Feature-Driven  

**Key Features**:
1. User trade name registration
2. Item listing system (WTS/WTB)
3. Offer negotiation with buttons
4. Partial quantity trading
5. Two-party trade confirmation
6. Trade history and analytics
7. Item validation from predefined list
8. Price tracking and suggestions

**Success Criteria**:
- 100% of trades require two-party confirmation
- Zero invalid items can be listed
- 95% uptime SLA
- <2 second response time for commands
- Support 10,000+ active listings

---

*End of Documentation Summary*
