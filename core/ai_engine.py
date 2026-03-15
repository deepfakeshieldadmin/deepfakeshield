"""
DeepFake Shield - Image Authenticity Detection Engine
Hybrid CPU-friendly analysis using OpenCV, NumPy, scikit-learn, and optional PyTorch.

This engine analyzes:
- EXIF metadata and camera information
- Face detection and quality scoring
- AI artifact detection
- Compression/block analysis
- Natural noise patterns
- Edge realism
- Texture realism
- Color distribution realism
- Screenshot likelihood
- Synthetic smoothness
- Optional deep semantic features (torchvision)
- Scene description generation

Score interpretation:
  0-39:  Likely Fake
  40-74: Suspicious
  75-99: Likely Real
  100:   Highly Authentic
"""

import io
import os
import logging
import hashlib
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# OpenCV
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Image analysis will be limited.")

# Pillow
try:
    from PIL import Image, ImageStat, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow not available.")

# EXIF
try:
    import exifread
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False
    logger.warning("exifread not available. EXIF analysis disabled.")

# scikit-learn
try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# PyTorch (optional deep features)
TORCH_AVAILABLE = False
TORCH_MODEL = None
TORCH_TRANSFORMS = None
try:
    import torch
    import torchvision.models as models
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
    logger.info("PyTorch available for deep feature analysis.")
except ImportError:
    logger.info("PyTorch not available. Deep feature analysis disabled (not required).")


def _load_torch_model():
    """Lazy-load a lightweight torchvision model for semantic feature extraction."""
    global TORCH_MODEL, TORCH_TRANSFORMS
    if TORCH_MODEL is not None:
        return TORCH_MODEL, TORCH_TRANSFORMS
    if not TORCH_AVAILABLE:
        return None, None
    try:
        model = models.mobilenet_v2(pretrained=False)
        # Try to load pretrained weights
        try:
            model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        except Exception:
            try:
                model = models.mobilenet_v2(pretrained=True)
            except Exception:
                logger.info("Could not load pretrained MobileNetV2. Using random weights for feature extraction.")
        model.eval()
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        TORCH_MODEL = model
        TORCH_TRANSFORMS = transform
        return model, transform
    except Exception as e:
        logger.error(f"Failed to load torch model: {e}")
        return None, None


# ─────────────────────────────────────────────
# EXIF Analysis
# ─────────────────────────────────────────────

def analyze_exif(file_bytes):
    """Extract and analyze EXIF metadata from image bytes."""
    result = {
        'exif_present': False,
        'exif_data': {},
        'camera_make': 'Unknown',
        'camera_model': 'Unknown',
        'has_gps': False,
        'has_thumbnail': False,
        'software': 'Unknown',
        'datetime': 'Unknown',
        'exif_score': 50.0,  # neutral by default
    }

    if not EXIF_AVAILABLE:
        return result

    try:
        tags = exifread.process_file(io.BytesIO(file_bytes), details=False)
        if not tags:
            result['exif_score'] = 40.0  # No EXIF is slightly suspicious
            return result

        result['exif_present'] = True
        exif_dict = {}

        for key, val in tags.items():
            try:
                exif_dict[str(key)] = str(val)
            except Exception:
                pass

        result['exif_data'] = exif_dict

        # Camera info
        make = exif_dict.get('Image Make', '').strip()
        model = exif_dict.get('Image Model', '').strip()
        result['camera_make'] = make if make else 'Unknown'
        result['camera_model'] = model if model else 'Unknown'

        # Software
        software = exif_dict.get('Image Software', '').strip()
        result['software'] = software if software else 'Unknown'

        # DateTime
        dt = exif_dict.get('EXIF DateTimeOriginal', exif_dict.get('Image DateTime', '')).strip()
        result['datetime'] = dt if dt else 'Unknown'

        # GPS
        result['has_gps'] = any('GPS' in k for k in exif_dict.keys())

        # Thumbnail
        result['has_thumbnail'] = 'JPEGThumbnail' in tags or any('Thumbnail' in k for k in exif_dict.keys())

        # Score EXIF quality
        score = 50.0
        if make and make != 'Unknown':
            score += 15.0
        if model and model != 'Unknown':
            score += 10.0
        if dt and dt != 'Unknown':
            score += 10.0
        if result['has_gps']:
            score += 5.0
        if result['has_thumbnail']:
            score += 5.0

        # Suspicious software indicators
        suspicious_software = ['photoshop', 'gimp', 'paint', 'canva', 'midjourney', 'dalle', 'stable diffusion']
        if software and any(s in software.lower() for s in suspicious_software):
            score -= 20.0

        result['exif_score'] = max(0.0, min(100.0, score))

    except Exception as e:
        logger.error(f"EXIF analysis error: {e}")
        result['exif_score'] = 45.0

    return result


# ─────────────────────────────────────────────
# Screenshot Detection
# ─────────────────────────────────────────────

def detect_screenshot_likelihood(img_cv, pil_img, exif_data):
    """Detect if image is likely a screenshot."""
    score = 0.0
    reasons = []

    try:
        h, w = img_cv.shape[:2]

        # Common screenshot resolutions
        screenshot_resolutions = [
            (1920, 1080), (2560, 1440), (1366, 768), (1536, 864),
            (3840, 2160), (1440, 900), (1280, 720), (1024, 768),
            (2560, 1600), (2880, 1800), (1680, 1050),
            (750, 1334), (1125, 2436), (1170, 2532),  # iPhone
            (1080, 1920), (1080, 2340), (1440, 3200),  # Android
        ]

        for sw, sh in screenshot_resolutions:
            if (w == sw and h == sh) or (w == sh and h == sw):
                score += 30.0
                reasons.append(f'Resolution matches common screen: {w}x{h}')
                break

        # Check for UI-like borders (uniform color bands)
        top_row = img_cv[0:3, :, :] if len(img_cv.shape) == 3 else img_cv[0:3, :]
        bottom_row = img_cv[-3:, :, :] if len(img_cv.shape) == 3 else img_cv[-3:, :]
        top_std = np.std(top_row)
        bottom_std = np.std(bottom_row)
        if top_std < 5.0 and bottom_std < 5.0:
            score += 20.0
            reasons.append('Uniform color bands at edges (UI bars)')

        # No EXIF camera data suggests screenshot
        if not exif_data.get('exif_present', False):
            score += 10.0
            reasons.append('No EXIF camera data')

        # Very clean/no noise in flat regions
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
        flat_region = gray[h // 4:h // 4 + 50, w // 4:w // 4 + 50]
        local_std = np.std(flat_region.astype(float))
        if local_std < 2.0:
            score += 15.0
            reasons.append('Very low noise in flat regions')

        # Check for sharp text-like edges
        edges = cv2.Canny(gray, 100, 200)
        edge_ratio = np.count_nonzero(edges) / edges.size
        if edge_ratio > 0.15:
            score += 10.0
            reasons.append('High edge density (text/UI elements)')

    except Exception as e:
        logger.error(f"Screenshot detection error: {e}")

    return {
        'screenshot_likelihood': min(100.0, score),
        'screenshot_reasons': reasons,
    }


# ─────────────────────────────────────────────
# Face Detection
# ─────────────────────────────────────────────

def detect_faces(img_cv):
    """Detect faces using OpenCV Haar cascades with strict filtering to reduce false positives."""
    results = {
        'face_count': 0,
        'face_boxes': [],
        'face_detector_used': 'none',
        'face_quality_score': 50.0,
    }

    if not CV2_AVAILABLE:
        return results

    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
        h, w = gray.shape[:2]

        # Use only the most reliable cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        if not os.path.exists(cascade_path):
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

        if not os.path.exists(cascade_path):
            return results

        cascade = cv2.CascadeClassifier(cascade_path)
        if cascade.empty():
            return results

        # Stricter parameters to reduce false positives
        min_face_size = max(30, min(w, h) // 10)

        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.15,       # Slightly larger step = fewer false positives
            minNeighbors=6,         # Higher = stricter (was 4)
            minSize=(min_face_size, min_face_size),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) == 0:
            # Try profile faces with even stricter settings
            profile_path = cv2.data.haarcascades + 'haarcascade_profileface.xml'
            if os.path.exists(profile_path):
                profile_cascade = cv2.CascadeClassifier(profile_path)
                if not profile_cascade.empty():
                    faces = profile_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.2,
                        minNeighbors=7,
                        minSize=(min_face_size, min_face_size),
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )
                    if len(faces) > 0:
                        results['face_detector_used'] = 'profile'

        all_faces = []
        for (x, y, fw, fh) in faces:
            # Additional validation: face aspect ratio should be roughly square
            aspect = fw / fh if fh > 0 else 0
            if aspect < 0.6 or aspect > 1.6:
                continue  # Skip non-square detections (likely false positive)

            # Face should not be too small relative to image
            face_area_ratio = (fw * fh) / (w * h)
            if face_area_ratio < 0.001:
                continue  # Skip very tiny detections

            # Validate face region has enough detail (not flat background)
            face_region = gray[y:y+fh, x:x+fw]
            if face_region.size > 0:
                region_std = np.std(face_region.astype(float))
                if region_std < 15:
                    continue  # Skip flat/uniform regions (false positive)

            all_faces.append({
                'x': int(x), 'y': int(y),
                'w': int(fw), 'h': int(fh),
                'detector': results.get('face_detector_used', 'frontal')
            })

        # Deduplicate overlapping detections with stricter IoU
        if len(all_faces) > 1:
            all_faces = _deduplicate_faces(all_faces, iou_threshold=0.3)

        if results['face_detector_used'] == 'none' and all_faces:
            results['face_detector_used'] = 'frontal_alt2'

        results['face_count'] = len(all_faces)
        results['face_boxes'] = all_faces

        # Face quality scoring
        if all_faces:
            quality_scores = []
            for face in all_faces:
                fx, fy, fw, fh = face['x'], face['y'], face['w'], face['h']
                fx = max(0, fx)
                fy = max(0, fy)
                fw = min(fw, w - fx)
                fh = min(fh, h - fy)

                if fw < 10 or fh < 10:
                    quality_scores.append(30.0)
                    continue

                face_region = gray[fy:fy + fh, fx:fx + fw]
                if face_region.size == 0:
                    quality_scores.append(30.0)
                    continue

                brightness = np.mean(face_region)
                contrast = np.std(face_region)
                laplacian_var = cv2.Laplacian(face_region, cv2.CV_64F).var()

                q = 50.0
                if 80 < brightness < 180:
                    q += 15.0
                elif 50 < brightness < 210:
                    q += 8.0

                if contrast > 30:
                    q += 15.0
                elif contrast > 15:
                    q += 8.0

                if laplacian_var > 100:
                    q += 20.0
                elif laplacian_var > 30:
                    q += 10.0
                elif laplacian_var < 10:
                    q -= 10.0

                quality_scores.append(max(0.0, min(100.0, q)))

            results['face_quality_score'] = np.mean(quality_scores)

    except Exception as e:
        logger.error(f"Face detection error: {e}")

    return results


def _deduplicate_faces(faces, iou_threshold=0.4):
    """Remove overlapping face detections using IoU."""
    if len(faces) <= 1:
        return faces

    def iou(a, b):
        ax1, ay1, ax2, ay2 = a['x'], a['y'], a['x'] + a['w'], a['y'] + a['h']
        bx1, by1, bx2, by2 = b['x'], b['y'], b['x'] + b['w'], b['y'] + b['h']
        ix1 = max(ax1, bx1)
        iy1 = max(ay1, by1)
        ix2 = min(ax2, bx2)
        iy2 = min(ay2, by2)
        if ix2 <= ix1 or iy2 <= iy1:
            return 0.0
        intersection = (ix2 - ix1) * (iy2 - iy1)
        area_a = (ax2 - ax1) * (ay2 - ay1)
        area_b = (bx2 - bx1) * (by2 - by1)
        union = area_a + area_b - intersection
        return intersection / union if union > 0 else 0.0

    keep = [True] * len(faces)
    for i in range(len(faces)):
        if not keep[i]:
            continue
        for j in range(i + 1, len(faces)):
            if not keep[j]:
                continue
            if iou(faces[i], faces[j]) > iou_threshold:
                # Keep the larger detection
                area_i = faces[i]['w'] * faces[i]['h']
                area_j = faces[j]['w'] * faces[j]['h']
                if area_i >= area_j:
                    keep[j] = False
                else:
                    keep[i] = False
                    break

    return [f for f, k in zip(faces, keep) if k]


# ─────────────────────────────────────────────
# Draw face boxes on image
# ─────────────────────────────────────────────

def draw_face_boxes(img_cv, face_boxes):
    """Draw green rectangles around detected faces."""
    output = img_cv.copy()
    for face in face_boxes:
        x, y, w, h = face['x'], face['y'], face['w'], face['h']
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 3)
        # Label
        label = f"Face"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.5, min(w, h) / 200.0)
        thickness = max(1, int(font_scale * 2))
        cv2.putText(output, label, (x, y - 10), font, font_scale, (0, 255, 0), thickness)
    return output


# ─────────────────────────────────────────────
# AI Artifact Detection
# ─────────────────────────────────────────────

def detect_ai_artifacts(img_cv):
    """Detect artifacts commonly found in AI-generated images."""
    score = 0.0  # Higher = more artifacts detected = more likely fake

    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
        h, w = gray.shape[:2]

        # 1. Check for unnatural smoothness in local patches
        patch_size = max(16, min(w, h) // 10)
        smoothness_scores = []
        for _ in range(20):
            py = np.random.randint(0, max(1, h - patch_size))
            px = np.random.randint(0, max(1, w - patch_size))
            patch = gray[py:py + patch_size, px:px + patch_size].astype(float)
            if patch.size > 0:
                smoothness_scores.append(np.std(patch))

        if smoothness_scores:
            avg_smoothness = np.mean(smoothness_scores)
            if avg_smoothness < 5.0:
                score += 25.0  # Extremely smooth = suspicious
            elif avg_smoothness < 10.0:
                score += 15.0
            elif avg_smoothness < 15.0:
                score += 8.0

        # 2. Check for repeating patterns (GAN artifacts)
        if w >= 64 and h >= 64:
            center_crop = gray[h // 4:3 * h // 4, w // 4:3 * w // 4]
            f_transform = np.fft.fft2(center_crop.astype(float))
            f_shift = np.fft.fftshift(f_transform)
            magnitude = np.abs(f_shift)
            magnitude_log = np.log1p(magnitude)

            # Check for unusual frequency spikes
            mean_mag = np.mean(magnitude_log)
            max_mag = np.max(magnitude_log)
            spike_ratio = max_mag / mean_mag if mean_mag > 0 else 1.0
            if spike_ratio > 8.0:
                score += 15.0
            elif spike_ratio > 5.0:
                score += 8.0

        # 3. Check color channel correlation
        if len(img_cv.shape) == 3 and img_cv.shape[2] == 3:
            b, g, r = cv2.split(img_cv)
            rg_corr = np.corrcoef(r.flatten()[:10000], g.flatten()[:10000])[0, 1]
            rb_corr = np.corrcoef(r.flatten()[:10000], b.flatten()[:10000])[0, 1]

            # AI images often have unnaturally high channel correlations
            avg_corr = (abs(rg_corr) + abs(rb_corr)) / 2
            if avg_corr > 0.98:
                score += 15.0
            elif avg_corr > 0.95:
                score += 8.0

        # 4. Check for grid-like artifacts (DCT block boundaries don't match JPEG)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = laplacian.var()
        if lap_var < 20:
            score += 10.0  # Very low variance suggests synthetic smoothness

    except Exception as e:
        logger.error(f"AI artifact detection error: {e}")

    return {
        'ai_artifact_score': min(100.0, score),
        'synthetic_smoothness_score': min(100.0, score * 1.2),
    }


# ─────────────────────────────────────────────
# Compression / Block Analysis
# ─────────────────────────────────────────────

def analyze_compression(img_cv):
    """Analyze JPEG compression artifacts and block patterns."""
    score = 50.0  # Neutral

    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
        h, w = gray.shape[:2]

        # Check 8x8 block boundaries (JPEG compression)
        block_diffs = []
        for y in range(8, h - 8, 8):
            row_diff = np.abs(gray[y, :].astype(float) - gray[y - 1, :].astype(float))
            block_diffs.append(np.mean(row_diff))

        for x in range(8, w - 8, 8):
            col_diff = np.abs(gray[:, x].astype(float) - gray[:, x - 1].astype(float))
            block_diffs.append(np.mean(col_diff))

        if block_diffs:
            avg_block_diff = np.mean(block_diffs)
            # Natural JPEG images have visible block boundaries
            if 2.0 < avg_block_diff < 15.0:
                score = 65.0  # Normal JPEG compression
            elif avg_block_diff >= 15.0:
                score = 40.0  # Heavy compression
            elif avg_block_diff < 2.0:
                score = 45.0  # Too smooth, possibly synthetic or heavily processed

    except Exception as e:
        logger.error(f"Compression analysis error: {e}")

    return {'compression_noise_score': score}


# ─────────────────────────────────────────────
# Noise Analysis
# ─────────────────────────────────────────────

def analyze_noise(img_cv):
    """Analyze noise patterns for naturalness."""
    score = 50.0

    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv

        # Noise estimation using Laplacian
        noise = cv2.Laplacian(gray, cv2.CV_64F)
        noise_std = np.std(noise)

        # Natural photos have moderate noise
        if 3.0 < noise_std < 30.0:
            score = 75.0
        elif 30.0 <= noise_std < 60.0:
            score = 65.0
        elif 1.0 < noise_std <= 3.0:
            score = 40.0  # Suspiciously clean
        elif noise_std <= 1.0:
            score = 25.0  # Almost no noise = synthetic
        else:
            score = 50.0  # Very noisy

        # Check noise distribution (should be roughly Gaussian for real photos)
        noise_flat = noise.flatten()
        sample = noise_flat[::max(1, len(noise_flat) // 5000)]  # Subsample for speed
        kurtosis_val = _kurtosis(sample)

        if abs(kurtosis_val) < 5:  # Near Gaussian
            score += 10.0
        elif abs(kurtosis_val) > 20:  # Very non-Gaussian
            score -= 10.0

        score = max(0.0, min(100.0, score))

    except Exception as e:
        logger.error(f"Noise analysis error: {e}")

    return {'noise_score': score}


def _kurtosis(data):
    """Calculate excess kurtosis."""
    n = len(data)
    if n < 4:
        return 0.0
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0
    return np.mean(((data - mean) / std) ** 4) - 3.0


# ─────────────────────────────────────────────
# Edge Analysis
# ─────────────────────────────────────────────

def analyze_edges(img_cv):
    """Analyze edge characteristics for realism."""
    score = 50.0

    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv

        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_ratio = np.count_nonzero(edges) / edges.size

        # Natural images: moderate edge density
        if 0.03 < edge_ratio < 0.20:
            score = 75.0
        elif 0.01 < edge_ratio <= 0.03:
            score = 60.0
        elif 0.20 <= edge_ratio < 0.35:
            score = 55.0
        elif edge_ratio <= 0.01:
            score = 35.0  # Too few edges
        else:
            score = 40.0  # Too many edges (screenshot/text)

        # Edge coherence check using Sobel
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
        grad_std = np.std(gradient_magnitude)
        grad_mean = np.mean(gradient_magnitude)

        if grad_mean > 0:
            cv_gradient = grad_std / grad_mean  # Coefficient of variation
            if 1.0 < cv_gradient < 3.0:
                score += 10.0  # Good variation in gradients (natural)
            elif cv_gradient < 0.5:
                score -= 10.0  # Too uniform

        score = max(0.0, min(100.0, score))

    except Exception as e:
        logger.error(f"Edge analysis error: {e}")

    return {'edge_score': score}


# ─────────────────────────────────────────────
# Texture Analysis
# ─────────────────────────────────────────────

def analyze_texture(img_cv):
    """Analyze texture patterns for naturalness."""
    score = 50.0

    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
        h, w = gray.shape[:2]

        # Local Binary Pattern-like analysis
        # Check texture diversity across patches
        patch_size = max(32, min(w, h) // 8)
        texture_scores = []

        for row in range(0, h - patch_size, patch_size):
            for col in range(0, w - patch_size, patch_size):
                patch = gray[row:row + patch_size, col:col + patch_size]
                if patch.size == 0:
                    continue
                # Texture features
                std_val = np.std(patch.astype(float))
                texture_scores.append(std_val)

        if texture_scores:
            texture_diversity = np.std(texture_scores)
            avg_texture = np.mean(texture_scores)

            # Natural images have diverse textures
            if texture_diversity > 15.0 and avg_texture > 10.0:
                score = 78.0
            elif texture_diversity > 8.0:
                score = 65.0
            elif texture_diversity < 3.0:
                score = 35.0  # Very uniform = synthetic
            else:
                score = 50.0

        # Gabor filter responses for texture verification
        kernels = []
        for theta in np.arange(0, np.pi, np.pi / 4):
            kern = cv2.getGaborKernel((21, 21), 4.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
            kernels.append(kern)

        gabor_responses = []
        for kern in kernels:
            filtered = cv2.filter2D(gray, cv2.CV_8UC3, kern)
            gabor_responses.append(np.mean(filtered))

        if gabor_responses:
            gabor_std = np.std(gabor_responses)
            if gabor_std > 5.0:
                score += 5.0  # Good directional texture variation

        score = max(0.0, min(100.0, score))

    except Exception as e:
        logger.error(f"Texture analysis error: {e}")

    return {'texture_score': score}


# ─────────────────────────────────────────────
# Color Analysis
# ─────────────────────────────────────────────

def analyze_color(img_cv):
    """Analyze color distribution for naturalness."""
    score = 50.0

    try:
        if len(img_cv.shape) < 3 or img_cv.shape[2] < 3:
            return {'color_score': 50.0}

        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        h_channel, s_channel, v_channel = cv2.split(hsv)

        # Saturation analysis
        mean_sat = np.mean(s_channel)
        std_sat = np.std(s_channel)

        # Natural images have moderate saturation
        if 30 < mean_sat < 150 and std_sat > 20:
            score = 75.0
        elif mean_sat < 10:
            score = 55.0  # Grayscale or very desaturated
        elif mean_sat > 200:
            score = 40.0  # Oversaturated = filtered/synthetic

        # Hue diversity
        h_hist = cv2.calcHist([h_channel], [0], None, [180], [0, 180])
        h_hist = h_hist.flatten()
        h_nonzero = np.count_nonzero(h_hist)
        hue_diversity = h_nonzero / 180.0

        if hue_diversity > 0.3:
            score += 10.0  # Good color diversity
        elif hue_diversity < 0.1:
            score -= 10.0  # Very limited palette

        # Color histogram smoothness
        hist_diff = np.diff(h_hist.astype(float))
        hist_roughness = np.std(hist_diff)
        if hist_roughness < 50:
            score -= 5.0  # Too smooth histogram = synthetic

        score = max(0.0, min(100.0, score))

    except Exception as e:
        logger.error(f"Color analysis error: {e}")

    return {'color_score': score}


# ─────────────────────────────────────────────
# Deep Feature Analysis (Optional PyTorch)
# ─────────────────────────────────────────────

def analyze_deep_features(pil_img):
    """Use pretrained CNN for semantic feature analysis."""
    result = {'deep_feature_score': 50.0, 'deep_features_available': False}

    if not TORCH_AVAILABLE:
        return result

    try:
        model, transform = _load_torch_model()
        if model is None or transform is None:
            return result

        # Prepare image
        img_rgb = pil_img.convert('RGB')
        input_tensor = transform(img_rgb).unsqueeze(0)

        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            top_prob = probabilities.max().item()
            top_class = probabilities.argmax().item()
            entropy = -torch.sum(probabilities * torch.log(probabilities + 1e-9)).item()

        result['deep_features_available'] = True

        # Scoring based on prediction confidence and entropy
        score = 50.0
        if top_prob > 0.5:
            score += 20.0  # High confidence = recognizable content = more likely real
        elif top_prob > 0.2:
            score += 10.0

        # Lower entropy = more coherent content
        if entropy < 3.0:
            score += 10.0
        elif entropy > 6.0:
            score -= 5.0

        result['deep_feature_score'] = max(0.0, min(100.0, score))
        result['top_class_confidence'] = round(top_prob * 100, 1)
        result['prediction_entropy'] = round(entropy, 2)

    except Exception as e:
        logger.error(f"Deep feature analysis error: {e}")

    return result


# ─────────────────────────────────────────────
# Scene Description Generator
# ─────────────────────────────────────────────

def generate_scene_description(img_cv, face_data, exif_data, screenshot_data):
    """Generate a human-readable description of the image content."""
    parts = []

    try:
        h, w = img_cv.shape[:2]
        aspect = w / h if h > 0 else 1.0

        # Orientation
        if aspect > 1.3:
            parts.append("landscape-oriented")
        elif aspect < 0.77:
            parts.append("portrait-oriented")
        else:
            parts.append("square-format")

        # Resolution category
        megapixels = (w * h) / 1_000_000
        if megapixels > 8:
            parts.append(f"high-resolution ({w}x{h})")
        elif megapixels > 2:
            parts.append(f"standard-resolution ({w}x{h})")
        else:
            parts.append(f"low-resolution ({w}x{h})")

        # Color characteristics
        if len(img_cv.shape) == 3:
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            mean_brightness = np.mean(hsv[:, :, 2])
            mean_saturation = np.mean(hsv[:, :, 1])

            if mean_brightness > 180:
                parts.append("bright")
            elif mean_brightness < 80:
                parts.append("dark/low-light")

            if mean_saturation > 120:
                parts.append("vibrant/colorful")
            elif mean_saturation < 30:
                parts.append("muted/grayscale")

        # Face info
        fc = face_data.get('face_count', 0)
        if fc == 0:
            parts.append("no human faces detected")
        elif fc == 1:
            parts.append("single person/face detected")
        elif fc <= 5:
            parts.append(f"{fc} faces detected (group)")
        else:
            parts.append(f"{fc} faces detected (crowd)")

        # Screenshot
        if screenshot_data.get('screenshot_likelihood', 0) > 50:
            parts.append("likely a screenshot")

        # Camera
        make = exif_data.get('camera_make', 'Unknown')
        model = exif_data.get('camera_model', 'Unknown')
        if make != 'Unknown' and model != 'Unknown':
            parts.append(f"captured with {make} {model}")
        elif exif_data.get('exif_present', False):
            parts.append("has camera EXIF metadata")
        else:
            parts.append("no camera metadata found")

    except Exception as e:
        logger.error(f"Scene description error: {e}")
        parts.append("image content analysis")

    description = "This is a " + ", ".join(parts) + " image."
    return description


# ─────────────────────────────────────────────
# Generate Analysis Summary
# ─────────────────────────────────────────────

def generate_summary(score, all_metrics):
    """Generate a comprehensive analysis summary."""
    # Classification
    if score >= 100:
        label = "Highly Authentic"
        verdict = "This media shows very strong indicators of being an authentic, unmodified photograph."
    elif score >= 75:
        label = "Likely Real"
        verdict = "This media shows strong indicators of being genuine with natural photographic characteristics."
    elif score >= 40:
        label = "Suspicious"
        verdict = "This media shows mixed signals. Some characteristics are consistent with authentic media, but several anomalies were detected."
    else:
        label = "Likely Fake"
        verdict = "This media shows significant indicators of synthetic generation or heavy manipulation."

    # Build detailed explanation
    explanations = []

    exif_score = all_metrics.get('exif_score', 50)
    if exif_score >= 70:
        explanations.append("Rich EXIF metadata consistent with genuine camera capture.")
    elif exif_score < 40:
        explanations.append("Missing or minimal EXIF metadata, which can indicate synthetic origin or screenshot.")

    ai_artifact = all_metrics.get('ai_artifact_score', 0)
    if ai_artifact > 50:
        explanations.append("Significant AI-generation artifacts detected in frequency and texture analysis.")
    elif ai_artifact > 25:
        explanations.append("Some potential AI artifacts detected, though not conclusive.")
    else:
        explanations.append("No significant AI-generation artifacts found.")

    noise_score = all_metrics.get('noise_score', 50)
    if noise_score >= 70:
        explanations.append("Noise patterns are consistent with natural camera sensor noise.")
    elif noise_score < 40:
        explanations.append("Noise patterns appear unnatural or suspiciously clean.")

    face_count = all_metrics.get('face_count', 0)
    face_quality = all_metrics.get('face_quality_score', 50)
    if face_count > 0:
        if face_quality >= 70:
            explanations.append(f"{face_count} face(s) detected with good quality and natural appearance.")
        elif face_quality < 40:
            explanations.append(f"{face_count} face(s) detected but with low quality or potential anomalies.")
        else:
            explanations.append(f"{face_count} face(s) detected with moderate quality.")
    else:
        explanations.append("No human faces detected. Analysis based on general image characteristics.")

    screenshot_likelihood = all_metrics.get('screenshot_likelihood', 0)
    if screenshot_likelihood > 50:
        explanations.append("Image characteristics suggest this may be a screenshot rather than a direct photograph.")

    explanation_text = " ".join(explanations)

    summary = f"Authenticity Score: {score:.1f}/100 — {label}. {verdict} {explanation_text}"

    return {
        'summary': summary,
        'explanation': explanation_text,
        'classification': label,
        'real_vs_fake': f"{'Likely Real / Authentic' if score >= 75 else ('Suspicious / Inconclusive' if score >= 40 else 'Likely Fake / Synthetic')}",
    }


# ═══════════════════════════════════════════════
# MAIN ANALYSIS FUNCTION
# ═══════════════════════════════════════════════

def analyze_image(file_bytes, filename='unknown'):
    """
    Main image analysis function.
    Takes raw file bytes, returns comprehensive analysis results.
    """
    logger.info(f"Starting image analysis for: {filename}")

    results = {
        'filename': filename,
        'face_count': 0,
        'face_boxes': [],
        'face_detector_used': 'none',
        'face_quality_score': 50.0,
        'exif_present': False,
        'exif_data': {},
        'camera_make': 'Unknown',
        'camera_model': 'Unknown',
        'ai_artifact_score': 0.0,
        'compression_noise_score': 50.0,
        'noise_score': 50.0,
        'edge_score': 50.0,
        'texture_score': 50.0,
        'color_score': 50.0,
        'deep_feature_score': 50.0,
        'screenshot_likelihood': 0.0,
        'synthetic_smoothness_score': 0.0,
        'scene_description': '',
        'analysis_summary': '',
        'description': '',
        'explanation': '',
        'summary': '',
        'real_vs_fake': 'Unknown',
        'authenticity_score': 0.0,
        'classification': 'suspicious',
        'processed_image_bytes': None,
        'image_dimensions': {'width': 0, 'height': 0},
    }

    try:
        # Load image with OpenCV
        img_array = np.frombuffer(file_bytes, dtype=np.uint8)
        img_cv = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img_cv is None:
            logger.error("Failed to decode image")
            results['explanation'] = 'Could not decode the image file.'
            results['summary'] = 'Image analysis failed: unable to decode file.'
            return results

        h, w = img_cv.shape[:2]
        results['image_dimensions'] = {'width': w, 'height': h}

        # Load with PIL for deep features
        pil_img = None
        if PIL_AVAILABLE:
            try:
                pil_img = Image.open(io.BytesIO(file_bytes))
            except Exception:
                pass

        # ── Run all analysis modules ──

        # 1. EXIF Analysis
        exif_results = analyze_exif(file_bytes)
        results.update({k: v for k, v in exif_results.items() if k != 'exif_score'})
        exif_score = exif_results.get('exif_score', 50.0)

        # 2. Face Detection
        face_results = detect_faces(img_cv)
        results.update(face_results)

        # 3. Screenshot Detection
        screenshot_results = detect_screenshot_likelihood(img_cv, pil_img, exif_results)
        results.update(screenshot_results)

        # 4. AI Artifact Detection
        artifact_results = detect_ai_artifacts(img_cv)
        results.update(artifact_results)

        # 5. Compression Analysis
        compression_results = analyze_compression(img_cv)
        results.update(compression_results)

        # 6. Noise Analysis
        noise_results = analyze_noise(img_cv)
        results.update(noise_results)

        # 7. Edge Analysis
        edge_results = analyze_edges(img_cv)
        results.update(edge_results)

        # 8. Texture Analysis
        texture_results = analyze_texture(img_cv)
        results.update(texture_results)

        # 9. Color Analysis
        color_results = analyze_color(img_cv)
        results.update(color_results)

        # 10. Deep Feature Analysis (optional)
        deep_results = analyze_deep_features(pil_img) if pil_img else {'deep_feature_score': 50.0}
        results.update(deep_results)

        # 11. Scene Description
        results['scene_description'] = generate_scene_description(
            img_cv, face_results, exif_results, screenshot_results
        )
        results['description'] = results['scene_description']

        # ── Calculate Final Authenticity Score ──
        weights = {
            'exif': 0.12,
            'face_quality': 0.10,
            'artifact': 0.18,
            'compression': 0.08,
            'noise': 0.14,
            'edge': 0.10,
            'texture': 0.10,
            'color': 0.08,
            'deep': 0.10,
        }

        # Invert artifact score (higher artifacts = lower authenticity)
        artifact_auth = 100.0 - results['ai_artifact_score']
        smoothness_penalty = max(0, results['synthetic_smoothness_score'] - 30) * 0.15

        weighted_score = (
            exif_score * weights['exif'] +
            results['face_quality_score'] * weights['face_quality'] +
            artifact_auth * weights['artifact'] +
            results['compression_noise_score'] * weights['compression'] +
            results['noise_score'] * weights['noise'] +
            results['edge_score'] * weights['edge'] +
            results['texture_score'] * weights['texture'] +
            results['color_score'] * weights['color'] +
            results['deep_feature_score'] * weights['deep']
        )

        # Apply screenshot penalty
        screenshot_penalty = results.get('screenshot_likelihood', 0) * 0.1
        weighted_score -= screenshot_penalty
        weighted_score -= smoothness_penalty

        # Ensure score is in valid range
        final_score = max(0.0, min(100.0, round(weighted_score, 1)))

        # If no faces but good other signals, don't penalize too much
        if results['face_count'] == 0:
            # Recalculate without face weight, redistribute
            non_face_weights = {k: v for k, v in weights.items() if k != 'face_quality'}
            total_w = sum(non_face_weights.values())
            normalized_weights = {k: v / total_w for k, v in non_face_weights.items()}

            recalc_score = (
                exif_score * normalized_weights['exif'] +
                artifact_auth * normalized_weights['artifact'] +
                results['compression_noise_score'] * normalized_weights['compression'] +
                results['noise_score'] * normalized_weights['noise'] +
                results['edge_score'] * normalized_weights['edge'] +
                results['texture_score'] * normalized_weights['texture'] +
                results['color_score'] * normalized_weights['color'] +
                results['deep_feature_score'] * normalized_weights['deep']
            )
            recalc_score -= screenshot_penalty
            recalc_score -= smoothness_penalty
            final_score = max(0.0, min(100.0, round(recalc_score, 1)))

        results['authenticity_score'] = final_score

        # ── Generate Summary ──
        all_metrics = {
            'exif_score': exif_score,
            'ai_artifact_score': results['ai_artifact_score'],
            'noise_score': results['noise_score'],
            'face_count': results['face_count'],
            'face_quality_score': results['face_quality_score'],
            'screenshot_likelihood': results.get('screenshot_likelihood', 0),
        }

        summary_data = generate_summary(final_score, all_metrics)
        results['summary'] = summary_data['summary']
        results['explanation'] = summary_data['explanation']
        results['classification'] = summary_data['classification']
        results['real_vs_fake'] = summary_data['real_vs_fake']
        results['analysis_summary'] = summary_data['summary']

        # ── Draw face boxes on processed image ──
        if results['face_boxes']:
            processed_img = draw_face_boxes(img_cv, results['face_boxes'])
        else:
            processed_img = img_cv.copy()

        # Encode processed image
        success, encoded = cv2.imencode('.jpg', processed_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if success:
            results['processed_image_bytes'] = encoded.tobytes()

        logger.info(f"Image analysis complete: score={final_score}, classification={results['classification']}")

    except Exception as e:
        logger.error(f"Image analysis failed: {e}", exc_info=True)
        results['explanation'] = f'Analysis encountered an error: {str(e)}'
        results['summary'] = 'Image analysis could not be completed due to a processing error.'
        results['authenticity_score'] = 0.0
        results['classification'] = 'likely_fake'
        results['real_vs_fake'] = 'Analysis Error'

    return results