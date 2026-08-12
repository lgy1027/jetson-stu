from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
import sys

import cv2


def parse_args():
    parser = ArgumentParser(description="Resize and annotate one image")
    parser.add_argument("input", type=Path, help="input image path")
    parser.add_argument("output", type=Path, help="output image path")
    parser.add_argument("--width", type=int, default=480, help="output width in pixels")
    return parser.parse_args()


def main():
    args = parse_args()

    # 先验证参数和路径，再调用 OpenCV，避免产生空的“成功”输出文件。
    if args.width <= 0:
        raise ValueError("--width must be greater than zero")
    if not args.input.is_file():
        raise FileNotFoundError(f"input image does not exist: {args.input}")

    image = cv2.imread(str(args.input))
    if image is None:
        raise ValueError(f"OpenCV could not decode image: {args.input}")

    # 根据原始宽高比计算新高度，保持图片不变形。
    height, width = image.shape[:2]
    new_height = round(height * args.width / width)
    resized = cv2.resize(image, (args.width, new_height), interpolation=cv2.INTER_AREA)

    # 白色文字加深色描边，在亮暗背景上都能看清处理信息。
    label = f"{args.input.name} | {width}x{height} -> {args.width}x{new_height}"
    cv2.putText(resized, label, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    cv2.putText(resized, label, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 1)

    # 输出目录可能尚未存在；程序负责创建它，再检查 imwrite 的返回值。
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), resized):
        raise OSError(f"failed to write output image: {args.output}")

    print("input:", args.input)
    print("output:", args.output)
    print("shape:", image.shape, "->", resized.shape)
    print("processed_at:", datetime.now().isoformat(timespec="seconds"))


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
