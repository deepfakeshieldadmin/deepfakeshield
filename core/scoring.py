"""
═══════════════════════════════════════════════════════════
DEEP FAKE SHIELD — ENHANCED AUTHENTICITY SCORING SYSTEM

Score Range: 0 → 100

Scoring Categories:
  Score 90-100: Highly Authentic
  Score 75-89:  Likely Real
  Score 40-74:  Suspicious / Possibly Edited
  Score 0-39:   Likely Fake / AI Generated
  Score 0:      Confirmed AI/Synthetic
  Score 100:    Confirmed Original Camera Image
═══════════════════════════════════════════════════════════
"""


class AuthenticityScorer:
    """
    Comprehensive scoring algorithm for media authenticity.

    Evaluates:
    1. EXIF metadata presence and quality
    2. Camera make/model detection
    3. Face detection consistency
    4. AI artifact detection
    5. Compression artifact analysis
    6. Image noise pattern analysis
    """

    def __init__(self):
        # Weight for each scoring category (total = 100)
        self.weights = {
            'exif_metadata': 20,        # 0-20 points
            'camera_info': 15,           # 0-15 points
            'face_consistency': 10,      # 0-10 points
            'ai_artifacts': 20,          # 0-20 points
            'compression': 15,           # 0-15 points
            'noise_patterns': 15,        # 0-15 points
            'format_quality': 5,         # 0-5 points
        }

    def calculate_score(self, analysis_results):
        """
        Calculate final authenticity score from all analysis components.

        Args:
            analysis_results: dict with scores from each analyzer

        Returns:
            dict with:
                - final_score (0-100)
                - classification (string)
                - confidence (string)
                - breakdown (dict of component scores)
                - reasons (list of strings explaining the score)
        """
        scores = {}
        reasons = []

        # ═══ 1. EXIF METADATA (0-20 points) ═══
        exif_score = analysis_results.get('exif_analysis', 0)
        scores['exif_metadata'] = min(exif_score, 20)

        if exif_score >= 18:
            reasons.append("✅ EXIF: Rich metadata found — original camera data present")
        elif exif_score >= 12:
            reasons.append("✅ EXIF: Partial metadata — some camera information available")
        elif exif_score >= 5:
            reasons.append("⚠️ EXIF: Limited metadata — possible processing or editing")
        else:
            reasons.append("❌ EXIF: No metadata — common in AI-generated or heavily edited images")

        # ═══ 2. CAMERA MAKE/MODEL (0-15 points) ═══
        has_camera = analysis_results.get('has_camera_info', False)
        camera_make = analysis_results.get('camera_make', '')
        camera_model = analysis_results.get('camera_model', '')

        if camera_make and camera_model:
            scores['camera_info'] = 15
            reasons.append(f"✅ Camera: {camera_make} {camera_model} detected — genuine capture device")
        elif camera_make or camera_model:
            scores['camera_info'] = 10
            reasons.append(f"✅ Camera: Partial device info found ({camera_make or camera_model})")
        else:
            scores['camera_info'] = 0
            reasons.append("❌ Camera: No device information — not from a physical camera")

        # ═══ 3. FACE CONSISTENCY (0-10 points) ═══
        face_score = analysis_results.get('face_analysis', 5)
        face_count = analysis_results.get('face_count', 0)
        face_smooth = analysis_results.get('face_unnaturally_smooth', False)

        if face_smooth:
            scores['face_consistency'] = max(face_score - 5, 0)
            reasons.append("❌ Faces: Unnaturally smooth face regions — possible AI generation")
        elif face_count > 0:
            scores['face_consistency'] = min(face_score, 10)
            if face_score >= 7:
                reasons.append(f"✅ Faces: {face_count} face(s) with natural texture patterns")
            else:
                reasons.append(f"⚠️ Faces: {face_count} face(s) with some irregularities")
        else:
            scores['face_consistency'] = 5  # Neutral
            reasons.append("ℹ️ Faces: No faces to analyze")

        # ═══ 4. AI ARTIFACT DETECTION (0-20 points) ═══
        noise_score = analysis_results.get('noise_analysis', 7)
        edge_score = analysis_results.get('edge_analysis', 7)
        texture_score = analysis_results.get('texture_analysis', 5)

        # AI artifacts manifest as: unnaturally smooth noise, inconsistent edges,
        # repeating patterns, unrealistic edge sharpness
        ai_artifact_score = 0

        # Noise pattern check
        noise_variance = analysis_results.get('noise_variance', 500)
        if noise_variance < 20:
            # Extremely smooth = likely AI
            ai_artifact_score += 2
            reasons.append("❌ AI Artifacts: Unnaturally smooth — possible GAN generation")
        elif noise_variance < 50:
            ai_artifact_score += 5
            reasons.append("⚠️ AI Artifacts: Very low noise — suspicious smoothness")
        elif 100 < noise_variance < 3000:
            ai_artifact_score += 15
            reasons.append("✅ AI Artifacts: Natural sensor noise pattern detected")
        elif noise_variance >= 3000:
            ai_artifact_score += 8
            reasons.append("⚠️ AI Artifacts: Extremely high noise — possible heavy processing")
        else:
            ai_artifact_score += 10

        # Edge consistency adds to AI artifact score
        edge_density = analysis_results.get('edge_density', 0.1)
        if 0.05 < edge_density < 0.25:
            ai_artifact_score += 5
        elif edge_density <= 0.02:
            ai_artifact_score += 1
            reasons.append("❌ AI Artifacts: Unrealistic edge patterns")
        else:
            ai_artifact_score += 3

        scores['ai_artifacts'] = min(ai_artifact_score, 20)

        # ═══ 5. COMPRESSION ARTIFACTS (0-15 points) ═══
        compression_score = analysis_results.get('compression_analysis', 5)
        bpp = analysis_results.get('bits_per_pixel', 5)

        if 2 < bpp < 24:
            scores['compression'] = min(compression_score + 5, 15)
            reasons.append("✅ Compression: Authentic JPEG compression pattern")
        elif bpp <= 2:
            scores['compression'] = max(compression_score - 3, 0)
            reasons.append("⚠️ Compression: Heavy compression — quality loss detected")
        else:
            scores['compression'] = min(compression_score, 15)

        # ═══ 6. NOISE PATTERNS (0-15 points) ═══
        color_score = analysis_results.get('color_analysis', 7)
        color_entropy = analysis_results.get('color_entropy', 5.5)

        if 4.5 < color_entropy < 7.5:
            scores['noise_patterns'] = min(noise_score + 3, 15)
            reasons.append("✅ Noise: Natural color distribution and noise patterns")
        elif color_entropy <= 3.5:
            scores['noise_patterns'] = 4
            reasons.append("❌ Noise: Abnormal color distribution — possible synthetic image")
        else:
            scores['noise_patterns'] = min(noise_score, 15)

        # ═══ 7. FORMAT QUALITY (0-5 points) ═══
        format_score = analysis_results.get('format_analysis', 3)
        scores['format_quality'] = min(format_score, 5)

        # ═══════════════════════════════════════════════════
        # CALCULATE FINAL SCORE
        # ═══════════════════════════════════════════════════
        final_score = sum(scores.values())
        final_score = min(max(round(final_score, 1), 0), 100)

        # ═══ CLASSIFICATION ═══
        if final_score >= 90:
            classification = 'authentic'
            confidence = 'Very High'
            reasons.insert(0, "🏆 VERDICT: Highly Authentic — This appears to be an original, unmodified capture.")
        elif final_score >= 75:
            classification = 'likely_real'
            confidence = 'High'
            reasons.insert(0, "✅ VERDICT: Likely Real — Minor anomalies but overall authentic characteristics.")
        elif final_score >= 40:
            classification = 'suspicious'
            confidence = 'Medium'
            reasons.insert(0, "⚠️ VERDICT: Suspicious — Mixed signals detected, possible editing or AI assistance.")
        else:
            classification = 'likely_fake'
            confidence = 'High'
            reasons.insert(0, "❌ VERDICT: Likely Fake/AI — Strong indicators of AI generation or heavy manipulation.")

        # ═══ SPECIAL CASES ═══
        # Score 0: Confirmed AI
        if final_score <= 5 and not analysis_results.get('has_exif', False) and noise_variance < 30:
            final_score = 0
            classification = 'likely_fake'
            confidence = 'Very High'
            reasons.insert(0, "🚨 VERDICT: Detected as AI-generated image — synthetic patterns confirmed.")

        # Score 100: Confirmed original
        if (final_score >= 95 and
            analysis_results.get('has_exif', False) and
            camera_make and camera_model and
            100 < noise_variance < 2000):
            final_score = 100
            classification = 'authentic'
            confidence = 'Very High'
            reasons.insert(0, "🏆 VERDICT: Confirmed Original — Untouched camera capture with full metadata.")

        return {
            'final_score': final_score,
            'classification': classification,
            'confidence': confidence,
            'breakdown': scores,
            'reasons': reasons,
        }


def get_score_description(score):
    """Return human-readable description for a given score."""
    if score >= 90:
        return {
            'label': 'Highly Authentic',
            'emoji': '🏆',
            'color': '#28a745',
            'description': 'Original camera image with untouched metadata, natural sensor noise, and authentic compression.',
        }
    elif score >= 75:
        return {
            'label': 'Likely Real',
            'emoji': '✅',
            'color': '#17a2b8',
            'description': 'EXIF present, minor compression changes, no AI artifacts detected.',
        }
    elif score >= 40:
        return {
            'label': 'Suspicious',
            'emoji': '⚠️',
            'color': '#ffc107',
            'description': 'Missing EXIF, slight artifacts detected, possibly edited metadata.',
        }
    elif score > 0:
        return {
            'label': 'Likely Fake / AI',
            'emoji': '❌',
            'color': '#dc3545',
            'description': 'No EXIF, AI artifacts detected, repeating patterns, unrealistic edges, GAN noise pattern.',
        }
    else:
        return {
            'label': 'Confirmed AI Generated',
            'emoji': '🚨',
            'color': '#dc3545',
            'description': 'Synthetic face generation detected, GAN fingerprints confirmed, no authentic camera data.',
        }