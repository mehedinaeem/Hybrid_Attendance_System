import os
import cv2

# Input and output folders
RAW_DIR = "dataset/raw"
OUTPUT_DIR = "dataset/resized"

# Resize size
# For FaceNet, 160x160 is commonly used.
IMG_WIDTH = 160
IMG_HEIGHT = 160

# Supported image extensions
VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

os.makedirs(OUTPUT_DIR, exist_ok=True)

for roll_number in os.listdir(RAW_DIR):
    student_raw_path = os.path.join(RAW_DIR, roll_number)

    if not os.path.isdir(student_raw_path):
        continue

    student_output_path = os.path.join(OUTPUT_DIR, roll_number)
    os.makedirs(student_output_path, exist_ok=True)

    image_files = [
        file for file in os.listdir(student_raw_path)
        if file.lower().endswith(VALID_EXTENSIONS)
    ]

    image_files.sort()

    count = 0

    print(f"Processing roll: {roll_number}")

    for image_name in image_files:
        image_path = os.path.join(student_raw_path, image_name)

        image = cv2.imread(image_path)

        if image is None:
            print(f"Could not read image: {image_path}")
            continue

        resized_image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT))

        count += 1
        new_file_name = f"{roll_number}_{count:03d}.jpg"
        save_path = os.path.join(student_output_path, new_file_name)

        cv2.imwrite(save_path, resized_image)

        print(f"Saved: {save_path}")

print("All images resized and renamed successfully.")