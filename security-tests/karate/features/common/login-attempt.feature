Feature: Login attempt helper

  Scenario: send a login attempt without asserting the outcome
    * url baseUrl
    * header X-Forwarded-For = xff
    * path 'api/auth/login'
    * form field username = username
    * form field password = password
    * method post
    * def code = responseStatus
    * def body = response
    * def raw = JSON.stringify(response)
