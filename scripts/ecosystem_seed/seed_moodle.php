<?php
// Seed a fake training Moodle for OpenCyberRange capstones.
//
// Run inside the Moodle container:
//   docker compose exec -T moodle php /seed/seed_moodle.php
//
// Everything this script creates is synthetic training data. It is idempotent:
// re-running it updates the same users, courses, groups, and enrolments.

define('CLI_SCRIPT', true);
chdir('/bitnami/moodle');
require('/bitnami/moodle/config.php');
require_once($CFG->libdir . '/enrollib.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/user/lib.php');
require_once($CFG->dirroot . '/group/lib.php');
require_once($CFG->dirroot . '/cohort/lib.php');

global $DB;

$password = getenv('TRAINING_PASSWORD') ?: 'TrainLab!2026#Student';

function training_ensure_category(string $name, int $parent = 0): int {
    global $DB;
    $existing = $DB->get_record('course_categories', ['name' => $name, 'parent' => $parent]);
    if ($existing) {
        return (int)$existing->id;
    }
    $category = core_course_category::create([
        'name' => $name,
        'parent' => $parent,
        'visible' => 1,
        'description' => 'Synthetic category for OpenCyberRange training capstones.',
    ]);
    return (int)$category->id;
}

function training_ensure_user(string $username, string $firstname, string $lastname, string $email, string $password): int {
    global $DB;
    $existing = $DB->get_record('user', ['username' => $username, 'deleted' => 0]);
    if ($existing) {
        return (int)$existing->id;
    }
    $user = (object)[
        'auth' => 'manual',
        'confirmed' => 1,
        'mnethostid' => $CFG->mnet_localhost_id ?? 1,
        'username' => $username,
        'password' => $password,
        'firstname' => $firstname,
        'lastname' => $lastname,
        'email' => $email,
        'city' => 'Training',
        'country' => 'CA',
        'timezone' => 'America/Toronto',
        'description' => 'Synthetic training account. Not a real person.',
    ];
    return (int)user_create_user($user, true, false);
}

function training_ensure_course(string $shortname, string $fullname, int $categoryid, string $summary): int {
    global $DB;
    $existing = $DB->get_record('course', ['shortname' => $shortname]);
    if ($existing) {
        return (int)$existing->id;
    }
    $course = create_course((object)[
        'fullname' => $fullname,
        'shortname' => $shortname,
        'category' => $categoryid,
        'summary' => $summary,
        'summaryformat' => FORMAT_HTML,
        'format' => 'topics',
        'visible' => 1,
        'enablecompletion' => 1,
    ]);
    return (int)$course->id;
}

function training_enrol(int $courseid, int $userid, string $roleshortname): void {
    global $DB;
    $roleid = (int)$DB->get_field('role', 'id', ['shortname' => $roleshortname], MUST_EXIST);
    $context = context_course::instance($courseid);
    if (!$DB->record_exists('role_assignments', ['roleid' => $roleid, 'contextid' => $context->id, 'userid' => $userid])) {
        role_assign($roleid, $userid, $context->id);
    }

    $instances = enrol_get_instances($courseid, false);
    $instance = null;
    foreach ($instances as $candidate) {
        if ($candidate->enrol === 'manual') {
            $instance = $candidate;
            break;
        }
    }
    if ($instance === null) {
        $plugin = enrol_get_plugin('manual');
        $instanceid = $plugin->add_default_instance($DB->get_record('course', ['id' => $courseid], '*', MUST_EXIST));
        $instance = $DB->get_record('enrol', ['id' => $instanceid], '*', MUST_EXIST);
    }
    $plugin = enrol_get_plugin('manual');
    if (!$DB->record_exists('user_enrolments', ['enrolid' => $instance->id, 'userid' => $userid])) {
        $plugin->enrol_user($instance, $userid, $roleid, time(), 0, ENROL_USER_ACTIVE);
    }
}

function training_ensure_group(int $courseid, string $name): int {
    global $DB;
    $existing = $DB->get_record('groups', ['courseid' => $courseid, 'name' => $name]);
    if ($existing) {
        return (int)$existing->id;
    }
    return (int)groups_create_group((object)[
        'courseid' => $courseid,
        'name' => $name,
        'description' => 'Synthetic capstone cohort.',
        'descriptionformat' => FORMAT_HTML,
        'enrolmentkey' => '',
        'idnumber' => '',
    ]);
}

function training_group_member(int $groupid, int $userid): void {
    global $DB;
    if (!$DB->record_exists('groups_members', ['groupid' => $groupid, 'userid' => $userid])) {
        groups_add_member($groupid, $userid);
    }
}

$categoryid = training_ensure_category('OpenCyberRange Training');

$courses = [
    'OCR-CAP-SINGLE' => [
        'fullname' => 'Capstone: Single-Student Security Operations',
        'summary' => 'Synthetic single-student capstone. Learners triage a fake incident, document evidence, and submit a short defence.',
    ],
    'OCR-CAP-COHORT' => [
        'fullname' => 'Capstone: Multi-Student Cohort Defence',
        'summary' => 'Synthetic cohort capstone. Teams split detection, identity, and asset work, then produce one joint defence brief.',
    ],
    'OCR-FOUND' => [
        'fullname' => 'Foundations: Identity, Network, and Data Protection',
        'summary' => 'Synthetic foundation course used to test role-aware reporting and progress surfaces.',
    ],
];

$courseids = [];
foreach ($courses as $shortname => $meta) {
    $courseids[$shortname] = training_ensure_course($shortname, $meta['fullname'], $categoryid, $meta['summary']);
    echo "course {$shortname} => {$courseids[$shortname]}\n";
}

$staff = [
    'instructor01' => ['Morgan', 'Instructor', 'editingteacher'],
    'mentor01' => ['Alex', 'Mentor', 'teacher'],
    'ta01' => ['Jamie', 'Assistant', 'editingteacher'],
];
foreach ($staff as $username => $meta) {
    $userid = training_ensure_user($username, $meta[0], $meta[1], $username . '@example.invalid', $password);
    foreach ($courseids as $courseid) {
        training_enrol($courseid, $userid, $meta[2]);
    }
    echo "staff {$username} => {$userid} ({$meta[2]})\n";
}

$students = [];
for ($i = 1; $i <= 8; $i++) {
    $username = sprintf('student%02d', $i);
    $userid = training_ensure_user($username, 'Student', 'Number' . $i, $username . '@example.invalid', $password);
    foreach (['OCR-CAP-SINGLE', 'OCR-FOUND'] as $shortname) {
        training_enrol($courseids[$shortname], $userid, 'student');
    }
    $students[$i] = $userid;
    echo "student {$username} => {$userid}\n";
}

$cohortA = training_ensure_group($courseids['OCR-CAP-COHORT'], 'Cohort A');
$cohortB = training_ensure_group($courseids['OCR-CAP-COHORT'], 'Cohort B');
foreach ($students as $i => $userid) {
    training_enrol($courseids['OCR-CAP-COHORT'], $userid, 'student');
    training_group_member($i <= 4 ? $cohortA : $cohortB, $userid);
}

$cohort = $DB->get_record('cohort', ['idnumber' => 'OCR-TRAINING-COHORT']);
if (!$cohort) {
    $cohortid = cohort_add_cohort((object)[
        'contextid' => context_system::instance()->id,
        'name' => 'OCR Training Cohort',
        'idnumber' => 'OCR-TRAINING-COHORT',
        'description' => 'Synthetic cohort used for multi-student capstone testing.',
    ]);
} else {
    $cohortid = (int)$cohort->id;
}
foreach ($students as $userid) {
    if (!$DB->record_exists('cohort_members', ['cohortid' => $cohortid, 'userid' => $userid])) {
        cohort_add_member($cohortid, $userid);
    }
}

echo "Seeded Moodle training data.\n";
echo "Admin: admin / (see .env MOODLE_ADMIN_PASSWORD)\n";
echo "Staff: instructor01, mentor01, ta01 / {$password}\n";
echo "Students: student01 .. student08 / {$password}\n";
