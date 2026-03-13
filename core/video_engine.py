import cv2
import numpy as np
import os
import tempfile
from .ai_engine import analyze_image
from .utils import get_classification


def analyze_video(video_path):
    result = {
        'authenticity_score': 50.0,
        'classification': 'suspicious',
        'total_frames_analyzed': 0,
        'frame_scores': [],
        'details': {},
        'explanation': '',
    }

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            result['explanation'] = 'Could not open video file.'
            return result

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0

        result['details'] = {
            'Total Frames': total_frames,
            'FPS': round(fps, 2),
            'Resolution': f"{width}x{height}",
            'Duration (s)': round(duration, 2),
        }

        if total_frames <= 0:
            cap.release()
            result['explanation'] = 'Video contains no readable frames.'
            return result

        max_frames_to_analyze = min(8, total_frames)
        interval = max(1, total_frames // max_frames_to_analyze)

        frame_scores = []
        explanations = [
            f"Video loaded successfully: {width}x{height}, {fps:.1f} FPS, {duration:.1f} seconds."
        ]

        temp_dir = tempfile.mkdtemp()

        for i in range(max_frames_to_analyze):
            frame_number = i * interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ok, frame = cap.read()
            if not ok:
                continue

            frame_path = os.path.join(temp_dir, f"frame_{i}.jpg")
            cv2.imwrite(frame_path, frame)

            try:
                frame_result = analyze_image(frame_path)
                frame_score = frame_result.get('authenticity_score', 50.0)

                frame_scores.append({
                    'frame_index': i + 1,
                    'frame_number': frame_number,
                    'time_seconds': round(frame_number / fps, 2) if fps > 0 else 0,
                    'score': round(frame_score, 1),
                    'classification': frame_result.get('classification', 'suspicious'),
                })
            except Exception:
                continue

            try:
                os.remove(frame_path)
            except Exception:
                pass

        cap.release()

        try:
            os.rmdir(temp_dir)
        except Exception:
            pass

        if frame_scores:
            score_values = [f['score'] for f in frame_scores]
            avg_score = round(float(np.mean(score_values)), 1)
            min_score = round(float(np.min(score_values)), 1)
            max_score = round(float(np.max(score_values)), 1)
            std_score = round(float(np.std(score_values)), 1)

            result['authenticity_score'] = avg_score
            result['classification'] = get_classification(avg_score)
            result['total_frames_analyzed'] = len(frame_scores)
            result['frame_scores'] = frame_scores
            result['details']['Average Score'] = avg_score
            result['details']['Min Frame Score'] = min_score
            result['details']['Max Frame Score'] = max_score
            result['details']['Score Variation'] = std_score

            explanations.append(f"Analyzed {len(frame_scores)} sample frames.")
            explanations.append(f"Average frame score: {avg_score}%.")
            explanations.append(f"Score range: {min_score}% to {max_score}%.")

            if std_score > 20:
                explanations.append("High variation between frames may indicate inconsistency or edited content.")
            elif std_score > 10:
                explanations.append("Moderate variation detected between frames.")
            else:
                explanations.append("Frame scores appear relatively consistent.")
        else:
            explanations.append("No frames could be analyzed successfully.")

        result['explanation'] = "\n".join(explanations)

    except Exception as e:
        result['explanation'] = f"Video analysis error: {str(e)}"

    return result