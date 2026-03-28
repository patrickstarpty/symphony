# Test Design Techniques

## Equivalence Partitioning (EP)

Divide input domain into classes where all values in a class should produce the same behavior.

**How to apply:**
1. Identify input parameters
2. For each parameter, define valid and invalid partitions
3. Write one test per partition

**Example — age validation (18-65):**
| Partition | Range | Expected | Test Value |
|-----------|-------|----------|------------|
| Below minimum (invalid) | < 18 | reject | 10 |
| Valid range | 18-65 | accept | 30 |
| Above maximum (invalid) | > 65 | reject | 80 |

## Boundary Value Analysis (BVA)

Test at exact boundaries where behavior changes.

**How to apply:**
1. Identify boundaries from EP partitions
2. Test: min-1, min, min+1, max-1, max, max+1

**Example — age validation (18-65):**
| Point | Value | Expected |
|-------|-------|----------|
| min-1 | 17 | reject |
| min | 18 | accept |
| min+1 | 19 | accept |
| max-1 | 64 | accept |
| max | 65 | accept |
| max+1 | 66 | reject |

## Decision Tables

For logic with multiple conditions, enumerate combinations.

**Example — discount eligibility:**
| Member? | Coupon? | Order > $50? | Discount |
|---------|---------|--------------|----------|
| Y | Y | Y | 20% |
| Y | Y | N | 15% |
| Y | N | Y | 10% |
| Y | N | N | 5% |
| N | Y | Y | 10% |
| N | Y | N | 5% |
| N | N | Y | 0% |
| N | N | N | 0% |

## State Transition Testing

For stateful systems, test all valid transitions and reject invalid ones.

**How to apply:**
1. Draw state diagram
2. Test every valid transition
3. Test at least one invalid transition per state
