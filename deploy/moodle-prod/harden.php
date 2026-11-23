<?php
// Production-pilot Moodle hardening.
//
// Run once after the first boot, as the web user:
//   docker compose exec -T -u daemon moodle php /harden.php
//
// This is a baseline for a controlled pilot, not a substitute for institutional
// SSO, MFA, privacy review, backups, monitoring, or change control.

define('CLI_SCRIPT', true);
chdir('/bitnami/moodle');
require('/bitnami/moodle/config.php');

global $DB;

$siteUrl = getenv('MOODLE_SITE_URL') ?: '';
$platformHost = getenv('OCR_PUBLIC_HOST') ?: 'platform.example.com';
if ($platformHost !== '' && str_contains($siteUrl, $platformHost)) {
    fwrite(STDERR, "REFUSING: this is the OpenCyberRange host, not the Moodle site URL\n");
    exit(2);
}

$settings = [
    // No public registration or guest browsing.
    'registerauth' => '',
    'guestloginbutton' => 0,
    'forcelogin' => 1,
    'forceloginforprofiles' => 1,
    'opentogoogle' => 0,
    'allowaccountssameemail' => 0,

    // Bootstrap with local accounts until institutional SSO is configured.
    'auth' => 'manual',

    // Strong password policy.
    'passwordpolicy' => 1,
    'minpasswordlength' => 12,
    'minpassworddigits' => 1,
    'minpasswordlower' => 1,
    'minpasswordupper' => 1,
    'minpasswordnonalphanum' => 1,
    'maxconsecutiveidentchars' => 3,

    // HTTPS session cookies; NPM terminates TLS.
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

    // The pilot uses course completion and the LTI gradebook.
    'enablecompletion' => 1,
];

foreach ($settings as $name => $value) {
    set_config($name, $value);
}

$site = $DB->get_record('course', ['id' => SITEID], '*', MUST_EXIST);
$site->fullname = 'SWOCTS Moodle Pilot';
$site->shortname = 'SWOCTS Pilot';
$site->summary = 'Authorised pilot area for the SWOCTS Moodle and OpenCyberRange LTI evaluation.';
$DB->update_record('course', $site);
rebuild_course_cache(SITEID, true);

purge_caches();
echo "Production pilot Moodle hardened: registration off, guest off, strong passwords, secure cookies, debug off.\n";
