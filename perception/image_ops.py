"""Reusable image transformations and visual/structured result writing."""

from __future__ import annotations

from pathlib import Path
import json

import cv2
import numpy as np


def resize_keep_aspect(image: np.ndarray, width: int) -> np.ndarray:
    """Resize BGR image to width while preserving its aspect ratio."""
    if width <= 0:
        raise ValueError("width must be greater than zero")
    height, old_width = image.shape[:2]
    if old_width == 0:
        raise ValueError("image width must be greater than zero")
    new_height = round(height * width / old_width)
    return cv2.resize(image, (width, new_height), interpolation=cv2.INTER_AREA)


def center_crop(image: np.ndarray, crop_width: int, crop_height: int) -> np.ndarray:
    """Return a centered crop; reject a crop that does not fit the input."""
    height, width = image.shape[:2]
    if crop_width <= 0 or crop_height <= 0:
        raise ValueError("crop dimensions must be greater than zero")
    if crop_width > width or crop_height > height:
        raise ValueError(f"crop {crop_width}x{crop_height} exceeds image {width}x{height}")
    x0 = (width - crop_width) // 2
    y0 = (height - crop_height) // 2
    return image[y0:y0 + crop_height, x0:x0 + crop_width].copy()


def bgr_to_normalized_rgb(image: np.ndarray) -> np.ndarray:
    """Convert uint8 BGR data into float32 RGB values in the [0, 1] range."""
    if image.dtype != np.uint8:
        raise ValueError(f"expected uint8 BGR image, got {image.dtype}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0


def annotate_detections(image: np.ndarray, detections: list[dict]) -> np.ndarray:
    """Draw xyxy boxes, labels and scores without changing the input array."""
    annotated = image.copy()
    for item in detections:
        x1, y1, x2, y2 = (int(value) for value in item["bbox_xyxy"])
        label = f'{item["label"]} {item["score"]:.2f}'
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (80, 240, 120), 2)
        cv2.putText(annotated, label, (x1, max(22, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(annotated, label, (x1, max(22, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 1)
    return annotated


def write_result_json(path: Path, image: np.ndarray, transform: dict, detections: list[dict]) -> None:
    """Write machine-readable evidence next to a visual result."""
    path.parent.mkdir(parents=True, exist_ok=True)
    height, width = image.shape[:2]
    payload = {
        "image_size": {"width": width, "height": height},
        "transform": transform,
        "detections": detections,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    input_path = Path("perception/inputs/wide.png")
    image = cv2.imread(str(input_path))
    if image is None:
        raise FileNotFoundError(f"run Day 1 first; cannot read {input_path}")

    resized = resize_keep_aspect(image, 480)
    cropped = center_crop(resized, 360, 240)
    detections = [{"label": "demo-object", "score": 0.87, "bbox_xyxy": [70, 45, 285, 205]}]
    annotated = annotate_detections(cropped, detections)
    output_dir = Path("perception/outputs/day02")
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / "wide_annotated.png"
    if not cv2.imwrite(str(image_path), annotated):
        raise OSError(f"failed to write output image: {image_path}")
    write_result_json(output_dir / "wide_annotated.json", annotated, {"resize_width": 480, "center_crop": [360, 240]}, detections)
    print("saved:", image_path)
    print("saved:", output_dir / "wide_annotated.json")
    print("normalized RGB dtype/range:", bgr_to_normalized_rgb(cropped).dtype, "[0, 1]")


if __name__ == "__main__":
    main()
