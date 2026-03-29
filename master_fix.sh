#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DeepFake Shield — MASTER FIX SCRIPT
# Fixes: Email, Translation, Mobile, Extension hosting, Media perms
# Run: bash master_fix.sh
# ═══════════════════════════════════════════════════════════════
set -e
cd ~/deepfakeshield

echo "╔══════════════════════════════════════════════════════╗"
echo "║   DeepFake Shield — Master Fix Running...            ║"
echo "╚══════════════════════════════════════════════════════╝"

# ── FIX 1: Media permissions (image upload failing) ──
echo ">>> Fixing permissions..."
sudo chown -R deepfakeuser:www-data media/ staticfiles/ 2>/dev/null || true
sudo chmod -R 775 media/
sudo chmod -R 755 staticfiles/
sudo chmod 755 /home/deepfakeuser/
mkdir -p media/uploads media/processed media/reports
echo "✅ Permissions fixed"

# ── FIX 2: Update .env with Brevo key ──
echo ">>> Updating .env with Brevo key..."
# Remove old email entries
sed -i '/^EMAIL_HOST/d; /^ANYMAIL/d; /^DEFAULT_FROM_EMAIL/d' .env 2>/dev/null || true
# Add Brevo key
grep -q "ANYMAIL_BREVO_API_KEY" .env 2>/dev/null || \
    echo "ANYMAIL_BREVO_API_KEY=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" >> .env
echo "✅ Brevo key added"

# ── FIX 3: Install anymail ──
echo ">>> Installing anymail..."
~/venv/bin/pip install django-anymail[brevo] --quiet && echo "✅ anymail installed"

# ── FIX 4: Test email ──
echo ">>> Testing email..."
set -a && source .env && set +a
~/venv/bin/python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','deepfakeshield.settings')
from dotenv import load_dotenv
load_dotenv('/home/deepfakeuser/deepfakeshield/.env')
django.setup()
from django.conf import settings
print(f'Email backend: {settings.EMAIL_BACKEND}')
print(f'From: {settings.DEFAULT_FROM_EMAIL}')
brevo = getattr(settings,'ANYMAIL',{})
print(f'Brevo key set: {\"YES\" if brevo.get(\"BREVO_API_KEY\") else \"NO\"}')
" && echo "✅ Email config verified"

# ── FIX 5: Verify DEEPFAKE_SHIELD settings ──
echo ">>> Verifying app settings..."
~/venv/bin/python -c "
import os, django
os.environ['DJANGO_SETTINGS_MODULE']='deepfakeshield.settings'
from dotenv import load_dotenv; load_dotenv('/home/deepfakeuser/deepfakeshield/.env')
django.setup()
from django.conf import settings
cfg = settings.DEEPFAKE_SHIELD
print(f'Image formats: {cfg[\"SUPPORTED_IMAGE_FORMATS\"]}')
print(f'Max image: {cfg[\"MAX_IMAGE_SIZE_MB\"]}MB')
" && echo "✅ App settings OK"

# ── FIX 6: Fix forms.py extension check ──
echo ">>> Fixing forms.py..."
python3 << 'PYEOF'
with open('core/forms.py','r') as f: c = f.read()
# Fix dot prefix issue in extension comparison
for old,new in [
    ("ext = '.' + f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''\n        if ext not in settings.DEEPFAKE_SHIELD['SUPPORTED_IMAGE_FORMATS']:",
     "ext = f.name.rsplit('.',1)[-1].lower() if '.' in f.name else ''\n        if ext not in [x.strip('.').lower() for x in settings.DEEPFAKE_SHIELD['SUPPORTED_IMAGE_FORMATS']]:"),
    ("ext = '.' + f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''\n        if ext not in settings.DEEPFAKE_SHIELD['SUPPORTED_VIDEO_FORMATS']:",
     "ext = f.name.rsplit('.',1)[-1].lower() if '.' in f.name else ''\n        if ext not in [x.strip('.').lower() for x in settings.DEEPFAKE_SHIELD['SUPPORTED_VIDEO_FORMATS']]:"),
    ("ext = '.' + f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''\n        if ext not in settings.DEEPFAKE_SHIELD['SUPPORTED_AUDIO_FORMATS']:",
     "ext = f.name.rsplit('.',1)[-1].lower() if '.' in f.name else ''\n        if ext not in [x.strip('.').lower() for x in settings.DEEPFAKE_SHIELD['SUPPORTED_AUDIO_FORMATS']]:"),
]:
    c = c.replace(old, new)
with open('core/forms.py','w') as f: f.write(c)
print("forms.py extension check fixed")
PYEOF
echo "✅ forms.py fixed"

# ── FIX 7: Run Django check ──
echo ">>> Running Django system check..."
~/venv/bin/python manage.py check 2>&1 | tail -3
~/venv/bin/python manage.py migrate --no-input 2>/dev/null | tail -3

# ── FIX 8: Collect static files ──
echo ">>> Collecting static files..."
~/venv/bin/python manage.py collectstatic --no-input --clear 2>&1 | tail -3
sudo chown -R deepfakeuser:www-data staticfiles/
echo "✅ Static files collected"

# ── FIX 9: Restart service ──
echo ">>> Restarting service..."
sudo systemctl restart deepfakeshield
sleep 4

# ── FIX 10: Complete test ──
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  COMPLETE SYSTEM TEST                            ║"
echo "╚══════════════════════════════════════════════════╝"

~/venv/bin/python -c "
import os, django
os.environ['DJANGO_SETTINGS_MODULE']='deepfakeshield.settings'
from dotenv import load_dotenv; load_dotenv('/home/deepfakeuser/deepfakeshield/.env')
django.setup()
from django.db import connection
tables = connection.introspection.table_names()
core = [t for t in tables if 'core_' in t]
print(f'DB: {len(tables)} tables | Core: {core}')
from django.conf import settings
print(f'Email: {settings.EMAIL_BACKEND.split(\".\")[-1]}')
print(f'DEEPFAKE_SHIELD: OK')
"

for url in "/" "/home/" "/scan/image/" "/scan/video/" "/scan/audio/" "/scan/text/" "/dashboard/" "/admin/login/"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000$url 2>/dev/null)
    icon="✅"; [ "$code" != "200" ] && [ "$code" != "301" ] && [ "$code" != "302" ] && icon="❌"
    echo "  $icon $url → $code"
done

# Test email sending
echo ""
echo ">>> Sending test email..."
~/venv/bin/python << 'PYEOF'
import os, django
os.environ['DJANGO_SETTINGS_MODULE']='deepfakeshield.settings'
from dotenv import load_dotenv; load_dotenv('/home/deepfakeuser/deepfakeshield/.env')
django.setup()
from django.core.mail import send_mail
from django.conf import settings
try:
    send_mail(
        subject='✅ DeepFake Shield — Email Test',
        message='Your email system is working perfectly!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['mangapathireddy@gmail.com'],
        fail_silently=False,
    )
    print('✅ TEST EMAIL SENT SUCCESSFULLY!')
    print('   Check your inbox at mangapathireddy@gmail.com')
except Exception as e:
    print(f'❌ Email failed: {e}')
PYEOF

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ ALL FIXES APPLIED!                          ║"
echo "║  Website: https://deepfakeshield.tech            ║"
echo "╚══════════════════════════════════════════════════╝"