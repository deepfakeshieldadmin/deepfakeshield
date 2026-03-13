import cv2
import numpy as np
from PIL import Image
import exifread
import os
from .utils import get_classification


def analyze_image(image_path):
    """
    Precision-focused heuristic image authenticity analyzer.

    Target behavior:
    - Real camera images with EXIF + natural patterns -> high score
    - AI / synthetic / overprocessed images -> low score
    - Edited / compressed / metadata-removed images -> suspicious range
    """
    result = {
        'authenticity_score': 50.0,
        'classification': 'suspicious',
        'is_ai_generated': False,
        'is_edited': False,
        'face_count': 0,
        'has_exif': False,
        'exif_data': {},
        'details': {},
        'explanation': '',
    }

    try:
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            result['explanation'] = 'Image could not be read.'
            return result

        # Resize for speed and stable processing
        max_dim = 1400
        h, w = img_cv.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img_cv = cv2.resize(img_cv, (int(w * scale), int(h * scale)))

        img_pil = Image.open(image_path)

        # ---- ANALYSIS BLOCKS ----
        exif_info = analyze_exif(image_path)
        noise_info = analyze_noise(img_cv)
        edge_info = analyze_edges(img_cv)
        color_info = analyze_color_distribution(img_cv)
        face_info = analyze_faces(img_cv)
        compression_info = analyze_compression(img_cv, image_path)
        texture_info = analyze_texture(img_cv)
        format_info = analyze_format(img_pil, image_path)

        # Store raw outputs
        result['has_exif'] = exif_info['has_exif']
        result['exif_data'] = exif_info['exif_data']
        result['face_count'] = face_info['face_count']
        result['face_locations'] = face_info['face_locations']

        # ---- SCORING ----
        score = 0
        notes = []

        # 1. EXIF + CAMERA AUTHENTICITY (0–30)
        score += exif_info['score']
        if exif_info['score'] >= 24:
            notes.append("Strong camera metadata found")
        elif exif_info['score'] >= 12:
            notes.append("Partial metadata found")
        else:
            notes.append("Metadata is weak or missing")

        # 2. NOISE NATURALNESS (0–15)
        score += noise_info['score']
        if noise_info['score'] >= 12:
            notes.append("Noise pattern appears natural")
        elif noise_info['score'] <= 5:
            notes.append("Noise pattern appears unnatural")

        # 3. EDGE NATURALNESS (0–15)
        score += edge_info['score']
        if edge_info['score'] >= 12:
            notes.append("Edge structure is realistic")
        elif edge_info['score'] <= 5:
            notes.append("Edge structure is unusual")

        # 4. COLOR DISTRIBUTION (0–10)
        score += color_info['score']
        if color_info['score'] >= 8:
            notes.append("Color distribution is natural")
        elif color_info['score'] <= 4:
            notes.append("Color distribution is suspicious")

        # 5. FACE CONSISTENCY (0–10)
        score += face_info['score']
        if face_info['face_count'] > 0:
            if face_info['score'] >= 8:
                notes.append(f"{face_info['face_count']} face(s) detected with acceptable consistency")
            else:
                notes.append(f"Face analysis suggests possible irregularity")
        else:
            notes.append("No clear faces detected")

        # 6. COMPRESSION / FILE PATTERN (0–10)
        score += compression_info['score']
        if compression_info['score'] >= 8:
            notes.append("Compression pattern appears normal")
        elif compression_info['score'] <= 4:
            notes.append("Compression pattern is suspicious")

        # 7. TEXTURE CONSISTENCY (0–5)
        score += texture_info['score']
        if texture_info['score'] >= 4:
            notes.append("Texture consistency appears natural")
        elif texture_info['score'] <= 2:
            notes.append("Texture inconsistency detected")

        # 8. FORMAT QUALITY (0–5)
        score += format_info['score']

        # ---- HARD PENALTIES FOR SYNTHETIC-LIKE BEHAVIOR ----
        penalties = 0

        # No EXIF + too smooth + weird edges = strong synthetic suspicion
        if not exif_info['has_exif'] and noise_info['variance'] < 35:
            penalties += 12

        if edge_info['edge_density'] < 0.015 or edge_info['edge_density'] > 0.30:
            penalties += 8

        if color_info['entropy'] < 3.4 or color_info['entropy'] > 8.3:
            penalties += 6

        if face_info['face_count'] > 0 and face_info['face_score_flag'] == 'smooth':
            penalties += 10

        if exif_info['editing_software_detected']:
            penalties += 6

        score -= penalties

        # ---- BONUS FOR CLEARLY GENUINE CAMERA IMAGE ----
        bonus = 0
        if exif_info['has_exif'] and exif_info['has_camera']:
            bonus += 6
        if noise_info['variance'] > 100 and noise_info['variance'] < 1800:
            bonus += 4
        if compression_info['bits_per_pixel'] > 1.8 and compression_info['bits_per_pixel'] < 14:
            bonus += 3
        if face_info['face_count'] > 0 and face_info['score'] >= 8:
            bonus += 2

        score += bonus

        final_score = min(max(round(score, 1), 0), 100)

        # ---- CLASSIFICATION ----
        classification = get_classification(final_score)

        result['authenticity_score'] = final_score
        result['classification'] = classification
        result['is_ai_generated'] = final_score < 40
        result['is_edited'] = 40 <= final_score < 75

        # ---- DETAILS ----
        result['details'] = {
            'EXIF Score': exif_info['score'],
            'Noise Score': noise_info['score'],
            'Edge Score': edge_info['score'],
            'Color Score': color_info['score'],
            'Face Score': face_info['score'],
            'Compression Score': compression_info['score'],
            'Texture Score': texture_info['score'],
            'Format Score': format_info['score'],
            'Noise Variance': round(noise_info['variance'], 2),
            'Edge Density': round(edge_info['edge_density'], 4),
            'Color Entropy': round(color_info['entropy'], 2),
            'Bits Per Pixel': round(compression_info['bits_per_pixel'], 2),
            'Penalty Applied': penalties,
            'Bonus Applied': bonus,
        }

        # ---- SHORT EXPLANATION ----
        verdict_map = {
            'authentic': 'Highly authentic image',
            'likely_real': 'Likely real image',
            'suspicious': 'Suspicious or edited image',
            'likely_fake': 'Likely AI-generated or fake image',
        }

        short_notes = notes[:5]
        result['explanation'] = f"{verdict_map.get(classification, 'Analysis completed')}.\n" + " • ".join(short_notes)

    except Exception as e:
        result['explanation'] = f'Image analysis error: {str(e)}'

    return result


# ==========================================================
# EXIF ANALYSIS
# ==========================================================

def analyze_exif(image_path):
    score = 0
    exif_data = {}
    has_exif = False
    has_camera = False
    editing_software_detected = False

    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)

        if tags:
            has_exif = True

            if 'Image Make' in tags:
                exif_data['Camera Make'] = str(tags['Image Make'])
                score += 10
                has_camera = True

            if 'Image Model' in tags:
                exif_data['Camera Model'] = str(tags['Image Model'])
                score += 10
                has_camera = True

            if 'EXIF DateTimeOriginal' in tags:
                exif_data['Date Taken'] = str(tags['EXIF DateTimeOriginal'])
                score += 4
            elif 'Image DateTime' in tags:
                exif_data['Date Modified'] = str(tags['Image DateTime'])
                score += 2

            if 'Image Software' in tags:
                software = str(tags['Image Software'])
                exif_data['Software'] = software
                if any(s in software.lower() for s in ['photoshop', 'gimp', 'lightroom', 'snapseed', 'canva']):
                    editing_software_detected = True
                    score -= 4

    except Exception:
        pass

    return {
        'score': min(max(score, 0), 30),
        'has_exif': has_exif,
        'has_camera': has_camera,
        'editing_software_detected': editing_software_detected,
        'exif_data': exif_data,
    }


# ==========================================================
# NOISE ANALYSIS
# ==========================================================

def analyze_noise(img_cv):
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()

        if 120 < variance < 1800:
            score = 15
        elif 70 < variance <= 120 or 1800 <= variance < 2800:
            score = 11
        elif 35 < variance <= 70:
            score = 6
        else:
            score = 2

        return {
            'score': score,
            'variance': variance,
        }
    except Exception:
        return {
            'score': 7,
            'variance': 0,
        }


# ==========================================================
# EDGE ANALYSIS
# ==========================================================

def analyze_edges(img_cv):
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 80, 180)
        edge_density = np.count_nonzero(edges) / edges.size

        if 0.025 < edge_density < 0.16:
            score = 15
        elif 0.016 < edge_density <= 0.025 or 0.16 <= edge_density < 0.24:
            score = 10
        elif 0.010 < edge_density <= 0.016 or 0.24 <= edge_density < 0.30:
            score = 6
        else:
            score = 2

        return {
            'score': score,
            'edge_density': edge_density,
        }
    except Exception:
        return {
            'score': 7,
            'edge_density': 0,
        }


# ==========================================================
# COLOR ANALYSIS
# ==========================================================

def analyze_color_distribution(img_cv):
    try:
        hist_b = cv2.calcHist([img_cv], [0], None, [256], [0, 256]).flatten()
        hist_g = cv2.calcHist([img_cv], [1], None, [256], [0, 256]).flatten()
        hist_r = cv2.calcHist([img_cv], [2], None, [256], [0, 256]).flatten()

        total_pixels = img_cv.shape[0] * img_cv.shape[1]
        hist_b = hist_b / total_pixels
        hist_g = hist_g / total_pixels
        hist_r = hist_r / total_pixels

        def entropy(hist):
            hist = hist[hist > 0]
            return -np.sum(hist * np.log2(hist))

        avg_entropy = (entropy(hist_b) + entropy(hist_g) + entropy(hist_r)) / 3

        if 4.8 < avg_entropy < 7.2:
            score = 10
        elif 4.0 < avg_entropy <= 4.8 or 7.2 <= avg_entropy < 8.0:
            score = 7
        elif 3.4 < avg_entropy <= 4.0 or 8.0 <= avg_entropy < 8.3:
            score = 4
        else:
            score = 1

        return {
            'score': score,
            'entropy': avg_entropy,
        }
    except Exception:
        return {
            'score': 5,
            'entropy': 0,
        }


# ==========================================================
# FACE ANALYSIS
# ==========================================================

def analyze_faces(img_cv):
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=8,
            minSize=(60, 60)
        )

        filtered = []
        for (x, y, w, h) in faces:
            if w >= 60 and h >= 60:
                filtered.append((x, y, w, h))

        face_locations = []
        smooth_flag = None

        for (x, y, w, h) in filtered:
            face_locations.append({
                'x': int(x),
                'y': int(y),
                'w': int(w),
                'h': int(h),
            })

        face_count = len(filtered)

        if face_count == 0:
            score = 5
        elif face_count <= 4:
            score = 10
        else:
            score = 6

        # inspect smoothness of faces
        for (x, y, w, h) in filtered:
            face_region = gray[y:y+h, x:x+w]
            face_variance = cv2.Laplacian(face_region, cv2.CV_64F).var()
            if face_variance < 18:
                smooth_flag = 'smooth'
                score = max(score - 4, 0)
                break

        return {
            'score': score,
            'face_count': face_count,
            'face_locations': face_locations,
            'face_score_flag': smooth_flag,
        }

    except Exception:
        return {
            'score': 5,
            'face_count': 0,
            'face_locations': [],
            'face_score_flag': None,
        }


# ==========================================================
# COMPRESSION ANALYSIS
# ==========================================================

def analyze_compression(img_cv, image_path):
    try:
        file_size = os.path.getsize(image_path)
        height, width = img_cv.shape[:2]
        total_pixels = height * width
        bits_per_pixel = (file_size * 8) / total_pixels if total_pixels > 0 else 0

        if 2.0 < bits_per_pixel < 12:
            score = 10
        elif 1.2 < bits_per_pixel <= 2.0 or 12 <= bits_per_pixel < 18:
            score = 7
        elif 0.8 < bits_per_pixel <= 1.2 or 18 <= bits_per_pixel < 25:
            score = 4
        else:
            score = 2

        return {
            'score': score,
            'bits_per_pixel': bits_per_pixel,
        }
    except Exception:
        return {
            'score': 5,
            'bits_per_pixel': 0,
        }


# ==========================================================
# TEXTURE ANALYSIS
# ==========================================================

def analyze_texture(img_cv):
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        h2, w2 = h // 2, w // 2

        if h2 < 20 or w2 < 20:
            return {'score': 3}

        regions = [
            gray[:h2, :w2],
            gray[:h2, w2:],
            gray[h2:, :w2],
            gray[h2:, w2:],
        ]

        values = [cv2.Laplacian(region, cv2.CV_64F).var() for region in regions]
        mean_val = np.mean(values)
        std_val = np.std(values)

        if mean_val > 50 and std_val < mean_val * 0.55:
            score = 5
        elif std_val < mean_val:
            score = 3
        else:
            score = 1

        return {'score': score}
    except Exception:
        return {'score': 3}


# ==========================================================
# FORMAT ANALYSIS
# ==========================================================

def analyze_format(img_pil, image_path):
    try:
        width, height = img_pil.size
        ext = os.path.splitext(image_path)[1].lower()

        score = 3
        if ext in ['.jpg', '.jpeg']:
            score += 2
        elif ext == '.png':
            score += 1

        if width < 200 or height < 200:
            score -= 1

        return {
            'score': min(max(score, 0), 5),
            'resolution': f"{width}x{height}",
            'format': ext.upper(),
        }
    except Exception:
        return {
            'score': 3,
            'resolution': 'Unknown',
            'format': 'Unknown',
        }


# ==========================================================
# FACE BOX IMAGE GENERATOR
# ==========================================================

def generate_face_detection_image(image_path, output_path=None):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None, 0, []

        max_dim = 1400
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=8,
            minSize=(60, 60)
        )

        filtered = []
        for (x, y, w, h) in faces:
            if w >= 60 and h >= 60:
                filtered.append((x, y, w, h))

        face_locations = []
        for i, (x, y, w, h) in enumerate(filtered):
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"Face {i + 1}"
            cv2.putText(img, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            face_locations.append({
                'x': int(x),
                'y': int(y),
                'w': int(w),
                'h': int(h),
                'label': label
            })

        cv2.putText(img, f"Faces Detected: {len(filtered)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        if output_path is None:
            dir_name = os.path.dirname(image_path)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(dir_name, f"{base_name}_faces.jpg")

        cv2.imwrite(output_path, img)
        return output_path, len(filtered), face_locations

    except Exception:
        return None, 0, []