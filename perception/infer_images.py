"""Run a pretrained MobileNet classifier over a directory of images."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json
import time

import cv2
import torch
from PIL import Image
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small


class ImageClassifier:
    def __init__(self, device: str = "auto") -> None:
        if device == "auto":
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.weights = MobileNet_V3_Small_Weights.DEFAULT
        self.preprocess = self.weights.transforms()
        self.categories = self.weights.meta["categories"]
        self.model = mobilenet_v3_small(weights=self.weights).eval().to(self.device)

    @torch.inference_mode()
    def predict_bgr(self, frame_bgr: "cv2.typing.MatLike", top_k: int = 3) -> tuple[list[dict], float]:
        image_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        tensor = self.preprocess(Image.fromarray(image_rgb)).unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            torch.cuda.synchronize(self.device)
        started = time.perf_counter()
        probabilities = self.model(tensor).softmax(dim=1)[0]
        if self.device.type == "cuda":
            torch.cuda.synchronize(self.device)
        latency_ms = (time.perf_counter() - started) * 1000
        values, indices = probabilities.topk(top_k)
        results = [
            {"label": self.categories[index.item()], "score": round(value.item(), 5)}
            for value, index in zip(values.cpu(), indices.cpu())
        ]
        return results, latency_ms


def annotate(frame_bgr, results: list[dict], latency_ms: float):
    output = frame_bgr.copy()
    lines = [f"{item['label']}: {item['score']:.2f}" for item in results]
    lines.append(f"inference: {latency_ms:.1f} ms")
    for row, line in enumerate(lines):
        y = 32 + row * 28
        cv2.putText(output, line, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(output, line, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 1)
    return output


def parse_args():
    parser = ArgumentParser(description="Classify images and save JSON plus annotated images")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda:0"])
    parser.add_argument("--top-k", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = sorted(path for path in args.input_dir.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not paths:
        raise SystemExit(f"no jpg/jpeg/png files found in {args.input_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    classifier = ImageClassifier(args.device)
    summary = []
    for path in paths:
        frame = cv2.imread(str(path))
        if frame is None:
            print("SKIP unreadable:", path)
            continue
        results, latency_ms = classifier.predict_bgr(frame, args.top_k)
        annotated_path = args.output_dir / f"{path.stem}_annotated.jpg"
        cv2.imwrite(str(annotated_path), annotate(frame, results, latency_ms))
        record = {"input": str(path), "output": str(annotated_path), "latency_ms": round(latency_ms, 3), "predictions": results}
        summary.append(record)
        print(path.name, "->", results[0]["label"], f"{latency_ms:.1f} ms")
    (args.output_dir / "results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("saved:", args.output_dir / "results.json")


if __name__ == "__main__":
    main()
