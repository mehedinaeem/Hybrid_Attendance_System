# Hybrid Attendance System

This project implements a hybrid attendance system using fingerprint authentication, CCTV monitoring, FaceNet-based face recognition, and SVM classification. It includes a special rule for hijab/niqab cases using entry and exit fingerprint verification.

## Project Workflow
1. **Collect raw student images** inside `dataset/raw/<roll_number>/` for each student (e.g., 22102001, 22102002, 22102003).
2. **Preprocess and crop faces** into `dataset/processed/<roll_number>/` using face detection.
3. **Extract FaceNet embeddings** from processed face images.
4. **Train SVM classifier** using roll numbers as class labels.
5. **Test single/group images** for face recognition and attendance marking.
6. **Calculate attendance** using the 75% presence rule.
7. **Handle hijab/niqab cases** by verifying entry and exit with fingerprint authentication.

See scripts in the `scripts/` folder for each step.
