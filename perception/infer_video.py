"""Classify sampled video frames and write an annotated, playable MP4."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json
import time

import cv2

from perception.infer_images import ImageClassifier, annotate


def parse_args():
    parser = ArgumentParser(description="Run Day 4 classifier over video")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda:0"])
    parser.add_argument("--every", type=int, default=5, help="run inference once every N frames")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.every <= 0:
        raise ValueError("--every must be greater than zero")
    if args.input.resolve() == args.output.resolve():
        raise ValueError("input and output video paths must be different")
    capture = cv2.VideoCapture(str(args.input))
    if not capture.isOpened():
        raise FileNotFoundError(f"cannot open video: {args.input}")
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(args.output), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        raise OSError(f"cannot create output video: {args.output}")
    frame_index, inference_count = 0, 0
    total_inference_ms = 0.0
    latest_results, latest_latency = [], 0.0
    run_started = time.perf_counter()
    try:
        classifier = ImageClassifier(args.device)
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if frame_index % args.every == 0:
                latest_results, latest_latency = classifier.predict_bgr(frame)
                inference_count += 1
                total_inference_ms += latest_latency
            annotated = annotate(frame, latest_results, latest_latency)
            elapsed = max(time.perf_counter() - run_started, 1e-6)
            cv2.putText(annotated, f"frame {frame_index} | pipeline {frame_index / elapsed:.1f} FPS", (12, height - 16), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 240, 120), 2)
            writer.write(annotated)
            frame_index += 1
    finally:
        capture.release()
        writer.release()
    if frame_index == 0:
        raise RuntimeError("video opened but produced no decodable frames")
    wall_time = time.perf_counter() - run_started
    duration = frame_index / fps
    summary = {
        "input": str(args.input),
        "output": str(args.output),
        "device": str(classifier.device),
        "model": classifier.model_name,
        "weights": classifier.weights_name,
        "input_fps": fps,
        "frames": frame_index,
        "duration_s": round(duration, 3),
        "inference_every_n_frames": args.every,
        "inference_count": inference_count,
        "average_inference_ms": round(total_inference_ms / inference_count, 3),
        "wall_time_s": round(wall_time, 3),
        "end_to_end_fps": round(frame_index / wall_time, 3),
    }
    summary_path = args.output.with_suffix(".json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
