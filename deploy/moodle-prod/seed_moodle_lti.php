<?php
// Register OpenCyberRange as an LTI 1.3 course tool in the training Moodle
// and create a pre-linked demo activity.
//
// Run inside the Moodle container:
//   php /seed/seed_moodle_lti.php
//
// Moodle 5 requires a course-level tool definition before an activity can be
// created. This seed is idempotent and reuses the course tool and activity on
// later runs.
//
// Optional environment:
//   OCR_PUBLIC_URL                   Browser-facing OCR base URL
//   OCR_INTERNAL_URL                 OCR base URL Moodle uses for JWKS (defaults to public)
//   MOODLE_LTI_CLIENT_ID             Client id to use when creating a new course tool
//   MOODLE_LTI_COURSE                Course shortname (default OCR-CAP-COHORT)
//   MOODLE_LTI_COURSE_TOOL_NAME      Course tool name
//   MOODLE_LTI_ACTIVITY_NAME         Demo activity name
//   MOODLE_LTI_LAB_SLUG              Exercise slug (default network-1-1-packet-capture-analysis)
//   MOODLE_LTI_SECTION               Course section number (default 1)
//   MOODLE_ALLOW_PRIVATE_LTI_URLS    Set to 1 to relax dev Moodle cURL security

define('CLI_SCRIPT', true);
chdir('/bitnami/moodle');
require('/bitnami/moodle/config.php');
require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->dirroot . '/course/lib.php');

global $DB;

$clientId = trim(getenv('MOODLE_LTI_CLIENT_ID') ?: 'ocr-training-client');
$ocrBase = rtrim(getenv('OCR_PUBLIC_URL') ?: 'https://172.16.16.44', '/');
$ocrInternal = rtrim(getenv('OCR_INTERNAL_URL') ?: $ocrBase, '/');
$courseShortname = getenv('MOODLE_LTI_COURSE') ?: 'OCR-CAP-COHORT';
$courseToolName = getenv('MOODLE_LTI_COURSE_TOOL_NAME') ?: 'OpenCyberRange Showcase';
$activityName = getenv('MOODLE_LTI_ACTIVITY_NAME') ?: 'Avalon Biotech - Suspicious Traffic Analysis';
$labSlug = getenv('MOODLE_LTI_LAB_SLUG') ?: 'network-1-1-packet-capture-analysis';
$section = (int)(getenv('MOODLE_LTI_SECTION') ?: 1);
$allowPrivate = getenv('MOODLE_ALLOW_PRIVATE_LTI_URLS') === '1';

$course = $DB->get_record('course', ['shortname' => $courseShortname], '*', MUST_EXIST);
$admins = get_admins();
if (empty($admins)) {
    throw new moodle_exception('No site administrator found');
}
$admin = reset($admins);
$parsed = parse_url($ocrBase);
$tooldomain = $parsed['host'] ?? '';
if (!empty($parsed['port'])) {
    $tooldomain .= ':' . $parsed['port'];
}
$launchUrl = $ocrBase . '/api/lti/launch';

if ($allowPrivate) {
    // Dev-only: host.docker.internal resolves to a private Docker gateway, and
    // the local tool runs on a non-standard port. Moodle's SSRF allow-list
    // would otherwise block JWKS and AGS/NRPS calls.
    set_config('curlsecurityblockedhosts', '');
    $ports = ['80', '443'];
    foreach ([$ocrBase, $ocrInternal] as $url) {
        $port = parse_url($url, PHP_URL_PORT);
        if ($port) {
            $ports[] = (string)$port;
        }
    }
    set_config('curlsecurityallowedport', implode("\n", array_unique($ports)));
    echo "warning=relaxed Moodle cURL security for private LTI URLs (dev only)\n";
}

/**
 * Upsert one course-tool configuration value.
 */
function training_lti_config(int $typeid, string $name, string $value): void {
    global $DB;
    $existing = $DB->get_record('lti_types_config', ['typeid' => $typeid, 'name' => $name]);
    if ($existing) {
        if ((string)$existing->value !== $value) {
            $existing->value = $value;
            $DB->update_record('lti_types_config', $existing);
        }
        return;
    }
    $DB->insert_record('lti_types_config', (object)[
        'typeid' => $typeid,
        'name' => $name,
        'value' => $value,
    ]);
}

// Moodle 5 course tool. Reuse by name, then by client id, and only create when
// neither exists. This keeps the seed idempotent and avoids changing an
// existing client id that an LMS platform already registered.
$type = $DB->get_record('lti_types', [
    'course' => $course->id,
    'name' => $courseToolName,
]);
if (!$type) {
    $type = $DB->get_record('lti_types', [
        'course' => $course->id,
        'clientid' => $clientId,
    ]);
}
if (!$type) {
    $effectiveClientId = $clientId;
    if ($DB->record_exists('lti_types', ['clientid' => $effectiveClientId])) {
        $effectiveClientId .= '-course';
    }
    $typeId = $DB->insert_record('lti_types', (object)[
        'name' => $courseToolName,
        'baseurl' => $launchUrl,
        'tooldomain' => $tooldomain,
        'state' => 1,
        'course' => $course->id,
        'coursevisible' => 2,
        'ltiversion' => '1.3.0',
        'clientid' => $effectiveClientId,
        'createdby' => $admin->id,
        'timecreated' => time(),
        'timemodified' => time(),
        'description' => 'Synthetic LTI 1.3 course tool for the dev training lab.',
    ]);
    $type = $DB->get_record('lti_types', ['id' => $typeId], '*', MUST_EXIST);
}

if (empty($type->clientid)) {
    $effectiveClientId = $clientId;
    if ($DB->record_exists('lti_types', ['clientid' => $effectiveClientId])) {
        $effectiveClientId .= '-course';
    }
    $type->clientid = $effectiveClientId;
}

$type->name = $courseToolName;
$type->baseurl = $launchUrl;
$type->tooldomain = $tooldomain;
$type->state = 1;
$type->course = $course->id;
$type->coursevisible = 2;
$type->ltiversion = '1.3.0';
$type->timemodified = time();
$DB->update_record('lti_types', $type);
$clientId = $type->clientid;

$config = [
    'keytype' => 'JWK_KEYSET',
    'publickeyset' => $ocrInternal . '/api/lti/jwks',
    'initiatelogin' => $ocrBase . '/api/lti/login',
    'redirectionuris' => $ocrBase . '/api/lti/launch',
    'customparameters' => '',
    'coursevisible' => '2',
    'launchcontainer' => '3',
    'contentitem' => '1',
    'toolurl_ContentItemSelectionRequest' => $launchUrl,
    'ltiservice_gradesynchronization' => '2',
    'ltiservice_memberships' => '1',
    'ltiservice_toolsettings' => '1',
    'sendname' => '1',
    'sendemailaddr' => '1',
    'acceptgrades' => '1',
    'forcessl' => ($parsed['scheme'] ?? '') === 'https' ? '1' : '0',
];
foreach ($config as $name => $value) {
    training_lti_config((int)$type->id, $name, $value);
}
if (!$DB->record_exists('lti_types_config', ['typeid' => $type->id, 'name' => 'servicesalt'])) {
    training_lti_config((int)$type->id, 'servicesalt', uniqid('', true));
}

$toolUrl = $launchUrl . '?lab=' . rawurlencode($labSlug);
$custom = 'lab_slug=' . $labSlug;
$lti = $DB->get_record('lti', ['course' => $course->id, 'name' => $activityName]);
if ($lti) {
    $lti->typeid = (int)$type->id;
    $lti->toolurl = $toolUrl;
    $lti->instructorcustomparameters = $custom;
    $lti->instructorchoicesendname = 1;
    $lti->instructorchoicesendemailaddr = 1;
    $lti->instructorchoiceallowroster = 1;
    $lti->instructorchoiceacceptgrades = 1;
    $lti->grade = 100;
    $lti->launchcontainer = 1;
    $lti->showtitlelaunch = 1;
    $lti->showdescriptionlaunch = 0;
    $lti->timemodified = time();
    $DB->update_record('lti', $lti);
} else {
    $module = $DB->get_record('modules', ['name' => 'lti'], '*', MUST_EXIST);
    add_moduleinfo((object)[
        'modulename' => 'lti',
        'module' => (int)$module->id,
        'course' => $course->id,
        'section' => $section,
        'visible' => 1,
        'name' => $activityName,
        'intro' => 'Launch the synthetic OpenCyberRange exercise from this Moodle course.',
        'introformat' => FORMAT_HTML,
        'typeid' => (int)$type->id,
        'toolurl' => $toolUrl,
        'securetoolurl' => '',
        'instructorcustomparameters' => $custom,
        'instructorchoicesendname' => 1,
        'instructorchoicesendemailaddr' => 1,
        'instructorchoiceallowroster' => 1,
        'instructorchoiceallowsetting' => 0,
        'instructorchoiceacceptgrades' => 1,
        'grade' => 100,
        'launchcontainer' => 1,
        'showtitlelaunch' => 1,
        'showdescriptionlaunch' => 0,
        'resourcekey' => '',
        'password' => '',
        'debuglaunch' => 0,
    ], $course);
    $lti = $DB->get_record('lti', [
        'course' => $course->id,
        'name' => $activityName,
    ], '*', MUST_EXIST);
}

$module = $DB->get_record('modules', ['name' => 'lti'], '*', MUST_EXIST);
$cm = $DB->get_record('course_modules', [
    'module' => $module->id,
    'instance' => $lti->id,
]);
if ($cm) {
    $cm->visible = 1;
    $DB->update_record('course_modules', $cm);
}
rebuild_course_cache($course->id, true);

echo "course_tool_id={$type->id}\n";
echo "client_id={$clientId}\n";
echo "deployment_id={$type->id}\n";
echo "activity_id={$lti->id}\n";
echo "cmid=" . ($cm ? $cm->id : 0) . "\n";
echo "course_id={$course->id}\n";
echo "lab_slug={$labSlug}\n";
