# Trading Bot - Error Handling Documentation

## Table of Contents
1. [Error Class Structure](#error-class-structure)
2. [Error Response Formats](#error-response-formats)
3. [Error Flow Diagrams](#error-flow-diagrams)
4. [Error Codes Reference](#error-codes-reference)
5. [Retry Logic](#retry-logic)
6. [Error Logging](#error-logging)

---

## 1. Error Class Structure

### Base Error Class

```javascript
class BotError extends Error {
  constructor(message, code, userMessage, isOperational = true) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.userMessage = userMessage;
    this.isOperational = isOperational;
    this.timestamp = new Date().toISOString();
    Error.captureStackTrace(this, this.constructor);
  }

  getUserMessage() {
    return this.userMessage || this.message;
  }

  log() {
    console.error(`[${this.code}] ${this.name}: ${this.message}`);
  }
}
```

### Error Type Hierarchy

```
BotError (Base)
│
├── ValidationError (1000-1999)
│   ├── NoTradeNameError
│   ├── InvalidItemError
│   ├── InvalidQuantityError
│   ├── InvalidPriceError
│   └── MissingRequiredFieldError
│
├── BusinessError (2000-2999)
│   ├── ListingNotFoundError
│   ├── ListingLockedError
│   ├── InsufficientQuantityError
│   ├── CannotTradeWithSelfError
│   ├── NotOwnerError
│   ├── NoPriceSetError
│   ├── AlreadyConfirmedError
│   ├── TradeExpiredError
│   └── OfferExpiredError
│
├── PermissionError (3000-3999)
│   ├── InsufficientPermissionsError
│   └── NotTradeParticipantError
│
└── SystemError (4000-4999)
    ├── DatabaseError
    ├── DiscordAPIError
    ├── TimeoutError
    └── UnknownError
```

---

## 2. Error Response Formats

All errors should be displayed to users in a consistent format using Discord embeds.

### Template Structure

```
┌─────────────────────────────────────────────────┐
│ [ICON] [ERROR TYPE]                             │
├─────────────────────────────────────────────────┤
│ [User-friendly description of what went wrong]  │
│                                                 │
│ [Additional context or details]                 │
│                                                 │
│ 💡 Tip: [Suggestion for how to fix/proceed]    │
├─────────────────────────────────────────────────┤
│ Error Code: [CODE]                              │
└─────────────────────────────────────────────────┘
```

### Example: Validation Error

**Scenario**: User tries to sell an invalid item

**Input**: `/sell item:InvalidItem quantity:5 price_per_unit:100g`

**Response**:
```
┌─────────────────────────────────────────────────┐
│ ❌ Validation Error                             │
├─────────────────────────────────────────────────┤
│ The item "InvalidItem" is not in our database.  │
│                                                 │
│ Did you mean one of these?                      │
│ • Invincible Sword                              │
│ • Invisible Cloak                               │
│ • Inverted Shield                               │
│                                                 │
│ 💡 Tip: Use the dropdown menu to select items  │
│         to avoid typos.                         │
├─────────────────────────────────────────────────┤
│ Error Code: E1002                               │
└─────────────────────────────────────────────────┘
```

### Example: Business Logic Error

**Scenario**: User tries to accept more quantity than available

**Input**: `/accept 42 10` (but only 5 available)

**Response**:
```
┌─────────────────────────────────────────────────┐
│ ❌ Cannot Complete Trade                        │
├─────────────────────────────────────────────────┤
│ You requested 10 units, but only 5 are available│
│                                                 │
│ Listing #42: Sword of Fire                      │
│ Available: 5 units                              │
│ Requested: 10 units                             │
│                                                 │
│ Please use:                                     │
│ /accept 42 5                                    │
│                                                 │
│ Or make an offer for a different quantity:      │
│ /offer 42 <qty> <price>                         │
├─────────────────────────────────────────────────┤
│ Error Code: E2003                               │
└─────────────────────────────────────────────────┘
```

### Example: Permission Error

**Scenario**: User tries to remove someone else's listing

**Input**: `/remove 42` (not their listing)

**Response**:
```
┌─────────────────────────────────────────────────┐
│ ❌ Permission Denied                            │
├─────────────────────────────────────────────────┤
│ You can only remove your own listings.          │
│                                                 │
│ Listing #42 belongs to @AliceTheWarrior         │
│                                                 │
│ To view your own listings, use:                 │
│ /mylistings                                     │
├─────────────────────────────────────────────────┤
│ Error Code: E2005                               │
└─────────────────────────────────────────────────┘
```

### Example: System Error

**Scenario**: Database connection failed

**Response**:
```
┌─────────────────────────────────────────────────┐
│ ⚠️ System Error                                 │
├─────────────────────────────────────────────────┤
│ We're experiencing technical difficulties.      │
│                                                 │
│ Our team has been automatically notified and    │
│ is working to resolve the issue.                │
│                                                 │
│ Please try again in a few moments.              │
│                                                 │
│ If the problem persists, contact an admin.      │
├─────────────────────────────────────────────────┤
│ Error ID: ERR-2024-10-25-1634-A7F3              │
└─────────────────────────────────────────────────┘
```

---

## 3. Error Flow Diagrams

### Main Error Handling Flow

```
(User sends command)
        │
        ▼
[Parse command]
        │
        ├─ Parse Error ──────────► [ValidationError]
        │                                │
        ▼                                ▼
[Validate parameters]          [Create error embed]
        │                                │
        ├─ Invalid ──────────► [ValidationError]
        │                                │
        ▼                                ▼
[Check permissions]             [Add suggestions]
        │                                │
        ├─ No permission ──► [PermissionError]
        │                                │
        ▼                                ▼
[Execute business logic]        [Send to user (ephemeral)]
        │                                │
        ├─ Business rule ───► [BusinessError]
        │   violation                    │
        │                                ▼
        ▼                        [Log error details]
[Database operation]                    │
        │                                │
        ├─ DB Error ────────► [SystemError] ──► [Alert admin]
        │                                │              │
        ▼                                │              ▼
[Success!]                               │        [Error logged]
        │                                │              │
        ▼                                └──────────────┘
[Return success response]
```

### Error Response Creation Flow

```
(Error thrown)
        │
        ▼
[Error Handler catches error]
        │
        ▼
<Is operational?>
        │
    ┌───┴───┐
   Yes     No
    │       │
    │       └──► [Log full stack trace]
    │            [Alert admin immediately]
    │            [Send generic error to user]
    │            [Consider bot restart]
    ▼
[Determine error type]
        │
        ├─ Validation ──► [Red embed, helpful suggestions]
        ├─ Business ────► [Yellow/Red embed, alternative actions]
        ├─ Permission ──► [Red embed, permission info]
        └─ System ──────► [Yellow embed, retry message]
        │
        ▼
[Create user-friendly message]
        │
        ▼
[Add contextual suggestions]
        │
        ▼
[Send to user (ephemeral)]
        │
        ▼
[Log error with context]
        │
        ▼
[Track error metrics]
        │
        ▼
<Critical error?>
        │
    ┌───┴───┐
   Yes     No
    │       │
    └──► [Alert admin]
            │
            ▼
          (End)
```

### Retry Logic Flow

```
(Operation attempted)
        │
        ▼
[Try operation]
        │
        ├─ Success ──────────────► Return result
        │
        ├─ Retryable error (e.g., timeout, connection)
        │       │
        │       ▼
        │  <Retry count < max?>
        │       │
        │   ┌───┴───┐
        │  Yes     No
        │   │       │
        │   │       └──► [Mark as permanent failure]
        │   │                     │
        │   │                     ▼
        │   │              [Log failure details]
        │   │                     │
        │   │                     ▼
        │   │              [Alert admin if critical]
        │   │                     │
        │   │                     ▼
        │   │              [Send user error message]
        │   │
        │   ▼
        │  [Wait (exponential backoff)]
        │   │
        │   └──────────────────► Retry operation
        │
        └─ Non-retryable error ──► Handle immediately
                                          │
                                          ▼
                                   [Return error to user]

Retry Schedule:
- Attempt 1: Immediate
- Attempt 2: Wait 1 second
- Attempt 3: Wait 2 seconds  
- Attempt 4: Wait 4 seconds
- Attempt 5: Wait 8 seconds
- Max retries reached: Alert admin
```

---

## 4. Error Codes Reference

### Complete Error Code List

```javascript
const ErrorCodes = {
  // ============================================
  // VALIDATION ERRORS (1000-1999)
  // ============================================
  
  NO_TRADE_NAME: {
    code: 'E1001',
    message: 'You must set your trade name first',
    suggestion: 'Use /settradename to set your in-game name',
    severity: 'warning'
  },
  
  INVALID_ITEM: {
    code: 'E1002',
    message: 'Item not found in database',
    suggestion: 'Use the dropdown menu to select a valid item',
    severity: 'error'
  },
  
  INVALID_QUANTITY: {
    code: 'E1003',
    message: 'Quantity must be a positive number',
    suggestion: 'Please enter a number greater than 0',
    severity: 'error'
  },
  
  INVALID_PRICE: {
    code: 'E1004',
    message: 'Price format is invalid',
    suggestion: 'Use format like: 100g, 1.5mg',
    severity: 'error'
  },
  
  MISSING_REQUIRED_FIELD: {
    code: 'E1005',
    message: 'Required field is missing',
    suggestion: 'Please fill in all required fields',
    severity: 'error'
  },
  
  TRADE_NAME_TOO_LONG: {
    code: 'E1006',
    message: 'Trade name is too long',
    suggestion: 'Trade name must be 32 characters or less',
    severity: 'error'
  },
  
  TRADE_NAME_INVALID_CHARS: {
    code: 'E1007',
    message: 'Trade name contains invalid characters',
    suggestion: 'Use only letters, numbers, spaces, and basic punctuation',
    severity: 'error'
  },

  // ============================================
  // BUSINESS LOGIC ERRORS (2000-2999)
  // ============================================
  
  LISTING_NOT_FOUND: {
    code: 'E2001',
    message: 'Listing not found or no longer active',
    suggestion: 'Use /market to see active listings',
    severity: 'error'
  },
  
  LISTING_LOCKED: {
    code: 'E2002',
    message: 'Listing has a pending offer',
    suggestion: 'Wait for the current offer to be resolved',
    severity: 'warning'
  },
  
  INSUFFICIENT_QUANTITY: {
    code: 'E2003',
    message: 'Requested quantity exceeds available',
    suggestion: 'Check available quantity with /tradeinfo',
    severity: 'error'
  },
  
  CANNOT_TRADE_WITH_SELF: {
    code: 'E2004',
    message: 'You cannot trade with yourself',
    suggestion: null,
    severity: 'error'
  },
  
  NOT_OWNER: {
    code: 'E2005',
    message: 'You do not own this listing',
    suggestion: 'Use /mylistings to see your listings',
    severity: 'error'
  },
  
  NO_PRICE_SET: {
    code: 'E2006',
    message: 'This listing has no price set',
    suggestion: 'Use /offer to make an offer instead',
    severity: 'warning'
  },
  
  ALREADY_CONFIRMED: {
    code: 'E2007',
    message: 'You have already confirmed this trade',
    suggestion: 'Wait for the other party to confirm',
    severity: 'warning'
  },
  
  TRADE_EXPIRED: {
    code: 'E2008',
    message: 'Trade confirmation period has expired',
    suggestion: 'Contact an admin if you completed the trade',
    severity: 'error'
  },
  
  OFFER_EXPIRED: {
    code: 'E2009',
    message: 'This offer has expired',
    suggestion: 'Make a new offer if the listing is still active',
    severity: 'error'
  },
  
  PENDING_OFFER_EXISTS: {
    code: 'E2010',
    message: 'This listing already has a pending offer',
    suggestion: 'Wait for the current offer to be resolved before making a new offer',
    severity: 'warning'
  },
  
  LISTING_HAS_PENDING_TRADES: {
    code: 'E2011',
    message: 'Cannot remove listing with pending trades',
    suggestion: 'Wait for pending trades to be confirmed or expired',
    severity: 'error'
  },
  
  MAX_LISTINGS_REACHED: {
    code: 'E2012',
    message: 'You have reached the maximum number of active listings',
    suggestion: 'Remove some listings before creating new ones',
    severity: 'warning'
  },

  // ============================================
  // PERMISSION ERRORS (3000-3999)
  // ============================================
  
  INSUFFICIENT_PERMISSIONS: {
    code: 'E3001',
    message: 'You do not have permission for this action',
    suggestion: 'This command requires admin permissions',
    severity: 'error'
  },
  
  NOT_TRADE_PARTICIPANT: {
    code: 'E3002',
    message: 'You are not part of this trade',
    suggestion: null,
    severity: 'error'
  },
  
  NOT_OFFER_PARTICIPANT: {
    code: 'E3003',
    message: 'You cannot interact with this offer',
    suggestion: 'Only the seller can accept or decline offers',
    severity: 'error'
  },

  // ============================================
  // SYSTEM ERRORS (4000-4999)
  // ============================================
  
  DATABASE_ERROR: {
    code: 'E4001',
    message: 'Database connection error',
    suggestion: 'Please try again in a moment',
    severity: 'critical',
    retryable: true
  },
  
  DISCORD_API_ERROR: {
    code: 'E4002',
    message: 'Discord API error',
    suggestion: 'Please try again in a moment',
    severity: 'critical',
    retryable: true
  },
  
  TIMEOUT_ERROR: {
    code: 'E4003',
    message: 'Request timed out',
    suggestion: 'Please try again',
    severity: 'warning',
    retryable: true
  },
  
  RATE_LIMIT_ERROR: {
    code: 'E4004',
    message: 'Too many requests',
    suggestion: 'Please wait a moment before trying again',
    severity: 'warning',
    retryable: true
  },
  
  CONFIGURATION_ERROR: {
    code: 'E4005',
    message: 'Bot configuration error',
    suggestion: 'Please contact an admin',
    severity: 'critical',
    retryable: false
  },
  
  UNKNOWN_ERROR: {
    code: 'E4999',
    message: 'An unexpected error occurred',
    suggestion: 'Contact an admin if this persists',
    severity: 'critical',
    retryable: false
  }
};
```

---

## 5. Retry Logic

### Retryable Operations

Only certain errors should trigger automatic retries:
- Database connection errors
- Discord API timeouts
- Rate limiting
- Network errors

### Implementation

```javascript
async function executeWithRetry(operation, maxRetries = 5) {
  let lastError;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      
      // Check if error is retryable
      if (!error.retryable || attempt === maxRetries - 1) {
        throw error;
      }
      
      // Calculate exponential backoff
      const delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s, 8s, 16s
      
      console.log(`Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`);
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
}
```

### Retry Schedule

```
Attempt 1: Execute immediately
  ↓ (fails)
  
Attempt 2: Wait 1 second
  ↓ (fails)
  
Attempt 3: Wait 2 seconds
  ↓ (fails)
  
Attempt 4: Wait 4 seconds
  ↓ (fails)
  
Attempt 5: Wait 8 seconds
  ↓ (fails)
  
Give up: Log error, alert admin
```

---

## 6. Error Logging

### Log Levels

```javascript
const LogLevel = {
  DEBUG: 0,
  INFO: 1,
  WARNING: 2,
  ERROR: 3,
  CRITICAL: 4
};
```

### Log Entry Structure

```javascript
{
  timestamp: '2024-10-25T16:34:22.123Z',
  level: 'ERROR',
  code: 'E2003',
  message: 'Insufficient quantity',
  userId: '123456789',
  username: 'BobTheTrader',
  command: '/accept 42 10',
  tradeId: 42,
  context: {
    requested: 10,
    available: 5
  },
  stackTrace: '...',
  errorId: 'ERR-2024-10-25-1634-A7F3'
}
```

### Logging Implementation

```javascript
class ErrorLogger {
  static log(error, context = {}) {
    const entry = {
      timestamp: new Date().toISOString(),
      level: this.getLogLevel(error),
      code: error.code,
      message: error.message,
      userId: context.userId,
      username: context.username,
      command: context.command,
      context: context.data,
      stackTrace: error.stack,
      errorId: this.generateErrorId()
    };
    
    // Write to file
    this.writeToFile(entry);
    
    // Send to monitoring service (optional)
    if (entry.level === 'CRITICAL') {
      this.alertAdmin(entry);
    }
    
    return entry.errorId;
  }
  
  static generateErrorId() {
    const date = new Date().toISOString().split('T')[0];
    const time = new Date().toTimeString().split(' ')[0].replace(/:/g, '');
    const random = Math.random().toString(36).substr(2, 4).toUpperCase();
    return `ERR-${date}-${time}-${random}`;
  }
  
  static getLogLevel(error) {
    if (error.severity === 'critical') return 'CRITICAL';
    if (error.severity === 'error') return 'ERROR';
    if (error.severity === 'warning') return 'WARNING';
    return 'INFO';
  }
}
```

### Admin Alert Triggers

Admins should be immediately notified for:
- All CRITICAL errors
- Repeated ERROR occurrences (3+ in 5 minutes)
- System component failures
- Database connection issues
- Trade disputes

### Error Metrics

Track these metrics for monitoring:
- Error rate by type
- Most common errors
- Error distribution by user
- Average resolution time
- Retry success rate

---

## 7. User Error Handling Best Practices

### DO:
✅ Use clear, non-technical language
✅ Explain what went wrong
✅ Provide actionable suggestions
✅ Show relevant context (e.g., available quantity)
✅ Use consistent formatting
✅ Make errors ephemeral (only visible to user)
✅ Log all errors for debugging

### DON'T:
❌ Show stack traces to users
❌ Use technical jargon
❌ Blame the user
❌ Give generic "error occurred" messages
❌ Expose internal system details
❌ Make permanent error messages in public channels

### Error Message Template

```
What happened:     Clear description of the error
Why it happened:   Brief explanation
What to do:        Actionable next steps
How to prevent:    Tips for avoiding this in the future
```

---

## 8. Testing Error Scenarios

### Test Cases

1. **Validation Errors**
   - Invalid item name
   - Negative quantity
   - Malformed price
   - Missing required fields

2. **Business Logic Errors**
   - Trading with self
   - Insufficient quantity
   - Listing not found
   - Expired trade/offer

3. **Permission Errors**
   - Non-owner trying to remove listing
   - Non-admin using admin command
   - Non-participant confirming trade

4. **System Errors**
   - Database disconnection
   - Discord API timeout
   - Rate limiting

### Automated Error Testing

```javascript
describe('Error Handling', () => {
  test('should return validation error for invalid item', async () => {
    const result = await executeSellCommand({
      item: 'InvalidItem',
      quantity: 1
    });
    
    expect(result.error.code).toBe('E1002');
    expect(result.error.userMessage).toContain('not in our database');
  });
  
  test('should retry on database connection error', async () => {
    // Mock database to fail twice then succeed
    mockDB.fail(2);
    
    const result = await executeSellCommand({
      item: 'Valid Item',
      quantity: 1
    });
    
    expect(mockDB.attemptCount).toBe(3);
    expect(result.success).toBe(true);
  });
});
```

---

## Summary

This error handling system provides:
- ✅ Clear error hierarchy
- ✅ User-friendly messages
- ✅ Detailed logging
- ✅ Automatic retries for transient failures
- ✅ Admin alerts for critical issues
- ✅ Comprehensive error tracking
- ✅ Consistent formatting
- ✅ Actionable suggestions

By following these patterns, the bot can gracefully handle errors while maintaining a positive user experience.
