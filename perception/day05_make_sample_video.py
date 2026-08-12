"""用 Day 4 图片生成固定内容的短视频。"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

import cv2
import numpy as np


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def parse_args():
    parser = ArgumentParser(description="Create a reproducible sample video from an image directory")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--fps", type=float, default=10.0)
    parser.add_argument("--frames-per-image", type=int, default=10)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    return parser.parse_args()


def fit_with_letterbox(image, width: int, height: int):
    # 等比例缩放后补背景，保证统一尺寸且不拉伸图片。
    old_height, old_width = image.shape[:2]
    scale = min(width / old_width, height / old_height)
    resized = cv2.resize(image, (round(old_width * scale), round(old_height * scale)))
    canvas = np.full((height, width, 3), 24, dtype=image.dtype)
    y0 = (height - resized.shape[0]) // 2
    x0 = (width - resized.shape[1]) // 2
    canvas[y0:y0 + resized.shape[0], x0:x0 + resized.shape[1]] = resized
    return canvas


def main() -> None:
    args = parse_args()
    if args.fps <= 0 or args.frames_per_image <= 0 or args.width <= 0 or args.height <= 0:
        raise SystemExit("fps, frames-per-image, width and height must be greater than zero")
    if not args.input_dir.is_dir():
        raise SystemExit(f"input directory does not exist: {args.input_dir}")
    paths = sorted(path for path in args.input_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
    if not paths:
        raise SystemExit(f"no jpg/jpeg/png files found in {args.input_dir}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    # 使用固定编码器、FPS 和尺寸，生成可重复检查的短视频。
    writer = cv2.VideoWriter(
        str(args.output),
        cv2.VideoWriter_fourcc(*"mp4v"),
        args.fps,
        (args.width, args.height),
    )
    if not writer.isOpened():
        raise OSError(f"cannot create sample video: {args.output}")

    written = 0
    # 无论中途是否遇到坏图，都在 finally 中释放 writer。
    try:
        for path in paths:
            image = cv2.imread(str(path))
            if image is None:
                print("SKIP unreadable:", path)
                continue
            frame = fit_with_letterbox(image, args.width, args.height)
            cv2.putText(frame, path.name, (16, args.height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            for _ in range(args.frames_per_image):
                writer.write(frame)
                written += 1
    finally:
        writer.release()

    if written == 0:
        raise RuntimeError("no decodable images were written to the video")
    print(f"created: {args.output}")
    print(f"frames: {written} fps: {args.fps} duration_s: {written / args.fps:.3f}")


if __name__ == "__main__":
    main()
