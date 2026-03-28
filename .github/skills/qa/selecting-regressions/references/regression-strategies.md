# Regression Testing Strategies — Reference

## Strategy Selection by Risk

### Low Risk (score 0-24)

**Approach:** Minimal subset
- Only tests for directly affected modules
- Skip smoke/integration tests
- Est. time: <5 min

**When applicable:**
- Small bug fix in isolated utility
- Typo/comment fix
- Single-module feature addition

### Medium Risk (score 25-49)

**Approach:** Smart selection
- Affected modules + direct dependents
- Smoke test suite for system health
- Platform-specific tests if UI changes
- Est. time: 5-15 min

**When applicable:**
- Cross-module feature
- API endpoint change
- Database schema change (non-structural)

### High Risk (score 50-74)

**Approach:** Comprehensive
- Full transitive dependency chain
- Full smoke test suite
- All platform-specific test suites
- Security/auth smoke tests even if unaffected
- Est. time: 15-30 min

**When applicable:**
- Authentication/authorization change
- Dependency upgrade
- Database structural change
- Shared infrastructure modification

### Critical Risk (score 75-100)

**Approach:** Full regression
- Run all tests
- Can parallelize to reduce wall-clock time
- Est. time: 30+ min (60+ parallel)

**When applicable:**
- Payment/billing system change
- Security-critical module
- Policy approval/underwriting change
- Framework/library upgrade

## Test Selection Heuristics

### By File Pattern

```
src/auth/**           → Always include (auth tests critical)
src/payment/**        → Always include
src/policy/**         → Always include if risk ≥ high
src/api/**            → Include affected + smoke tests
src/utils/**          → Include affected only (low risk)
src/__tests__/**      → Include matching src file
```

### By Naming Convention

```
*.critical.test.ts    → Always include
*.smoke.test.ts       → Include for risk ≥ medium
*.integration.test.ts → Include for risk ≥ medium
*.unit.test.ts        → Include only if directly affected
*.e2e.test.ts         → Include for risk ≥ high
```

### Shared Infrastructure Changes

Always run full regression if changes touch:
- `package.json` (deps)
- `tsconfig.json` (compilation)
- `.env.example` (config schema)
- `src/middleware/**` (global middleware)
- `src/config/**` (configuration)
- Database migrations

**Reason:** Config/middleware changes affect all modules transitively.

## Confidence Levels

### High Confidence

✓ Full dependency graph available (from build system or Knowledge Base)
✓ Complete test catalog with accurate file mappings
✓ Risk score computed from change scope + component criticality + defect history

**Action:** Run selected tests only; approve if pass.

### Medium Confidence

⚠ Partial dependency graph (heuristic file matching)
⚠ Some test files may be missing from catalog
⚠ Risk score lacks defect history

**Action:** Run selection + smoke test suite; require manual review if smoke fails.

### Low Confidence

✗ No dependency graph available
✗ Test mappings are filename-based guesses
✗ Large change or unknown risk

**Action:** Warn and recommend full test suite; provide justification for selection.

## Best Practices

1. **Version your dependency graph:** Track imports/dependencies per commit for regression accuracy
2. **Maintain test catalog metadata:** Document test type (unit/integration/e2e), module, tags, estimated time
3. **Baseline smoke suite:** Define minimal smoke tests that must always pass
4. **Critical path coverage:** Ensure auth, payment, policy tests are always included for their changes
5. **Review skipped tests:** Periodically audit skipped tests to validate heuristics
6. **Monitor test reliability:** Track flaky tests separately from selection logic
7. **Parallel execution:** For risk ≥ high, parallelize to maintain reasonable CI time
