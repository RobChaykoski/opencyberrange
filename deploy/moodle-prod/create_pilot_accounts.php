<?php
// Create the production pilot accounts and enrol them in the pilot course.
//
//   docker compose exec -T -u daemon moodle php /create_pilot_accounts.php
//
// This creates a root-only CSV in /tmp with the generated passwords. Copy it
// out of the container immediately and remove the in-container copy.

define('CLI_SCRIPT', true);
chdir('/bitnami/moodle');
require('/bitnami/moodle/config.php');
require_once($CFG->dirroot . '/user/lib.php');
require_once($CFG->dirroot . '/enrol/locallib.php');
require_once($CFG->dirroot . '/course/lib.php');

global $DB;

$shortname = getenv('PILOT_COURSE_SHORTNAME') ?: 'PILOT-101';
$resetPasswords = getenv('PILOT_RESET_PASSWORDS') === '1';
$course = $DB->get_record('course', ['shortname' => $shortname], '*', MUST_EXIST);

$roleIds = [];
foreach (['editingteacher', 'teacher', 'student'] as $shortrole) {
    $roleIds[$shortrole] = (int)$DB->get_field(
        'role',
        'id',
        ['shortname' => $shortrole],
        MUST_EXIST
    );
}

$accounts = [
    ['pilot.instructor', 'Pilot', 'Instructor', 'Instructor', 'editingteacher'],
    ['pilot.mentor', 'Pilot', 'Mentor', 'Mentor', 'teacher'],
    ['pilot.ta', 'Pilot', 'Teaching Assistant', 'Teaching Assistant', 'teacher'],
];

for ($i = 1; $i <= 8; $i++) {
    $number = str_pad((string)$i, 2, '0', STR_PAD_LEFT);
    $accounts[] = [
        "pilot.student{$number}",
        'Pilot',
        "Student {$number}",
        'Learner',
        'student',
    ];
}

function pilot_password(): string {
    $chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
    $special = '!@#$%^&*';
    $password = 'Aa1' . $special[random_int(0, strlen($special) - 1)];
    for ($i = 0; $i < 12; $i++) {
        $password .= $chars[random_int(0, strlen($chars) - 1)];
    }
    return $password;
}

// Ensure a manual enrolment instance exists.
$plugin = enrol_get_plugin('manual');
$instance = $DB->get_record('enrol', [
    'courseid' => $course->id,
    'enrol' => 'manual',
]);
if (!$instance) {
    $instanceId = $plugin->add_instance($course);
    $instance = $DB->get_record('enrol', ['id' => $instanceId], '*', MUST_EXIST);
}
$context = context_course::instance($course->id);

$csvPath = '/tmp/pilot-accounts.csv';
$csv = fopen($csvPath, 'w');
if ($csv === false) {
    fwrite(STDERR, "Could not open {$csvPath}\n");
    exit(2);
}
fputcsv($csv, ['username', 'role', 'email', 'password']);

foreach ($accounts as [$username, $firstname, $lastname, $department, $shortrole]) {
    $email = "{$username}@example.invalid";
    $user = $DB->get_record('user', ['username' => $username, 'deleted' => 0]);
    $password = '';
    if ($user) {
        if ($resetPasswords) {
            $password = pilot_password();
            $user->password = hash_internal_user_password($password);
            $DB->update_record('user', $user);
        }
        echo "existing {$username} ({$shortrole})\n";
    } else {
        $password = pilot_password();
        $user = (object)[
            'auth' => 'manual',
            'confirmed' => 1,
            'policyagreed' => 1,
            'mnethostid' => $CFG->mnet_localhost_id,
            'username' => $username,
            'password' => $password,
            'firstname' => $firstname,
            'lastname' => $lastname,
            'email' => $email,
            'emailstop' => 0,
            'city' => 'Pilot',
            'country' => 'CA',
            'institution' => 'SWOCTS Pilot',
            'department' => $department,
            'description' => 'Synthetic pilot account. Replace or remove before general production use.',
            'lang' => 'en',
            'timezone' => 'America/Toronto',
            'mailformat' => 1,
            'maildigest' => 0,
            'autosubscribe' => 1,
        ];
        $userId = user_create_user($user, true, false);
        $user = $DB->get_record('user', ['id' => $userId], '*', MUST_EXIST);
        echo "created {$username} ({$shortrole})\n";
    }

    $roleId = $roleIds[$shortrole];
    $enrolled = $DB->record_exists('user_enrolments', [
        'enrolid' => $instance->id,
        'userid' => $user->id,
    ]);
    if (!$enrolled) {
        $plugin->enrol_user($instance, $user->id, $roleId);
    } else {
        role_assign($roleId, $user->id, $context->id);
    }

    if ($password !== '') {
        fputcsv($csv, [$username, $shortrole, $email, $password]);
    }
}
fclose($csv);
chmod($csvPath, 0600);

echo "Pilot accounts ready. Password CSV: {$csvPath}\n";
