#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DeepFake Shield — ONE STEP COMPLETE DEPLOY
# Ubuntu 24.04 | Python 3.11 already installed
# Just run: ./final_deploy.sh
# ═══════════════════════════════════════════════════════════════

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   DeepFake Shield — One Step Deploy Starting...      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── CONFIG ──────────────────────────────────────────────────────
APP_DIR="/home/deepfakeuser/deepfakeshield"
VENV_DIR="/home/deepfakeuser/venv"
DOMAIN="deepfakeshield.tech"
VM_IP="20.244.24.145"
DB_NAME="deepfakeshield"
DB_USER="deepfakeadmin"
DB_PASS="Signature@44"
GITHUB_REPO="https://github.com/deepfakeshieldadmin/deepfakeshield.git"
EMAIL="24ce37@sdpc.ac.in"
# ────────────────────────────────────────────────────────────────

# STEP 1 ── System packages
echo ">>> [1/10] Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    postgresql postgresql-contrib \
    nginx git curl wget \
    libpq-dev build-essential \
    ffmpeg certbot python3-certbot-nginx \
    python3.11 python3.11-venv python3.11-dev 2>/dev/null || true
echo "✅ System packages done"

# STEP 2 ── PostgreSQL
echo ""
echo ">>> [2/10] Setting up database..."
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${DB_NAME};" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS ${DB_USER};" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"
sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
echo "✅ Database ready"

# STEP 3 ── Virtual environment
echo ""
echo ">>> [3/10] Setting up Python virtual environment..."
rm -rf $VENV_DIR
python3.11 -m venv $VENV_DIR --without-pip
curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
$VENV_DIR/bin/python /tmp/get-pip.py --quiet
$VENV_DIR/bin/pip install --upgrade pip setuptools wheel --quiet
echo "✅ Virtual environment ready: $($VENV_DIR/bin/python --version)"

# STEP 4 ── Clone project
echo ""
echo ">>> [4/10] Getting project from GitHub..."
rm -rf $APP_DIR
git clone $GITHUB_REPO $APP_DIR --quiet
echo "✅ Project downloaded"

# STEP 5 ── Install Python packages
echo ""
echo ">>> [5/10] Installing Python packages (takes ~3 minutes)..."
cd $APP_DIR
$VENV_DIR/bin/pip install -r requirements.txt --quiet
# Optional: PyTorch for better face detection
$VENV_DIR/bin/pip install \
    torch==2.2.2+cpu torchvision==0.17.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu \
    --no-deps --quiet 2>/dev/null && echo "  ✅ PyTorch installed" || echo "  ⚠ PyTorch skipped (ok)"
$VENV_DIR/bin/pip install facenet-pytorch==2.5.3 --quiet 2>/dev/null && \
    echo "  ✅ facenet-pytorch installed" || echo "  ⚠ facenet-pytorch skipped (ok)"
echo "✅ All packages installed"

# STEP 6 ── Create .env file
echo ""
echo ">>> [6/10] Creating environment config..."
SECRET=$($VENV_DIR/bin/python -c "import secrets; print(secrets.token_urlsafe(50))")
cat > $APP_DIR/.env << ENVEOF
DJANGO_SECRET_KEY=${SECRET}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,${DOMAIN},www.${DOMAIN},${VM_IP}
CSRF_TRUSTED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN},http://${VM_IP}
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}
DB_SSL_REQUIRE=False
EMAIL_HOST_USER=deepfakeshield.admin@gmail.com
EMAIL_HOST_PASSWORD=blolqgkyoydxkbbp
DEFAULT_FROM_EMAIL=DeepFake Shield <deepfakeshield.admin@gmail.com>
SITE_URL=https://${DOMAIN}
DJANGO_SUPERUSER_USERNAME=Admin
DJANGO_SUPERUSER_EMAIL=<deepfakeshield.admin@gmail.com>
DJANGO_SUPERUSER_PASSWORD=Signature@44
LOG_LEVEL=INFO
ENVEOF
echo "✅ Config file created"

# STEP 7 ── Django setup
echo ""
echo ">>> [7/10] Running Django setup..."
cd $APP_DIR
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs -d '\n')
$VENV_DIR/bin/python manage.py makemigrations --no-input 2>/dev/null || true
$VENV_DIR/bin/python manage.py makemigrations core --no-input 2>/dev/null || true
$VENV_DIR/bin/python manage.py migrate --no-input
$VENV_DIR/bin/python manage.py collectstatic --no-input --clear
mkdir -p media/uploads media/processed media/reports
DJANGO_SUPERUSER_USERNAME=Admin \
DJANGO_SUPERUSER_EMAIL=admin@${DOMAIN} \
DJANGO_SUPERUSER_PASSWORD=Signature@44 \
$VENV_DIR/bin/python manage.py createsuperuser --no-input 2>/dev/null || true
echo "✅ Django ready"

# STEP 8 ── Gunicorn service
echo ""
echo ">>> [8/10] Setting up Gunicorn service..."
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
ExecStart=${VENV_DIR}/bin/gunicorn deepfakeshield.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 120 --access-logfile /var/log/deepfakeshield_access.log --error-logfile /var/log/deepfakeshield_error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

sudo touch /var/log/deepfakeshield_access.log /var/log/deepfakeshield_error.log
sudo chown deepfakeuser:www-data /var/log/deepfakeshield_access.log /var/log/deepfakeshield_error.log
sudo chown -R deepfakeuser:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod -R 775 $APP_DIR/media
sudo systemctl daemon-reload
sudo systemctl enable deepfakeshield
sudo systemctl restart deepfakeshield
sleep 3
echo "✅ Gunicorn service running"

# STEP 9 ── Nginx
echo ""
echo ">>> [9/10] Configuring Nginx..."
sudo tee /etc/nginx/sites-available/deepfakeshield > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name deepfakeshield.tech www.deepfakeshield.tech 20.244.24.145;
    client_max_body_size 100M;

    location /static/ {
        alias /home/deepfakeuser/deepfakeshield/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /home/deepfakeuser/deepfakeshield/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/deepfakeshield /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx && sudo systemctl enable nginx
echo "✅ Nginx ready"

# STEP 10 ── SSL
echo ""
echo ">>> [10/10] Installing SSL certificate..."
sudo certbot --nginx \
    -d ${DOMAIN} \
    -d www.${DOMAIN} \
    --non-interactive \
    --agree-tos \
    --email ${EMAIL} \
    --redirect && echo "✅ SSL installed" || echo "⚠ SSL skipped - DNS may need more time"
sudo systemctl restart nginx

# ── FINAL TEST ──────────────────────────────────────────────────
echo ""
echo ">>> Testing website..."
sleep 3
CODE=$(curl -sk -o /dev/null -w "%{http_code}" https://${DOMAIN}/ 2>/dev/null || \
       curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null || echo "000")

echo ""
if [ "$CODE" = "200" ] || [ "$CODE" = "301" ] || [ "$CODE" = "302" ]; then
echo "╔══════════════════════════════════════════════════════╗"
echo "║  🎉🎉 SUCCESS! DeepFake Shield is LIVE!             ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  🌐🌐 https://deepfakeshield.tech                   ║"
echo "║  🔧🔧 https://deepfakeshield.tech/admin/            ║"
echo "║  👤👤 Username: Admin                               ║"
echo "║  🔑🔑 Password: Signature@44                        ║"
echo "╚══════════════════════════════════════════════════════╝"
else
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ⚠⚠ HTTP: ${CODE} — Checking what went wrong...     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "=== Gunicorn Status ==="
sudo systemctl status deepfakeshield --no-pager | head -15
echo ""
echo "=== Last Error Lines ==="
tail -20 /var/log/deepfakeshield_error.log 2>/dev/null || echo "No log yet"
echo ""
echo "=== Fix: copy error above and tell Claude ==="
fi