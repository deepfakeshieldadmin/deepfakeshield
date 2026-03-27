#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DeepFake Shield — Auto Deploy Script
# Run this whenever you push new code and want to update live site
# Usage: ./deploy.sh
# ═══════════════════════════════════════════════════════════════

APP_DIR="/home/deepfakeuser/deepfakeshield"
VENV_DIR="/home/deepfakeuser/venv"

echo ">>> Pulling latest code from GitHub..."
cd $APP_DIR
git pull origin main

echo ">>> Installing any new requirements..."
source $VENV_DIR/bin/activate
pip install -r requirements.txt --quiet

echo ">>> Running migrations..."
python manage.py migrate --no-input

echo ">>> Collecting static files..."
python manage.py collectstatic --no-input

echo ">>> Restarting service..."
sudo systemctl restart deepfakeshield
sudo systemctl restart nginx

echo ""
echo "✅ Deployment complete!"
echo "   Site: https://deepfakeshield.tech"
sudo systemctl status deepfakeshield --no-pager