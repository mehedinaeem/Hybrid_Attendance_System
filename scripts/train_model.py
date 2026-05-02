import os
import joblib
import numpy as np
import pandas as pd

from deepface import DeepFace
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Dataset folder containing cropped faces
DATASET_DIR = "dataset/processed"

# Output folders
MODEL_DIR = "models"
REPORT_DIR = "outputs/reports"

# FaceNet model
MODEL_NAME = "Facenet"

# Since faces are already cropped, use skip
DETECTOR_BACKEND = "skip"

TEST_SIZE = 0.20
RANDOM_STATE = 42

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

embeddings = []
labels = []
image_paths = []

print("Extracting FaceNet embeddings...\n")

for roll_number in os.listdir(DATASET_DIR):
    student_dir = os.path.join(DATASET_DIR, roll_number)

    if not os.path.isdir(student_dir):
        continue

    print(f"Processing roll: {roll_number}")

    image_files = [
        file for file in os.listdir(student_dir)
        if file.lower().endswith(VALID_EXTENSIONS)
    ]

    image_files.sort()

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

X = np.array(embeddings)
y = np.array(labels)

print("\nTotal embeddings:", len(X))
print("Total labels:", len(y))
print("Students:", sorted(set(y)))

if len(X) == 0:
    raise ValueError("No embeddings found. Check dataset/processed folder.")

# Save embeddings for research/reuse
embedding_data = {
    "embeddings": X,
    "labels": y,
    "image_paths": image_paths
}
joblib.dump(embedding_data, os.path.join(MODEL_DIR, "embeddings.pkl"))

# Save readable embeddings CSV
embedding_df = pd.DataFrame(X)
embedding_df.insert(0, "label", y)
embedding_df.insert(0, "image_path", image_paths)
embedding_df.to_csv(os.path.join(REPORT_DIR, "embeddings.csv"), index=False)

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# 80/20 train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y_encoded
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

# Train SVM classifier
classifier = SVC(kernel="linear", probability=True)
classifier.fit(X_train, y_train)

# Test model
y_pred = classifier.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
report = classification_report(
    y_test,
    y_pred,
    target_names=label_encoder.classes_
)
matrix = confusion_matrix(y_test, y_pred)

print("\nAccuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:")
print(report)
print("\nConfusion Matrix:")
print(matrix)

# Save model files
joblib.dump(classifier, os.path.join(MODEL_DIR, "face_classifier.pkl"))
joblib.dump(label_encoder, os.path.join(MODEL_DIR, "label_encoder.pkl"))

# Save training report
report_path = os.path.join(REPORT_DIR, "training_report.txt")

with open(report_path, "w", encoding="utf-8") as f:
    f.write("FaceNet + SVM Training Report\n")
    f.write("=============================\n\n")
    f.write(f"Model Name: {MODEL_NAME}\n")
    f.write(f"Total Embeddings: {len(X)}\n")
    f.write(f"Training Samples: {len(X_train)}\n")
    f.write(f"Testing Samples: {len(X_test)}\n")
    f.write(f"Accuracy: {round(accuracy * 100, 2)}%\n\n")
    f.write("Classification Report:\n")
    f.write(report)
    f.write("\nConfusion Matrix:\n")
    f.write(str(matrix))

print("\nTraining completed successfully.")
print("Saved files:")
print("models/embeddings.pkl")
print("models/face_classifier.pkl")
print("models/label_encoder.pkl")
print("outputs/reports/embeddings.csv")
print("outputs/reports/training_report.txt")