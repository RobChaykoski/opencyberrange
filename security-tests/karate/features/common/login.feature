Feature: Login helper

  Scenario: log in with a fixture identity
    * url baseUrl
    * header X-Forwarded-For = xff
    * path 'api/auth/login'
    * form field username = username
    * form field password = password
    * method post
    * match responseStatus == 200
    * def token = response.access_token
    * def refreshToken = response.refresh_token
    * def sessionId = response.session_id
    * def userId = response.user.id
    * def loginUsername = response.user.username
