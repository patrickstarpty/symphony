# iOS XCTest Patterns

Best practices for iOS UI testing with XCTest.

## Page Object Structure

```swift
class LoginPage {
    let app: XCUIApplication

    init(_ app: XCUIApplication) {
        self.app = app
    }

    // Locators
    var usernameField: XCUIElement {
        app.textFields.matching(NSPredicate(format: "identifier == 'usernameInput'")).firstMatch
    }

    var passwordField: XCUIElement {
        app.secureTextFields.matching(NSPredicate(format: "identifier == 'passwordInput'")).firstMatch
    }

    var loginButton: XCUIElement {
        app.buttons.matching(NSPredicate(format: "identifier == 'loginBtn'")).firstMatch
    }

    // Actions
    func login(username: String, password: String) {
        usernameField.tap()
        usernameField.typeText(username)

        passwordField.tap()
        passwordField.typeText(password)

        loginButton.tap()
    }
}
```

## Async Wait Patterns

```swift
func testLogin() {
    let app = XCUIApplication()
    app.launch()

    // Wait for element existence
    let predicate = NSPredicate(format: "exists == true")
    expectation(for: predicate, evaluatedWith: app.staticTexts["Welcome"], handler: nil)
    waitForExpectations(timeout: 5)

    // Or explicit wait
    let element = app.staticTexts["Welcome"]
    let waitExpectation = expectation(for: NSPredicate(format: "isHittable == true"), evaluatedWith: element)
    wait(for: [waitExpectation], timeout: 5)
}
```

## Accessibility Testing

```swift
func testAccessibility() {
    let app = XCUIApplication()
    app.launch()

    // Verify accessibility label
    let button = app.buttons.element(matching: NSPredicate(format: "identifier == 'actionBtn'"))
    XCTAssertEqual(button.label, "Confirm Action") // VoiceOver label

    // Check image alternative text
    let icon = app.images["profileIcon"]
    XCTAssert(!icon.label.isEmpty, "Image must have accessibility label")
}
```

## Rotation Handling

```swift
func testPortraitAndLandscape() {
    let app = XCUIApplication()

    // Test in portrait
    XCUIDevice.shared.orientation = .portrait
    app.launch()
    let button = app.buttons["action"]
    XCTAssert(button.exists)

    // Rotate to landscape
    XCUIDevice.shared.orientation = .landscapeRight
    XCTAssert(button.exists, "Button must remain visible after rotation")
}
```
