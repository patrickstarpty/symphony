# Insurance System Load Profiles

Typical load patterns for insurance applications.

## Daily Load Pattern

Insurance systems experience peak load during business hours:

- **Off-peak (midnight-6am):** 5-10 concurrent users
- **Business hours (8am-5pm):** 100-500 concurrent users
- **Peak hours (10am, 2-3pm):** 500-1000 concurrent users
- **Evening (5pm-midnight):** 20-100 concurrent users

## Feature-Specific Load

- **Quote engine:** High load (users shop around), 50 RPS at peak
- **Policy management:** Moderate load, 20 RPS
- **Claims processing:** Spike load (after incidents), 100+ RPS
- **Admin dashboard:** Predictable, 5-10 RPS

## Seasonal Load

- **Open enrollment (Oct-Dec):** 3-5x normal load
- **Year-end (Nov-Dec):** Policy renewal rush, 2x normal
- **Incident season (hurricane, winter):** Claims spike, 10x normal

## Load Profile Examples

### Standard Quote Session
```
1. GET /api/quote-form (fetch form metadata)
2. Think 5s
3. POST /api/quotes (submit form)
4. Think 3s
5. GET /api/quotes/{id} (check status)
6. GET /api/quotes/{id}/download (download PDF)
```

### Claims Filing
```
1. GET /api/claims/new (form)
2. POST /api/claims (submit)
3. Think 10s (user attaches documents)
4. POST /api/claims/{id}/documents (upload)
5. GET /api/claims/{id} (confirm)
```

## Concurrency Sizing

For typical insurance SaaS (1M policies):

| VUs | Concurrent Sessions | Estimated Coverage |
|-----|-------------------|-------------------|
| 10 | 5-10 real users | Development |
| 50 | 25-50 real users | Staging |
| 100 | 50-100 real users | Load test (baseline) |
| 500 | 250-500 real users | Peak hour simulation |
| 2000 | 1000-2000 real users | Open enrollment peak |
