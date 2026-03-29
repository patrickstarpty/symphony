# Appium Cross-Platform Testing Patterns

Best practices for cross-platform mobile automation with Appium.

## Element Locators

Prefer accessibility ID > XPath:

```typescript
// Good: accessibility ID (works iOS & Android)
const loginButton = await driver.elementByAccessibilityId('login-button');

// Good: XPath with predicates (more stable)
const loginButton = await driver.elementByXPath('//XCUIElementTypeButton[@name="Login"]');

// Avoid: position-based or image locators (brittle)
const button = await driver.elementByImage('button.png');
```

## Gestures

```typescript
// Tap
await driver.elementByAccessibilityId('button').click();

// Swipe
const action = new wd.TouchAction(driver);
action.press({ x: 100, y: 100 })
      .moveTo({ x: 100, y: 200 })
      .release();
await action.perform();

// Long press
const action = new wd.TouchAction(driver);
action.longPress({ element: elem })
      .release();
await action.perform();
```

## Cross-Platform Test

```typescript
const platformName = await driver.platformName();

if (platformName === 'iOS') {
  // iOS-specific logic
  const elem = await driver.elementByAccessibilityId('ios-button');
} else if (platformName === 'Android') {
  // Android-specific logic
  const elem = await driver.elementByResourceId('com.example:id/android_button');
}
```

## Wait Strategies

```typescript
// Wait for element visible
await driver.waitForElementByAccessibilityId('content', 5000);

// Wait for condition
await driver.waitForElementByXPath('//XCUIElementTypeStaticText[@value="Loaded"]', 5000);
```
