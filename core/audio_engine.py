"""
DeepFake Shield - Audio Authenticity Detection Engine
CPU-friendly audio analysis using librosa and numpy.
Analyzes spectral, temporal, and harmonic features.
"""

import os
import logging
import tempfile
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

LIBROSA_AVAILABLE = False
SOUNDFILE_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    logger.warning("librosa not available. Audio analysis will be limited.")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    logger.warning("soundfile not available.")


def analyze_audio(file_bytes, filename='unknown.wav'):
    """
    Main audio analysis function.
    Analyzes spectral, temporal, and harmonic features for authenticity.
    """
    logger.info(f"Starting audio analysis for: {filename}")

    results = {
        'filename': filename,
        'duration': 0.0,
        'sample_rate': 0,
        'rms_energy': 0.0,
        'spectral_flatness': 0.0,
        'clipping_ratio': 0.0,
        'zero_crossing_rate': 0.0,
        'spectral_centroid': 0.0,
        'harmonic_confidence': 0.0,
        'spectral_bandwidth': 0.0,
        'spectral_rolloff': 0.0,
        'tempo_estimate': 0.0,
        'silence_ratio': 0.0,
        'authenticity_score': 0.0,
        'real_vs_fake': 'Unknown',
        'classification': 'suspicious',
        'summary': '',
        'explanation': '',
        'description': '',
        'detailed_metrics': {},
    }

    if not LIBROSA_AVAILABLE:
        results['explanation'] = 'Audio analysis library (librosa) is not available.'
        results['summary'] = 'Audio analysis could not be performed without librosa.'
        results['authenticity_score'] = 50.0
        return results

    tmp_path = None

    try:
        # Write to temp file
        suffix = Path(filename).suffix or '.wav'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        # Load audio
        y, sr = librosa.load(tmp_path, sr=None, mono=True, duration=120)  # Max 2 min

        if len(y) == 0:
            results['explanation'] = 'Audio file contains no data.'
            results['summary'] = 'Empty audio file.'
            return results

        duration = librosa.get_duration(y=y, sr=sr)
        results['duration'] = round(duration, 2)
        results['sample_rate'] = sr

        # ── RMS Energy ──
        rms = librosa.feature.rms(y=y)[0]
        rms_mean = float(np.mean(rms))
        results['rms_energy'] = round(rms_mean, 6)

        # ── Spectral Flatness ──
        flatness = librosa.feature.spectral_flatness(y=y)[0]
        flatness_mean = float(np.mean(flatness))
        results['spectral_flatness'] = round(flatness_mean, 6)

        # ── Clipping Detection ──
        max_amp = np.max(np.abs(y))
        if max_amp > 0:
            clipping_threshold = 0.99 * max_amp
            clipping_samples = np.sum(np.abs(y) >= clipping_threshold)
            clipping_ratio = clipping_samples / len(y)
        else:
            clipping_ratio = 0.0
        results['clipping_ratio'] = round(float(clipping_ratio), 6)

        # ── Zero Crossing Rate ──
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        zcr_mean = float(np.mean(zcr))
        results['zero_crossing_rate'] = round(zcr_mean, 6)

        # ── Spectral Centroid ──
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        centroid_mean = float(np.mean(centroid))
        results['spectral_centroid'] = round(centroid_mean, 2)

        # ── Spectral Bandwidth ──
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        bandwidth_mean = float(np.mean(bandwidth))
        results['spectral_bandwidth'] = round(bandwidth_mean, 2)

        # ── Spectral Rolloff ──
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        rolloff_mean = float(np.mean(rolloff))
        results['spectral_rolloff'] = round(rolloff_mean, 2)

        # ── Harmonic-Percussive Separation ──
        try:
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            harmonic_energy = np.sum(y_harmonic ** 2)
            total_energy = np.sum(y ** 2)
            harmonic_confidence = harmonic_energy / total_energy if total_energy > 0 else 0.5
            results['harmonic_confidence'] = round(float(harmonic_confidence), 4)
        except Exception:
            results['harmonic_confidence'] = 0.5

        # ── Silence Ratio ──
        silence_threshold = 0.01 * max_amp if max_amp > 0 else 0.001
        silence_samples = np.sum(np.abs(y) < silence_threshold)
        silence_ratio = silence_samples / len(y) if len(y) > 0 else 0
        results['silence_ratio'] = round(float(silence_ratio), 4)

        # ── Tempo Estimation ──
        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            if isinstance(tempo, np.ndarray):
                tempo = float(tempo[0]) if len(tempo) > 0 else 0.0
            results['tempo_estimate'] = round(float(tempo), 1)
        except Exception:
            results['tempo_estimate'] = 0.0

        # ═══════════════════════════════════════
        # AUTHENTICITY SCORING
        # ═══════════════════════════════════════

        score = 50.0  # Base score

        # 1. RMS Energy (natural audio has moderate energy)
        if 0.01 < rms_mean < 0.3:
            score += 10.0
        elif rms_mean < 0.005:
            score -= 5.0  # Very quiet = suspicious
        elif rms_mean > 0.5:
            score -= 5.0  # Clipping/distortion

        # 2. Spectral Flatness (pure tones have low flatness, noise has high)
        if 0.01 < flatness_mean < 0.3:
            score += 10.0  # Natural speech/music range
        elif flatness_mean > 0.5:
            score -= 8.0  # Too noisy/synthetic
        elif flatness_mean < 0.005:
            score -= 5.0  # Too pure/synthetic tone

        # 3. Clipping
        if clipping_ratio < 0.001:
            score += 8.0  # Clean recording
        elif clipping_ratio > 0.01:
            score -= 10.0  # Significant clipping
        elif clipping_ratio > 0.005:
            score -= 5.0

        # 4. Zero Crossing Rate (speech: moderate, synthetic: extreme)
        if 0.03 < zcr_mean < 0.15:
            score += 8.0  # Natural speech range
        elif zcr_mean > 0.3:
            score -= 5.0  # Too noisy
        elif zcr_mean < 0.01:
            score -= 5.0  # Unnaturally smooth

        # 5. Spectral Centroid (voice: ~1000-4000 Hz)
        if 500 < centroid_mean < 5000:
            score += 8.0  # Voice/music range
        elif centroid_mean > 8000:
            score -= 5.0  # High frequency dominant

        # 6. Harmonic Confidence
        if harmonic_confidence > 0.3:
            score += 8.0  # Good harmonic content (voice/music)
        elif harmonic_confidence < 0.1:
            score -= 5.0  # Low harmonic content

        # 7. Duration sanity
        if 0.5 < duration < 300:
            score += 3.0
        elif duration < 0.5:
            score -= 5.0  # Too short

        # 8. Silence ratio
        if silence_ratio < 0.5:
            score += 3.0
        elif silence_ratio > 0.8:
            score -= 8.0  # Mostly silence

        # 9. Dynamic range check
        if rms.size > 1:
            rms_std = np.std(rms)
            rms_cv = rms_std / rms_mean if rms_mean > 0 else 0
            if 0.3 < rms_cv < 2.0:
                score += 5.0  # Good dynamic range
            elif rms_cv < 0.1:
                score -= 5.0  # Too constant (TTS-like)

        # Clamp score
        final_score = max(0.0, min(100.0, round(score, 1)))
        results['authenticity_score'] = final_score

        # Classification
        if final_score >= 75:
            results['classification'] = 'likely_real'
            results['real_vs_fake'] = 'Likely Real / Authentic'
        elif final_score >= 40:
            results['classification'] = 'suspicious'
            results['real_vs_fake'] = 'Suspicious / Inconclusive'
        else:
            results['classification'] = 'likely_fake'
            results['real_vs_fake'] = 'Likely Fake / Synthetic'

        # Description
        results['description'] = (
            f"Audio file '{filename}': {duration:.1f}s duration, "
            f"{sr} Hz sample rate, {'mono' if True else 'stereo'} channel."
        )

        # Explanation
        explanations = []
        if rms_mean > 0.01:
            explanations.append(f"RMS energy ({rms_mean:.4f}) is within normal range.")
        else:
            explanations.append(f"RMS energy ({rms_mean:.4f}) is very low.")

        if 0.01 < flatness_mean < 0.3:
            explanations.append("Spectral characteristics are consistent with natural audio.")
        else:
            explanations.append("Spectral flatness suggests potential synthetic origin.")

        if clipping_ratio < 0.001:
            explanations.append("No significant audio clipping detected.")
        else:
            explanations.append(f"Audio clipping detected ({clipping_ratio:.4f} ratio).")

        if harmonic_confidence > 0.3:
            explanations.append("Good harmonic content indicating natural voice or music.")
        else:
            explanations.append("Low harmonic content may indicate synthetic audio.")

        results['explanation'] = " ".join(explanations)

        results['summary'] = (
            f"Audio Authenticity Score: {final_score:.1f}/100 — "
            f"{results['classification'].replace('_', ' ').title()}. "
            f"{results['explanation']}"
        )

        results['detailed_metrics'] = {
            'duration_seconds': round(duration, 2),
            'sample_rate': sr,
            'rms_energy': round(rms_mean, 6),
            'spectral_flatness': round(flatness_mean, 6),
            'clipping_ratio': round(float(clipping_ratio), 6),
            'zero_crossing_rate': round(zcr_mean, 6),
            'spectral_centroid_hz': round(centroid_mean, 2),
            'spectral_bandwidth_hz': round(bandwidth_mean, 2),
            'spectral_rolloff_hz': round(rolloff_mean, 2),
            'harmonic_confidence': round(float(harmonic_confidence), 4),
            'silence_ratio': round(float(silence_ratio), 4),
            'tempo_bpm': round(float(results['tempo_estimate']), 1),
        }

        logger.info(f"Audio analysis complete: score={final_score}")

    except Exception as e:
        logger.error(f"Audio analysis failed: {e}", exc_info=True)
        results['explanation'] = f'Audio analysis encountered an error: {str(e)}'
        results['summary'] = 'Audio analysis could not be completed.'
        results['authenticity_score'] = 0.0

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    return results