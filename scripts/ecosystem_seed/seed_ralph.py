"""Seed a synthetic Ralph administrator for the training lab.

Run inside the Ralph container:

    docker exec -i -w /opt/ralph/ralph-core -e RALPH_ADMIN_PASSWORD=... \
      ecosystem-test-ralph-1 /opt/ralph/ralph-core/bin/python /seed/seed_ralph.py

Everything here is fake training data. It is idempotent.
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ralph.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()

username = os.environ.get("RALPH_ADMIN_USER", "admin")
email = os.environ.get("RALPH_ADMIN_EMAIL", "admin@example.invalid")
# security-delta: allow credential-like assignment (synthetic lab password)
password = os.environ.get("RALPH_ADMIN_PASSWORD", "TrainLab!2026#Student")

user = User.objects.filter(username=username).first()
if user is None:
    user = User.objects.create_superuser(
        username=username, email=email, password=password
    )
    print(f"Created Ralph admin {username}.")
else:
    changed = False
    for field in ("is_staff", "is_superuser", "is_active"):
        if not getattr(user, field, False):
            setattr(user, field, True)
            changed = True
    if changed:
        user.save()
    print(f"Ralph admin {username} already exists.")

print("Ralph is ready for fake assets.")
