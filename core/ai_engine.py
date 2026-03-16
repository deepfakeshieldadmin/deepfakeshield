"""
DeepFake Shield — Image Authenticity Detection Engine v3.0
Professional deepfake and manipulation detection.

PHILOSOPHY: Real = Real, Fake = Fake.
- A real photo MUST score high regardless of EXIF/compression
- An AI-generated face MUST score low
- A morphed/edited face MUST be detected as manipulated
- A photo collage/screenshot of real content = still real

DETECTION METHODS:
1. Error Level Analysis (ELA) — Primary manipulation detector
2. Face Region Forensics — Detects face swaps, morphs, paste operations
3. AI Generation Fingerprints — GAN/Diffusion model artifacts
4. Noise Pattern Forensics — Inconsistent noise = editing detected
5. Edge Coherence Analysis — Splicing leaves edge artifacts
6. Statistical Anomaly Detection — Pixel-level forensics

EXIF/Metadata: Informational only. Does NOT affect score significantly.
Compression: Natural re-saving does NOT make an image fake.
"""

import io
import os
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import exifread
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False


# ══════════════════════════════════════════════════
# 1. ERROR LEVEL ANALYSIS (ELA)
# The gold standard for detecting image editing.
# Authentic images have UNIFORM error levels.
# Edited regions show DIFFERENT error levels.
# ══════════════════════════════════════════════════

def perform_ela_analysis(img_cv):
    """
    Error Level Analysis — the most reliable editing detection method.
    Used by FotoForensics and professional forensic tools.
    
    HOW IT WORKS:
    - Re-save image at known JPEG quality
    - Compare original vs re-saved
    - Unedited images: uniform difference everywhere
    - Edited images: edited regions show DIFFERENT difference levels
    
    IMPORTANT: We measure the VARIANCE of differences across regions,
    NOT the absolute difference level. High absolute difference from
    compression is NORMAL and does NOT indicate editing.
    """
    result = {
        'ela_manipulation_detected': False,
        'ela_confidence': 0.0,
        'ela_description': '',
        'ela_region_variance': 0.0,
    }
    
    try:
        # Re-save at quality 75
        _, encoded = cv2.imencode('.jpg', img_cv, [cv2.IMWRITE_JPEG_QUALITY, 75])
        resaved = cv2.imdecode(np.frombuffer(encoded, np.uint8), cv2.IMREAD_COLOR)
        if resaved is None:
            return result
        
        # Compute absolute difference
        diff = cv2.absdiff(img_cv, resaved)
        if len(diff.shape) == 3:
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        else:
            diff_gray = diff
        
        h, w = diff_gray.shape
        
        # Divide into blocks and measure mean error per block
        block_size = max(24, min(w, h) // 10)
        block_errors = []
        
        for row in range(0, h - block_size, block_size):
            for col in range(0, w - block_size, block_size):
                block = diff_gray[row:row+block_size, col:col+block_size]
                block_errors.append(float(np.mean(block)))
        
        if len(block_errors) < 4:
            result['ela_description'] = 'Image too small for reliable ELA analysis.'
            return result
        
        # THE KEY INSIGHT:
        # It's NOT about how much error there is (compression causes error)
        # It's about whether error is UNIFORM or HAS OUTLIER REGIONS
        
        errors_array = np.array(block_errors)
        overall_mean = np.mean(errors_array)
        overall_std = np.std(errors_array)
        
        # Calculate coefficient of variation
        cv = overall_std / overall_mean if overall_mean > 0 else 0
        
        # Count outlier blocks (blocks that deviate significantly from mean)
        threshold = overall_mean + 2.5 * overall_std
        outlier_count = np.sum(errors_array > threshold)
        outlier_ratio = outlier_count / len(errors_array)
        
        # Also check for blocks with VERY LOW error (pasted uncompressed content)
        low_threshold = max(0.5, overall_mean - 2.0 * overall_std)
        low_outliers = np.sum(errors_array < low_threshold)
        low_outlier_ratio = low_outliers / len(errors_array)
        
        result['ela_region_variance'] = round(cv, 4)
        
        # SCORING LOGIC:
        # High CV + outliers = MANIPULATION
        # Low CV = UNIFORM = AUTHENTIC
        manipulation_score = 0
        
        if cv > 0.8 and outlier_ratio > 0.05:
            manipulation_score = 3
            result['ela_description'] = 'ELA reveals strong regional inconsistency. Certain areas show very different compression artifacts, which is a hallmark of image splicing, face pasting, or Photoshop manipulation. The edited regions compress differently than the original background.'
        elif cv > 0.5 and (outlier_ratio > 0.03 or low_outlier_ratio > 0.08):
            manipulation_score = 2
            result['ela_description'] = 'ELA shows moderate regional differences that may indicate editing. Some areas appear to have been modified or added from a different source.'
        elif cv > 0.35 and outlier_ratio > 0.02:
            manipulation_score = 1
            result['ela_description'] = 'Slight ELA variations detected. Could indicate minor retouching or format conversion.'
        else:
            result['ela_description'] = 'ELA analysis shows uniform compression across the entire image. This is consistent with an authentic, unmodified photograph that has not been spliced or edited.'
        
        result['ela_manipulation_detected'] = manipulation_score >= 2
        result['ela_confidence'] = min(100.0, manipulation_score * 33.0)
        
    except Exception as e:
        logger.error(f"ELA error: {e}")
    
    return result


# ══════════════════════════════════════════════════
# 2. FACE MANIPULATION DETECTION
# Detects face swaps, morphs, and paste operations
# ══════════════════════════════════════════════════

def analyze_face_forensics(img_cv, faces):
    """
    Detect face swaps, morphs, and paste operations.
    STRENGTHENED: Better edge analysis, gradient checks, double compression.
    """
    result = {
        'face_forensics_score': 85.0,
        'face_swap_detected': False,
        'face_paste_detected': False,
        'face_forensics_description': 'No faces to analyze.',
    }
    
    if not faces or not CV2_AVAILABLE:
        return result
    
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
        h, w = gray.shape
        issues = []
        total_suspicion = 0
        
        for face in faces:
            fx, fy, fw, fh = face['x'], face['y'], face['w'], face['h']
            fx, fy = max(0, fx), max(0, fy)
            fw, fh = min(fw, w - fx), min(fh, h - fy)
            if fw < 20 or fh < 20:
                continue
            
            face_region = gray[fy:fy+fh, fx:fx+fw]
            
            # ═══ CHECK 1: Noise mismatch (face vs 8 surrounding regions) ═══
            face_noise = cv2.Laplacian(face_region, cv2.CV_64F).var()
            surround_noises = []
            
            regions = [
                (max(0,fy-fh//2), fy, fx, fx+fw),           # above
                (fy+fh, min(h,fy+fh+fh//2), fx, fx+fw),     # below
                (fy, fy+fh, max(0,fx-fw//2), fx),            # left
                (fy, fy+fh, fx+fw, min(w,fx+fw+fw//2)),      # right
                (max(0,fy-fh//3), fy, max(0,fx-fw//3), fx),  # top-left
                (max(0,fy-fh//3), fy, fx+fw, min(w,fx+fw+fw//3)),  # top-right
                (fy+fh, min(h,fy+fh+fh//3), max(0,fx-fw//3), fx),  # bottom-left
                (fy+fh, min(h,fy+fh+fh//3), fx+fw, min(w,fx+fw+fw//3)),  # bottom-right
            ]
            
            for r in regions:
                y1, y2, x1, x2 = r
                if y2 > y1 and x2 > x1:
                    reg = gray[y1:y2, x1:x2]
                    if reg.size > 100:
                        surround_noises.append(cv2.Laplacian(reg, cv2.CV_64F).var())
            
            if surround_noises:
                avg_surround = np.mean(surround_noises)
                if avg_surround > 0:
                    noise_ratio = face_noise / avg_surround
                    if noise_ratio < 0.2 or noise_ratio > 5.0:
                        total_suspicion += 3
                        result['face_paste_detected'] = True
                        issues.append('STRONG noise mismatch between face and background — face appears pasted from different source.')
                    elif noise_ratio < 0.35 or noise_ratio > 3.0:
                        total_suspicion += 2
                        result['face_paste_detected'] = True
                        issues.append('Noise difference between face and surrounding area indicates possible face manipulation.')
                    elif noise_ratio < 0.5 or noise_ratio > 2.0:
                        total_suspicion += 1
                        issues.append('Slight noise difference detected between face and background.')
            
            # ═══ CHECK 2: Edge gradient analysis around face boundary ═══
            # Morphed/pasted faces have smooth blending or sharp cuts at edges
            border_w = max(4, min(fw, fh) // 10)
            
            edge_diffs = []
            # Check all 4 borders of face rectangle
            # Top border
            if fy >= border_w:
                inner = gray[fy:fy+border_w, fx:fx+fw].astype(float)
                outer = gray[fy-border_w:fy, fx:fx+fw].astype(float)
                if inner.size > 0 and outer.size > 0:
                    edge_diffs.append(abs(np.mean(inner) - np.mean(outer)))
            # Bottom border
            if fy+fh+border_w <= h:
                inner = gray[fy+fh-border_w:fy+fh, fx:fx+fw].astype(float)
                outer = gray[fy+fh:fy+fh+border_w, fx:fx+fw].astype(float)
                if inner.size > 0 and outer.size > 0:
                    edge_diffs.append(abs(np.mean(inner) - np.mean(outer)))
            # Left border
            if fx >= border_w:
                inner = gray[fy:fy+fh, fx:fx+border_w].astype(float)
                outer = gray[fy:fy+fh, fx-border_w:fx].astype(float)
                if inner.size > 0 and outer.size > 0:
                    edge_diffs.append(abs(np.mean(inner) - np.mean(outer)))
            # Right border
            if fx+fw+border_w <= w:
                inner = gray[fy:fy+fh, fx+fw-border_w:fx+fw].astype(float)
                outer = gray[fy:fy+fh, fx+fw:fx+fw+border_w].astype(float)
                if inner.size > 0 and outer.size > 0:
                    edge_diffs.append(abs(np.mean(inner) - np.mean(outer)))
            
            if edge_diffs:
                max_edge_diff = max(edge_diffs)
                avg_edge_diff = np.mean(edge_diffs)
                
                if max_edge_diff > 30 or avg_edge_diff > 20:
                    total_suspicion += 3
                    result['face_paste_detected'] = True
                    issues.append('Sharp intensity transitions at face boundaries — strong indicator of face pasting or morphing.')
                elif max_edge_diff > 18 or avg_edge_diff > 12:
                    total_suspicion += 2
                    issues.append('Notable edge artifacts around face boundary suggest manipulation.')
                elif max_edge_diff > 10:
                    total_suspicion += 1
            
            # ═══ CHECK 3: Color temperature mismatch ═══
            if len(img_cv.shape) == 3:
                face_bgr = img_cv[fy:fy+fh, fx:fx+fw]
                face_b = float(np.mean(face_bgr[:,:,0]))
                face_g = float(np.mean(face_bgr[:,:,1]))
                face_r = float(np.mean(face_bgr[:,:,2]))
                
                bg_colors = []
                bg_regions_coords = [
                    (0, min(40, fy), 0, w),
                    (max(0, h-40), h, 0, w),
                ]
                for by1, by2, bx1, bx2 in bg_regions_coords:
                    if by2 > by1 and bx2 > bx1:
                        bg = img_cv[by1:by2, bx1:bx2]
                        if bg.size > 100:
                            bg_colors.append((float(np.mean(bg[:,:,0])), float(np.mean(bg[:,:,1])), float(np.mean(bg[:,:,2]))))
                
                for bg_b, bg_g, bg_r in bg_colors:
                    warmth_face = face_r - face_b
                    warmth_bg = bg_r - bg_b
                    warmth_diff = abs(warmth_face - warmth_bg)
                    
                    tint_face = face_g - (face_r + face_b) / 2
                    tint_bg = bg_g - (bg_r + bg_b) / 2
                    tint_diff = abs(tint_face - tint_bg)
                    
                    if warmth_diff > 25 or tint_diff > 20:
                        total_suspicion += 2
                        result['face_swap_detected'] = True
                        issues.append('Face color temperature differs from background — face likely sourced from different lighting conditions (morph/swap indicator).')
                    elif warmth_diff > 15 or tint_diff > 12:
                        total_suspicion += 1
                        issues.append('Slight color mismatch between face and background detected.')
            
            # ═══ CHECK 4: Blur inconsistency ═══
            # Pasted faces often have different blur/sharpness than background
            face_laplacian = cv2.Laplacian(face_region, cv2.CV_64F).var()
            
            # Sample background sharpness
            bg_sharpness = []
            for _ in range(5):
                by = np.random.randint(0, max(1, h - fh))
                bx = np.random.randint(0, max(1, w - fw))
                # Skip if overlaps with face
                if by < fy + fh and by + fh > fy and bx < fx + fw and bx + fw > fx:
                    continue
                bg_patch = gray[by:min(h, by+fh), bx:min(w, bx+fw)]
                if bg_patch.size > 100:
                    bg_sharpness.append(cv2.Laplacian(bg_patch, cv2.CV_64F).var())
            
            if bg_sharpness:
                avg_bg_sharp = np.mean(bg_sharpness)
                if avg_bg_sharp > 0:
                    sharp_ratio = face_laplacian / avg_bg_sharp
                    if sharp_ratio < 0.2 or sharp_ratio > 5.0:
                        total_suspicion += 2
                        issues.append('Face sharpness differs significantly from background — possible compositing detected.')
                    elif sharp_ratio < 0.35 or sharp_ratio > 3.0:
                        total_suspicion += 1
            
            # ═══ CHECK 5: Double JPEG compression around face ═══
            # When a face is pasted and saved, the face region gets compressed twice
            face_uint8 = face_region if face_region.dtype == np.uint8 else face_region.astype(np.uint8)
            _, recompressed = cv2.imencode('.jpg', face_uint8, [cv2.IMWRITE_JPEG_QUALITY, 85])
            recomp_face = cv2.imdecode(recompressed, cv2.IMREAD_GRAYSCALE)
            if recomp_face is not None and recomp_face.shape == face_region.shape:
                recomp_diff = np.mean(cv2.absdiff(face_region, recomp_face).astype(float))
                
                # Do same for a background region
                if bg_sharpness:
                    by = np.random.randint(0, max(1, h - fh))
                    bx = np.random.randint(0, max(1, w - fw))
                    bg_patch = gray[by:min(h, by+fh), bx:min(w, bx+fw)]
                    if bg_patch.size > 100:
                        bg_uint8 = bg_patch if bg_patch.dtype == np.uint8 else bg_patch.astype(np.uint8)
                        _, bg_recomp = cv2.imencode('.jpg', bg_uint8, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        bg_recomp_img = cv2.imdecode(bg_recomp, cv2.IMREAD_GRAYSCALE)
                        if bg_recomp_img is not None and bg_recomp_img.shape == bg_patch.shape:
                            bg_recomp_diff = np.mean(cv2.absdiff(bg_patch, bg_recomp_img).astype(float))
                            
                            if bg_recomp_diff > 0:
                                comp_ratio = recomp_diff / bg_recomp_diff
                                if comp_ratio < 0.4 or comp_ratio > 2.5:
                                    total_suspicion += 2
                                    issues.append('Double compression artifacts detected around face region — indicates face was inserted from a separately compressed source.')
        
        # ═══ SCORING ═══
        if total_suspicion >= 8:
            result['face_forensics_score'] = 5.0
        elif total_suspicion >= 6:
            result['face_forensics_score'] = 15.0
        elif total_suspicion >= 4:
            result['face_forensics_score'] = 25.0
        elif total_suspicion >= 3:
            result['face_forensics_score'] = 35.0
        elif total_suspicion >= 2:
            result['face_forensics_score'] = 50.0
        elif total_suspicion >= 1:
            result['face_forensics_score'] = 65.0
        else:
            result['face_forensics_score'] = 88.0
            issues.append('Face analysis shows consistent characteristics with the rest of the image — no manipulation indicators.')
        
        result['face_forensics_description'] = ' '.join(issues) if issues else 'No manipulation detected.'
        
    except Exception as e:
        logger.error(f"Face forensics error: {e}")
    
    return result


# ══════════════════════════════════════════════════
# 3. AI GENERATION DETECTION
# ══════════════════════════════════════════════════

def detect_ai_generated(img_cv):
    """
    Detect if image was generated by AI (GANs, Diffusion models).
    
    AI-generated images have specific fingerprints:
    - Unnaturally smooth skin without pores
    - GAN checkerboard patterns in frequency domain
    - Too-perfect symmetry
    - Unusual color distributions
    - Missing natural sensor noise
    """
    result = {
        'ai_generated_score': 50.0,
        'is_ai_generated': False,
        'ai_description': '',
    }
    
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
        h, w = gray.shape
        
        ai_indicators = 0
        descriptions = []
        
        # === CHECK 1: Natural noise presence ===
        # Real cameras ALWAYS produce sensor noise
        # AI images are often too clean
        noise_estimate = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if noise_estimate < 8.0:
            ai_indicators += 2
            descriptions.append('Image lacks natural camera sensor noise — appears synthetically clean, typical of AI-generated content.')
        elif noise_estimate < 15.0:
            ai_indicators += 1
            descriptions.append('Low noise level may indicate AI generation or heavy post-processing.')
        elif noise_estimate > 50.0:
            # Good natural noise = REAL camera
            ai_indicators -= 1
        
        # === CHECK 2: Frequency domain (GAN fingerprints) ===
        if min(w, h) >= 64:
            cs = min(256, min(w, h))
            cy, cx = h//2, w//2
            crop = gray[cy-cs//2:cy+cs//2, cx-cs//2:cx+cs//2].astype(np.float64)
            
            fft = np.fft.fft2(crop)
            fft_shift = np.fft.fftshift(fft)
            mag = np.log1p(np.abs(fft_shift))
            
            # GAN images show periodic spikes at specific frequencies
            mag_mean = np.mean(mag)
            mag_std = np.std(mag)
            
            if mag_std > 0:
                # Check for spectral peaks (GAN checkerboard)
                normalized = (mag - mag_mean) / mag_std
                extreme_peaks = np.sum(normalized > 5.0)
                peak_ratio = extreme_peaks / mag.size
                
                if peak_ratio > 0.003:
                    ai_indicators += 2
                    descriptions.append('Frequency analysis reveals periodic patterns characteristic of GAN (Generative Adversarial Network) generated images.')
                elif peak_ratio > 0.001:
                    ai_indicators += 1
        
        # === CHECK 3: Texture naturalness ===
        # Real images have varied micro-textures; AI images don't
        patch_size = max(24, min(w, h) // 10)
        texture_stds = []
        
        for _ in range(20):
            py = np.random.randint(0, max(1, h-patch_size))
            px = np.random.randint(0, max(1, w-patch_size))
            patch = gray[py:py+patch_size, px:px+patch_size].astype(float)
            if patch.size > 0:
                # High-frequency content via gradient
                gx = cv2.Sobel(patch.astype(np.uint8), cv2.CV_64F, 1, 0, ksize=3)
                gy = cv2.Sobel(patch.astype(np.uint8), cv2.CV_64F, 0, 1, ksize=3)
                grad_mag = np.sqrt(gx**2 + gy**2)
                texture_stds.append(np.std(grad_mag))
        
        if texture_stds:
            avg_texture = np.mean(texture_stds)
            texture_variation = np.std(texture_stds)
            
            if avg_texture < 5.0 and texture_variation < 3.0:
                ai_indicators += 2
                descriptions.append('Image lacks natural micro-texture variation, consistent with AI-generated content.')
            elif avg_texture < 10.0:
                ai_indicators += 1
        
        # === CHECK 4: Color distribution ===
        if len(img_cv.shape) == 3:
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            sat = hsv[:,:,1]
            val = hsv[:,:,2]
            
            # AI images often have very smooth saturation distribution
            sat_hist = cv2.calcHist([sat], [0], None, [256], [0, 256]).flatten()
            sat_entropy = -np.sum((sat_hist/sat_hist.sum() + 1e-10) * np.log2(sat_hist/sat_hist.sum() + 1e-10))
            
            if sat_entropy < 4.0:
                ai_indicators += 1
                descriptions.append('Color distribution appears unnaturally uniform.')
        
        # === SCORING ===
        if ai_indicators >= 5:
            result['ai_generated_score'] = 10.0
            result['is_ai_generated'] = True
        elif ai_indicators >= 3:
            result['ai_generated_score'] = 25.0
            result['is_ai_generated'] = True
        elif ai_indicators >= 2:
            result['ai_generated_score'] = 45.0
        elif ai_indicators >= 1:
            result['ai_generated_score'] = 60.0
        elif ai_indicators <= -1:
            result['ai_generated_score'] = 90.0  # Strong real indicators
        else:
            result['ai_generated_score'] = 75.0
        
        if descriptions:
            result['ai_description'] = ' '.join(descriptions)
        else:
            result['ai_description'] = 'Image shows natural photographic characteristics including sensor noise, natural textures, and normal frequency distribution. No AI generation indicators detected.'
        
    except Exception as e:
        logger.error(f"AI detection error: {e}")
    
    return result


# ══════════════════════════════════════════════════
# 4. NOISE CONSISTENCY ANALYSIS
# ══════════════════════════════════════════════════

def check_noise_consistency(img_cv):
    """
    Real photos have consistent noise everywhere.
    Edited photos have different noise in edited vs original regions.
    """
    result = {
        'noise_consistent': True,
        'noise_forensics_score': 80.0,
        'noise_description': '',
    }
    
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
        h, w = gray.shape
        
        block_size = max(24, min(w, h) // 8)
        block_noises = []
        
        for row in range(0, h-block_size, block_size):
            for col in range(0, w-block_size, block_size):
                block = gray[row:row+block_size, col:col+block_size]
                noise = cv2.Laplacian(block, cv2.CV_64F).var()
                block_noises.append(noise)
        
        if len(block_noises) < 4:
            return result
        
        noises = np.array(block_noises)
        noise_mean = np.mean(noises)
        noise_std = np.std(noises)
        noise_cv = noise_std / noise_mean if noise_mean > 0 else 0
        
        # Check for outlier blocks
        if noise_mean > 0:
            z_scores = np.abs((noises - noise_mean) / (noise_std + 1e-6))
            outlier_count = np.sum(z_scores > 2.5)
            outlier_ratio = outlier_count / len(noises)
        else:
            outlier_ratio = 0
        
        if noise_cv > 1.2 and outlier_ratio > 0.08:
            result['noise_consistent'] = False
            result['noise_forensics_score'] = 20.0
            result['noise_description'] = 'Strong noise inconsistency detected. Different regions of the image have very different noise levels, which is a clear indicator of splicing or compositing from multiple sources.'
        elif noise_cv > 0.8 and outlier_ratio > 0.05:
            result['noise_consistent'] = False
            result['noise_forensics_score'] = 40.0
            result['noise_description'] = 'Moderate noise inconsistency found. Some regions appear to have been modified or sourced differently.'
        elif noise_cv > 0.5:
            result['noise_forensics_score'] = 60.0
            result['noise_description'] = 'Slight noise variation detected. This could be due to different textures in the scene or minor editing.'
        else:
            result['noise_forensics_score'] = 88.0
            result['noise_description'] = 'Noise distribution is uniform across the image, consistent with a single-capture authentic photograph.'
        
    except Exception as e:
        logger.error(f"Noise consistency error: {e}")
    
    return result


# ══════════════════════════════════════════════════
# 5. FACE DETECTION
# ══════════════════════════════════════════════════

def detect_faces(img_cv):
    results = {'face_count': 0, 'face_boxes': [], 'face_detector_used': 'none'}
    if not CV2_AVAILABLE:
        return results
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv
        h, w = gray.shape
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        if not os.path.exists(cascade_path):
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            return results
        cascade = cv2.CascadeClassifier(cascade_path)
        if cascade.empty():
            return results
        min_size = max(30, min(w, h) // 10)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=6, minSize=(min_size, min_size))
        all_faces = []
        for (x, y, fw, fh) in faces:
            if fw/fh < 0.6 or fw/fh > 1.6: continue
            if (fw*fh)/(w*h) < 0.001: continue
            region = gray[y:y+fh, x:x+fw]
            if region.size > 0 and np.std(region.astype(float)) < 12: continue
            all_faces.append({'x':int(x),'y':int(y),'w':int(fw),'h':int(fh),'detector':'frontal'})
        if len(all_faces) > 1:
            all_faces = _dedup_faces(all_faces)
        results['face_count'] = len(all_faces)
        results['face_boxes'] = all_faces
        results['face_detector_used'] = 'haar_alt2' if all_faces else 'none'
    except Exception as e:
        logger.error(f"Face detection error: {e}")
    return results

def _dedup_faces(faces, iou_th=0.3):
    if len(faces) <= 1: return faces
    keep = [True]*len(faces)
    for i in range(len(faces)):
        if not keep[i]: continue
        for j in range(i+1, len(faces)):
            if not keep[j]: continue
            a,b = faces[i],faces[j]
            ix1,iy1 = max(a['x'],b['x']),max(a['y'],b['y'])
            ix2,iy2 = min(a['x']+a['w'],b['x']+b['w']),min(a['y']+a['h'],b['y']+b['h'])
            if ix2>ix1 and iy2>iy1:
                inter=(ix2-ix1)*(iy2-iy1)
                union=a['w']*a['h']+b['w']*b['h']-inter
                if union>0 and inter/union>iou_th:
                    if a['w']*a['h']>=b['w']*b['h']: keep[j]=False
                    else: keep[i]=False; break
    return [f for f,k in zip(faces,keep) if k]

def draw_face_boxes(img_cv, face_boxes):
    output = img_cv.copy()
    for f in face_boxes:
        cv2.rectangle(output,(f['x'],f['y']),(f['x']+f['w'],f['y']+f['h']),(0,255,0),3)
        cv2.putText(output,'Face',(f['x'],f['y']-10),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)
    return output


# ══════════════════════════════════════════════════
# 6. EXIF (Informational only — minimal score impact)
# ══════════════════════════════════════════════════

def get_exif_info(file_bytes):
    info = {'exif_present':False,'exif_data':{},'camera_make':'Unknown','camera_model':'Unknown','software':'Unknown'}
    if not EXIF_AVAILABLE: return info
    try:
        tags = exifread.process_file(io.BytesIO(file_bytes), details=False)
        if tags:
            info['exif_present'] = True
            for k,v in tags.items():
                try: info['exif_data'][str(k)] = str(v)
                except: pass
            info['camera_make'] = info['exif_data'].get('Image Make','Unknown').strip() or 'Unknown'
            info['camera_model'] = info['exif_data'].get('Image Model','Unknown').strip() or 'Unknown'
            info['software'] = info['exif_data'].get('Image Software','Unknown').strip() or 'Unknown'
    except: pass
    return info


# ══════════════════════════════════════════════════
# MAIN ANALYSIS FUNCTION
# ══════════════════════════════════════════════════

def analyze_image(file_bytes, filename='unknown'):
    """
    MAIN ANALYSIS — Professional deepfake detection.
    
    Score weights:
    - ELA (editing detection): 30%
    - AI generation detection: 30%
    - Noise consistency: 20%
    - Face forensics: 15% (if faces present)
    - General quality: 5%
    """
    logger.info(f"Analyzing: {filename}")
    
    results = {
        'filename': filename,
        'face_count':0, 'face_boxes':[], 'face_detector_used':'none',
        'exif_present':False, 'exif_data':{}, 'camera_make':'Unknown', 'camera_model':'Unknown',
        'ela_manipulation_detected':False, 'ela_confidence':0.0,
        'ai_generated_score':50.0, 'is_ai_generated':False,
        'noise_consistent':True, 'noise_forensics_score':80.0,
        'face_forensics_score':85.0, 'face_swap_detected':False, 'face_paste_detected':False,
        'authenticity_score':0.0, 'classification':'suspicious',
        'real_vs_fake':'Unknown', 'explanation':'', 'summary':'', 'description':'',
        'scene_description':'', 'processed_image_bytes':None,
        'image_dimensions':{'width':0,'height':0},
    }
    
    try:
        img_array = np.frombuffer(file_bytes, dtype=np.uint8)
        img_cv = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img_cv is None:
            results['explanation'] = 'Could not decode image.'
            return results
        
        h, w = img_cv.shape[:2]
        results['image_dimensions'] = {'width':w, 'height':h}
        
        # Run all detection modules
        exif_info = get_exif_info(file_bytes)
        results.update(exif_info)
        
        face_data = detect_faces(img_cv)
        results.update(face_data)
        
        ela_data = perform_ela_analysis(img_cv)
        results.update(ela_data)
        
        ai_data = detect_ai_generated(img_cv)
        results.update(ai_data)
        
        noise_data = check_noise_consistency(img_cv)
        results.update(noise_data)
        
        face_forensics = {'face_forensics_score': 85.0, 'face_forensics_description': 'No faces to analyze.'}
        if results['face_count'] > 0:
            face_forensics = analyze_face_forensics(img_cv, results['face_boxes'])
            results.update(face_forensics)
        
        # ══════════════════════════════════════
        # FINAL SCORE CALCULATION
        # ══════════════════════════════════════
        
        # Convert ELA to authenticity score
        # ela_manipulation_detected=True means LOWER authenticity
        if ela_data.get('ela_manipulation_detected'):
            ela_auth = max(15.0, 50.0 - ela_data.get('ela_confidence', 0) * 0.5)
        else:
            ela_auth = min(90.0, 70.0 + (1.0 - ela_data.get('ela_region_variance', 0)) * 30)
        
        ai_auth = ai_data.get('ai_generated_score', 50.0)
        noise_auth = noise_data.get('noise_forensics_score', 80.0)
        face_auth = face_forensics.get('face_forensics_score', 85.0)
        
        if results['face_count'] > 0:
            final = (
                ela_auth * 0.30 +
                ai_auth * 0.25 +
                noise_auth * 0.20 +
                face_auth * 0.20 +
                65.0 * 0.05  # general baseline
            )
        else:
            final = (
                ela_auth * 0.35 +
                ai_auth * 0.35 +
                noise_auth * 0.25 +
                65.0 * 0.05
            )
        
        # Boost: if all modules agree it's real, boost score
        if ela_auth > 70 and ai_auth > 70 and noise_auth > 70 and face_auth > 70:
            final = max(final, 78.0)
        
        # Penalty: if any module strongly says fake, cap the score
        if ela_data.get('ela_manipulation_detected') and ela_data.get('ela_confidence', 0) > 60:
            final = min(final, 40.0)
        if ai_data.get('is_ai_generated') and ai_auth < 30:
            final = min(final, 35.0)
        if face_forensics.get('face_swap_detected') or face_forensics.get('face_paste_detected'):
            final = min(final, 38.0)
        
        final = max(0.0, min(100.0, round(final, 1)))
        results['authenticity_score'] = final
        
        # Classification
        # Classification
        if final >= 90:
            results['classification'] = 'highly_authentic'
            results['real_vs_fake'] = 'Authentic — No manipulation detected'
        elif final >= 70:
            results['classification'] = 'likely_real'
            results['real_vs_fake'] = 'Likely Real — No manipulation found'
        elif final >= 40:
            results['classification'] = 'suspicious'
            results['real_vs_fake'] = 'Suspicious — Possible manipulation'
        else:
            if ai_data.get('is_ai_generated'):
                results['classification'] = 'ai_generated'
                results['real_vs_fake'] = 'AI Generated Image Detected'
            elif face_forensics.get('face_swap_detected') or face_forensics.get('face_paste_detected'):
                results['classification'] = 'deepfake'
                results['real_vs_fake'] = 'DeepFake / Face Manipulation'
            elif ela_data.get('ela_manipulation_detected'):
                results['classification'] = 'edited'
                results['real_vs_fake'] = 'Edited / Manipulated Image'
            else:
                results['classification'] = 'likely_fake'
                results['real_vs_fake'] = 'Likely Fake / Manipulated'
        
        # Safety: truncate to fit database
        results['real_vs_fake'] = results['real_vs_fake'][:250]
        results['classification'] = results['classification'][:95]
        results['explanation'] = results['explanation'][:5000]
        results['summary'] = results['summary'][:5000]
        results['description'] = results['description'][:5000]
        
        # Build explanation
        explanations = []
        if ela_data.get('ela_description'):
            explanations.append(ela_data['ela_description'])
        if ai_data.get('ai_description'):
            explanations.append(ai_data['ai_description'])
        if noise_data.get('noise_description'):
            explanations.append(noise_data['noise_description'])
        if results['face_count'] > 0 and face_forensics.get('face_forensics_description'):
            explanations.append(face_forensics['face_forensics_description'])
        
        results['explanation'] = ' '.join(explanations)
        
        # Description
        desc_parts = [f"{'Landscape' if w>h else 'Portrait'} ({w}x{h})"]
        if results['face_count'] > 0:
            desc_parts.append(f"{results['face_count']} face(s)")
        if results['camera_make'] != 'Unknown':
            desc_parts.append(f"Camera: {results['camera_make']} {results['camera_model']}")
        results['description'] = ', '.join(desc_parts)
        results['scene_description'] = results['description']
        
        results['summary'] = f"Score: {final}/100 — {results['classification']}. {results['explanation'][:200]}"
        
        # Processed image
        if results['face_boxes']:
            proc = draw_face_boxes(img_cv, results['face_boxes'])
        else:
            proc = img_cv.copy()
        ok, enc = cv2.imencode('.jpg', proc, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if ok:
            results['processed_image_bytes'] = enc.tobytes()
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        results['explanation'] = f'Error: {str(e)}'
    
    return results