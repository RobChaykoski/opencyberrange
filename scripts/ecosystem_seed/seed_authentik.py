# security-delta: allow exec (loads this local seed file inside the Authentik container)
"""Seed synthetic Authentik groups and users for the training lab.

Run inside the Authentik server container:

    # security-delta: allow exec
    ak shell -c "exec(open('/seed/seed_authentik.py').read())"

Everything here is fake training data. It is idempotent.
"""

from authentik.core.models import Group, User

# security-delta: allow credential-like assignment (synthetic lab password)
PASSWORD = "TrainLab!2026#Cohort"

GROUPS = {
    "ocr-learners": "OpenCyberRange learners (synthetic)",
    "ocr-mentors": "OpenCyberRange mentors (synthetic)",
    "ocr-teaching-assistants": "OpenCyberRange teaching assistants (synthetic)",
    "ocr-instructors": "OpenCyberRange instructors (synthetic)",
    "ocr-privacy-office": "Privacy office (synthetic)",
    "ocr-auditors": "Auditors (synthetic)",
}

USERS = [
    ("student01", "Student Number1", ["ocr-learners"]),
    ("student02", "Student Number2", ["ocr-learners"]),
    ("student03", "Student Number3", ["ocr-learners"]),
    ("student04", "Student Number4", ["ocr-learners"]),
    ("student05", "Student Number5", ["ocr-learners"]),
    ("student06", "Student Number6", ["ocr-learners"]),
    ("student07", "Student Number7", ["ocr-learners"]),
    ("student08", "Student Number8", ["ocr-learners"]),
    ("mentor01", "Alex Mentor", ["ocr-mentors"]),
    ("ta01", "Jamie Assistant", ["ocr-teaching-assistants"]),
    ("instructor01", "Morgan Instructor", ["ocr-instructors"]),
    ("privacy01", "Pat Privacy", ["ocr-privacy-office"]),
    ("auditor01", "Avery Auditor", ["ocr-auditors"]),
]

for group_name, description in GROUPS.items():
    group, _ = Group.objects.get_or_create(
        name=group_name, defaults={"is_superuser": False}
    )
    if not group.attributes.get("description"):
        group.attributes["description"] = description
        group.save()

for username, display_name, group_names in USERS:
    user = User.objects.filter(username=username).first()
    if user is None:
        user = User(
            username=username,
            email=f"{username}@example.invalid",
            name=display_name,
        )
        user.set_password(PASSWORD)
        user.save()
    for group_name in group_names:
        user.groups.add(Group.objects.get(name=group_name))

print("Seeded Authentik training groups and users.")
print("Groups:", ", ".join(sorted(GROUPS)))
print("Users: student01..student08, mentor01, ta01, instructor01, privacy01, auditor01")
