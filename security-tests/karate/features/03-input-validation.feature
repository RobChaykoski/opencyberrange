@security @input-validation
Feature: Hostile and malformed input (OWASP A03, A04, A05)

  Background:
    * def authA = karate.callSingle('common/session-student-a.feature')
    * def suffix = fixture.run_id
    * url baseUrl

  Scenario: a non-string username is a validation error, not a server error
    * path 'api/auth/register'
    * def payload = {}
    * payload.username = { nested: 'object' }
    * payload.email = 'type1@example.invalid'
    * payload.password = 'Kx7#Qv2!Lm9\$'
    * payload.privacy_acknowledged = true
    * payload.age_band = '18_plus'
    * request payload
    * method post
    * match responseStatus == 422

  Scenario: a non-string password is a validation error
    * path 'api/auth/register'
    * def payload = {}
    * payload.username = 'karate_type_' + suffix
    * payload.email = 'type2@example.invalid'
    * payload.password = ['not', 'a', 'string']
    * payload.privacy_acknowledged = true
    * payload.age_band = '18_plus'
    * request payload
    * method post
    * match responseStatus == 422

  Scenario Outline: injection strings are rejected without a server error
    * path 'api/auth/register'
    * def payload = {}
    * payload.username = usernameValue
    * payload.email = emailValue
    * payload.password = 'Kx7#Qv2!Lm9\$'
    * payload.privacy_acknowledged = true
    * payload.age_band = '18_plus'
    * request payload
    * method post
    * assert responseStatus === 400 || responseStatus === 422
    * assert responseStatus !== 500

    Examples:
      | usernameValue             | emailValue            |
      | a' OR '1'='1              | sqli@example.invalid  |
      | <script>alert(1)</script> | xss@example.invalid   |

  Scenario: a control character in the username is rejected
    * def badName = 'control' + String.fromCharCode(0) + 'name'
    * path 'api/auth/register'
    * def payload = {}
    * payload.username = badName
    * payload.email = 'control@example.invalid'
    * payload.password = 'Kx7#Qv2!Lm9\$'
    * payload.privacy_acknowledged = true
    * payload.age_band = '18_plus'
    * request payload
    * method post
    * assert responseStatus === 400 || responseStatus === 422

  Scenario: registration without the privacy acknowledgment is refused
    * path 'api/auth/register'
    * def payload = {}
    * payload.username = 'karate_privacy_' + suffix
    * payload.email = 'privacy@example.invalid'
    * payload.password = 'Kx7#Qv2!Lm9\$'
    * payload.privacy_acknowledged = false
    * payload.age_band = '18_plus'
    * request payload
    * method post
    * match responseStatus == 400

  Scenario: an under-13 self-registration is refused
    * path 'api/auth/register'
    * def payload = {}
    * payload.username = 'karate_minor_' + suffix
    * payload.email = 'minor@example.invalid'
    * payload.password = 'Kx7#Qv2!Lm9\$'
    * payload.privacy_acknowledged = true
    * payload.age_band = 'under_13'
    * request payload
    * method post
    * match responseStatus == 403

  Scenario: an oversized email is a validation error
    * def longEmail = 'a'.repeat(500) + '@example.invalid'
    * path 'api/auth/register'
    * def payload = {}
    * payload.username = 'karate_long_' + suffix
    * payload.email = longEmail
    * payload.password = 'Kx7#Qv2!Lm9\$'
    * payload.privacy_acknowledged = true
    * payload.age_band = '18_plus'
    * request payload
    * method post
    * match responseStatus == 422

  Scenario: malformed JSON is rejected
    * path 'api/auth/register'
    * header Content-Type = 'application/json'
    * request '{this is not json'
    * method post
    * match responseStatus == 422

  Scenario Outline: path traversal on the about endpoints is refused
    * def target = baseUrl + pathValue
    * url target
    * header Authorization = 'Bearer ' + authA.token
    * method get
    * assert responseStatus === 400 || responseStatus === 404
    * assert responseStatus !== 200

    Examples:
      | pathValue                                             |
      | /api/about/sbom/..%2f..%2fapp%2fconfig.py            |
      | /api/about/licence/%2e%2e%2f%2e%2e%2fapp%2fconfig.py |
