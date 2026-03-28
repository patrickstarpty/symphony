# Page Object Model Conventions

Structure and naming conventions for Page Objects.

## Class Structure

```typescript
export class LoginPage {
  constructor(readonly page: Page) {}

  // Locators (private, use methods to access)
  private usernameField = () => this.page.locator('[data-testid="username"]');
  private passwordField = () => this.page.locator('[data-testid="password"]');
  private submitButton = () => this.page.locator('button[type="submit"]');

  // Actions (public methods)
  async enterUsername(username: string): Promise<void> {
    await this.usernameField().fill(username);
  }

  async enterPassword(password: string): Promise<void> {
    await this.passwordField().fill(password);
  }

  async clickLogin(): Promise<void> {
    await this.submitButton().click();
  }

  async login(username: string, password: string): Promise<void> {
    await this.enterUsername(username);
    await this.enterPassword(password);
    await this.clickLogin();
  }

  // Assertions (return state/value for chaining)
  async isLoginButtonEnabled(): Promise<boolean> {
    return await this.submitButton().isEnabled();
  }

  async getErrorMessage(): Promise<string> {
    return await this.page.locator('[role="alert"]').textContent();
  }
}
```

## Naming Conventions

- **Locator methods:** snake_case, describe element type: `submitButton()`, `emailInput()`, `submitError()`
- **Action methods:** `click*`, `fill*`, `select*`, `hover*`: `clickSubmit()`, `fillEmail()`, `selectCountry()`
- **Assertion methods:** `is*`, `get*`, `has*`: `isEnabled()`, `getText()`, `hasError()`
- **Navigation methods:** `goto*`, `navigate*`: `gotoLoginPage()`, `navigateTo(url)`

## Encapsulation Rules

1. Locators are private; expose via methods
2. Actions return void or derived Page Object
3. Assertions return values (string, boolean, number)
4. Navigation returns new Page Object or void

```typescript
// Good: Encapsulated
export class CheckoutPage {
  async proceedToPayment(): Promise<PaymentPage> {
    await this.continueButton().click();
    return new PaymentPage(this.page);
  }
}

// Bad: Exposed locator
export class CheckoutPage {
  continueButton = () => this.page.locator('button.continue');
}
```
