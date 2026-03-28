# Insurance Domain Test Patterns

## Policy Lifecycle

Test the complete state machine:
```
Quote → Application → Underwriting → Bind → Active → Endorse → Renew → Cancel
                         ↓
                      Decline
```

**Key test scenarios:**
- Quote-to-bind happy path
- Mid-term endorsement (coverage change, address change)
- Renewal with premium change
- Cancellation with pro-rata refund calculation
- Reinstatement after lapse
- Declined application (underwriting rules)

## Claims Processing

```
FNOL → Assignment → Investigation → Adjudication → Payment → Close
  ↓                                      ↓
Duplicate                             Denial → Appeal
```

**Key test scenarios:**
- FNOL with all required fields
- Duplicate claim detection
- Subrogation identification
- Reserve calculation and adjustment
- Payment with deductible application
- Denial with required notice generation

## Premium Calculation

**Rating factors to test:**
- Base rate by coverage type
- Territory/location modifier
- Claims history modifier (0-claim discount, surcharge for at-fault)
- Multi-policy discount
- Deductible credit
- Minimum premium floor
- State-specific surcharges and fees

**Edge cases:**
- Minimum premium applies (calculated < floor)
- Maximum discount cap
- Overlapping discount rules
- Mid-term rate change effective dating
- Leap year handling in pro-rata calculations

## Regulatory Compliance

- State-specific cancellation notice periods (10/30/60 days)
- Required form filings by state
- Rate filing effective dates
- Surplus lines tax calculations
- Residual market mechanisms
