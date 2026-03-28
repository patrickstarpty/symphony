# Android Espresso & UIAutomator Patterns

Best practices for Android UI testing.

## Page Object with Espresso

```kotlin
class LoginPageObject(private val device: UiDevice) {

    // Locators using UiSelector
    private val usernameField = device.findObject(
        UiSelector().resourceId("com.example:id/usernameInput")
    )

    private val passwordField = device.findObject(
        UiSelector().resourceId("com.example:id/passwordInput")
    )

    private val loginButton = device.findObject(
        UiSelector().resourceId("com.example:id/loginBtn")
    )

    // Actions
    fun login(username: String, password: String) {
        usernameField.clearTextField()
        usernameField.text = username

        passwordField.clearTextField()
        passwordField.text = password

        loginButton.click()
    }
}
```

## Espresso Matchers

```kotlin
@Test
fun testLogin() {
    onView(withId(R.id.usernameInput))
        .perform(typeText("testuser"))

    onView(withId(R.id.passwordInput))
        .perform(typeText("password123"))

    onView(withId(R.id.loginBtn))
        .perform(click())

    onView(withText("Welcome"))
        .check(matches(isDisplayed()))
}
```

## Content Description (A11y)

```kotlin
@Test
fun testAccessibility() {
    onView(withId(R.id.profilePic))
        .check(matches(hasContentDescription()))

    onView(withContentDescription("User Avatar"))
        .perform(click())
}
```

## Handling Device Rotation

```kotlin
@Test
fun testRotation() {
    // Assume activity survives rotation
    activity.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
    onView(withId(R.id.button)).check(matches(isDisplayed()))

    // Rotate
    activity.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
    onView(withId(R.id.button)).check(matches(isDisplayed()))
}
```
