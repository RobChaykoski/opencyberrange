<?php
// Create the production pilot course shell. No fake users or fake enrolments.
//
//   docker compose exec -T -u daemon moodle php /create_pilot_course.php

define('CLI_SCRIPT', true);
chdir('/bitnami/moodle');
require('/bitnami/moodle/config.php');
require_once($CFG->dirroot . '/course/lib.php');

global $DB;

$shortname = getenv('PILOT_COURSE_SHORTNAME') ?: 'PILOT-101';
$fullname = getenv('PILOT_COURSE_FULLNAME') ?: 'SWOCTS Moodle Pilot Course';

$course = $DB->get_record('course', ['shortname' => $shortname]);
if ($course) {
    echo "Pilot course already exists: id={$course->id} shortname={$shortname}\n";
    exit(0);
}

$category = $DB->get_record('course_categories', ['name' => 'SWOCTS Pilot']);
if (!$category) {
    $created = core_course_category::create([
        'name' => 'SWOCTS Pilot',
        'parent' => 0,
        'visible' => 1,
        'description' => 'Production pilot courses for live feedback.',
    ]);
    $categoryid = (int)$created->id;
} else {
    $categoryid = (int)$category->id;
}

$course = create_course((object)[
    'fullname' => $fullname,
    'shortname' => $shortname,
    'category' => $categoryid,
    'summary' => 'Authorised production pilot course for the SWOCTS Moodle and OpenCyberRange LTI evaluation. Real participants only.',
    'summaryformat' => FORMAT_HTML,
    'format' => 'topics',
    'visible' => 1,
    'enablecompletion' => 1,
]);

echo "Created pilot course id={$course->id} shortname={$shortname}\n";
