#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════
# DeepFake Shield — build.sh
# Works on: Azure App Service, Render, Oracle VM
# ═══════════════════════════════════════════════════════
set -o errexit

echo "========================================="
echo "  DeepFake Shield - Build Starting"
echo "========================================="

# ── Step 1: Upgrade pip ──
pip install --upgrade pip

# ── Step 2: Install core requirements ──
echo "Installing requirements..."
pip install -r requirements-minimal.txt

# ── Step 3: Try PyTorch CPU (optional, skip if fails or too large) ──
echo "Attempting PyTorch CPU install (optional)..."
pip install torch==2.2.2+cpu torchvision==0.17.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu \
    --no-deps 2>/dev/null || echo "PyTorch skipped (system will use OpenCV fallback)"

# ── Step 4: Try facenet-pytorch (optional) ──
pip install facenet-pytorch==2.5.3 2>/dev/null || echo "facenet-pytorch skipped (OpenCV Haar cascade will be used)"

# ── Step 5: Create Django migrations ──
echo "Creating migrations..."
python manage.py makemigrations --no-input 2>/dev/null || echo "No new migrations"
python manage.py makemigrations core --no-input 2>/dev/null || echo "Core migrations up to date"

# ── Step 6: Apply migrations ──
echo "Applying migrations..."
python manage.py migrate --no-input

# ── Step 7: Verify core database tables ──
echo "Verifying database tables..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deepfakeshield.settings')
django.setup()
from django.db import connection
tables = connection.introspection.table_names()
core_tables = [t for t in tables if 'core_' in t]
print(f'Total tables: {len(tables)}')
print(f'Core tables: {core_tables}')
missing = []
for t in ['core_scanresult', 'core_userprofile', 'core_emailverificationtoken']:
    if t not in tables:
        missing.append(t)
        print(f'  WARNING: {t} missing!')
    else:
        print(f'  OK: {t}')
if missing:
    print('ERROR: Some tables missing. Run makemigrations again.')
else:
    print('All core tables OK!')
"

# ── Step 8: Collect static files ──
echo "Collecting static files..."
python manage.py collectstatic --no-input

# ── Step 9: Create media directories ──
echo "Creating media directories..."
mkdir -p media/uploads media/processed media/reports staticfiles

# ── Step 10: Create superuser (if env vars set) ──
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --no-input 2>/dev/null || echo "Superuser already exists"
fi

echo "========================================="
echo "  DeepFake Shield - Build Complete!"
echo "========================================="