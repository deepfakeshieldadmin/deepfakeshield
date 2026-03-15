#!/usr/bin/env bash
# DeepFake Shield - Build Script for Render Deployment

set -o errexit

echo "========================================="
echo "  DeepFake Shield - Build Starting"
echo "========================================="

# Upgrade pip
pip install --upgrade pip

# Install dependencies (use minimal if torch causes issues)
if [ -f requirements-minimal.txt ]; then
    echo "Installing minimal requirements..."
    pip install -r requirements-minimal.txt
else
    echo "Installing full requirements..."
    pip install -r requirements.txt
fi

# Try installing torch separately with CPU index (optional)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || echo "PyTorch not installed (optional - system works without it)"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "Running migrations..."
python manage.py migrate --no-input

# Create media directories
echo "Creating media directories..."
mkdir -p media/uploads media/processed media/reports

# Create superuser if environment variables are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --no-input 2>/dev/null || echo "Superuser already exists"
fi

echo "========================================="
echo "  DeepFake Shield - Build Complete!"
echo "========================================="