<?php
// Register OpenCyberRange as an LTI 1.3 tool in the training Moodle.
//
// Run inside the Moodle container:
//   php /seed/seed_moodle_lti.php
//
// The tool and the OCR platform use the same client ID. Moodle uses the tool
// type id as the LTI deployment id.

define('CLI_SCRIPT', true);
chdir('/bitnami/moodle');
require('/bitnami/moodle/config.php');
require_once($CFG->dirroot . '/course/modlib.php');

global $DB;

$toolName = 'OpenCyberRange Capstone Tool';
$clientId = 'ocr-training-client';
$ocrBase = getenv('OCR_PUBLIC_URL') ?: 'https://172.16.16.44';

$course = $DB->get_record('course', ['shortname' => 'OCR-CAP-COHORT'], '*', MUST_EXIST);
$admin = $DB->get_record('user', ['username' => 'admin'], '*', MUST_EXIST);

$type = $DB->get_record('lti_types', ['name' => $toolName]);
if (!$type) {
    $typeId = $DB->insert_record('lti_types', (object)[
        'name' => $toolName,
        'baseurl' => $ocrBase . '/api/lti/launch',
        'tooldomain' => parse_url($ocrBase, PHP_URL_HOST),
        'state' => 2,
        'course' => 0,
        'coursevisible' => 1,
        'ltiversion' => '1.3.0',
        'clientid' => $clientId,
        'createdby' => $admin->id,
        'timecreated' => time(),
        'timemodified' => time(),
        'description' => 'Synthetic LTI 1.3 tool for the dev training lab.',
    ]);
    $type = $DB->get_record('lti_types', ['id' => $typeId], '*', MUST_EXIST);
}

if ($type->ltiversion !== '1.3.0' || $type->clientid !== $clientId) {
    $type->ltiversion = '1.3.0';
    $type->clientid = $clientId;
    $DB->update_record('lti_types', $type);
}

$config = [
    'publickeyset' => $ocrBase . '/api/lti/jwks',
    'initiatelogin' => $ocrBase . '/api/lti/login',
    'redirectionuris' => $ocrBase . '/api/lti/launch',
];
foreach ($config as $name => $value) {
    $existing = $DB->get_record('lti_types_config', ['typeid' => $type->id, 'name' => $name]);
    if ($existing) {
        $existing->value = $value;
        $DB->update_record('lti_types_config', $existing);
    } else {
        $DB->insert_record('lti_types_config', (object)[
            'typeid' => $type->id,
            'name' => $name,
            'value' => $value,
        ]);
    }
}

$activity = $DB->get_record('lti', ['course' => $course->id, 'name' => 'OpenCyberRange capstone lab']);
if (!$activity) {
    $module = $DB->get_record('modules', ['name' => 'lti'], '*', MUST_EXIST);
    add_moduleinfo((object)[
        'modulename' => 'lti',
        'module' => (int)$module->id,
        'course' => $course->id,
        'section' => 1,
        'visible' => 1,
        'name' => 'OpenCyberRange capstone lab',
        'intro' => 'Launch the synthetic OpenCyberRange capstone lab.',
        'introformat' => FORMAT_HTML,
        'typeid' => (int)$type->id,
        'toolurl' => $ocrBase . '/api/lti/launch',
        'securetoolurl' => '',
        'launchcontainer' => 1,
        'showtitlelaunch' => 1,
        'showdescriptionlaunch' => 0,
        'instructorchoicesendname' => 1,
        'instructorchoicesendemailaddr' => 1,
        'instructorchoiceallowroster' => 1,
        'instructorchoiceallowsetting' => 0,
        'instructorchoiceacceptgrades' => 1,
        'grade' => 100,
        'resourcekey' => '',
        'password' => '',
        'debuglaunch' => 0,
    ], $course);
}

echo "Moodle LTI tool id={$type->id} client_id={$type->clientid} deployment_id={$type->id}\n";
