# Component Registry — Project-Specific

> Maintained by tech leads and architects. Defines component criticality for risk scoring. Updated annually or when architecture changes.

## Template

Copy this section per component and customize for your org:

```yaml
components:
  payment:
    tier: critical
    score: 35
    description: "Payment processing, ledger updates, card management"
    paths: ["src/services/payment/", "src/modules/payment/"]
    owners: ["@payment-team"]

  auth:
    tier: critical
    score: 30
    description: "Authentication, JWT, session management"
    paths: ["src/auth/", "src/middleware/auth.ts"]
    owners: ["@security-team"]

  policy:
    tier: high
    score: 20
    description: "Policy operations, underwriting rules"
    paths: ["src/policy/", "src/modules/underwriting/"]
    owners: ["@underwriting-team"]

  api:
    tier: high
    score: 20
    description: "REST/GraphQL API contracts"
    paths: ["src/api/"]
    owners: ["@platform-team"]

  utils:
    tier: low
    score: 10
    description: "Utility functions, helpers"
    paths: ["src/utils/", "src/lib/"]
    owners: ["@platform-team"]
```

## Instructions for Teams

1. List all major components (functional domains)
2. Assign tier based on impact if component fails:
   - **Critical:** Revenue impact, security breach, compliance violation
   - **High:** Operational impact, user experience degradation
   - **Low:** Non-critical features, developer tools
3. Add file paths (glob patterns OK)
4. Assign owning team for escalations
5. Review annually or when architecture changes

## Example (Insurance Domain)

```yaml
components:
  claims:
    tier: critical
    score: 35
    description: "Claims processing, settlements, fraud detection"
    paths: ["src/claims/**", "src/services/claim*.ts"]
    owners: ["@claims-team"]

  underwriting:
    tier: critical
    score: 30
    description: "Risk assessment, policy approval, rating rules"
    paths: ["src/underwriting/**"]
    owners: ["@underwriting-team"]

  billing:
    tier: high
    score: 20
    description: "Premium calculations, invoicing"
    paths: ["src/billing/**"]
    owners: ["@finance-team"]

  customer:
    tier: high
    score: 20
    description: "Customer profiles, communications"
    paths: ["src/customer/**", "src/modules/customer/**"]
    owners: ["@customer-success"]
```
