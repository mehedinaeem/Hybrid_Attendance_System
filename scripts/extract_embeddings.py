# extract_embeddings.py
# Script to extract FaceNet embeddings from processed face images.
import os
import joblib
import numpy as np
import pandas as pd
from deepface import DeepFace

# --------------------------------------------------
# Configuration
# --------------------------------------------------

DATASET_DIR = "dataset/processed"
MODEL_DIR = "models"
REPORT_DIR = "outputs/reports"

MODEL_NAME = "Facenet"

# Use "skip" because images in dataset/processed are already cropped faces
DETECTOR_BACKEND = "skip"

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

# --------------------------------------------------
# Create output folders
# --------------------------------------------------

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

embeddings = []
labels = []
image_paths = []

# --------------------------------------------------
# Extract embeddings
# --------------------------------------------------

print("Starting FaceNet embedding extraction...\n")

if not os.path.exists(DATASET_DIR):
    raise FileNotFoundError(f"Dataset folder not found: {DATASET_DIR}")

for roll_number in os.listdir(DATASET_DIR):
    student_dir = os.path.join(DATASET_DIR, roll_number)

    if not os.path.isdir(student_dir):
        continue

    image_files = [
        file for file in os.listdir(student_dir)
        if file.lower().endswith(VALID_EXTENSIONS)
    ]

    image_files.sort()

    if len(image_files) == 0:
        print(f"Warning: No images found for roll {roll_number}")
        continue

    print(f"Processing roll: {roll_number} ({len(image_files)} images)")

    for image_name in image_files:
        image_path = os.path.join(student_dir, image_name)

        try:
            result = DeepFace.represent(
                img_path=image_path,
                model_name=MODEL_NAME,
                detector_backend=DETECTOR_BACKEND,
                enforce_detection=False
            )

            embedding = result[0]["embedding"]

            embeddings.append(embedding)
            labels.append(roll_number)
            image_paths.append(image_path)

        except Exception as e:
            print(f"Error extracting embedding from {image_path}: {e}")

# --------------------------------------------------
# Validate results
# --------------------------------------------------

if len(embeddings) == 0:
    raise ValueError(
        "No embeddings were extracted. Check dataset/processed folders and image files."
    )

X = np.array(embeddings)
y = np.array(labels)

unique_labels = sorted(set(labels))

print("\nEmbedding extraction completed.")
print(f"Total embeddings: {len(X)}")
print(f"Total labels: {len(y)}")
print(f"Students found: {unique_labels}")

if len(unique_labels) < 2:
    print(
        "\nWarning: Only one student/class was found. "
        "You can extract embeddings, but SVM training needs at least two students/classes."
    )

# --------------------------------------------------
# Save embeddings as PKL
# --------------------------------------------------

embedding_data = {
    "embeddings": X,
    "labels": y,
    "image_paths": image_paths,
    "model_name": MODEL_NAME
}

pkl_path = os.path.join(MODEL_DIR, "embeddings.pkl")
joblib.dump(embedding_data, pkl_path)

print(f"\nSaved embedding PKL file: {pkl_path}")

# --------------------------------------------------
# Save readable CSV
# --------------------------------------------------

embedding_df = pd.DataFrame(X)
embedding_df.insert(0, "label", y)
embedding_df.insert(0, "image_path", image_paths)

csv_path = os.path.join(REPORT_DIR, "embeddings.csv")
embedding_df.to_csv(csv_path, index=False)

print(f"Saved readable embeddings CSV: {csv_path}")

print("\nDone.")