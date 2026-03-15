import os
import cv2
import numpy as np
import tempfile

from .ai_engine import analyze_image


def analyze_video(file_path, max_frames=12):
    results = {
        'frames_analyzed': 0,
        'frame_scores': [],
        'average_score': 0,
        'total_frames': 0,
        'fps': 0,
        'duration': 0,
        'resolution': '',
        'temporal_variation_score': 0,
        'face_consistency_score': 0,
        'motion_score': 0,
        'description': '',
        'analysis_summary': '',
        'real_vs_fake': 'Uncertain',
    }

    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            results['description'] = 'Failed to open video file.'
            return results, 0

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        results['total_frames'] = total_frames
        results['fps'] = round(fps, 2) if fps else 0
        results['duration'] = round(total_frames / fps, 2) if fps and fps > 0 else 0
        results['resolution'] = f'{width}x{height}'

        if total_frames <= 0:
            cap.release()
            results['description'] = 'Video contains no readable frames.'
            return results, 0

        if total_frames <= max_frames:
            frame_indices = list(range(total_frames))
        else:
            frame_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int).tolist()

        frame_scores = []
        face_counts = []
        previous_gray = None
        motion_values = []

        temp_dir = tempfile.mkdtemp(prefix="dfs_video_frames_")

        for idx, frame_no in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            frame_path = os.path.join(temp_dir, f'frame_{idx+1}.jpg')
            cv2.imwrite(frame_path, frame)

            frame_result, frame_score = analyze_image(frame_path)

            frame_scores.append({
                'frame': f'Frame {idx + 1} (#{frame_no})',
                'score': frame_score,
                'face_count': frame_result.get('face_count', 0),
                'real_vs_fake': frame_result.get('real_vs_fake', 'Uncertain'),
            })

            face_counts.append(frame_result.get('face_count', 0))

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if previous_gray is not None:
                diff = cv2.absdiff(gray, previous_gray)
                motion_values.append(np.mean(diff))
            previous_gray = gray

        cap.release()

        results['frames_analyzed'] = len(frame_scores)
        results['frame_scores'] = frame_scores

        if not frame_scores:
            results['description'] = 'No valid frames could be analyzed.'
            return results, 0

        scores_only = [f['score'] for f in frame_scores]
        avg_score = round(float(np.mean(scores_only)))
        score_std = float(np.std(scores_only))

        if score_std < 8:
            temporal_score = 85
        elif score_std < 15:
            temporal_score = 70
        elif score_std < 25:
            temporal_score = 50
        else:
            temporal_score = 30
        results['temporal_variation_score'] = round(temporal_score, 2)

        if face_counts:
            face_std = float(np.std(face_counts))
            if face_std < 0.5:
                face_consistency = 85
            elif face_std < 1.5:
                face_consistency = 70
            elif face_std < 3:
                face_consistency = 50
            else:
                face_consistency = 30
        else:
            face_consistency = 50
        results['face_consistency_score'] = round(face_consistency, 2)

        if motion_values:
            motion_avg = float(np.mean(motion_values))
            if 5 < motion_avg < 35:
                motion_score = 80
            elif 2 < motion_avg <= 5 or 35 <= motion_avg < 60:
                motion_score = 65
            else:
                motion_score = 50
        else:
            motion_score = 60
        results['motion_score'] = round(motion_score, 2)

        final_score = (
            avg_score * 0.72 +
            temporal_score * 0.12 +
            face_consistency * 0.08 +
            motion_score * 0.08
        )
        final_score = int(round(max(0, min(100, final_score))))
        results['average_score'] = final_score

        if final_score >= 75:
            results['real_vs_fake'] = 'Real'
        elif final_score <= 39:
            results['real_vs_fake'] = 'Fake'
        else:
            results['real_vs_fake'] = 'Uncertain'

        results['analysis_summary'] = _generate_video_summary(results, scores_only)
        results['description'] = _generate_video_description(results, scores_only)

        return results, final_score

    except Exception as e:
        results['description'] = f'Error during video analysis: {str(e)}'
        results['analysis_summary'] = 'Video analysis failed due to an internal processing error.'
        return results, 0


def _generate_video_summary(results, scores):
    if not scores:
        return "No frames were successfully analyzed."

    min_score = min(scores)
    max_score = max(scores)
    avg = round(np.mean(scores), 2)

    if results['average_score'] >= 75:
        verdict = "likely real"
    elif results['average_score'] <= 39:
        verdict = "likely fake"
    else:
        verdict = "suspicious"

    return (
        f"The video was analyzed using {results['frames_analyzed']} sampled frames across its duration. "
        f"Frame-level scores ranged from {min_score} to {max_score}, with a base mean of {avg}. "
        f"Temporal consistency was evaluated to detect irregular authenticity shifts between frames. "
        f"Overall, the video appears {verdict}."
    )


def _generate_video_description(results, scores):
    parts = []
    parts.append(
        f"Video resolution is {results.get('resolution', 'Unknown')} at "
        f"{results.get('fps', 0)} FPS with duration {results.get('duration', 0)} seconds."
    )
    parts.append(f"{results.get('frames_analyzed', 0)} frames were sampled and individually evaluated.")
    if scores:
        parts.append(f"Frame authenticity scores ranged from {min(scores)} to {max(scores)}.")
    parts.append(f"Temporal variation score: {results.get('temporal_variation_score', 0)}.")
    parts.append(f"Face consistency score: {results.get('face_consistency_score', 0)}.")
    parts.append(f"Motion realism score: {results.get('motion_score', 0)}.")

    if results.get('average_score', 0) >= 75:
        parts.append("The video demonstrates mostly stable and natural characteristics.")
    elif results.get('average_score', 0) <= 39:
        parts.append("The video shows multiple suspicious synthetic or manipulated patterns.")
    else:
        parts.append("The video has mixed authenticity signals and should be reviewed carefully.")
    return " ".join(parts)