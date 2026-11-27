@security @upload
Feature: Upload authorization and archive validation (OWASP A04, A05)

  Background:
    * def authA = karate.callSingle('common/session-student-a.feature')
    * def authI = karate.callSingle('common/session-instructor.feature')
    * def suffix = fixture.run_id
    * url baseUrl

  Scenario: an anonymous upload is rejected
    * path 'api/admin/workbook/upload'
    * multipart file file = { read: '../fixtures/valid.zip', filename: 'valid.zip', contentType: 'application/zip' }
    * multipart field chapter_dir = 'CH_KARATE_TEST_' + suffix
    * multipart field section_name = 'Karate Test'
    * multipart field auto_build = false
    * method post
    * match responseStatus == 401

  Scenario: a learner cannot upload workbook content
    * path 'api/admin/workbook/upload'
    * header Authorization = 'Bearer ' + authA.token
    * multipart file file = { read: '../fixtures/valid.zip', filename: 'valid.zip', contentType: 'application/zip' }
    * multipart field chapter_dir = 'CH_KARATE_TEST_' + suffix
    * multipart field section_name = 'Karate Test'
    * multipart field auto_build = false
    * method post
    * match responseStatus == 403

  Scenario: a file that is not a zip is rejected before extraction
    * path 'api/admin/workbook/upload'
    * header Authorization = 'Bearer ' + authI.token
    * multipart file file = { read: '../fixtures/not-a-zip.zip', filename: 'not-a-zip.zip', contentType: 'application/zip' }
    * multipart field chapter_dir = 'CH_KARATE_TEST_' + suffix
    * multipart field section_name = 'Karate Test'
    * multipart field auto_build = false
    * method post
    * match responseStatus == 400

  Scenario: a zip with no markdown is rejected
    * path 'api/admin/workbook/upload'
    * header Authorization = 'Bearer ' + authI.token
    * multipart file file = { read: '../fixtures/non-md.zip', filename: 'non-md.zip', contentType: 'application/zip' }
    * multipart field chapter_dir = 'CH_KARATE_TEST_' + suffix
    * multipart field section_name = 'Karate Test'
    * multipart field auto_build = false
    * method post
    * match responseStatus == 400

  Scenario: a traversal chapter directory is rejected
    * path 'api/admin/workbook/upload'
    * header Authorization = 'Bearer ' + authI.token
    * multipart file file = { read: '../fixtures/valid.zip', filename: 'valid.zip', contentType: 'application/zip' }
    * multipart field chapter_dir = '../escape'
    * multipart field section_name = 'Karate Test'
    * multipart field auto_build = false
    * method post
    * match responseStatus == 400
