# video_attendance_demo.py
# Video-based attendance demo using FaceNet embeddings and the trained SVM model.
import argparse
from collections import defaultdict
from pathlib import Path

import cv2
import joblib
import numpy as np
import pandas as pd
from deepface import DeepFace


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "opencv"
# Cropped faces are passed to FaceNet, so representation can skip a second detector.
EMBEDDING_DETECTOR_BACKEND = "skip"

FRAME_INTERVAL_SECONDS = 3
CONFIDENCE_THRESHOLD = 50.0
ATTENDANCE_THRESHOLD = 70.0
MIN_PRESENT_PERCENTAGE = 60.0
ATTENDANCE_MODE = "percentage"
ATTENDANCE_MODES = ("percentage", "any")

DEFAULT_VIDEO_PATH = BASE_DIR / "dataset" / "test_videos" / "classroom_demo.mp4"
CLASSIFIER_PATH = BASE_DIR / "models" / "face_classifier.pkl"
LABEL_ENCODER_PATH = BASE_DIR / "models" / "label_encoder.pkl"

FRAME_LOG_PATH = BASE_DIR / "attendance_logs" / "video_frame_presence_log.csv"
FINAL_ATTENDANCE_PATH = BASE_DIR / "attendance_logs" / "video_final_attendance.csv"
MARKED_VIDEO_PATH = BASE_DIR / "outputs" / "marked_videos" / "classroom_demo_marked.mp4"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run video attendance recognition with FaceNet + SVM."
    )
    parser.add_argument(
        "--video",
        default=str(DEFAULT_VIDEO_PATH),
        help="Input video path. Default: dataset/test_videos/classroom_demo.mp4",
    )
    parser.add_argument(
        "--detector-backend",
        default=DETECTOR_BACKEND,
        help="DeepFace detector backend. Default: opencv",
    )
    parser.add_argument(
        "--frame-interval",
        type=float,
        default=FRAME_INTERVAL_SECONDS,
        help="Seconds between processed frames. Default: 3",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=CONFIDENCE_THRESHOLD,
        help="Minimum prediction confidence for a known student. Default: 50",
    )
    parser.add_argument(
        "--attendance-threshold",
        type=float,
        default=ATTENDANCE_THRESHOLD,
        help="Presence percentage required for Present status in percentage mode. Default: 70",
    )
    parser.add_argument(
        "--attendance-mode",
        choices=ATTENDANCE_MODES,
        default=ATTENDANCE_MODE,
        help=(
            "Attendance mode: 'percentage' uses threshold percentage, "
            "'any' marks Present if the student is detected in any processed frame. "
            "Default: percentage"
        ),
    )
    return parser.parse_args()


def resolve_path(path_value):
    path = Path(path_value)
    if path.is_absolute():
        return path
    return BASE_DIR / path


def ensure_directories(input_video_path):
    input_video_path.parent.mkdir(parents=True, exist_ok=True)
    FRAME_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    FINAL_ATTENDANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKED_VIDEO_PATH.parent.mkdir(parents=True, exist_ok=True)


def validate_required_files(input_video_path):
    missing_files = [
        path
        for path in (CLASSIFIER_PATH, LABEL_ENCODER_PATH, input_video_path)
        if not path.exists()
    ]

    if missing_files:
        missing_text = "\n".join(f"- {path}" for path in missing_files)
        raise FileNotFoundError(f"Required file(s) not found:\n{missing_text}")


def load_trained_model():
    classifier = joblib.load(CLASSIFIER_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)

    if not hasattr(classifier, "predict_proba"):
        raise AttributeError(
            "The loaded classifier does not support predict_proba(). "
            "Train the SVM with probability=True."
        )

    known_students = [str(student_id) for student_id in label_encoder.classes_]
    if not known_students:
        raise ValueError("No student labels were found in the label encoder.")

    return classifier, label_encoder, known_students


def clamp_face_box(face_area, frame_width, frame_height):
    x = int(face_area.get("x", 0))
    y = int(face_area.get("y", 0))
    w = int(face_area.get("w", 0))
    h = int(face_area.get("h", 0))

    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(frame_width, x + w)
    y2 = min(frame_height, y + h)

    if x2 <= x1 or y2 <= y1:
        return None

    return x1, y1, x2, y2


def detect_faces(frame, detector_backend):
    try:
        return DeepFace.extract_faces(
            img_path=frame,
            detector_backend=detector_backend,
            enforce_detection=True,
            align=True,
        )
    except ValueError:
        return []
    except Exception as error:
        print(f"Face detection error: {error}")
        return []


def recognize_face(face_crop, classifier, label_encoder, confidence_threshold):
    result = DeepFace.represent(
        img_path=face_crop,
        model_name=MODEL_NAME,
        detector_backend=EMBEDDING_DETECTOR_BACKEND,
        enforce_detection=False,
    )

    embedding = np.array(result[0]["embedding"]).reshape(1, -1)
    probabilities = classifier.predict_proba(embedding)[0]
    best_index = int(np.argmax(probabilities))
    encoded_label = classifier.classes_[best_index]
    confidence = float(probabilities[best_index] * 100)

    if confidence < confidence_threshold:
        return "Unknown", confidence

    student_id = label_encoder.inverse_transform([encoded_label])[0]
    return str(student_id), confidence


def recognize_frame(frame, classifier, label_encoder, detector_backend, confidence_threshold):
    frame_height, frame_width = frame.shape[:2]
    annotations = []
    detected_students = set()
    detected_faces = detect_faces(frame, detector_backend)

    for face in detected_faces:
        face_box = clamp_face_box(
            face.get("facial_area", {}),
            frame_width=frame_width,
            frame_height=frame_height,
        )

        if face_box is None:
            continue

        x1, y1, x2, y2 = face_box
        face_crop = frame[y1:y2, x1:x2]

        if face_crop.size == 0:
            continue

        try:
            student_id, confidence = recognize_face(
                face_crop=face_crop,
                classifier=classifier,
                label_encoder=label_encoder,
                confidence_threshold=confidence_threshold,
            )
        except Exception as error:
            print(f"Recognition error for one face: {error}")
            student_id = "Unknown"
            confidence = 0.0

        if student_id != "Unknown":
            detected_students.add(student_id)

        annotations.append(
            {
                "box": face_box,
                "student_id": student_id,
                "confidence": confidence,
            }
        )

    return annotations, detected_students


def draw_label(frame, text, x, y, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 2
    text_size, baseline = cv2.getTextSize(text, font, font_scale, thickness)
    text_width, text_height = text_size

    top = max(0, y - text_height - baseline - 8)
    bottom = max(text_height + baseline + 8, y)
    right = min(frame.shape[1], x + text_width + 10)

    cv2.rectangle(frame, (x, top), (right, bottom), color, cv2.FILLED)
    cv2.putText(
        frame,
        text,
        (x + 5, bottom - baseline - 4),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )


def draw_annotations(frame, annotations):
    for annotation in annotations:
        x1, y1, x2, y2 = annotation["box"]
        student_id = annotation["student_id"]
        confidence = annotation["confidence"]
        color = (0, 180, 0) if student_id != "Unknown" else (0, 165, 255)
        label = f"{student_id} ({confidence:.1f}%)"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        draw_label(frame, label, x1, y1, color)


def draw_frame_info(frame, video_frame_index, processed_frame_no, is_processed_frame):
    status = "processed" if is_processed_frame else "skipped"
    text = (
        f"Video frame: {video_frame_index} | "
        f"Processed frame: {processed_frame_no} | {status}"
    )

    cv2.rectangle(frame, (10, 10), (min(frame.shape[1] - 10, 560), 48), (0, 0, 0), -1)
    cv2.putText(
        frame,
        text,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


def create_final_attendance(
    known_students,
    detected_counts,
    total_processed_frames,
    threshold,
    mode,
):
    rows = []

    for student_id in known_students:
        detected_frames = int(detected_counts.get(student_id, 0))
        if total_processed_frames > 0:
            presence_percentage = (detected_frames / total_processed_frames) * 100
        else:
            presence_percentage = 0.0

        if mode == "any":
            status = "Present" if detected_frames > 0 else "Absent"
            threshold_percentage = 0.0
        else:
            effective_threshold = min(threshold, MIN_PRESENT_PERCENTAGE)
            status = "Present" if presence_percentage >= effective_threshold else "Absent"
            threshold_percentage = float(threshold)

        rows.append(
            {
                "student_id": student_id,
                "detected_frames": detected_frames,
                "total_processed_frames": int(total_processed_frames),
                "presence_percentage": round(presence_percentage, 2),
                "threshold_percentage": threshold_percentage,
                "attendance_mode": mode,
                "status": status,
            }
        )

    return pd.DataFrame(rows)


def process_video(
    input_video_path,
    classifier,
    label_encoder,
    known_students,
    detector_backend,
    frame_interval_seconds,
    confidence_threshold,
    attendance_threshold,
    attendance_mode,
):
    video_capture = cv2.VideoCapture(str(input_video_path))
    if not video_capture.isOpened():
        raise OSError(f"Could not open video file: {input_video_path}")

    fps = float(video_capture.get(cv2.CAP_PROP_FPS))
    total_video_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if width <= 0 or height <= 0:
        video_capture.release()
        raise ValueError("Could not read video width/height from the input file.")

    output_fps = fps if fps > 0 else 25.0
    frame_step = max(1, int(round(output_fps * frame_interval_seconds)))

    video_writer = cv2.VideoWriter(
        str(MARKED_VIDEO_PATH),
        cv2.VideoWriter_fourcc(*"mp4v"),
        output_fps,
        (width, height),
    )

    if not video_writer.isOpened():
        video_capture.release()
        raise OSError(f"Could not create marked video: {MARKED_VIDEO_PATH}")

    print("Video Attendance Demo")
    print("---------------------")
    print(f"Input video: {input_video_path}")
    print(f"FPS: {output_fps:.2f}")
    print(f"Total frames: {total_video_frames}")
    print(f"Resolution: {width}x{height}")
    print(f"Processing one frame every {frame_interval_seconds} seconds")
    print(f"Frame step: {frame_step}")
    print(f"Detector backend: {detector_backend}")
    print(f"Attendance mode: {attendance_mode}")
    print()
    detected_counts = defaultdict(int)
    frame_log_rows = []
    processed_frame_no = 0
    video_frame_index = 0
    latest_annotations = []

    try:
        while True:
            success, frame = video_capture.read()
            if not success:
                break

            is_processed_frame = video_frame_index % frame_step == 0

            if is_processed_frame:
                processed_frame_no += 1
                timestamp_seconds = video_frame_index / output_fps

                if total_video_frames > 0:
                    progress = (video_frame_index / total_video_frames) * 100
                    progress_text = f"{progress:.1f}%"
                else:
                    progress_text = "unknown progress"

                print(
                    f"Processing frame {processed_frame_no}: "
                    f"video frame {video_frame_index}, "
                    f"time {timestamp_seconds:.2f}s, {progress_text}"
                )

                annotations, detected_students = recognize_frame(
                    frame=frame,
                    classifier=classifier,
                    label_encoder=label_encoder,
                    detector_backend=detector_backend,
                    confidence_threshold=confidence_threshold,
                )
                latest_annotations = annotations

                for student_id in known_students:
                    detected = student_id in detected_students
                    if detected:
                        detected_counts[student_id] += 1

                    frame_log_rows.append(
                        {
                            "processed_frame_no": processed_frame_no,
                            "video_frame_index": video_frame_index,
                            "timestamp_seconds": round(timestamp_seconds, 2),
                            "student_id": student_id,
                            "detected": detected,
                        }
                    )

            draw_annotations(frame, latest_annotations)
            draw_frame_info(
                frame=frame,
                video_frame_index=video_frame_index,
                processed_frame_no=processed_frame_no,
                is_processed_frame=is_processed_frame,
            )
            video_writer.write(frame)
            video_frame_index += 1

    finally:
        video_capture.release()
        video_writer.release()

    frame_log_df = pd.DataFrame(
        frame_log_rows,
        columns=[
            "processed_frame_no",
            "video_frame_index",
            "timestamp_seconds",
            "student_id",
            "detected",
        ],
    )
    final_attendance_df = create_final_attendance(
        known_students=known_students,
        detected_counts=detected_counts,
        total_processed_frames=processed_frame_no,
        threshold=attendance_threshold,
        mode=attendance_mode,
    )

    frame_log_df.to_csv(FRAME_LOG_PATH, index=False)
    final_attendance_df.to_csv(FINAL_ATTENDANCE_PATH, index=False)

    print()
    print("Processing completed.")
    print(f"Processed frames: {processed_frame_no}")
    print(f"Frame-wise log saved to: {FRAME_LOG_PATH}")
    print(f"Final attendance saved to: {FINAL_ATTENDANCE_PATH}")
    print(f"Marked video saved to: {MARKED_VIDEO_PATH}")
    print()
    print("Final attendance:")
    print(final_attendance_df)

    return final_attendance_df


def main():
    args = parse_args()
    input_video_path = resolve_path(args.video)

    if args.frame_interval <= 0:
        raise ValueError("--frame-interval must be greater than 0.")

    ensure_directories(input_video_path)
    validate_required_files(input_video_path)

    classifier, label_encoder, known_students = load_trained_model()

    process_video(
        input_video_path=input_video_path,
        classifier=classifier,
        label_encoder=label_encoder,
        known_students=known_students,
        detector_backend=args.detector_backend,
        frame_interval_seconds=args.frame_interval,
        confidence_threshold=args.confidence_threshold,
        attendance_threshold=args.attendance_threshold,
        attendance_mode=args.attendance_mode,
    )


if __name__ == "__main__":
    main()
