"""
DeepFake Shield — Detection Testing Tool
Run: python test_detection.py <image_path>
Shows detailed breakdown of every module's score.
"""
import sys
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deepfakeshield.settings')

import django
django.setup()

from core.ai_engine import (
    _detect_and_analyze_faces, _analyze_ela, _analyze_frequency,
    _analyze_texture, _analyze_noise, _analyze_metadata, _analyze_compression
)
import cv2
import numpy as np


def test_image(image_path):
    print(f"\n{'='*60}")
    print(f"  TESTING: {os.path.basename(image_path)}")
    print(f"{'='*60}")

    # Read image
    with open(image_path, 'rb') as f:
        file_bytes = f.read()

    img = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print("ERROR: Could not read image")
        return

    h, w = img.shape[:2]
    print(f"Size: {w}x{h}")
    print()

    # Test each module
    print("--- FACE DETECTION ---")
    face = _detect_and_analyze_faces(img)
    print(f"  Faces found: {face['count']}")
    print(f"  Face score: {face['score']:.1f}")
    print(f"  Deepfake score: {face.get('deepfake_score', 'N/A')}")
    print(f"  MTCNN used: {face.get('mtcnn_used', False)}")
    print(f"  Detail: {face['detail'][:200]}")
    print()

    print("--- ELA ---")
    ela = _analyze_ela(img)
    print(f"  Score: {ela['score']:.1f}")
    print(f"  Manipulated: {ela['manipulated']}")
    print(f"  Detail: {ela['detail']}")
    print()

    print("--- FREQUENCY ---")
    freq = _analyze_frequency(img)
    print(f"  Score: {freq['score']:.1f}")
    print(f"  GAN detected: {freq['gan_detected']}")
    print(f"  Detail: {freq['detail']}")
    print()

    print("--- TEXTURE ---")
    tex = _analyze_texture(img)
    print(f"  Score: {tex['score']:.1f}")
    print(f"  Natural: {tex['natural']}")
    print(f"  Detail: {tex['detail']}")
    print()

    print("--- NOISE ---")
    noise = _analyze_noise(img)
    print(f"  Score: {noise['score']:.1f}")
    print(f"  Level: {noise['level']}")
    print(f"  Detail: {noise['detail']}")
    print()

    print("--- METADATA ---")
    meta = _analyze_metadata(file_bytes)
    print(f"  Score: {meta['score']:.1f}")
    print(f"  EXIF: {meta['present']}")
    print(f"  Camera: {meta['make']} {meta['model']}")
    print(f"  Trusted: {meta.get('trusted_camera', False)}")
    print()

    print("--- COMPRESSION ---")
    comp = _analyze_compression(img)
    print(f"  Score: {comp['score']:.1f}")
    print(f"  Detail: {comp['detail']}")
    print()

    # Also show raw measurements
    print("--- RAW MEASUREMENTS ---")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Noise level
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    print(f"  Laplacian variance (noise): {lap_var:.2f}")

    # Gradient
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad = np.sqrt(gx**2 + gy**2)
    print(f"  Mean gradient (texture): {np.mean(grad):.2f}")

    # High-pass
    kernel = np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]], dtype=np.float32)
    hp = cv2.filter2D(gray, -1, kernel)
    print(f"  High-pass std: {np.std(hp.astype(float)):.2f}")

    # Face-specific if faces found
    if face['boxes']:
        f0 = face['boxes'][0]
        fx, fy, fw, fh = f0['x'], f0['y'], f0['w'], f0['h']
        face_region = gray[fy:fy+fh, fx:fx+fw]
        face_lap = cv2.Laplacian(face_region, cv2.CV_64F).var()
        print(f"  Face sharpness: {face_lap:.2f}")

        # Neck region
        neck_y = fy + fh
        neck_h = min(fh//2, h - neck_y)
        if neck_h > 10:
            neck = gray[neck_y:neck_y+neck_h, fx:fx+fw]
            neck_lap = cv2.Laplacian(neck, cv2.CV_64F).var()
            print(f"  Neck sharpness: {neck_lap:.2f}")
            print(f"  Face/Neck ratio: {face_lap/neck_lap:.2f}" if neck_lap > 0 else "  Neck: N/A")

    print(f"\n{'='*60}")
    print("  WHAT SHOULD THIS IMAGE BE?")
    print("  If REAL: All scores should be 65+, deepfake_score 70+")
    print("  If FAKE: deepfake_score should be <40, some modules <50")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_detection.py <image_path>")
        print("       python test_detection.py path/to/real.jpg")
        print("       python test_detection.py path/to/fake.jpg")
        sys.exit(1)

    for path in sys.argv[1:]:
        if os.path.exists(path):
            test_image(path)
        else:
            print(f"File not found: {path}")