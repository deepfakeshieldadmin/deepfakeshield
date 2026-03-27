#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DeepFake Shield — COMPLETE AUTO SETUP SCRIPT FOR AZURE VM
# Run this ONCE after SSH into your VM
# It installs everything and starts the website automatically
# ═══════════════════════════════════════════════════════════════

set -e  # Stop on any error

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     DeepFake Shield — VM Auto Setup Starting...      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── CONFIGURATION — Edit these values before running ──
DB_NAME="deepfakeshield"
DB_USER="deepfakeadmin"
DB_PASS="Signature@44"
DOMAIN="deepfakeshield.tech"
GITHUB_REPO="https://github.com/deepfakeshieldadmin/deepfakeshield.git"
APP_DIR="/home/deepfakeuser/deepfakeshield"
VENV_DIR="/home/deepfakeuser/venv"
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

echo ">>> STEP 1: Updating system packages..."
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y python3.11.0 python3.11.0-pip python3.11.0-venv python3-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx git curl wget unzip
sudo apt install -y libpq-dev build-essential
sudo apt install -y libopencv-dev python3-opencv
echo "✅ System packages installed"

echo ""
echo ">>> STEP 2: Setting up PostgreSQL database..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

sudo -u postgres psql <<EOF
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
echo "✅ PostgreSQL database created: ${DB_NAME}"

echo ""
echo ">>> STEP 3: Cloning project from GitHub..."
cd /home/deepfakeuser
if [ -d "$APP_DIR" ]; then
    echo "Project exists, pulling latest..."
    cd $APP_DIR && git pull origin main
else
    git clone $GITHUB_REPO $APP_DIR
fi
echo "✅ Project cloned"

echo ""
echo ">>> STEP 4: Creating Python virtual environment..."
python3.11.0 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip
echo "✅ Virtual environment created"

echo ""
echo ">>> STEP 5: Installing Python requirements..."
cd $APP_DIR
pip install -r requirements.txt
# Try PyTorch (optional)
pip install torch==2.2.2+cpu torchvision==0.17.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu \
    --no-deps 2>/dev/null || echo "PyTorch skipped (optional)"
pip install facenet-pytorch==2.5.3 2>/dev/null || echo "facenet-pytorch skipped (optional)"
echo "✅ Python packages installed"

echo ""
echo ">>> STEP 6: Creating .env file..."
cat > $APP_DIR/.env <<ENVEOF
DJANGO_SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,${DOMAIN},www.${DOMAIN}
CSRF_TRUSTED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN},http://${DOMAIN}
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}
DB_SSL_REQUIRE=False
EMAIL_HOST_USER=deepfakeshield.admin@gmail.com
EMAIL_HOST_PASSWORD=deepfakeshield.admin@gmail.com
DEFAULT_FROM_EMAIL=DeepFake Shield <deepfakeshield.admin@gmail.com>
SITE_URL=https://${DOMAIN}
DJANGO_SUPERUSER_USERNAME=Admin
DJANGO_SUPERUSER_EMAIL=admin@${DOMAIN}
DJANGO_SUPERUSER_PASSWORD=Signature@44
LOG_LEVEL=INFO
ENVEOF
echo "✅ .env file created"

echo ""
echo ">>> STEP 7: Running Django setup..."
cd $APP_DIR
source $VENV_DIR/bin/activate
python manage.py makemigrations --no-input 2>/dev/null || true
python manage.py makemigrations core --no-input 2>/dev/null || true
python manage.py migrate --no-input
python manage.py collectstatic --no-input
mkdir -p media/uploads media/processed media/reports
python manage.py createsuperuser --no-input 2>/dev/null || echo "Superuser already exists"
echo "✅ Django migrations done"

echo ""
echo ">>> STEP 8: Creating Gunicorn service..."
sudo bash -c "cat > /etc/systemd/system/deepfakeshield.service <<SVCEOF
[Unit]
Description=DeepFake Shield Gunicorn Service
After=network.target postgresql.service

[Service]
User=deepfakeuser
Group=www-data
WorkingDirectory=${APP_DIR}
Environment=\"PATH=${VENV_DIR}/bin\"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/gunicorn deepfakeshield.wsgi:application \\
    --bind 127.0.0.1:8000 \\
    --workers 2 \\
    --timeout 120 \\
    --access-logfile /var/log/deepfakeshield_access.log \\
    --error-logfile /var/log/deepfakeshield_error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF"

sudo systemctl daemon-reload
sudo systemctl enable deepfakeshield
sudo systemctl start deepfakeshield
echo "✅ Gunicorn service created and started"

echo ""
echo ">>> STEP 9: Configuring Nginx..."
sudo bash -c "cat > /etc/nginx/sites-available/deepfakeshield <<NGINXEOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN} _;

    client_max_body_size 100M;

    location /static/ {
        alias ${APP_DIR}/staticfiles/;
        expires 30d;
        add_header Cache-Control \"public, no-transform\";
    }

    location /media/ {
        alias ${APP_DIR}/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \\\$host;
        proxy_set_header X-Real-IP \\\$remote_addr;
        proxy_set_header X-Forwarded-For \\\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\\$scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
}
NGINXEOF"

sudo ln -sf /etc/nginx/sites-available/deepfakeshield /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
sudo systemctl enable nginx
echo "✅ Nginx configured"

echo ""
echo ">>> STEP 10: Setting permissions..."
sudo chown -R deepfakeuser:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod -R 777 $APP_DIR/media
echo "✅ Permissions set"

echo ""
echo ">>> STEP 11: Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
echo "✅ Firewall configured"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   ✅✅ SETUP COMPLETE!                              ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║                                                      ║"
echo "║   Website:  http://${DOMAIN}                         ║"
echo "║   Admin:    http://${DOMAIN}/admin/                  ║"
echo "║   Username: admin                                    ║"
echo "║   Password: Admin@Shield2024                         ║"
echo "║                                                      ║"
echo "║   Check status: sudo systemctl status deepfakeshield ║"
echo "║   View logs:    sudo journalctl -u deepfakeshield -f ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "NEXT STEP: Install SSL certificate"
echo "Run: sudo apt install certbot python3-certbot-nginx -y"
echo "Then: sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo ""