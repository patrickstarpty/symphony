# Web Testing Standards

Accessibility, responsive design, and cross-browser testing.

## WCAG A11y Checklist

- [ ] Form inputs have associated `<label>` elements
- [ ] Interactive elements have `aria-label` or visible text
- [ ] Color contrast ratio >= 4.5:1 (normal text), 3:1 (large text)
- [ ] Focus indicators visible (outline or custom)
- [ ] Touch targets >= 44x44 px
- [ ] Images have alt text (empty alt for decorative)
- [ ] Links have descriptive text (not "click here")
- [ ] Headings in logical order (h1, h2, h3)
- [ ] ARIA landmarks: main, nav, contentinfo
- [ ] Error messages linked to form fields

## Responsive Design Testing

```typescript
// Test multiple viewports
const viewports = [
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1920, height: 1080 },
];

for (const vp of viewports) {
  await page.setViewportSize({ width: vp.width, height: vp.height });
  // Assert layout changes, buttons visible, no overflow
  expect(await page.locator('button').count()).toBeGreaterThan(0);
}
```

## Cross-Browser Compatibility

Test on multiple browsers to catch platform-specific issues:

```typescript
export default {
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
};
```

## Test Data Best Practices

- Use realistic data (test.example email, 555-0100 phone)
- Avoid PII in assertions
- Clean up test data after each suite
- Use fixtures for shared data
