#!/usr/bin/env bash
# Build script for deployment (Render, Railway, etc.)
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# Load demo data on first deploy (safely skips if data already exists).
python manage.py seed_demo
python manage.py seed_college_students
# Create an admin login on first deploy (idempotent — skips if it already exists).
# Override the defaults by setting DJANGO_SUPERUSER_* env vars in the Render dashboard.
python manage.py shell -c "import os; from django.contrib.auth import get_user_model; U = get_user_model(); u = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'); e = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'); p = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin@12345'); U.objects.filter(username=u).exists() or U.objects.create_superuser(u, e, p)"
