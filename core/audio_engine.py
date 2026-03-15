import numpy as np


def analyze_audio(file_path):
    results = {
        'rms_energy': 0,
        'spectral_flatness': 0,
        'clipping_ratio': 0,
        'duration': 0,
        'sample_rate': 0,
        'zero_crossing_rate': 0,
        'spectral_centroid': 0,
        'harmonic_confidence': 0,
        'description': '',
        'analysis_summary': '',
        'real_vs_fake': 'Uncertain',
    }

    try:
        import librosa

        y, sr = librosa.load(file_path, sr=None, mono=True, duration=120)
        if y is None or len(y) == 0:
            results['description'] = 'Audio file could not be read properly.'
            return results, 0

        results['sample_rate'] = int(sr)
        results['duration'] = round(len(y) / sr, 2)

        rms = np.sqrt(np.mean(y ** 2))
        results['rms_energy'] = round(float(rms), 6)

        flatness = librosa.feature.spectral_flatness(y=y)
        flatness_mean = float(np.mean(flatness))
        results['spectral_flatness'] = round(flatness_mean, 6)

        clipping_threshold = 0.99
        clipping_ratio = float(np.sum(np.abs(y) >= clipping_threshold) / len(y))
        results['clipping_ratio'] = round(clipping_ratio, 6)

        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = float(np.mean(zcr))
        results['zero_crossing_rate'] = round(zcr_mean, 6)

        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        centroid_mean = float(np.mean(centroid))
        results['spectral_centroid'] = round(centroid_mean, 2)

        harmonic, percussive = librosa.effects.hpss(y)
        harmonic_energy = np.mean(np.abs(harmonic))
        percussive_energy = np.mean(np.abs(percussive))
        if (harmonic_energy + percussive_energy) > 0:
            harmonic_conf = harmonic_energy / (harmonic_energy + percussive_energy)
        else:
            harmonic_conf = 0.5
        results['harmonic_confidence'] = round(float(harmonic_conf) * 100, 2)

        score = _calculate_audio_score(results)

        if score >= 75:
            results['real_vs_fake'] = 'Real'
        elif score <= 39:
            results['real_vs_fake'] = 'Fake'
        else:
            results['real_vs_fake'] = 'Uncertain'

        results['analysis_summary'] = _generate_audio_summary(results, score)
        results['description'] = _generate_audio_description(results, score)

        return results, score

    except Exception as e:
        results['description'] = f'Error during audio analysis: {str(e)}'
        results['analysis_summary'] = 'Audio analysis failed due to an internal processing error.'
        return results, 0


def _calculate_audio_score(results):
    score = 50

    rms = results.get('rms_energy', 0)
    flatness = results.get('spectral_flatness', 0)
    clipping = results.get('clipping_ratio', 0)
    zcr = results.get('zero_crossing_rate', 0)
    centroid = results.get('spectral_centroid', 0)
    harmonic_conf = results.get('harmonic_confidence', 50)

    if 0.01 < rms < 0.30:
        score += 14
    elif rms < 0.005:
        score -= 14
    elif rms > 0.50:
        score -= 8

    if flatness < 0.10:
        score += 14
    elif flatness < 0.25:
        score += 7
    elif flatness > 0.60:
        score -= 18
    elif flatness > 0.40:
        score -= 8

    if clipping < 0.001:
        score += 10
    elif clipping < 0.01:
        score += 5
    elif clipping > 0.05:
        score -= 15

    if 0.02 < zcr < 0.15:
        score += 8
    elif zcr > 0.25:
        score -= 8

    if 300 < centroid < 4000:
        score += 6
    elif centroid > 7000:
        score -= 5

    if harmonic_conf > 55:
        score += 8
    elif harmonic_conf < 30:
        score -= 8

    return int(round(max(0, min(100, score))))


def _generate_audio_summary(results, score):
    if score >= 75:
        verdict = "likely real"
    elif score <= 39:
        verdict = "likely fake"
    else:
        verdict = "suspicious"

    return (
        f"The audio was evaluated using signal-level authenticity features including RMS energy, "
        f"spectral flatness, clipping ratio, zero crossing rate, and harmonic confidence. "
        f"Overall, the audio appears {verdict}."
    )


def _generate_audio_description(results, score):
    parts = []
    parts.append(
        f"Audio duration is {results.get('duration', 0)} seconds at "
        f"{results.get('sample_rate', 0)} Hz sample rate."
    )
    parts.append(f"RMS energy: {results.get('rms_energy', 0):.6f}.")
    parts.append(f"Spectral flatness: {results.get('spectral_flatness', 0):.6f}.")
    parts.append(f"Clipping ratio: {results.get('clipping_ratio', 0):.6f}.")
    parts.append(f"Zero crossing rate: {results.get('zero_crossing_rate', 0):.6f}.")
    parts.append(f"Spectral centroid: {results.get('spectral_centroid', 0):.2f}.")
    parts.append(f"Harmonic confidence: {results.get('harmonic_confidence', 0):.2f}%.")

    if score >= 75:
        parts.append("The signal characteristics appear mostly natural and consistent with real audio.")
    elif score <= 39:
        parts.append("The signal contains suspicious patterns often associated with synthetic or heavily processed audio.")
    else:
        parts.append("The signal contains mixed indicators and should be interpreted carefully.")

    return " ".join(parts)