@security @access-control
Feature: Vertical and horizontal privilege boundaries (OWASP A01)

  Background:
    * def authA = karate.callSingle('common/session-student-a.feature')
    * def authB = karate.callSingle('common/session-student-b.feature')
    * def authI = karate.callSingle('common/session-instructor.feature')
    * def studentA = fixture.users.student_a
    * def studentB = fixture.users.student_b
    * url baseUrl

  Scenario Outline: a learner cannot reach the admin surface
    * path '<path>'
    * header Authorization = 'Bearer ' + authA.token
    * header X-Forwarded-For = '10.60.1.1'
    * method get
    * match responseStatus == 403

    Examples:
      | path                              |
      | api/admin/users                   |
      | api/admin/stats                   |
      | api/admin/security/rbac/matrix    |
      | api/admin/system/status           |
      | api/admin/system/data-integrity   |

  Scenario: an unauthenticated caller is rejected before authorization
    * path 'api/admin/users'
    * header Authorization = null
    * method get
    * match responseStatus == 401

  Scenario: an instructor is still not a platform administrator
    * path 'api/admin/users'
    * header Authorization = 'Bearer ' + authI.token
    * method get
    * match responseStatus == 403

  Scenario: a learner cannot read another learner's admin record
    * path 'api/admin/users/' + studentB.id
    * header Authorization = 'Bearer ' + authA.token
    * method get
    * match responseStatus == 403
    * def raw = JSON.stringify(response)
    * assert raw.indexOf(studentB.email) === -1

  Scenario: a learner cannot delete their own account through the admin API
    * path 'api/admin/users/' + studentA.id
    * header Authorization = 'Bearer ' + authA.token
    * method delete
    * match responseStatus == 403

  Scenario: query parameters do not widen the admin user list
    * path 'api/admin/users'
    * param user_id = studentB.id
    * header Authorization = 'Bearer ' + authA.token
    * method get
    * match responseStatus == 403

  Scenario: extra JSON fields cannot grant the admin role
    * path 'api/auth/settings'
    * header Authorization = 'Bearer ' + authA.token
    * request { is_admin: true, role: 'admin', is_approved: true }
    * method put
    * match responseStatus == 200
    * path 'api/auth/me'
    * header Authorization = 'Bearer ' + authA.token
    * method get
    * match responseStatus == 200
    * def elevated = response.is_admin
    * assert elevated === undefined || elevated === false

  Scenario: one learner cannot revoke another learner's session
    * path 'api/auth/sessions/' + authA.sessionId
    * header Authorization = 'Bearer ' + authB.token
    * method delete
    * assert responseStatus === 403 || responseStatus === 404
    * path 'api/auth/me'
    * header Authorization = 'Bearer ' + authA.token
    * method get
    * match responseStatus == 200
