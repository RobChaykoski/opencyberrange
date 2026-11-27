@security @auth
Feature: Login and token handling (OWASP A01, A02, A07)

  Background:
    * def session = karate.callSingle('common/session-student-a.feature')
    * def student = fixture.users.student_a

  Scenario: a valid login returns a usable bearer token
    * match session.token == '#string'
    * match session.loginUsername == student.username
    * url baseUrl
    * path 'api/auth/me'
    * header Authorization = 'Bearer ' + session.token
    * method get
    * match responseStatus == 200
    * match response.username == student.username
    * def raw = JSON.stringify(response)
    * assert raw.indexOf('hashed_password') === -1
    * assert raw.indexOf('password_hash') === -1
    * assert raw.indexOf('failed_attempts') === -1

  Scenario: a wrong password and an unknown user return the same generic error
    * def username = student.username
    * def password = 'definitely-not-the-password'
    * def xff = '10.50.1.1'
    * def wrong = call read('common/login-attempt.feature')
    * def username = 'no-such-user-' + fixture.run_id
    * def password = 'irrelevant-password'
    * def xff = '10.50.1.2'
    * def unknown = call read('common/login-attempt.feature')
    * match wrong.code == 401
    * match unknown.code == 401
    * match wrong.body.detail == 'Incorrect username or password'
    * match wrong.body == unknown.body
    * assert wrong.body.access_token === undefined

  Scenario Outline: hostile login input still returns the generic error
    * def attempt = call read('common/login-attempt.feature')
    * match attempt.code == 401
    * match attempt.body.detail == 'Incorrect username or password'
    * assert attempt.body.access_token === undefined

    Examples:
      | username                        | password             | xff        |
      | ' OR '1'='1                     | anything             | 10.50.2.1  |
      | <script>alert(1)</script>       | anything             | 10.50.2.2  |

  Scenario: oversized and control-character usernames are rejected
    * def username = 'a'.repeat(5000)
    * def password = 'anything'
    * def xff = '10.50.2.3'
    * def big = call read('common/login-attempt.feature')
    * match big.code == 401
    * def username = 'control' + String.fromCharCode(0) + 'name'
    * def password = 'anything'
    * def xff = '10.50.2.4'
    * def control = call read('common/login-attempt.feature')
    * match control.code == 401
    * match control.body.detail == 'Incorrect username or password'

  Scenario: a JSON body is not accepted by the form login
    * url baseUrl
    * header X-Forwarded-For = '10.50.3.1'
    * path 'api/auth/login'
    * request { username: '#(student.username)', password: '#(fixture.password)' }
    * method post
    * match responseStatus == 422

  Scenario: a malformed authorization header is rejected
    * url baseUrl
    * path 'api/auth/me'
    * header Authorization = 'Basic abc123'
    * method get
    * match responseStatus == 401

  Scenario: a missing authorization header is rejected
    * url baseUrl
    * path 'api/auth/me'
    * method get
    * match responseStatus == 401

  Scenario: a token with a modified payload is rejected
    * def parts = session.token.split('.')
    * def Base64 = Java.type('java.util.Base64')
    * def utf8 = Java.type('java.nio.charset.StandardCharsets').UTF_8
    * def decode = function(s){ return new java.lang.String(Base64.getUrlDecoder().decode(s), utf8) }
    * def encode = function(s){ return Base64.getUrlEncoder().withoutPadding().encodeToString(new java.lang.String(s).getBytes(utf8)) }
    * def payload = JSON.parse(decode(parts[1]))
    * payload.sub = fixture.users.student_b.username
    * payload.sec = 1
    * def tampered = parts[0] + '.' + encode(JSON.stringify(payload)) + '.' + parts[2]
    * url baseUrl
    * path 'api/auth/me'
    * header Authorization = 'Bearer ' + tampered
    * method get
    * match responseStatus == 401

  Scenario: an unsigned alg=none token is rejected
    * def Base64 = Java.type('java.util.Base64')
    * def utf8 = Java.type('java.nio.charset.StandardCharsets').UTF_8
    * def encode = function(s){ return Base64.getUrlEncoder().withoutPadding().encodeToString(new java.lang.String(s).getBytes(utf8)) }
    * def header = encode('{"alg":"none","typ":"JWT"}')
    * def payload = { sub: fixture.users.student_b.username, type: 'access', sec: 1, exp: 4102444800 }
    * def noneToken = header + '.' + encode(JSON.stringify(payload)) + '.'
    * url baseUrl
    * path 'api/auth/me'
    * header Authorization = 'Bearer ' + noneToken
    * method get
    * match responseStatus == 401
