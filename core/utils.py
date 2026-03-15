def get_classification(score: int) -> str:
    if score >= 90:
        return 'authentic'
    elif score >= 75:
        return 'likely_real'
    elif score >= 40:
        return 'suspicious'
    return 'likely_fake'


def get_classification_label(classification: str) -> str:
    labels = {
        'authentic': 'Highly Authentic',
        'likely_real': 'Likely Real',
        'suspicious': 'Possibly Edited / Suspicious',
        'likely_fake': 'Likely Fake / AI Generated',
    }
    return labels.get(classification, classification)


def get_score_color(score: int) -> str:
    if score >= 90:
        return 'success'
    elif score >= 75:
        return 'info'
    elif score >= 40:
        return 'warning'
    return 'danger'


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def generate_explanation(scan_type: str, score: int, details: dict) -> str:
    if scan_type == 'image':
        return _image_explanation(score, details)
    if scan_type == 'video':
        return _video_explanation(score, details)
    if scan_type == 'audio':
        return _audio_explanation(score, details)
    if scan_type == 'text':
        return _text_explanation(score, details)
    return f"Authenticity Score: {score}/100."


def _image_explanation(score, d):
    parts = [f"Authenticity Score: {score}/100 — Classification: {get_classification_label(get_classification(score))}."]
    if d.get('exif_present'):
        parts.append("EXIF metadata is present, which supports possible real-camera origin.")
    else:
        parts.append("EXIF metadata is missing, which may indicate screenshot origin, metadata stripping, or synthetic generation.")

    if d.get('camera_make') or d.get('camera_model'):
        parts.append(f"Camera source detected: {d.get('camera_make', '')} {d.get('camera_model', '')}.")

    face_count = d.get('face_count', 0)
    if face_count > 0:
        parts.append(f"Detected {face_count} face(s) in the image.")
    else:
        parts.append("No human faces were detected, but the image was still evaluated using non-face authenticity signals.")

    parts.append(f"Artifact profile: {d.get('artifact_label', 'Unknown')}.")
    parts.append(f"Compression profile: {d.get('compression_label', 'Unknown')}.")
    parts.append(f"Real/Fake interpretation: {d.get('real_vs_fake', 'Uncertain')}.")

    return " ".join(parts)


def _video_explanation(score, d):
    return (
        f"Authenticity Score: {score}/100 — Classification: {get_classification_label(get_classification(score))}. "
        f"The video was analyzed using sampled frames, temporal consistency, motion realism, and face consistency."
    )


def _audio_explanation(score, d):
    return (
        f"Authenticity Score: {score}/100 — Classification: {get_classification_label(get_classification(score))}. "
        f"The audio was analyzed using RMS energy, spectral flatness, clipping ratio, harmonic confidence, and related signal features."
    )


def _text_explanation(score, d):
    return (
        f"Authenticity Score: {score}/100 — Classification: {get_classification_label(get_classification(score))}. "
        f"The text was analyzed using repetition, stopword ratio, punctuation density, sentence variance, and vocabulary diversity."
    )