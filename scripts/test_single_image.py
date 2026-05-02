# test_single_image.py
# Script to test face recognition on a single image and predict the student roll number.
import os
import joblib
import numpy as np
from deepface import DeepFace

MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "opencv"

IMAGE_PATH = "dataset/test_images/single_test.jpg"

classifier = joblib.load("models/face_classifier.pkl")
label_encoder = joblib.load("models/label_encoder.pkl")

if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(f"Test image not found: {IMAGE_PATH}")

result = DeepFace.represent(
    img_path=IMAGE_PATH,
    model_name=MODEL_NAME,
    detector_backend=DETECTOR_BACKEND,
    enforce_detection=False
)

embedding = np.array(result[0]["embedding"]).reshape(1, -1)

prediction = classifier.predict(embedding)
probabilities = classifier.predict_proba(embedding)

predicted_roll = label_encoder.inverse_transform(prediction)[0]
confidence = np.max(probabilities) * 100

print("Predicted Roll:", predicted_roll)
print("Confidence:", round(confidence, 2), "%")