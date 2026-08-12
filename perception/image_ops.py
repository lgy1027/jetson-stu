"""Reusable image transformations and visual/structured result writing."""

from __future__ import annotations

from pathlib import Path
import json

import cv2
import numpy as np


def resize_keep_aspect(image: np.ndarray, width: int) -> np.ndarray:
    """Resize a BGR image while preserving its aspect ratio.

    The caller supplies only the target width. Deriving the height here keeps
    this transformation deterministic and prevents accidental image stretching.
    """
    if width <= 0:
        raise ValueError("width must be greater than zero")
    # 只指定目标宽度，高度由原始比例推导，避免拉伸图像。
    height, old_width = image.shape[:2]
    if old_width == 0:
        raise ValueError("image width must be greater than zero")
    new_height = round(height * width / old_width)
    return cv2.resize(image, (width, new_height), interpolation=cv2.INTER_AREA)


def center_crop(image: np.ndarray, crop_width: int, crop_height: int) -> np.ndarray:
    """Return a centered crop and reject dimensions outside the input image.

    A copied array is returned so later annotation or preprocessing cannot
    mutate a view into the original input image.
    """
    height, width = image.shape[:2]
    if crop_width <= 0 or crop_height <= 0:
        raise ValueError("crop dimensions must be greater than zero")
    if crop_width > width or crop_height > height:
        raise ValueError(f"crop {crop_width}x{crop_height} exceeds image {width}x{height}")
    # 使用整数中心坐标，并复制切片，确保调用方不会意外修改原图。
    x0 = (width - crop_width) // 2
    y0 = (height - crop_height) // 2
    return image[y0:y0 + crop_height, x0:x0 + crop_width].copy()


def bgr_to_normalized_rgb(image: np.ndarray) -> np.ndarray:
    """Convert uint8 BGR data into float32 RGB values in the [0, 1] range.

    OpenCV uses BGR by default, while most model preprocessing expects RGB.
    The dtype check catches accidental re-normalization or unsupported inputs.
    """
    if image.dtype != np.uint8:
        raise ValueError(f"expected uint8 BGR image, got {image.dtype}")
    # OpenCV 读入的是 BGR；模型常用 RGB，且归一化到 [0, 1] 便于后续张量处理。
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0


def annotate_detections(image: np.ndarray, detections: list[dict]) -> np.ndarray:
    """Draw ``xyxy`` boxes, labels and scores on a copy of the input image.

    The structured detection list remains the source of truth; this function
    creates only the human-readable visualization and leaves the input intact.
    """
    # 可视化只修改副本，保留原始输入用于后续数值处理和对照。
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
    # 图片给人检查，JSON 给程序消费；两者写在同一输出目录中。
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

    # 这里串起今天的数据流：等比例缩放、中心裁剪、模拟检测和双格式输出。
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
