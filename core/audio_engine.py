import wave
import struct
import numpy as np
import os
from .utils import get_classification


def analyze_audio(audio_path):
    result = {
        'authenticity_score': 50.0,
        'classification': 'suspicious',
        'duration_seconds': 0.0,
        'details': {},
        'explanation': '',
    }

    try:
        ext = os.path.splitext(audio_path)[1].lower()

        if ext == '.wav':
            return analyze_wav(audio_path)
        else:
            return analyze_generic_audio(audio_path)

    except Exception as e:
        result['explanation'] = f'Audio analysis error: {str(e)}'
        return result


def analyze_wav(audio_path):
    result = {
        'authenticity_score': 50.0,
        'classification': 'suspicious',
        'duration_seconds': 0.0,
        'details': {},
        'explanation': '',
    }

    try:
        with wave.open(audio_path, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            duration = n_frames / frame_rate if frame_rate > 0 else 0

            result['duration_seconds'] = round(duration, 2)

            raw_data = wav_file.readframes(n_frames)

            if sample_width == 1:
                fmt = f'{n_frames * channels}B'
                data = np.array(struct.unpack(fmt, raw_data), dtype=np.float64) - 128
                max_val = 128
            elif sample_width == 2:
                fmt = f'{n_frames * channels}h'
                data = np.array(struct.unpack(fmt, raw_data), dtype=np.float64)
                max_val = 32768
            elif sample_width == 4:
                fmt = f'{n_frames * channels}i'
                data = np.array(struct.unpack(fmt, raw_data), dtype=np.float64)
                max_val = 2147483648
            else:
                result['explanation'] = 'Unsupported WAV sample width.'
                return result

            if len(data) == 0:
                result['explanation'] = 'Audio file is empty.'
                return result

            signal = data / max_val

            rms = float(np.sqrt(np.mean(signal ** 2)))
            clip_ratio = float(np.sum(np.abs(signal) > 0.99) / len(signal))
            zero_crossings = np.sum(np.abs(np.diff(np.sign(signal))) > 0)
            zcr = float(zero_crossings / len(signal))

            spectral_flatness = 0.0
            if len(signal) > 256:
                fft_vals = np.abs(np.fft.rfft(signal[:min(len(signal), frame_rate * 2)]))
                fft_vals = fft_vals[1:]
                if len(fft_vals) > 0 and np.mean(fft_vals) > 0:
                    geometric_mean = np.exp(np.mean(np.log(fft_vals + 1e-10)))
                    arithmetic_mean = np.mean(fft_vals)
                    spectral_flatness = float(geometric_mean / arithmetic_mean)

            score = 0
            explanations = [f"Audio loaded: {channels} channel(s), {frame_rate} Hz, duration {duration:.1f}s."]

            if 0.01 < rms < 0.5:
                score += 25
                explanations.append(f"RMS energy appears natural ({rms:.4f}).")
            elif 0.005 < rms <= 0.01 or 0.5 <= rms < 0.8:
                score += 15
                explanations.append(f"RMS energy is somewhat unusual ({rms:.4f}).")
            else:
                score += 8
                explanations.append(f"RMS energy is highly unusual ({rms:.4f}).")

            if clip_ratio < 0.001:
                score += 25
                explanations.append(f"Minimal clipping detected ({clip_ratio:.4%}).")
            elif clip_ratio < 0.01:
                score += 18
                explanations.append(f"Minor clipping present ({clip_ratio:.4%}).")
            elif clip_ratio < 0.05:
                score += 10
                explanations.append(f"Moderate clipping present ({clip_ratio:.4%}).")
            else:
                score += 5
                explanations.append(f"Severe clipping detected ({clip_ratio:.4%}).")

            if 0.02 < zcr < 0.3:
                score += 25
                explanations.append(f"Zero-crossing rate appears natural ({zcr:.4f}).")
            elif 0.01 < zcr <= 0.02 or 0.3 <= zcr < 0.5:
                score += 15
                explanations.append(f"Zero-crossing rate is somewhat unusual ({zcr:.4f}).")
            else:
                score += 8
                explanations.append(f"Zero-crossing rate is highly unusual ({zcr:.4f}).")

            if 0.01 < spectral_flatness < 0.5:
                score += 25
                explanations.append(f"Spectral profile appears natural ({spectral_flatness:.4f}).")
            elif spectral_flatness <= 0.01:
                score += 12
                explanations.append(f"Very tonal signal detected ({spectral_flatness:.4f}).")
            else:
                score += 10
                explanations.append(f"High spectral flatness detected ({spectral_flatness:.4f}).")

            score = min(max(round(score, 1), 0), 100)

            result['authenticity_score'] = score
            result['classification'] = get_classification(score)
            result['details'] = {
                'Channels': channels,
                'Sample Width': sample_width,
                'Frame Rate': frame_rate,
                'Duration': round(duration, 2),
                'RMS': round(rms, 4),
                'Clip Ratio': round(clip_ratio, 6),
                'Zero Crossing Rate': round(zcr, 4),
                'Spectral Flatness': round(spectral_flatness, 4),
            }
            result['explanation'] = "\n".join(explanations)

    except Exception as e:
        result['explanation'] = f'WAV analysis error: {str(e)}'

    return result


def analyze_generic_audio(audio_path):
    result = {
        'authenticity_score': 55.0,
        'classification': 'suspicious',
        'duration_seconds': 0.0,
        'details': {},
        'explanation': '',
    }

    try:
        file_size = os.path.getsize(audio_path)
        ext = os.path.splitext(audio_path)[1].lower()

        with open(audio_path, 'rb') as f:
            raw_data = f.read(min(file_size, 1024 * 1024))

        data = np.frombuffer(raw_data, dtype=np.uint8).astype(np.float64)

        if len(data) > 0:
            hist, _ = np.histogram(data, bins=256, range=(0, 256))
            hist = hist / len(data)
            hist = hist[hist > 0]
            entropy = float(-np.sum(hist * np.log2(hist)))

            if entropy > 7.0:
                score = 75
                explanation = f"Compressed audio data has high entropy ({entropy:.2f}), suggesting complex content."
            elif entropy > 5.0:
                score = 60
                explanation = f"Compressed audio data has moderate entropy ({entropy:.2f})."
            else:
                score = 40
                explanation = f"Compressed audio data has low entropy ({entropy:.2f}), which may be suspicious."

            result['authenticity_score'] = score
            result['classification'] = get_classification(score)
            result['details'] = {
                'Format': ext,
                'File Size (bytes)': file_size,
                'Byte Entropy': round(entropy, 2),
            }
            result['explanation'] = explanation + " For deeper analysis, WAV format is recommended."
        else:
            result['explanation'] = "Could not read compressed audio data."

    except Exception as e:
        result['explanation'] = f'Generic audio analysis error: {str(e)}'

    return result