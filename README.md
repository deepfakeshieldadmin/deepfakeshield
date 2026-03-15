# 🛡️ DeepFake Shield

**Real-Time Media Authenticity Verification System**

A production-grade Django web application for detecting deepfakes and synthetic media across images, videos, audio, and text using hybrid CPU-friendly AI analysis.

## Features

- 🖼️ **Image Analysis** - EXIF metadata, face detection, AI artifact detection, noise/edge/texture/color analysis
- 🎬 **Video Analysis** - Frame sampling, temporal consistency, face consistency, motion realism
- 🎵 **Audio Analysis** - Spectral features, harmonic analysis, clipping detection
- 📝 **Text Analysis** - AI-generated text detection using NLP statistical features
- 🔐 **Authentication** - Signup, login, email verification, CAPTCHA
- 📊 **Dashboard** - Scan history, statistics
- 📄 **PDF Reports** - Professional downloadable analysis reports
- 🎨 **Premium UI** - Dark/light theme, AOS animations, responsive design

## Tech Stack

- **Backend:** Django 4.2, Python 3.11
- **Database:** PostgreSQL (production), SQLite (development)
- **AI/ML:** OpenCV, NumPy, scikit-learn, librosa, PyTorch (optional)
- **Frontend:** HTML5, CSS3, JavaScript, AOS.js
- **Deployment:** Gunicorn, WhiteNoise, Render

## Quick Start (Local Development)

```bash
# Clone repository
git clone https://github.com/your-repo/deepfakeshield.git
cd deepfakeshield

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements-minimal.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings (DEBUG=True for local dev)

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --no-input

# Run development server
python manage.py runserver