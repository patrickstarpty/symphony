# Insurance Domain Data Schemas

Entity definitions, field types, valid ranges, and realistic distributions for test data generation.

## Policy

```json
{
  "id": "string (unique)",
  "policy_number": "string (POL-*)",
  "customer_name": "string",
  "customer_email": "string",
  "coverage_type": "enum: auto|home|life|health",
  "premium_amount": "number (50-5000, mode ~200)",
  "effective_date": "ISO8601 date",
  "expiration_date": "ISO8601 date",
  "status": "enum: active|expired|cancelled|suspended",
  "deductible": "number (250|500|1000|2500)",
  "beneficiary": "string (optional)",
  "claims_history": "array of claim_ids (optional)"
}
```

**Premium Distribution:** Claims cluster around $150-300 for auto, $200-400 for home, $500-1500 for life. Not uniform.

## Claim

```json
{
  "id": "string (unique)",
  "claim_number": "string (CLM-*)",
  "policy_id": "string",
  "incident_date": "ISO8601 date",
  "claim_date": "ISO8601 date",
  "claim_type": "enum: auto|home|life|health|general",
  "amount_claimed": "number (100-50000, mode ~2000)",
  "amount_approved": "number (0 to amount_claimed, optional)",
  "status": "enum: open|approved|denied|pending_review|settled",
  "description": "string",
  "supporting_documents": "array of file_paths (optional)"
}
```

## Customer

```json
{
  "id": "string (unique)",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "date_of_birth": "ISO8601 date (age 18-80)",
  "address": "string",
  "city": "string",
  "state": "string (2-letter code)",
  "zip_code": "string",
  "driver_license_state": "string (optional)",
  "occupation": "string (optional)"
}
```

## Quote

```json
{
  "id": "string (unique)",
  "customer_email": "string",
  "coverage_type": "enum: auto|home|life",
  "estimated_premium": "number (50-1000)",
  "quote_date": "ISO8601 date",
  "expiration_date": "ISO8601 date (quote_date + 30 days)",
  "status": "enum: pending|accepted|expired|rejected",
  "vehicle_info": "object (for auto quotes, optional)",
  "property_info": "object (for home quotes, optional)"
}
```
