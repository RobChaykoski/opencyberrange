<?php
// Apply the production OpenCyberRange SMTP settings to the pilot Moodle.
//
// This expects /tmp/mail.tsv, produced from the OpenCyberRange platform_settings
// table outside the container. Do not leave that file behind.

define('CLI_SCRIPT', true);
chdir('/bitnami/moodle');
require('/bitnami/moodle/config.php');

$path = '/tmp/mail.tsv';
if (!is_readable($path)) {
    fwrite(STDERR, "missing {$path}\n");
    exit(2);
}

$mail = [];
foreach (file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
    $parts = explode("\t", $line, 2);
    if (count($parts) === 2) {
        $mail[trim($parts[0])] = $parts[1];
    }
}

$host = trim($mail['mail_host'] ?? '');
$port = trim($mail['mail_port'] ?? '');
if ($host === '') {
    fwrite(STDERR, "mail_host is missing\n");
    exit(2);
}
if (str_contains($host, ':')) {
    [$host, $inlinePort] = explode(':', $host, 2);
    if ($port === '') {
        $port = $inlinePort;
    }
}

$security = strtolower(trim($mail['mail_security'] ?? ''));
$secure = '';
if ($security === 'ssl') {
    $secure = 'ssl';
} elseif (in_array($security, ['tls', 'starttls', 'start_tls'], true)) {
    $secure = 'tls';
}

$username = trim($mail['mail_username'] ?? '');
$password = $mail['mail_password'] ?? '';
$from = trim($mail['mail_from_email'] ?? '');
$fromName = trim($mail['mail_from_name'] ?? 'SWOCTS Moodle Pilot');

// Moodle's PHPMailer path takes the port from smtphosts, not from smtpport.
$smtpHosts = $host;
if ($port !== '' && !str_contains($host, ':')) {
    $smtpHosts .= ':' . $port;
}
set_config('smtphosts', $smtpHosts);
set_config('smtpport', $port);
set_config('smtpuser', $username);
$passwordSource = 'database';
if (is_readable('/run/secrets/moodle_smtp_pass')) {
    // config.php overrides this from the mounted secret at runtime.
    set_config('smtppass', '');
    $passwordSource = 'secret-file';
} else {
    set_config('smtppass', $password);
}
set_config('smtpsecure', $secure);
set_config('smtpauthtype', $username !== '' ? 'LOGIN' : '');
set_config('noreplyaddress', $from);
set_config('noreplyname', $fromName);
set_config('supportemail', $from);

$result = 'not attempted';
try {
    $admin = get_admin();
    $support = core_user::get_support_user();
    $sent = email_to_user(
        $admin,
        $support,
        'SWOCTS Moodle pilot SMTP test',
        'SMTP is configured for the production pilot Moodle.'
    );
    $result = $sent ? 'sent' : 'failed';
} catch (Throwable $error) {
    $result = 'failed: ' . $error->getMessage();
}

echo "smtp_configured host={$host} port={$port} secure={$secure} password_source={$passwordSource} test={$result}\n";
