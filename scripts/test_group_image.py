# test_group_image.py
# Script to test face recognition on group images and identify multiple students.
import argparse
from pathlib import Path
import cv2
import joblib
import numpy as np
from deepface import DeepFace

MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "opencv"
EMBEDDING_DETECTOR_BACKEND = "skip"
CLASSIFIER_PATH = Path("models") / "face_classifier.pkl"
LABEL_ENCODER_PATH = Path("models") / "label_encoder.pkl"
DEFAULT_IMAGE_PATH = Path("dataset") / "test_images" / "group_image.png"
DEFAULT_OUTPUT_PATH = Path("outputs") / "marked_group_images" / "group_image_marked.png"
DEFAULT_CONFIDENCE_THRESHOLD = 50.0


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Recognize multiple students in a group image using FaceNet + SVM."
    )
    parser.add_argument(
        "--image",
        default=str(DEFAULT_IMAGE_PATH),
        help="Path to the group image to test. Default: dataset/test_images/group_test.jpg",
    )
    parser.add_argument(
        "--classifier",
        default=str(CLASSIFIER_PATH),
        help="Path to the trained face classifier pickle file.",
    )
    parser.add_argument(
        "--label-encoder",
        default=str(LABEL_ENCODER_PATH),
        help="Path to the label encoder pickle file.",
    )
    parser.add_argument(
        "--detector-backend",
        default=DETECTOR_BACKEND,
        help="DeepFace detector backend used for face detection. Default: opencv",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=DEFAULT_CONFIDENCE_THRESHOLD,
        help="Minimum prediction confidence for a student to be considered known.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Optional path to save the annotated result image.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the annotated image in a window after processing.",
    )
    return parser.parse_args()


def validate_paths(image_path, classifier_path, label_encoder_path):
    missing = []
    for path in (image_path, classifier_path, label_encoder_path):
        if not path.exists():
            missing.append(path)

    if missing:
        missing_list = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Required file(s) not found:\n{missing_list}")


def detect_faces(image_path, detector_backend):
    try:
        faces = DeepFace.extract_faces(
            img_path=str(image_path),
            detector_backend=detector_backend,
            enforce_detection=False,
            align=True,
        )
        return faces if isinstance(faces, list) else []
    except Exception as error:
        print(f"Face detection failed: {error}")
        return []


def recognize_face(face_image, classifier, label_encoder, confidence_threshold):
    result = DeepFace.represent(
        img_path=face_image,
        model_name=MODEL_NAME,
        detector_backend=EMBEDDING_DETECTOR_BACKEND,
        enforce_detection=False,
    )

    embedding = np.array(result[0]["embedding"]).reshape(1, -1)
    probabilities = classifier.predict_proba(embedding)[0]
    best_index = int(np.argmax(probabilities))
    best_confidence = float(probabilities[best_index] * 100)
    predicted_encoded = classifier.classes_[best_index]
    predicted_roll = label_encoder.inverse_transform([predicted_encoded])[0]

    if best_confidence < confidence_threshold:
        return "Unknown", best_confidence

    return str(predicted_roll), best_confidence


def draw_annotations(image, annotations):
    for annotation in annotations:
        x1, y1, x2, y2 = annotation["box"]
        student_id = annotation["student_id"]
        confidence = annotation["confidence"]
        color = (0, 180, 0) if student_id != "Unknown" else (0, 165, 255)
        label_text = f"{student_id} ({confidence:.1f}%)"

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            image,
            label_text,
            (x1, max(y1 - 10, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )


def clamp_face_box(face_area, image_width, image_height):
    x = int(face_area.get("x", 0))
    y = int(face_area.get("y", 0))
    w = int(face_area.get("w", 0))
    h = int(face_area.get("h", 0))

    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(image_width, x + w)
    y2 = min(image_height, y + h)

    if x2 <= x1 or y2 <= y1:
        return None

    return x1, y1, x2, y2


def main():
    args = parse_arguments()
    image_path = Path(args.image)
    classifier_path = Path(args.classifier)
    label_encoder_path = Path(args.label_encoder)
    output_path = Path(args.output)

    validate_paths(image_path, classifier_path, label_encoder_path)

    classifier = joblib.load(classifier_path)
    label_encoder = joblib.load(label_encoder_path)

    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    detected_faces = detect_faces(image_path, args.detector_backend)
    if not detected_faces:
        print("No faces were detected in the image.")
        return

    annotations = []
    print(f"Detected {len(detected_faces)} face(s) in the image.")

    for face_index, face_data in enumerate(detected_faces, start=1):
        face_image = face_data.get("face")
        face_area = face_data.get("facial_area") or face_data.get("region") or {}

        if face_image is None:
            print(f"Skipping face {face_index}: missing cropped face image.")
            continue

        box = clamp_face_box(face_area, image.shape[1], image.shape[0])
        if box is None:
            print(f"Skipping face {face_index}: invalid bounding box.")
            continue

        try:
            student_id, confidence = recognize_face(
                face_image,
                classifier,
                label_encoder,
                args.confidence_threshold,
            )
        except Exception as error:
            print(f"Recognition error for face {face_index}: {error}")
            student_id = "Unknown"
            confidence = 0.0

        annotations.append(
            {
                "box": box,
                "student_id": student_id,
                "confidence": confidence,
            }
        )
        print(
            f"Face {face_index}: {student_id} with confidence {confidence:.2f}%"
        )

    if annotations:
        draw_annotations(image, annotations)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), image)
            print(f"Annotated image saved to: {output_path}")

        if args.show:
            cv2.imshow("Group Image Recognition", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
