"""
DeepFake Shield - Video Authenticity Detection Engine
Extracts frames from video and analyzes using the image engine.
CPU-friendly, production-safe.
"""

import os
import logging
import tempfile
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Import image analysis function
from .ai_engine import analyze_image, detect_faces


def analyze_video(file_bytes, filename='unknown.mp4'):
    """
    Main video analysis function.
    Extracts sample frames and analyzes each for authenticity.
    """
    logger.info(f"Starting video analysis for: {filename}")

    results = {
        'filename': filename,
        'total_frames': 0,
        'frames_analyzed': 0,
        'fps': 0.0,
        'duration': 0.0,
        'resolution': '0x0',
        'frame_scores': [],
        'temporal_variation_score': 50.0,
        'face_consistency_score': 50.0,
        'motion_score': 50.0,
        'average_score': 0.0,
        'authenticity_score': 0.0,
        'real_vs_fake': 'Unknown',
        'classification': 'suspicious',
        'summary': '',
        'explanation': '',
        'description': '',
        'detailed_metrics': {},
    }

    if not CV2_AVAILABLE:
        results['explanation'] = 'OpenCV not available for video analysis.'
        results['summary'] = 'Video analysis could not be performed.'
        return results

    tmp_path = None
    cap = None

    try:
        # Write video bytes to temp file
        suffix = Path(filename).suffix or '.mp4'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        # Open video
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            results['explanation'] = 'Could not open video file.'
            results['summary'] = 'Video file could not be opened for analysis.'
            return results

        # Video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0

        results['total_frames'] = total_frames
        results['fps'] = round(fps, 2)
        results['duration'] = round(duration, 2)
        results['resolution'] = f'{width}x{height}'

        if total_frames == 0:
            results['explanation'] = 'Video contains no frames.'
            results['summary'] = 'Empty video file.'
            return results

        # Determine sample frame indices
        from django.conf import settings
        sample_count = min(
            settings.DEEPFAKE_SHIELD.get('VIDEO_SAMPLE_FRAMES', 10),
            total_frames
        )

        if total_frames <= sample_count:
            frame_indices = list(range(total_frames))
        else:
            frame_indices = np.linspace(0, total_frames - 1, sample_count, dtype=int).tolist()

        # Extract and analyze frames
        frame_scores = []
        frame_face_counts = []
        prev_gray = None
        motion_diffs = []

        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            # Encode frame to bytes for image analysis
            success, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            if not success:
                continue

            frame_bytes = encoded.tobytes()
            frame_result = analyze_image(frame_bytes, filename=f'{filename}_frame_{idx}')

            frame_score = frame_result.get('authenticity_score', 50.0)
            frame_scores.append({
                'frame_index': idx,
                'score': round(frame_score, 1),
                'face_count': frame_result.get('face_count', 0),
            })
            frame_face_counts.append(frame_result.get('face_count', 0))

            # Motion analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                motion_diffs.append(np.mean(diff))
            prev_gray = gray

        results['frames_analyzed'] = len(frame_scores)
        results['frame_scores'] = frame_scores

        if not frame_scores:
            results['explanation'] = 'Could not extract analyzable frames.'
            results['summary'] = 'No frames could be analyzed from the video.'
            return results

        # Calculate scores
        score_values = [f['score'] for f in frame_scores]
        avg_score = np.mean(score_values)

        # Temporal variation (DON'T penalize static/slideshow content)
        score_std = np.std(score_values)
        if score_std < 5:
            temporal_score = 80.0  # Consistent = good
        elif score_std < 15:
            temporal_score = 70.0  # Slightly varying = still ok
        elif score_std < 25:
            temporal_score = 55.0
        else:
            temporal_score = 40.0

        # Face consistency
        if len(set(frame_face_counts)) <= 2 and max(frame_face_counts) > 0:
            face_consistency = 80.0
        elif len(set(frame_face_counts)) <= 3:
            face_consistency = 60.0
        elif max(frame_face_counts) == 0:
            face_consistency = 50.0  # No faces, neutral
        else:
            face_consistency = 35.0

        # Motion analysis — DON'T penalize static/slideshow videos
        if motion_diffs:
            avg_motion = np.mean(motion_diffs)
            motion_std = np.std(motion_diffs)
            if avg_motion < 1.0:
                motion_score = 65.0  # Static/slideshow — NOT fake, just static
            elif 1.0 <= avg_motion < 30.0 and motion_std > 0.5:
                motion_score = 80.0
            elif avg_motion > 50:
                motion_score = 50.0
            else:
                motion_score = 65.0
        else:
            motion_score = 65.0

        results['temporal_variation_score'] = round(temporal_score, 1)
        results['face_consistency_score'] = round(face_consistency, 1)
        results['motion_score'] = round(motion_score, 1)
        results['average_score'] = round(avg_score, 1)

        # ═══ SMART SCORING — Don't penalize slideshows/collages ═══
        
        # Detect if this is a slideshow/collage (low motion, high score variance is OK)
        is_slideshow = False
        if motion_diffs:
            avg_motion = np.mean(motion_diffs)
            if avg_motion < 2.0:  # Very little motion = slideshow
                is_slideshow = True
        
        if is_slideshow:
            # For slideshows: score is just the average frame authenticity
            # Don't penalize for temporal inconsistency or motion
            temporal_score = 75.0
            face_consistency = 70.0
            motion_score = 70.0  # Neutral — static content is NOT fake
        else:
            # For real videos: check temporal consistency
            if score_std < 5:
                temporal_score = 85.0
            elif score_std < 15:
                temporal_score = 70.0
            elif score_std < 25:
                temporal_score = 50.0
            else:
                temporal_score = 35.0

            # Face consistency
            if len(set(frame_face_counts)) <= 2 and max(frame_face_counts) > 0:
                face_consistency = 80.0
            elif len(set(frame_face_counts)) <= 3:
                face_consistency = 65.0
            elif max(frame_face_counts) == 0:
                face_consistency = 70.0
            else:
                face_consistency = 40.0

            # Motion realism
            if motion_diffs:
                avg_motion = np.mean(motion_diffs)
                if 1.0 < avg_motion < 30.0:
                    motion_score = 80.0
                elif avg_motion > 50:
                    motion_score = 50.0
                else:
                    motion_score = 65.0
            else:
                motion_score = 65.0

        results['temporal_variation_score'] = round(temporal_score, 1)
        results['face_consistency_score'] = round(face_consistency, 1)
        results['motion_score'] = round(motion_score, 1)

        # Final video score
        if is_slideshow:
            # Slideshow: 80% frame quality, 20% basic checks
            final_score = avg_score * 0.80 + temporal_score * 0.10 + 70.0 * 0.10
        else:
            final_score = (
                avg_score * 0.50 +
                temporal_score * 0.20 +
                face_consistency * 0.15 +
                motion_score * 0.15
            )
        
        final_score = max(0.0, min(100.0, round(final_score, 1)))
        results['authenticity_score'] = final_score

        results['detailed_metrics'] = {
            'total_frames': total_frames,
            'frames_analyzed': len(frame_scores),
            'fps': round(fps, 2),
            'duration_seconds': round(duration, 2),
            'resolution': f'{width}x{height}',
            'average_frame_score': round(avg_score, 1),
            'score_std_deviation': round(score_std, 2),
            'temporal_variation_score': round(temporal_score, 1),
            'face_consistency_score': round(face_consistency, 1),
            'motion_realism_score': round(motion_score, 1),
        }

        logger.info(f"Video analysis complete: score={final_score}")

    except Exception as e:
        logger.error(f"Video analysis failed: {e}", exc_info=True)
        results['explanation'] = f'Video analysis encountered an error: {str(e)}'
        results['summary'] = 'Video analysis could not be completed.'

    finally:
        if cap is not None:
            cap.release()
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    return results