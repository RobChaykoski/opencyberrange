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
require_once($CFG->dirroot . '/course/modlib.php');

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
        if (getenv('TRAINING_RESET_PASSWORDS') === '1') {
            $existing->password = hash_internal_user_password($password);
            $DB->update_record('user', $existing);
        }
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

function training_ensure_page(int $courseid, string $name, string $content): void {
    global $DB;
    if ($DB->record_exists('page', ['course' => $courseid, 'name' => $name])) {
        return;
    }
    $course = $DB->get_record('course', ['id' => $courseid], '*', MUST_EXIST);
    $module = $DB->get_record('modules', ['name' => 'page'], '*', MUST_EXIST);
    add_moduleinfo((object)[
        'modulename' => 'page',
        'module' => (int)$module->id,
        'course' => $courseid,
        'section' => 1,
        'visible' => 1,
        'name' => $name,
        'intro' => '',
        'introformat' => FORMAT_HTML,
        'content' => $content,
        'contentformat' => FORMAT_HTML,
        'revision' => 1,
        'display' => 0,
        'printheading' => 1,
        'printintro' => 0,
    ], $course);
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

$singleBrief = <<<'HTML'
<h3>Scenario</h3>
<p>You are the only analyst on shift. A fake workstation has raised a suspicious
login alert, and a fake web service shows unexpected scanning traffic.</p>
<h3>Deliverables</h3>
<ul>
  <li>A short timeline of what happened, in order.</li>
  <li>The evidence you used, with the system and time for each item.</li>
  <li>One containment action and one hardening action.</li>
  <li>A five-minute verbal defence of your conclusion.</li>
</ul>
<h3>Rules</h3>
<p>Use only the training stack. Do not connect to production systems, real
identity providers, or real data. Every account, host, and alert is synthetic.</p>
HTML;

$cohortBrief = <<<'HTML'
<h3>Scenario</h3>
<p>A fake multi-service environment is under a simulated intrusion. Two teams
must produce one joint defence brief.</p>
<h3>Team split</h3>
<ul>
  <li><strong>Cohort A:</strong> detection, endpoint, and network evidence.</li>
  <li><strong>Cohort B:</strong> identity, asset ownership, and access review.</li>
</ul>
<h3>Joint deliverables</h3>
<ul>
  <li>One shared timeline with owners for each step.</li>
  <li>One asset and identity map from the training inventory.</li>
  <li>Three findings, each with evidence and a control reference.</li>
  <li>One joint 10-minute defence.</li>
</ul>
<h3>Rules</h3>
<p>Work in your Moodle group. Use only the training stack and fake data. Do not
connect the lab to production services or real identity providers.</p>
HTML;

$foundGuide = <<<'HTML'
<h3>Training services</h3>
<ul>
  <li><strong>Moodle:</strong> courses, groups, and submissions.</li>
  <li><strong>Authentik:</strong> groups, MFA, and application access.</li>
  <li><strong>NetBox:</strong> sites, devices, prefixes, and ownership.</li>
  <li><strong>Ralph:</strong> asset lifecycle records.</li>
  <li><strong>Fleet:</strong> endpoint posture and compliance.</li>
</ul>
<h3>Accounts</h3>
<p>Staff and learner accounts are synthetic. Use the lab password from the
training environment instructions. Never reuse a lab credential anywhere real.</p>
<h3>Safety</h3>
<p>This environment contains fake data only. Do not connect it to production
systems, real patient or learner records, or a real identity provider.</p>
HTML;

$singleScenario = <<<'HTML'
<h3>Synthetic alert</h3>
<p>At 02:14, the fake identity service records six failed sign-ins for
<code>student03</code>, followed by a success from <code>10.20.4.17</code>.</p>
<h3>Fake context</h3>
<ul>
  <li>Asset: <code>hv-01</code> in NetBox, Training Data Centre.</li>
  <li>Group: <code>ocr-learners</code> in Authentik.</li>
  <li>Service: the fake web app at <code>192.0.2.50</code>.</li>
</ul>
<h3>Your task</h3>
<ul>
  <li>Build a timeline from the failed sign-ins to the successful one.</li>
  <li>Name the asset owner and the group that grants access.</li>
  <li>Choose one containment action and one hardening action.</li>
  <li>Explain what you can prove and what you cannot.</li>
</ul>
<p>All indicators are synthetic. Do not scan or connect to real hosts.</p>
HTML;

$cohortScenario = <<<'HTML'
<h3>Synthetic alert</h3>
<p>At 02:14, the fake identity service records six failed sign-ins for
<code>student03</code>, followed by a success from <code>10.20.4.17</code>. At
02:31, NetBox shows <code>hv-01</code> moved from the lab rack to the core rack,
and Authentik shows a new member added to <code>ocr-learners</code>.</p>
<h3>Fake context</h3>
<ul>
  <li>Assets: <code>hv-01</code>, <code>core-sw-01</code>, <code>edge-rtr-01</code>.</li>
  <li>Identity: <code>ocr-learners</code>, <code>ocr-instructors</code>.</li>
  <li>Network: <code>10.10.0.0/16</code> core and <code>10.20.0.0/16</code> lab.</li>
</ul>
<h3>Team task</h3>
<ul>
  <li><strong>Cohort A:</strong> authentication timeline and endpoint evidence.</li>
  <li><strong>Cohort B:</strong> asset movement, ownership, and group change.</li>
  <li>Join both into one timeline with owners and timestamps.</li>
  <li>Record three findings with evidence and one control reference each.</li>
</ul>
<p>All indicators are synthetic. Do not scan or connect to real hosts.</p>
HTML;

training_ensure_page($courseids['OCR-CAP-SINGLE'], 'Capstone brief', $singleBrief);
training_ensure_page($courseids['OCR-CAP-COHORT'], 'Cohort capstone brief', $cohortBrief);
training_ensure_page($courseids['OCR-FOUND'], 'Training lab guide', $foundGuide);
training_ensure_page($courseids['OCR-CAP-SINGLE'], 'Scenario pack: suspicious login', $singleScenario);
training_ensure_page($courseids['OCR-CAP-COHORT'], 'Scenario pack: suspicious login and asset drift', $cohortScenario);

$admins = get_admins();
$adminUsername = $admins ? reset($admins)->username : 'admin';
echo "Seeded Moodle training data.\n";
echo "Admin: {$adminUsername} / (see .env MOODLE_ADMIN_PASSWORD)\n";
echo "Staff: instructor01, mentor01, ta01 / (see TRAINING_PASSWORD)\n";
echo "Students: student01 .. student08 / (see TRAINING_PASSWORD)\n";
