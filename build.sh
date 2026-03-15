#!/usr/bin/env bash
set -o errexit

echo "========================================="
echo "  DeepFake Shield — Build Script"
echo "========================================="

echo ">> Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo ">> Installing dependencies..."
pip install -r requirements.txt

echo ">> Collecting static files..."
python manage.py collectstatic --no-input

echo ">> Running database migrations..."
python manage.py migrate

echo ">> Creating superuser..."
python manage.py shell << 'PYTHON_SCRIPT'
import os
from django.contrib.auth.models import User

su_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'Admin')
su_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'deepfakeshield.admin@gmail.com')
su_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Pavilion@44')

if not User.objects.filter(username=su_username).exists():
    User.objects.create_superuser(
        username=su_username,
        email=su_email,
        password=su_password
    )
    print(f'[SUCCESS] Superuser "{su_username}" created!')
else:
    # Update password in case it changed
    user = User.objects.get(username=su_username)
    user.set_password(su_password)
    user.email = su_email
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'[INFO] Superuser "{su_username}" already exists. Password updated.')

PYTHON_SCRIPT

echo ">> Build complete!"
echo "========================================="