import os
import cv2
import numpy as np
from PIL import Image

try:
    import exifread
except ImportError:
    exifread = None

try:
    import torch
    import torchvision.transforms as transforms
    from torchvision import models
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False

_DEEP_MODEL = None


def _get_deep_model():
    global _DEEP_MODEL
    if not TORCH_AVAILABLE:
        return None
    if _DEEP_MODEL is None:
        try:
            model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            model.eval()
            _DEEP_MODEL = model
        except Exception:
            _DEEP_MODEL = None
    return _DEEP_MODEL


def analyze_image(file_path):
    results = {
        "exif_present": False,
        "exif_data": {},
        "camera_make": "",
        "camera_model": "",
        "face_count": 0,
        "face_boxes": [],
        "face_detector_used": "Balanced Multi-Pass Haar",
        "face_quality_score": 0,
        "ai_artifact_score": 0,
        "compression_noise_score": 0,
        "noise_score": 0,
        "edge_score": 0,
        "texture_score": 0,
        "color_score": 0,
        "deep_feature_score": 0,
        "screenshot_likelihood": 0,
        "synthetic_smoothness_score": 0,
        "compression_label": "Normal",
        "artifact_label": "Low",
        "image_width": 0,
        "image_height": 0,
        "file_format": "",
        "description": "",
        "analysis_summary": "",
        "real_vs_fake": "Uncertain",
        "scene_description": "",
    }

    try:
        img_cv = cv2.imread(file_path)
        if img_cv is None:
            results["description"] = "Failed to load image file."
            return results, 0

        h, w = img_cv.shape[:2]
        results["image_width"] = w
        results["image_height"] = h
        _, ext = os.path.splitext(file_path)
        results["file_format"] = ext.upper().replace(".", "")

        exif_score = _analyze_exif(file_path, results)
        face_score = _detect_faces_balanced(img_cv, results)
        face_quality_score = _analyze_face_regions(img_cv, results)
        results["face_quality_score"] = round(face_quality_score, 2)

        artifact_score = _detect_ai_artifacts(img_cv, results)
        compression_score = _analyze_compression_blocks(img_cv, results)
        noise_score = _analyze_natural_noise(img_cv, results)
        edge_score = _analyze_edge_consistency(img_cv, results)
        texture_score = _analyze_texture_realism(img_cv, results)
        color_score = _analyze_color_realism(img_cv, results)
        screenshot_penalty = _detect_screenshot_like_properties(img_cv, results)
        smoothness_penalty = _detect_synthetic_smoothness(img_cv, results)
        deep_feature_score = _analyze_deep_visual_features(file_path)
        results["deep_feature_score"] = round(deep_feature_score, 2)

        has_faces = results["face_count"] > 0

        if has_faces:
            base_score = (
                exif_score * 0.18 +
                face_score * 0.10 +
                face_quality_score * 0.08 +
                (100 - artifact_score) * 0.14 +
                (100 - compression_score) * 0.08 +
                noise_score * 0.10 +
                edge_score * 0.08 +
                texture_score * 0.08 +
                color_score * 0.07 +
                deep_feature_score * 0.09
            )
        else:
            base_score = (
                exif_score * 0.23 +
                (100 - artifact_score) * 0.16 +
                (100 - compression_score) * 0.10 +
                noise_score * 0.11 +
                edge_score * 0.10 +
                texture_score * 0.09 +
                color_score * 0.08 +
                deep_feature_score * 0.13
            )

        base_score -= screenshot_penalty * 0.10
        base_score -= smoothness_penalty * 0.12

        if (
            results["exif_present"]
            and results["camera_make"]
            and results["camera_model"]
            and artifact_score < 15
            and compression_score < 18
            and noise_score > 72
        ):
            base_score += 10

        if (
            not results["exif_present"]
            and artifact_score > 45
            and smoothness_penalty > 22
            and deep_feature_score < 45
        ):
            base_score -= 10

        final_score = int(round(max(0, min(100, base_score))))

        if final_score >= 75:
            results["real_vs_fake"] = "Real"
        elif final_score <= 39:
            results["real_vs_fake"] = "Fake"
        else:
            results["real_vs_fake"] = "Uncertain"

        results["scene_description"] = _generate_scene_description(results)
        results["analysis_summary"] = _generate_summary(final_score)
        results["description"] = _generate_full_description(results, final_score)

        return results, final_score

    except Exception as e:
        results["description"] = f"Error during image analysis: {str(e)}"
        results["analysis_summary"] = "The analysis process could not complete successfully."
        return results, 0


def _analyze_exif(file_path, results):
    score = 0
    try:
        if exifread:
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f, details=False)

            if tags:
                results["exif_present"] = True
                score += 45

                important_tags = [
                    "Image Make", "Image Model", "EXIF DateTimeOriginal",
                    "EXIF DateTimeDigitized", "Image Software",
                    "EXIF ISOSpeedRatings", "EXIF FocalLength",
                    "EXIF ExposureTime", "EXIF FNumber",
                    "GPS GPSLatitude", "GPS GPSLongitude",
                    "Image Orientation", "EXIF Flash",
                ]

                exif_data = {}
                for tag in important_tags:
                    if tag in tags:
                        clean = tag.replace("Image ", "").replace("EXIF ", "").replace("GPS ", "")
                        exif_data[clean] = str(tags[tag])

                results["exif_data"] = exif_data

                if "Image Make" in tags:
                    results["camera_make"] = str(tags["Image Make"]).strip()
                    score += 18
                if "Image Model" in tags:
                    results["camera_model"] = str(tags["Image Model"]).strip()
                    score += 15
                if "EXIF DateTimeOriginal" in tags:
                    score += 10
                if "GPS GPSLatitude" in tags or "GPS GPSLongitude" in tags:
                    score += 5
    except Exception:
        pass

    try:
        img = Image.open(file_path)
        exif = img.getexif()
        if exif and not results["exif_present"]:
            results["exif_present"] = True
            score += 30
            if 271 in exif:
                results["camera_make"] = str(exif[271])
                score += 15
            if 272 in exif:
                results["camera_model"] = str(exif[272])
                score += 10
    except Exception:
        pass

    return min(100, score)


def _detect_faces_balanced(img_cv, results):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    img_h, img_w = gray.shape
    min_face = max(34, int(min(img_w, img_h) * 0.045))

    frontal = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    profile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")

    boxes = []

    passes = [
        (1.18, 6),
        (1.14, 5),
        (1.10, 4),
    ]

    for scale_factor, min_neighbors in passes:
        try:
            found = frontal.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=(min_face, min_face),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )
            for b in found:
                boxes.append(b)
        except Exception:
            pass

    try:
        p1 = profile.detectMultiScale(
            gray,
            scaleFactor=1.15,
            minNeighbors=4,
            minSize=(min_face, min_face),
        )
        for b in p1:
            boxes.append(b)
    except Exception:
        pass

    try:
        flip = cv2.flip(gray, 1)
        p2 = profile.detectMultiScale(
            flip,
            scaleFactor=1.15,
            minNeighbors=4,
            minSize=(min_face, min_face),
        )
        for (x, y, fw, fh) in p2:
            boxes.append([img_w - x - fw, y, fw, fh])
    except Exception:
        pass

    boxes = _non_max_suppression(boxes, threshold=0.22)

    validated = []
    for box in boxes:
        x, y, w, h = [int(v) for v in box]

        if w < min_face or h < min_face:
            continue

        aspect = w / max(h, 1)
        if not (0.58 <= aspect <= 1.38):
            continue

        area_ratio = (w * h) / float(img_w * img_h)
        if area_ratio < 0.012:
            continue

        border_margin = 6
        if (x <= border_margin or y <= border_margin or x + w >= img_w - border_margin or y + h >= img_h - border_margin):
            if area_ratio < 0.022:
                continue

        roi = gray[y:y+h, x:x+w]
        if roi.size == 0:
            continue

        lap_var = cv2.Laplacian(roi, cv2.CV_64F).var()
        if lap_var < 8:
            continue

        mean_intensity = np.mean(roi)
        if mean_intensity < 18 or mean_intensity > 245:
            continue

        blur = cv2.GaussianBlur(roi, (3, 3), 0)
        diff = cv2.absdiff(roi, blur)
        texture_energy = np.mean(diff)
        if texture_energy < 0.9:
            continue

        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / max(edges.size, 1)
        if edge_density < 0.010:
            continue

        upper_half = roi[:roi.shape[0] // 2, :]
        lower_half = roi[roi.shape[0] // 2:, :]
        if upper_half.size == 0 or lower_half.size == 0:
            continue

        upper_edges = cv2.Canny(upper_half, 50, 150)
        lower_edges = cv2.Canny(lower_half, 50, 150)
        upper_density = np.sum(upper_edges > 0) / max(upper_edges.size, 1)
        lower_density = np.sum(lower_edges > 0) / max(lower_edges.size, 1)

        if upper_density < 0.009:
            continue

        if lower_density > upper_density * 2.8 and area_ratio < 0.05:
            continue

        cx1 = roi.shape[1] // 4
        cx2 = 3 * roi.shape[1] // 4
        center_band = roi[:, cx1:cx2]
        if center_band.size == 0:
            continue
        center_edges = cv2.Canny(center_band, 50, 150)
        center_density = np.sum(center_edges > 0) / max(center_edges.size, 1)
        if center_density < 0.010:
            continue

        center_y = y + h / 2
        if center_y > img_h * 0.74 and area_ratio < 0.035:
            if texture_energy < 2.5:
                continue

        validated.append([x, y, w, h])

    results["face_boxes"] = validated
    results["face_count"] = len(validated)

    if len(validated) > 0:
        return min(100, 58 + len(validated) * 6)
    return 50


def _non_max_suppression(boxes, threshold=0.22):
    if not boxes:
        return []

    boxes = np.array(boxes, dtype=np.float32)
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 0] + boxes[:, 2]
    y2 = boxes[:, 1] + boxes[:, 3]
    areas = boxes[:, 2] * boxes[:, 3]

    order = np.argsort(areas)[::-1]
    keep = []

    while order.size > 0:
        i = order[0]
        keep.append(i)

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        inter = w * h

        union = areas[i] + areas[order[1:]] - inter
        iou = inter / np.maximum(union, 1e-6)

        inds = np.where(iou <= threshold)[0]
        order = order[inds + 1]

    return boxes[keep].astype(int).tolist()


def _analyze_face_regions(img_cv, results):
    boxes = results.get("face_boxes", [])
    if not boxes:
        return 50

    region_scores = []
    for (x, y, w, h) in boxes:
        try:
            roi = img_cv[y:y+h, x:x+w]
            if roi.size == 0:
                continue

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur = cv2.GaussianBlur(gray, (3, 3), 0)
            diff = cv2.absdiff(gray, blur)
            texture_energy = np.mean(diff)

            score = 50
            if lap_var > 90:
                score += 15
            elif lap_var < 20:
                score -= 6

            if 3 < texture_energy < 22:
                score += 12
            elif texture_energy < 1.8:
                score -= 6

            region_scores.append(max(0, min(100, score)))
        except Exception:
            continue

    if not region_scores:
        return 50
    return float(np.mean(region_scores))


def _detect_ai_artifacts(img_cv, results):
    score = 0
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    try:
        size = min(gray.shape[0], gray.shape[1], 256)
        crop = gray[:size, :size].astype(np.float32)
        dct = cv2.dct(crop)
        dct_abs = np.abs(dct)

        half = size // 2
        low = np.mean(dct_abs[:half, :half])
        high = np.mean(dct_abs[half:, half:])

        if low > 0:
            ratio = high / low
            if ratio < 0.008:
                score += 35
            elif ratio < 0.03:
                score += 18
    except Exception:
        pass

    try:
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if lap_var < 40:
            score += 18
        elif lap_var < 90:
            score += 7
    except Exception:
        pass

    try:
        small = cv2.resize(gray, (128, 128))
        fft = np.fft.fft2(small)
        fft_shift = np.fft.fftshift(fft)
        mag = np.log1p(np.abs(fft_shift))
        center = mag[50:78, 50:78]
        corners = np.concatenate([mag[:20, :20].flatten(), mag[-20:, -20:].flatten()])
        if np.mean(corners) > 0 and np.mean(center) / np.mean(corners) > 5.2:
            score += 12
    except Exception:
        pass

    results["ai_artifact_score"] = min(100, score)

    if score > 55:
        results["artifact_label"] = "High — Synthetic Traits"
    elif score > 28:
        results["artifact_label"] = "Moderate — Suspicious"
    else:
        results["artifact_label"] = "Low — Natural Looking"

    return min(100, score)


def _analyze_compression_blocks(img_cv, results):
    score = 0
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    try:
        diffs = []
        for y in range(8, min(h - 8, 256), 8):
            for x in range(8, min(w - 8, 256), 8):
                boundary = abs(int(gray[y, x]) - int(gray[y - 1, x]))
                inside = abs(int(gray[y + 1, x]) - int(gray[y + 2, x]))
                if inside > 0:
                    diffs.append(boundary / inside)

        if diffs:
            avg = np.mean(diffs)
            if avg > 2.0:
                score += 42
            elif avg > 1.5:
                score += 24
            elif avg > 1.2:
                score += 10
    except Exception:
        pass

    results["compression_noise_score"] = min(100, score)

    if score > 40:
        results["compression_label"] = "Heavy"
    elif score > 20:
        results["compression_label"] = "Moderate"
    else:
        results["compression_label"] = "Normal"

    return min(100, score)


def _analyze_natural_noise(img_cv, results):
    score = 50
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY).astype(np.float64)

    try:
        kernel = np.ones((5, 5), np.float64) / 25
        local_mean = cv2.filter2D(gray, -1, kernel)
        local_var = cv2.filter2D((gray - local_mean) ** 2, -1, kernel)
        noise_var = np.mean(local_var)

        if 5 < noise_var < 500:
            score = 68 + min(noise_var / 25, 24)
        elif noise_var <= 5:
            score = 20
        else:
            score = 40

        if len(img_cv.shape) == 3:
            b, g, r = cv2.split(img_cv)
            stds = [np.std(ch.astype(np.float64)) for ch in [b, g, r]]
            if np.std(stds) < 1:
                score -= 8
            else:
                score += 5
    except Exception:
        pass

    results["noise_score"] = round(max(0, min(100, score)), 2)
    return max(0, min(100, score))


def _analyze_edge_consistency(img_cv, results):
    score = 50
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        density = np.sum(edges > 0) / edges.size

        if 0.02 < density < 0.20:
            score = 70
        elif density < 0.01:
            score = 28
        elif density > 0.25:
            score = 38
    except Exception:
        pass

    results["edge_score"] = round(score, 2)
    return max(0, min(100, score))


def _analyze_texture_realism(img_cv, results):
    score = 50
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        diff = cv2.absdiff(gray, blur)
        texture_energy = np.mean(diff)

        if 4 < texture_energy < 18:
            score = 72
        elif texture_energy <= 3:
            score = 26
        elif texture_energy > 25:
            score = 42
    except Exception:
        pass

    results["texture_score"] = round(score, 2)
    return max(0, min(100, score))


def _analyze_color_realism(img_cv, results):
    score = 50
    try:
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        sat_std = np.std(hsv[:, :, 1])
        val_std = np.std(hsv[:, :, 2])

        if sat_std > 28:
            score += 10
        elif sat_std < 10:
            score -= 10

        if val_std > 35:
            score += 8
        elif val_std < 14:
            score -= 8

        small = cv2.resize(img_cv, (64, 64))
        uniq = len(np.unique(small.reshape(-1, 3), axis=0))
        if uniq > 1800:
            score += 8
        elif uniq < 500:
            score -= 8
    except Exception:
        pass

    results["color_score"] = round(max(0, min(100, score)), 2)
    return max(0, min(100, score))


def _detect_screenshot_like_properties(img_cv, results):
    penalty = 0
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 80, 160)

        vertical = np.sum(edges[:, ::20] > 0)
        horizontal = np.sum(edges[::20, :] > 0)
        line_density = (vertical + horizontal) / max(edges.size, 1)

        if line_density > 0.01:
            penalty += 15

        if results.get("noise_score", 50) < 30:
            penalty += 12

        if not results.get("exif_present"):
            penalty += 10
    except Exception:
        pass

    results["screenshot_likelihood"] = min(100, penalty)
    return min(100, penalty)


def _detect_synthetic_smoothness(img_cv, results):
    penalty = 0
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        residual = cv2.absdiff(gray, blur)
        mean_residual = np.mean(residual)

        if mean_residual < 2.8:
            penalty += 35
        elif mean_residual < 4.5:
            penalty += 18
    except Exception:
        pass

    results["synthetic_smoothness_score"] = min(100, penalty)
    return min(100, penalty)


def _analyze_deep_visual_features(file_path):
    if not TORCH_AVAILABLE:
        return 50

    model = _get_deep_model()
    if model is None:
        return 50

    try:
        img = Image.open(file_path).convert("RGB")
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        tensor = transform(img).unsqueeze(0)

        with torch.no_grad():
            logits = model(tensor)
            probs = torch.nn.functional.softmax(logits, dim=1).cpu().numpy()[0]

        top1 = float(np.max(probs))
        entropy = -np.sum(probs * np.log(probs + 1e-9))

        score = 50
        if top1 > 0.50:
            score += 20
        elif top1 > 0.25:
            score += 10
        elif top1 < 0.08:
            score -= 10

        if entropy < 4.5:
            score += 15
        elif entropy > 5.5:
            score -= 12

        return max(0, min(100, score))
    except Exception:
        return 50


def _generate_scene_description(results):
    face_count = results.get("face_count", 0)
    width = results.get("image_width", 0)
    height = results.get("image_height", 0)
    has_exif = results.get("exif_present", False)
    make = results.get("camera_make", "")
    model = results.get("camera_model", "")

    if face_count > 0:
        if face_count == 1:
            scene = "The image appears to contain a single visible person."
        elif face_count <= 4:
            scene = f"The image appears to contain approximately {face_count} visible people."
        else:
            scene = f"The image appears to contain multiple people (approximately {face_count})."
    else:
        scene = "No human faces were detected, so the image may represent a landscape, object, building, screenshot, document, or artwork."

    scene += f" Resolution is {width}×{height}."
    if has_exif and (make or model):
        scene += f" Metadata suggests capture from {make} {model}."
    elif has_exif:
        scene += " Metadata is present, suggesting camera-origin content."
    else:
        scene += " No reliable camera metadata was detected."

    return scene


def _generate_summary(score):
    if score >= 90:
        return "Highly authentic image with strong camera-origin evidence and very low synthetic indicators."
    elif score >= 75:
        return "Likely real image with mostly natural visual characteristics."
    elif score >= 40:
        return "Suspicious image with mixed authenticity signals."
    return "Likely fake or AI-generated image due to multiple synthetic indicators."


def _generate_full_description(results, score):
    parts = []
    parts.append(results.get("scene_description", "Scene details unavailable."))
    parts.append(f"Authenticity score calculated: {score}/100.")

    if results["exif_present"]:
        parts.append("EXIF metadata is present, supporting possible real-camera origin.")
    else:
        parts.append("EXIF metadata is missing, which may indicate screenshot origin, metadata stripping, or synthetic generation.")

    if results.get("camera_make") or results.get("camera_model"):
        parts.append(f"Detected source device: {results.get('camera_make', '')} {results.get('camera_model', '')}.")

    parts.append(f"Face detection found {results.get('face_count', 0)} face(s) using {results.get('face_detector_used', 'Unknown')}.")
    parts.append(f"Artifact analysis result: {results.get('artifact_label', 'Unknown')}.")
    parts.append(f"Compression analysis result: {results.get('compression_label', 'Unknown')}.")
    parts.append(f"Deep visual realism score: {results.get('deep_feature_score', 0)}.")
    parts.append(f"Real/Fake interpretation: {results.get('real_vs_fake', 'Uncertain')}.")

    return " ".join(parts)


def draw_face_boxes(file_path, output_path):
    try:
        img = cv2.imread(file_path)
        if img is None:
            return False

        temp_results, _ = analyze_image(file_path)
        boxes = temp_results.get("face_boxes", [])

        for (x, y, w, h) in boxes:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label_y = max(y - 26, 0)
            cv2.rectangle(img, (x, label_y), (x + 68, y), (0, 255, 0), -1)
            cv2.putText(img, "Face", (x + 5, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 2)

        cv2.imwrite(output_path, img)
        return True
    except Exception:
        return False