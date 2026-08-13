# Secondary Face Dataset

## Overview

The secondary dataset is derived from the **Pins Face Recognition** dataset and
is kept separate from the original student images in `dataset/processed`.

- Selection: person folders are sorted alphabetically, then the first 40
  folders with at least 50 readable, unique images are selected.
- Random seed: `42`
- Persons: `40`
- Images per person: `50`
- Total images: `2,000`
- Output: `dataset/secondary_processed`

## Preprocessing

The preparation script reads candidate files directly from `archive.zip`; it
does not extract the full archive. Each selected image has its EXIF orientation
corrected, is converted to RGB, center-cropped to a square without stretching,
and resized to 160 × 160 pixels using high-quality Lanczos interpolation. It is
saved as a JPEG without random augmentation. Unreadable and within-class
duplicate images are skipped.

## Naming and reproducibility

Class directories use continuous IDs from `22102001` through `22102040`.
Images follow the pattern `CLASS_ID_face_NNN.jpg`. `identity_mapping.csv`
records each anonymized class's source person and folder, while
`dataset_summary.csv` records validation results.

> **Warning:** `22102001`–`22102040` are anonymized experimental class labels.
> They are not the real identities of the people and are not student roll
> numbers.

Run from the repository root:

```bash
python scripts/prepare_secondary_dataset.py \
    --archive /home/mehedinaeem/Downloads/archive.zip \
    --output dataset/secondary_processed \
    --persons 40 \
    --images-per-person 50 \
    --image-size 160 \
    --seed 42
```

Use `--overwrite` only when intentionally replacing an existing secondary
dataset. The script prepares and validates a temporary dataset before replacing
the output.
