import os
import cv2
from deepface import DeepFace

# Use original images, not resized images
INPUT_DIR = "dataset/raw"
OUTPUT_DIR = "dataset/processed"
REJECTED_DIR = "dataset/rejected"

# Try stronger detectors first
DETECTOR_BACKENDS = ["retinaface", "mtcnn", "opencv"]

# Final cropped face size for FaceNet
FACE_WIDTH = 160
FACE_HEIGHT = 160

# Add margin around detected face
MARGIN_RATIO = 0.30

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REJECTED_DIR, exist_ok=True)


def crop_with_margin(image, x, y, w, h, margin_ratio=0.30):
    height, width = image.shape[:2]

    margin_x = int(w * margin_ratio)
    margin_y = int(h * margin_ratio)

    x1 = max(0, x - margin_x)
    y1 = max(0, y - margin_y)
    x2 = min(width, x + w + margin_x)
    y2 = min(height, y + h + margin_y)

    return image[y1:y2, x1:x2]


for roll_number in os.listdir(INPUT_DIR):
    student_input_dir = os.path.join(INPUT_DIR, roll_number)

    if not os.path.isdir(student_input_dir):
        continue

    student_output_dir = os.path.join(OUTPUT_DIR, roll_number)
    student_rejected_dir = os.path.join(REJECTED_DIR, roll_number)

    os.makedirs(student_output_dir, exist_ok=True)
    os.makedirs(student_rejected_dir, exist_ok=True)

    image_files = [
        file for file in os.listdir(student_input_dir)
        if file.lower().endswith(VALID_EXTENSIONS)
    ]

    image_files.sort()

    saved_count = 0
    rejected_count = 0

    print(f"\nProcessing roll: {roll_number}")

    for image_name in image_files:
        image_path = os.path.join(student_input_dir, image_name)
        image = cv2.imread(image_path)

        if image is None:
            print(f"Could not read image: {image_path}")
            continue

        detected = False

        for detector in DETECTOR_BACKENDS:
            try:
                faces = DeepFace.extract_faces(
                    img_path=image_path,
                    detector_backend=detector,
                    enforce_detection=False,
                    align=True
                )

                if len(faces) == 0:
                    continue

                # Choose largest detected face
                largest_face = None
                largest_area = 0

                for face_obj in faces:
                    area = face_obj.get("facial_area", None)

                    if area is None:
                        continue

                    x = int(area["x"])
                    y = int(area["y"])
                    w = int(area["w"])
                    h = int(area["h"])

                    current_area = w * h

                    if current_area > largest_area:
                        largest_area = current_area
                        largest_face = (x, y, w, h)

                if largest_face is None:
                    continue

                x, y, w, h = largest_face

                # Reject extremely small detections
                if w < 35 or h < 35:
                    print(f"Face too small using {detector}: {image_path}")
                    continue

                cropped_face = crop_with_margin(
                    image,
                    x,
                    y,
                    w,
                    h,
                    margin_ratio=MARGIN_RATIO
                )

                if cropped_face.size == 0:
                    continue

                resized_face = cv2.resize(cropped_face, (FACE_WIDTH, FACE_HEIGHT))

                saved_count += 1
                save_name = f"{roll_number}_face_{saved_count:03d}.jpg"
                save_path = os.path.join(student_output_dir, save_name)

                cv2.imwrite(save_path, resized_face)

                print(f"Saved using {detector}: {save_path}")

                detected = True
                break

            except Exception as e:
                print(f"{detector} failed for {image_path}: {e}")

        if not detected:
            rejected_count += 1
            rejected_path = os.path.join(student_rejected_dir, image_name)
            cv2.imwrite(rejected_path, image)
            print(f"Rejected: {rejected_path}")

    print(f"Finished roll {roll_number}")
    print(f"Saved faces: {saved_count}")
    print(f"Rejected images: {rejected_count}")

print("\nPreprocessing completed.")