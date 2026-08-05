"""Compare one deterministic matrix workload on CPU and CUDA."""

from __future__ import annotations

import time

import torch


def timed_matmul(left: torch.Tensor, right: torch.Tensor, device: torch.device, repeats: int) -> tuple[torch.Tensor, float]:
    """Time only the math, using the same inputs on CPU and GPU."""
    left = left.to(device)
    right = right.to(device)
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    started = time.perf_counter()
    result = left @ right
    for _ in range(repeats - 1):
        result = result + left @ right
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    return result, (time.perf_counter() - started) * 1000


def main() -> None:
    size, repeats = 2048, 8
    print("torch:", torch.__version__)
    print("cuda runtime:", torch.version.cuda)
    print("cuda available:", torch.cuda.is_available())
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is unavailable; stop here and resolve the Day 3 install path.")
    gpu = torch.device("cuda:0")
    print("gpu:", torch.cuda.get_device_name(gpu))
    generator = torch.Generator(device="cpu").manual_seed(7)
    left = torch.randn((size, size), generator=generator)
    right = torch.randn((size, size), generator=generator)
    cpu_result, cpu_ms = timed_matmul(left, right, torch.device("cpu"), repeats)
    gpu_result, gpu_ms = timed_matmul(left, right, gpu, repeats)
    max_error = (cpu_result - gpu_result.cpu()).abs().max().item()
    print(f"workload: {repeats} x {size}x{size} matrix multiply")
    print("cpu result device:", cpu_result.device)
    print("gpu result device:", gpu_result.device)
    print(f"cpu_ms: {cpu_ms:.2f}")
    print(f"gpu_ms: {gpu_ms:.2f}")
    print(f"speedup: {cpu_ms / gpu_ms:.2f}x")
    print(f"max_abs_error: {max_error:.6f}")


if __name__ == "__main__":
    main()
