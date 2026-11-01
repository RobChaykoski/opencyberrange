-- FinanceCorp portal backup
-- Generated 2025-01-02 for training use only.

CREATE TABLE users (
  id INT PRIMARY KEY,
  username VARCHAR(64),
  email VARCHAR(128)
);

INSERT INTO users (id, username, email) VALUES
  (1, 'webadmin', 'webadmin@financecorp.local'),
  (2, 'j.mitchell', 'j.mitchell@financecorp.local');

CREATE TABLE portal_settings (
  setting_key VARCHAR(64) PRIMARY KEY,
  setting_value VARCHAR(255)
);

INSERT INTO portal_settings (setting_key, setting_value) VALUES
  ('debug', 'true'),
  ('support_email', 'support@financecorp.local');
