#!/usr/bin/env bash
set -o errexit

echo "========================================="
echo "  DeepFake Shield - Build Starting"
echo "========================================="

pip install --upgrade pip

# Install requirements
pip install -r requirements-minimal.txt 2>&1 | tail -5

# Try PyTorch (optional)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || echo "PyTorch skipped (optional)"

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py makemigrations core --no-input 2>/dev/null || true
python manage.py migrate --no-input

mkdir -p media/uploads media/processed media/reports

if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --no-input 2>/dev/null || echo "Superuser exists"
fi

echo "========================================="
echo "  DeepFake Shield - Build Complete!"
echo "========================================="