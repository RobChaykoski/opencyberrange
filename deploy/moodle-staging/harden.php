<?php
// Harden the staging Moodle for an internet-facing demo.
//
// Run inside the staging Moodle container after the first boot:
//   docker compose exec -T moodle php /harden.php
//
// This is intentionally opinionated for a staging/demo site with local accounts
// and fake course data. It is not a production Moodle hardening baseline.

define('CLI_SCRIPT', true);
chdir('/bitnami/moodle');
require('/bitnami/moodle/config.php');

global $DB;

$siteUrl = getenv('MOODLE_SITE_URL') ?: '';
if (str_contains($siteUrl, 'ctfd.swocts.com')) {
    fwrite(STDERR, "REFUSING: this is the production OpenCyberRange host, not staging\n");
    exit(2);
}

$settings = [
    // Make the staging instance unmistakable in the page title.
    'fullname' => 'SWOCTS Moodle Staging',
    'shortname' => 'SWOCTS Staging',

    // No public registration or guest browsing.
    'registerauth' => '',
    'guestloginbutton' => 0,
    'forcelogin' => 1,
    'forceloginforprofiles' => 1,
    'opentogoogle' => 0,
    'allowaccountssameemail' => 0,

    // Local accounts only for the staging demo.
    'auth' => 'manual',

    // Strong password policy.
    'passwordpolicy' => 1,
    'minpasswordlength' => 12,
    'minpassworddigits' => 1,
    'minpasswordlower' => 1,
    'minpasswordupper' => 1,
    'minpasswordnonalphanum' => 1,
    'maxconsecutiveidentchars' => 3,

    // HTTPS session cookies; Caddy terminates TLS in front of Moodle.
    'cookiesecure' => 1,
    'cookiehttponly' => 1,

    // Quiet, production-like runtime.
    'debug' => 0,
    'debugdisplay' => 0,
    'themedesignermode' => 0,
    'cachejs' => 1,

    // Keep profiles and identity data minimal.
    'profilesforenrolledusersonly' => 1,
    'hiddenuserfields' => 'email,country,city,timezone,description,webpage,address,phone1,phone2,institution,department,idnumber',

    // The demo uses course completion and the LTI gradebook.
    'enablecompletion' => 1,
];

foreach ($settings as $name => $value) {
    set_config($name, $value);
}

// The front-page course carries the visible site name in Moodle.
$site = $DB->get_record('course', ['id' => SITEID], '*', MUST_EXIST);
$site->fullname = 'SWOCTS Moodle Staging';
$site->shortname = 'SWOCTS Staging';
$site->summary = 'Staging Moodle for OpenCyberRange LTI validation. Synthetic data only.';
$DB->update_record('course', $site);
rebuild_course_cache(SITEID, true);

purge_caches();
echo "Staging Moodle hardened: registration off, guest off, strong passwords, secure cookies, debug off.\n";
