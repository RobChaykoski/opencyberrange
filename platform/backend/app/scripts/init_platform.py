#!/usr/bin/env python3
"""
SWOCTS Cyber Range — First-Run Platform Initialization
Runs all seed scripts in the correct order for a clean deployment.

Usage (inside Docker):
  docker compose exec backend python /app/app/scripts/init_platform.py

This script is idempotent — safe to run multiple times.
It will:
  1. Seed curriculum tracks and levels
  2. Discover and import all exercises from /labs
  3. Create the example Penetration Testing course shell
  4. Seed the default learning-path achievements

It does NOT create any user accounts. The first admin is created
via the web-based /setup flow on first visit.
"""

import sys
sys.path.insert(0, '/app')

print("=" * 60)
print("  SWOCTS Cyber Range — Platform Initialization")
print("=" * 60)

print("\n[1/4] Seeding curriculum (tracks & levels)...")
from app.scripts.seed_curriculum import seed_curriculum
seed_curriculum()

print("\n[2/4] Discovering exercises from /labs...")
from app.scripts.discover_labs import discover_labs, sync_course_week_assignments
discover_labs()
sync_course_week_assignments()

print("\n[3/4] Creating example course...")
from app.scripts.seed_example_course import seed_example_course
seed_example_course()

print("\n[4/4] Seeding default learning achievements...")
from app.scripts.seed_achievements import seed_achievements
seed_achievements()

print("\n" + "=" * 60)
print("  Initialization complete!")
print("  Visit the platform in your browser to create your admin account.")
print("=" * 60)
