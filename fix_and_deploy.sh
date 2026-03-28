#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DeepFake Shield — COMPLETE FIX SCRIPT FOR UBUNTU 24.04
# Run this after SSH into VM
# Fixes Python version issue and deploys Django app
# ═══════════════════════════════════════════════════════════════

set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   DeepFake Shield — Ubuntu 24.04 Fix & Deploy       ║"
echo "╚══════════════════════════════════════════════════════╝"

DB_NAME="deepfakeshield"
DB_USER="deepfakeadmin"
DB_PASS="Signature@44"
DOMAIN="deepfakeshield.tech"
GITHUB_REPO="https://github.com/deepfakeshieldadmin/deepfakeshield.git"
APP_DIR="/home/deepfakeuser/deepfakeshield"
VENV_DIR="/home/deepfakeuser/venv"

# ──────────────────────────────────────────────
# STEP 1: Install Python 3.11 on Ubuntu 24.04
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 1: Installing Python 3.11 (Ubuntu 24.04 method)..."

sudo apt update -y

# Add deadsnakes PPA — this has Python 3.11 for Ubuntu 24.04
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update -y

# Now install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Verify
python3.11 --version
echo "✅ Python 3.11 installed"

# ──────────────────────────────────────────────
# STEP 2: Install system dependencies
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 2: Installing system packages..."
sudo apt install -y \
    postgresql postgresql-contrib \
    nginx git curl wget unzip \
    libpq-dev build-essential \
    libopencv-dev \
    ffmpeg \
    pkg-config
echo "✅ System packages installed"

# ──────────────────────────────────────────────
# STEP 3: Setup PostgreSQL
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 3: Setting up PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

sudo -u postgres psql << EOF
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';
   END IF;
END
\$\$;
DROP DATABASE IF EXISTS ${DB_NAME};
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
EOF
echo "✅ PostgreSQL ready"

# ──────────────────────────────────────────────
# STEP 4: Clone / Update project
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 4: Getting project from GitHub..."
cd /home/deepfakeuser

if [ -d "$APP_DIR" ]; then
    echo "Updating existing project..."
    cd $APP_DIR
    git fetch --all
    git reset --hard origin/main
    git pull origin main
else
    git clone $GITHUB_REPO $APP_DIR
fi
echo "✅ Project ready at $APP_DIR"

# ──────────────────────────────────────────────
# STEP 5: Create virtual environment
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 5: Creating Python 3.11 virtual environment..."

# Remove old venv if exists
rm -rf $VENV_DIR

# Create fresh venv with Python 3.11
python3.11 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Upgrade pip inside venv
pip install --upgrade pip setuptools wheel
echo "✅ Virtual environment ready"

# ──────────────────────────────────────────────
# STEP 6: Install Python packages
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 6: Installing Python packages (this takes 3-5 minutes)..."
cd $APP_DIR
source $VENV_DIR/bin/activate

pip install -r requirements.txt

# Try optional packages
echo "Installing optional AI packages..."
pip install torch==2.2.2+cpu torchvision==0.17.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu \
    --no-deps 2>/dev/null && echo "✅ PyTorch installed" || echo "PyTorch skipped"

pip install facenet-pytorch==2.5.3 2>/dev/null && \
    echo "✅ facenet-pytorch installed" || echo "facenet-pytorch skipped"

echo "✅ Python packages installed"

# ──────────────────────────────────────────────
# STEP 7: Create .env file
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 7: Creating environment file..."
SECRET_KEY=$(python3.11 -c "import secrets; print(secrets.token_urlsafe(50))")

cat > $APP_DIR/.env << ENVEOF
DJANGO_SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,${DOMAIN},www.${DOMAIN},20.244.24.145
CSRF_TRUSTED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN},http://20.244.24.145
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}
DB_SSL_REQUIRE=False
EMAIL_HOST_USER=deepfakeshield.admin@gmail.com
EMAIL_HOST_PASSWORD=blolqgkyoydxkbbp
DEFAULT_FROM_EMAIL=DeepFake Shield <deepfakeshield.admin@gmail.com>
SITE_URL=https://${DOMAIN}
DJANGO_SUPERUSER_USERNAME=Admin
DJANGO_SUPERUSER_EMAIL=<deepfakeshield.admin@gmail.com>
DJANGO_SUPERUSER_PASSWORD=Admin@Shield2024
LOG_LEVEL=INFO
ENVEOF

echo "✅ .env file created"

# ──────────────────────────────────────────────
# STEP 8: Django setup
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 8: Running Django migrations..."
cd $APP_DIR
source $VENV_DIR/bin/activate

python manage.py makemigrations --no-input 2>/dev/null || true
python manage.py makemigrations core --no-input 2>/dev/null || true
python manage.py migrate --no-input
python manage.py collectstatic --no-input --clear
mkdir -p media/uploads media/processed media/reports

# Create superuser
DJANGO_SUPERUSER_USERNAME=Admin \
DJANGO_SUPERUSER_EMAIL=deepfakeshield.admin@gmail.com \
DJANGO_SUPERUSER_PASSWORD=Signature@44 \
python manage.py createsuperuser --no-input 2>/dev/null || echo "Superuser exists"

echo "✅ Django ready"

# ──────────────────────────────────────────────
# STEP 9: Create Gunicorn systemd service
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 9: Setting up Gunicorn service..."

sudo tee /etc/systemd/system/deepfakeshield.service > /dev/null << SVCEOF
[Unit]
Description=DeepFake Shield Gunicorn
After=network.target postgresql.service

[Service]
User=deepfakeuser
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/gunicorn deepfakeshield.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile /var/log/deepfakeshield_access.log \
    --error-logfile /var/log/deepfakeshield_error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

sudo systemctl daemon-reload
sudo systemctl enable deepfakeshield
sudo systemctl start deepfakeshield
sleep 3
sudo systemctl status deepfakeshield --no-pager
echo "✅ Gunicorn service running"

# ──────────────────────────────────────────────
# STEP 10: Configure Nginx
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 10: Configuring Nginx..."

sudo tee /etc/nginx/sites-available/deepfakeshield > /dev/null << NGINXEOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN} 20.244.24.145;
    client_max_body_size 100M;

    location /static/ {
        alias ${APP_DIR}/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias ${APP_DIR}/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/deepfakeshield /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
echo "✅ Nginx configured"

# ──────────────────────────────────────────────
# STEP 11: Permissions
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 11: Setting permissions..."
sudo chown -R deepfakeuser:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod -R 775 $APP_DIR/media
sudo touch /var/log/deepfakeshield_access.log /var/log/deepfakeshield_error.log
sudo chown deepfakeuser:www-data /var/log/deepfakeshield_access.log
sudo chown deepfakeuser:www-data /var/log/deepfakeshield_error.log
echo "✅ Permissions set"

# ──────────────────────────────────────────────
# STEP 12: Reinstall SSL (since Nginx was reconfigured)
# ──────────────────────────────────────────────
echo ""
echo ">>> STEP 12: Reinstalling SSL certificate..."
sudo apt install -y certbot python3-certbot-nginx 2>/dev/null || true
sudo certbot --nginx \
    -d ${DOMAIN} \
    -d www.${DOMAIN} \
    --non-interactive \
    --agree-tos \
    --email 24ce37@sdpc.ac.in \
    --redirect 2>/dev/null && echo "✅ SSL ready" || echo "SSL will work after DNS fully propagates"

sudo systemctl restart nginx

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   ✅✅ DEPLOYMENT COMPLETE!                         ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║                                                      ║"
echo "║   🌐🌐 https://deepfakeshield.tech                  ║"
echo "║   🔧🔧 https://deepfakeshield.tech/admin/           ║"
echo "║   👤👤 Username: Admin                              ║"
echo "║   🔑🔑 Password: Signature@44                       ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "Check status: sudo systemctl status deepfakeshield"
echo "View logs:    sudo journalctl -u deepfakeshield -f"
echo "Error logs:   tail -f /var/log/deepfakeshield_error.log"