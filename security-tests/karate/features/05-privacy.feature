@security @privacy
Feature: Privacy boundaries and data minimization

  Background:
    * def authA = karate.callSingle('common/session-student-a.feature')
    * def authB = karate.callSingle('common/session-student-b.feature')
    * def studentA = fixture.users.student_a
    * def studentB = fixture.users.student_b
    * url baseUrl

  Scenario: the account export contains only the caller's identity
    * path 'api/auth/export'
    * header Authorization = 'Bearer ' + authA.token
    * method get
    * match responseStatus == 200
    * def raw = typeof response === 'string' ? response : JSON.stringify(response)
    * assert raw.indexOf(studentA.username) >= 0
    * assert raw.indexOf(studentB.username) === -1
    * assert raw.indexOf(studentB.email) === -1
    * assert raw.indexOf('hashed_password') === -1
    * assert raw.indexOf('password_hash') === -1

  Scenario: the profile summary is scoped to the caller
    * path 'api/profile/summary'
    * header Authorization = 'Bearer ' + authA.token
    * method get
    * match responseStatus == 200
    * def raw = JSON.stringify(response)
    * assert raw.indexOf(studentA.username) >= 0
    * assert raw.indexOf(studentB.username) === -1
    * assert raw.indexOf(studentB.email) === -1

  Scenario: a denied admin request does not leak learner rows
    * path 'api/admin/users'
    * header Authorization = 'Bearer ' + authA.token
    * method get
    * match responseStatus == 403
    * def raw = JSON.stringify(response)
    * assert raw.indexOf(studentB.email) === -1
    * assert raw.indexOf(studentA.email) === -1

  Scenario: a public record that does not exist reveals nothing about learners
    * path 'api/competitions/public/999999'
    * header Authorization = null
    * method get
    * match responseStatus == 404
    * def raw = JSON.stringify(response)
    * assert raw.indexOf(studentA.email) === -1
    * assert raw.indexOf(studentB.email) === -1

  Scenario: the DNA surface is consent-gated or scoped to the caller
    * path 'api/dna/v3/dna'
    * header Authorization = 'Bearer ' + authA.token
    * method get
    * def code = responseStatus
    * assert code === 200 || code === 403
    * def raw = JSON.stringify(response)
    * assert raw.indexOf(studentB.username) === -1
    * assert raw.indexOf(studentB.email) === -1
    * def consentHeaderOk = (code !== 403) || (responseHeaders['x-consent-status'] != null)
    * assert consentHeaderOk

  Scenario: a public events feed carries no fixture identity
    * path 'api/public/community-events'
    * header Authorization = null
    * method get
    * match responseStatus == 200
    * def raw = JSON.stringify(response)
    * assert raw.indexOf(studentA.email) === -1
    * assert raw.indexOf(studentB.email) === -1
