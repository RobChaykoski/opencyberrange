# Privacy and Your Data

You can download a copy of your account data or delete your account from
**Profile → Privacy and data**.

## Download your data

1. Open your profile.
2. Scroll to **Privacy and data**.
3. Click **Download my data**.

The download is a JSON file containing your profile, VPN metadata, course
enrolments, completions, flag attempts, quiz attempts, achievements, lab
sessions, competition entries, and activity history. Password hashes, MFA
secrets, recovery codes, and your WireGuard private key are not included.

## Delete your account

Deletion is immediate and cannot be undone.

1. Open **Profile → Privacy and data**.
2. Click **Delete my account**.
3. Enter your current password.
4. If MFA is enabled, enter an authenticator or recovery code.
5. Type `DELETE` and click **Delete permanently**.

You are signed out when the deletion completes.

**What is removed:** your profile, email, avatar, password, MFA settings, VPN
configuration, course enrolments, progress, flags, quiz attempts, badges, lab
sessions, WebSocket tickets, and activity identifiers.

**What is kept:**

- Security and audit records are anonymised and kept for a limited period.
- Authored course material is kept with the author link removed.
- A backup taken before the deletion may contain your account until the backup
  retention period ends (30 days by default). Restores re-apply the deletion
  suppression ledger.

## If deletion is blocked

- **You own courses.** A platform administrator must transfer each course to
  another instructor first. Deleting you would also delete every enrolled
  student's course records.
- **You are the last administrator.** Promote or create another administrator
  first.

Contact your platform administrator if either applies. An instructor can
transfer your courses from **Admin → Courses → Manage**.

## Related pages

- [Changing Your Password](17_Changing_Your_Password.md)
- [Viewing Your Profile](16_Viewing_Your_Profile.md)
- [Achievements and Badges](15_Achievements_and_Badges.md)
