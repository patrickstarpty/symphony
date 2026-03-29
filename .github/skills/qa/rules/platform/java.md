# Java Testing Rules — P2

> Applied by generating-api-tests when target is Java (JUnit/Mockito/RestAssured).

## Annotations & Junit 5

- Use JUnit 5 annotations (not JUnit 4):
  - ✅ `@Test`, `@BeforeEach`, `@AfterEach`, `@ParameterizedTest`
  - ❌ `@org.junit.Test`, `setUp()`, `tearDown()`
- Test classes must have public scope:
  - ✅ `public class PolicyRenewalTest { }`
  - ❌ `class PolicyRenewalTest { }`
- Test methods must be public and void:
  ```java
  @Test
  public void shouldRenewPolicyWithValidDates() {
      // Arrange, Act, Assert
  }
  ```

## Exception Handling in Tests

- Use `assertThrows()` for exception testing:
  ```java
  InvalidPolicyException thrown = assertThrows(
      InvalidPolicyException.class,
      () -> policy.renew(invalidDate),
      "Premium must be positive"
  );
  assertEquals("Premium must be positive", thrown.getMessage());
  ```
- Never use try-catch to catch expected exceptions

## Stream API Testing

- Test Stream operations in isolation:
  ```java
  @Test
  public void shouldFilterActivePolicies() {
      List<Policy> policies = Arrays.asList(
          new Policy("P1", true),
          new Policy("P2", false),
          new Policy("P3", true)
      );

      List<Policy> active = policies.stream()
          .filter(Policy::isActive)
          .collect(Collectors.toList());

      assertEquals(2, active.size());
  }
  ```
- Use `.toList()` (Java 16+) instead of `collect(Collectors.toList())`

## Spring Test Slicing

- Use `@WebMvcTest` for controller testing (not full context):
  ```java
  @WebMvcTest(PolicyController.class)
  class PolicyControllerTest {
      @MockBean
      private PolicyService policyService;

      @Autowired
      private MockMvc mockMvc;
  }
  ```
- Use `@DataJpaTest` for repository testing (only DB layer, no services)
- Use `@SpringBootTest` only for full integration tests (isolated, not CI/CD)

## Mockito

- Use `@Mock` and `@InjectMocks`:
  ```java
  @Mock
  private PolicyRepository repository;

  @InjectMocks
  private PolicyService service;
  ```
- Verify interactions explicitly:
  ```java
  verify(repository, times(1)).save(any(Policy.class));
  verify(repository, never()).delete(any());
  ```
- Stub return values with `when().thenReturn()`:
  ```java
  when(repository.findById("123"))
      .thenReturn(Optional.of(policy));
  ```

## RestAssured for API Tests

- Use fluent API for readability:
  ```java
  given()
      .contentType(ContentType.JSON)
      .body(createPolicyRequest)
  .when()
      .post("/policies")
  .then()
      .statusCode(201)
      .body("id", notNullValue())
      .body("status", equalTo("active"));
  ```
- Always validate response status code
- Never skip error response validation

## Assertions (AssertJ)

- Use AssertJ for fluent assertions (not Hamcrest in new tests):
  ```java
  assertThat(policy)
      .isNotNull()
      .extracting(Policy::getStatus)
      .isEqualTo("active");
  ```

## Parameterized Tests

- Use `@ParameterizedTest` with `@ValueSource` or `@CsvSource`:
  ```java
  @ParameterizedTest
  @CsvSource({
      "100.00, true",
      "-50.00, false",
      "0.00, false"
  })
  public void shouldValidatePremium(Double premium, boolean expected) {
      assertEquals(expected, Policy.isValidPremium(premium));
  }
  ```
