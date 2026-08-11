from pathlib import Path

import cv2
import numpy as np


def write_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise OSError(f"failed to write sample image: {path}")


def main() -> None:
    out_dir = Path("perception/inputs")

    wide = np.zeros((360, 640, 3), dtype=np.uint8)
    wide[:] = (40, 110, 30)  # OpenCV 使用 BGR
    cv2.circle(wide, (320, 180), 95, (40, 220, 255), -1)
    cv2.putText(wide, "wide input", (30, 55), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

    tall = np.zeros((640, 360, 3), dtype=np.uint8)
    tall[:] = (90, 45, 140)
    cv2.rectangle(tall, (75, 150), (285, 490), (255, 220, 60), -1)
    cv2.putText(tall, "tall input", (35, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    for name, image in (("wide.png", wide), ("tall.png", tall)):
        path = out_dir / name
        write_image(path, image)
        print(f"created: {path} shape={image.shape} dtype={image.dtype}")


if __name__ == "__main__":
    main()
