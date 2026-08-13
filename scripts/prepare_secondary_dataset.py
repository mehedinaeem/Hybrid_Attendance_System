#!/usr/bin/env python3
"""Create and validate a balanced anonymized dataset from a ZIP archive."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import random
import shutil
import sys
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterable

from PIL import Image, ImageOps, UnidentifiedImageError

SOURCE_DATASET = "Pins Face Recognition"
FIRST_CLASS_ID = 22102001
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True, help="Source ZIP file")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--persons", type=int, default=40)
    parser.add_argument("--images-per-person", type=int, default=50)
    parser.add_argument("--image-size", type=int, default=160)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing output directory after successful preparation",
    )
    return parser.parse_args()


def source_folder_for(member_name: str) -> str | None:
    """Return the immediate pins_* folder, allowing an archive root directory."""
    parts = PurePosixPath(member_name).parts
    for part in parts[:-1]:
        if part.startswith("pins_"):
            return part
    return None


def collect_members(archive: zipfile.ZipFile) -> dict[str, list[zipfile.ZipInfo]]:
    folders: dict[str, list[zipfile.ZipInfo]] = defaultdict(list)
    for info in archive.infolist():
        if info.is_dir():
            continue
        folder = source_folder_for(info.filename)
        if folder and PurePosixPath(info.filename).suffix.lower() in IMAGE_SUFFIXES:
            folders[folder].append(info)
    return dict(folders)


def processed_tree_digest(processed_dir: Path) -> str | None:
    """Hash relative paths and contents to prove the original dataset is unchanged."""
    if not processed_dir.exists():
        return None
    digest = hashlib.sha256()
    for path in sorted(item for item in processed_dir.rglob("*") if item.is_file()):
        digest.update(path.relative_to(processed_dir).as_posix().encode("utf-8"))
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def prepare_image(stream: BinaryIO, image_size: int) -> Image.Image:
    """Decode, orient, RGB-convert, square-crop, and resize without stretching."""
    with Image.open(stream) as source:
        source.load()
        oriented = ImageOps.exif_transpose(source)
        rgb = oriented.convert("RGB")
        width, height = rgb.size
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        square = rgb.crop((left, top, left + side, top + side))
        return square.resize((image_size, image_size), Image.Resampling.LANCZOS)


def select_and_save(
    archive: zipfile.ZipFile,
    candidates: Iterable[zipfile.ZipInfo],
    destination: Path,
    class_id: str,
    count: int,
    image_size: int,
    rng: random.Random,
) -> int:
    """Shuffle candidates, skip unreadable/duplicate images, and save up to count."""
    ordered = list(candidates)
    rng.shuffle(ordered)
    hashes: set[str] = set()
    saved = 0
    destination.mkdir(parents=True)

    for info in ordered:
        try:
            data = archive.read(info)
            image = prepare_image(io.BytesIO(data), image_size)
            buffer = io.BytesIO()
            image.save(buffer, "JPEG", quality=95, subsampling=0, optimize=True)
            jpeg = buffer.getvalue()
        except (OSError, ValueError, UnidentifiedImageError, zipfile.BadZipFile):
            continue

        image_hash = hashlib.sha256(jpeg).hexdigest()
        if image_hash in hashes:
            continue
        hashes.add(image_hash)
        saved += 1
        filename = f"{class_id}_face_{saved:03d}.jpg"
        (destination / filename).write_bytes(jpeg)
        if saved == count:
            break
    return saved


def write_csvs(
    output: Path,
    records: list[tuple[str, str]],
    images_per_person: int,
    image_size: int,
) -> None:
    with (output / "identity_mapping.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["class_id", "source_person", "source_folder", "selected_image_count", "source_dataset"]
        )
        for class_id, folder in records:
            writer.writerow(
                [class_id, folder.removeprefix("pins_"), folder, images_per_person, SOURCE_DATASET]
            )

    with (output / "dataset_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["class_id", "image_count", "valid_images", "image_width", "image_height", "status"]
        )
        for class_id, _ in records:
            writer.writerow(
                [class_id, images_per_person, images_per_person, image_size, image_size, "OK"]
            )


def validate_dataset(
    output: Path, persons: int, images_per_person: int, image_size: int
) -> None:
    expected_ids = [str(FIRST_CLASS_ID + index) for index in range(persons)]
    class_dirs = sorted(path.name for path in output.iterdir() if path.is_dir())
    if class_dirs != expected_ids:
        raise RuntimeError("Class folders are missing, extra, or non-continuous")

    total = 0
    for class_id in expected_ids:
        images = sorted((output / class_id).glob("*.jpg"))
        if len(images) != images_per_person:
            raise RuntimeError(f"{class_id} contains {len(images)} JPEGs")
        hashes: set[str] = set()
        for path in images:
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if digest in hashes:
                raise RuntimeError(f"Duplicate image in class {class_id}: {path.name}")
            hashes.add(digest)
            try:
                with Image.open(io.BytesIO(data)) as image:
                    image.load()
                    if image.format != "JPEG" or image.mode != "RGB":
                        raise RuntimeError(f"Invalid format/mode: {path}")
                    if image.size != (image_size, image_size):
                        raise RuntimeError(f"Invalid dimensions: {path}")
            except (OSError, UnidentifiedImageError) as error:
                raise RuntimeError(f"Unreadable output image: {path}") from error
        total += len(images)

    if total != persons * images_per_person:
        raise RuntimeError(f"Expected {persons * images_per_person} images, found {total}")
    with (output / "identity_mapping.csv").open(newline="", encoding="utf-8") as f:
        if len(list(csv.DictReader(f))) != persons:
            raise RuntimeError("identity_mapping.csv has an invalid record count")


def build_dataset(args: argparse.Namespace) -> None:
    if args.persons < 1 or args.images_per_person < 1 or args.image_size < 1:
        raise ValueError("persons, images-per-person, and image-size must be positive")
    archive_path = args.archive.resolve()
    output = args.output.resolve()
    if not archive_path.is_file():
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    if output.exists() and not args.overwrite:
        raise FileExistsError(f"Output already exists: {output} (use --overwrite to replace it)")

    processed_dir = output.parent / "processed"
    processed_before = processed_tree_digest(processed_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    rng = random.Random(args.seed)
    records: list[tuple[str, str]] = []

    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = collect_members(archive)
            print(f"Found {len(members)} person folders in {archive_path}")
            for folder in sorted(members):
                if len(records) == args.persons:
                    break
                class_id = str(FIRST_CLASS_ID + len(records))
                class_dir = temp_dir / class_id
                saved = select_and_save(
                    archive,
                    members[folder],
                    class_dir,
                    class_id,
                    args.images_per_person,
                    args.image_size,
                    rng,
                )
                if saved < args.images_per_person:
                    shutil.rmtree(class_dir)
                    print(f"Skipped {folder}: only {saved} readable unique images")
                    continue
                records.append((class_id, folder))
                print(f"[{len(records):02d}/{args.persons:02d}] {folder} -> {class_id}")

        if len(records) != args.persons:
            raise RuntimeError(
                f"Only {len(records)} persons have at least {args.images_per_person} "
                "readable unique images"
            )
        write_csvs(temp_dir, records, args.images_per_person, args.image_size)
        validate_dataset(temp_dir, args.persons, args.images_per_person, args.image_size)
        if processed_tree_digest(processed_dir) != processed_before:
            raise RuntimeError(f"Original dataset changed during preparation: {processed_dir}")

        if output.exists():
            shutil.rmtree(output)
        temp_dir.replace(output)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

    print("\nSecondary dataset preparation completed")
    print(f"Classes: {args.persons}")
    print(f"Images per class: {args.images_per_person}")
    print(f"Total images: {args.persons * args.images_per_person}")
    print(f"Image size: {args.image_size} × {args.image_size}")
    print(f"Output: {args.output}")
    print("Validation: PASSED")


def main() -> int:
    try:
        build_dataset(parse_args())
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
