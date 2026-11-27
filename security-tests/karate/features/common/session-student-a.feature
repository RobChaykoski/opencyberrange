Feature: Student A session

  Scenario: log in once
    * def username = fixture.users.student_a.username
    * def password = fixture.password
    * def xff = '10.40.0.11'
    * def session = call read('common/login.feature')
    * def token = session.token
    * def sessionId = session.sessionId
    * def userId = session.userId
    * def loginUsername = session.loginUsername
