#!/usr/bin/env bash
set -o errexit

echo "========================================="
echo "  DeepFake Shield - Build Starting"
echo "========================================="

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f requirements-minimal.txt ]; then
    echo "Installing requirements..."
    pip install -r requirements-minimal.txt
fi

# Try PyTorch (optional, skip if fails)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || echo "PyTorch skipped"

# CRITICAL: Create migrations first
echo "Creating migrations..."
python manage.py makemigrations core --no-input || echo "No new migrations needed"

# CRITICAL: Apply ALL migrations
echo "Applying migrations..."
python manage.py migrate --no-input

# Verify tables exist
echo "Verifying database tables..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deepfakeshield.settings')
django.setup()
from django.db import connection
tables = connection.introspection.table_names()
print('Tables found:', len(tables))
for t in tables:
    if 'core_' in t:
        print('  ✓', t)
if 'core_scanresult' not in tables:
    print('ERROR: core_scanresult table missing!')
else:
    print('All core tables OK')
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Create directories
mkdir -p media/uploads media/processed media/reports

# Create superuser
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --no-input 2>/dev/null || echo "Superuser already exists"
fi

echo "========================================="
echo "  DeepFake Shield - Build Complete!"
echo "========================================="