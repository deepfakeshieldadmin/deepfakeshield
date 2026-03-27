╔══════════════════════════════════════════════════════════════╗
║   DEEPFAKE SHIELD — REAL-TIME HOSTING CHECKLIST              ║
║   Website: deepfakeshield.tech                               ║
║   Follow every step in order. Don't skip any.                ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHASE 1 — UPDATE YOUR LOCAL PROJECT FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ 1. Open your project in VS Code
□ 2. Replace these files with downloaded versions from Claude:
      - deepfakeshield/settings.py    ← replace with settings.py
      - requirements.txt              ← replace with requirements.txt
      - build.sh                      ← replace with build.sh
      - runtime.txt                   ← replace with runtime.txt
      - Procfile                      ← replace with Procfile
      - .env.example                  ← replace with .env.example

□ 3. Open your .env file. Make sure it has:
      DEBUG=False
      (Keep DATABASE_URL empty for now — we'll fill it in Phase 2)

□ 4. Test locally one more time:
      python manage.py runserver
      → If it works, continue. If error, tell Claude.

□ 5. Push all changes to GitHub:
      git add .
      git commit -m "Azure ready: updated settings, requirements, build"
      git push origin main

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHASE 2 — FREE POSTGRESQL DATABASE (Neon.tech)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

URL: https://neon.tech

□ 1. Go to neon.tech → Click "Sign Up"
□ 2. Sign in with GitHub (use deepfakeshieldadmin account)
□ 3. Click "New Project"
□ 4. Fill in:
      Project name: deepfakeshield
      PostgreSQL version: 16
      Region: AWS ap-south-1 (Mumbai — closest to India)
□ 5. Click "Create Project"
□ 6. You'll see a connection string. It looks like:
      postgresql://user:password@ep-xxx.ap-south-1.aws.neon.tech/neondb?sslmode=require
□ 7. COPY THIS ENTIRE STRING — save it in Notepad
      (You'll need it in Phase 3 Step 5)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHASE 3 — AZURE WEB APP SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IF YOU DON'T HAVE AZURE ACCOUNT:
→ Go to: https://azure.microsoft.com/en-in/free/students/
→ Click "Start Free"
→ Use your COLLEGE EMAIL to get $100 free credit
→ No credit card needed with college email!

□ 1. Go to: https://portal.azure.com
□ 2. Click "Create a resource" (+ button, top left)
□ 3. In the search box type: Web App → Click "Create"
□ 4. Fill in the form:

   ┌─────────────────────────────────────────────────────┐
   │ Subscription:     Azure for Students                │
   │ Resource Group:   Click "Create new" → deepfake-rg  │
   │ Name:             deepfakeshield                    │
   │                   (URL will be:                     │
   │                   deepfakeshield.azurewebsites.net) │
   │ Publish:          Code                              │
   │ Runtime stack:    Python 3.11                       │
   │ Operating System: Linux                             │
   │ Region:           Central India                     │
   │ Pricing plan:     Free F1                           │
   └─────────────────────────────────────────────────────┘

□ 5. Click "Review + Create" → "Create"
□ 6. Wait 2-3 minutes for deployment ⏳
□ 7. Click "Go to resource" when done

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHASE 4 — SET ENVIRONMENT VARIABLES IN AZURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ 1. In your Web App → Click "Configuration" (left sidebar)
□ 2. Click "Application settings" tab
□ 3. Click "+ New application setting" for EACH variable below:

   ══ COPY THESE EXACTLY ══

   Name: DJANGO_SECRET_KEY
   Value: (Generate by running this in your laptop terminal:)
          python -c "import secrets; print(secrets.token_urlsafe(50))"
          (Copy the output and paste it here)

   Name: DEBUG
   Value: False

   Name: ALLOWED_HOSTS
   Value: deepfakeshield.azurewebsites.net,deepfakeshield.tech,www.deepfakeshield.tech

   Name: CSRF_TRUSTED_ORIGINS
   Value: https://deepfakeshield.azurewebsites.net,https://deepfakeshield.tech,https://www.deepfakeshield.tech

   Name: DATABASE_URL
   Value: (Paste your Neon.tech connection string from Phase 2 Step 7)

   Name: DB_SSL_REQUIRE
   Value: True

   Name: EMAIL_HOST_USER
   Value: (your Gmail address, e.g. yourname@gmail.com)

   Name: EMAIL_HOST_PASSWORD
   Value: (your Gmail App Password — see HOW TO GET GMAIL APP PASSWORD below)

   Name: DEFAULT_FROM_EMAIL
   Value: DeepFake Shield <yourname@gmail.com>

   Name: SITE_URL
   Value: https://deepfakeshield.azurewebsites.net

   Name: DJANGO_SUPERUSER_USERNAME
   Value: admin

   Name: DJANGO_SUPERUSER_EMAIL
   Value: admin@deepfakeshield.tech

   Name: DJANGO_SUPERUSER_PASSWORD
   Value: Admin@Shield2024

   Name: SCM_DO_BUILD_DURING_DEPLOYMENT
   Value: true

□ 4. Click "SAVE" button at the top (IMPORTANT!)
□ 5. Click "Continue" when it asks to restart

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HOW TO GET GMAIL APP PASSWORD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Go to: https://myaccount.google.com/security
2. Turn ON "2-Step Verification" if not already on
3. Search "App passwords" on that page
4. App: Mail | Device: Other → type "DeepFake Shield"
5. Click Generate
6. Copy the 16-character password (e.g.: abcd efgh ijkl mnop)
7. Remove spaces → abcdefghijklmnop
8. Use this as EMAIL_HOST_PASSWORD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHASE 5 — SET STARTUP COMMAND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ 1. Azure Portal → Your Web App → Configuration
□ 2. Click "General settings" tab
□ 3. Find "Startup Command" field
□ 4. Enter EXACTLY:
      gunicorn deepfakeshield.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
□ 5. Click Save

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHASE 6 — CONNECT GITHUB TO AZURE (AUTO-DEPLOY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ 1. Azure Portal → Your Web App → "Deployment Center"
□ 2. Source: GitHub
□ 3. Click "Authorize" → Sign in with deepfakeshieldadmin
□ 4. Select:
      Organization: deepfakeshieldadmin
      Repository:   deepfakeshield
      Branch:       main
□ 5. Click "Save"
□ 6. Azure will automatically create a GitHub Actions file
□ 7. Go to GitHub → Your repo → "Actions" tab
□ 8. Watch the deployment run (takes 3-5 minutes) ⏳
□ 9. Green checkmark ✅ = SUCCESS!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHASE 7 — TEST YOUR LIVE WEBSITE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ 1. Go to: https://deepfakeshield.azurewebsites.net
□ 2. Your website should load! ✅
□ 3. Test login at: https://deepfakeshield.azurewebsites.net/admin/
      Username: admin
      Password: Admin@Shield2024
□ 4. Test signup and image upload

IF YOU GET AN ERROR:
→ Azure Portal → Your Web App → "Log stream"
→ Copy the error and tell Claude

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHASE 8 — GET .TECH DOMAIN (GitHub Student Pack)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ 1. Go to: https://education.github.com/pack
□ 2. Sign in with: deepfakeshieldadmin
□ 3. If not verified yet:
      - Click "Get student benefits"
      - Upload your college ID or use .edu email
      - Wait for approval (can take 1-7 days)

□ 4. Once approved, search for "get.tech" in benefits list
□ 5. Click "Get access" next to get.tech
□ 6. You'll be redirected to get.tech website
□ 7. Search: deepfakeshield
□ 8. Register: deepfakeshield.tech (FREE for 1 year) ✅
□ 9. Create account on get.tech
□ 10. Complete registration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PHASE 9 — CONNECT deepfakeshield.tech TO AZURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

(Do this ONLY after Phase 7 website works AND Phase 8 domain registered)

Step A — Add domain in Azure:
□ 1. Azure Portal → Your Web App → "Custom domains"
□ 2. Click "+ Add custom domain"
□ 3. Enter: deepfakeshield.tech
□ 4. Azure shows you 2 DNS records to add:
      - TXT record: asuid.deepfakeshield.tech → (some value)
      - A record: @ → (Azure IP address)
      WRITE THESE DOWN!

Step B — Add DNS records in get.tech:
□ 1. Log in to: https://manage.get.tech
□ 2. Click on your domain: deepfakeshield.tech
□ 3. Go to "DNS Management" or "Name Servers"
□ 4. Add TXT record:
      Host: asuid
      Value: (the value Azure gave you)
      TTL: 3600
□ 5. Add A record:
      Host: @
      Value: (Azure IP address)
      TTL: 3600
□ 6. Add CNAME record:
      Host: www
      Value: deepfakeshield.azurewebsites.net
      TTL: 3600
□ 7. Save all records
□ 8. Wait 5-30 minutes for DNS to update ⏳

Step C — Verify in Azure:
□ 9. Back in Azure → Custom domains
□ 10. Click "Validate" next to deepfakeshield.tech
□ 11. Click "Add custom domain"

Step D — Free SSL Certificate:
□ 12. Azure → Your Web App → "Certificates"
□ 13. Click "Add certificate" → "Create App Service Managed Certificate"
□ 14. Select: deepfakeshield.tech
□ 15. Click Create (takes 2-5 minutes)
□ 16. Go to "Custom domains" → Click on deepfakeshield.tech
□ 17. Click "Add binding" → Select your certificate → SNI SSL
□ 18. Save ✅

□ 19. Test: https://deepfakeshield.tech  ← YOUR LIVE WEBSITE! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 COMMON ERRORS & FIXES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Error: Application Error / 500
→ Check Log stream in Azure Portal
→ Usually: wrong DATABASE_URL or missing env variable

Error: Static files missing (CSS not loading)
→ Make sure collectstatic ran in build.sh
→ Check STATIC_ROOT is set correctly in settings.py

Error: CSRF verification failed
→ Make sure CSRF_TRUSTED_ORIGINS includes your domain
→ Must start with https://

Error: ModuleNotFoundError
→ Check requirements.txt has all packages
→ Force redeploy: make a small change and push to GitHub

Error: 502 Bad Gateway
→ Startup command is wrong
→ Check gunicorn command in General settings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FINAL RESULT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After completing all phases:
✅ https://deepfakeshield.azurewebsites.net (live)
✅ https://deepfakeshield.tech (custom domain)
✅ SSL certificate (green padlock)
✅ Auto-deploy: every git push updates the live site
✅ Free PostgreSQL database on Neon.tech
✅ Admin panel at /admin/