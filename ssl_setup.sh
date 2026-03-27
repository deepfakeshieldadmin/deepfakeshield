#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DeepFake Shield — SSL Certificate Setup (Free HTTPS)
# Run this AFTER vm_setup.sh AND after DNS records are pointed
# ═══════════════════════════════════════════════════════════════

DOMAIN="deepfakeshield.tech"
EMAIL="24ce37@sdpc.ac.in"

echo ">>> Installing Certbot (free SSL from Let's Encrypt)..."
sudo apt install -y certbot python3-certbot-nginx

echo ">>> Getting SSL certificate for ${DOMAIN}..."
sudo certbot --nginx \
    -d ${DOMAIN} \
    -d www.${DOMAIN} \
    --non-interactive \
    --agree-tos \
    --email ${EMAIL} \
    --redirect

echo ">>> Setting up auto-renewal..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
sudo crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

echo ""
echo "✅ SSL Certificate installed!"
echo "   Your website is now at: https://${DOMAIN}"
echo "   Certificate auto-renews every 90 days"