"""比较 CPU 和 CUDA 上的矩阵乘法。"""

from __future__ import annotations

from argparse import ArgumentParser
import time

import torch


def timed_matmul(left: torch.Tensor, right: torch.Tensor, device: torch.device, repeats: int) -> tuple[torch.Tensor, float]:
    """在指定设备上运行矩阵乘法，并只统计计算耗时。"""
    # 复制到目标设备；预热和同步分别避免首次初始化及异步队列干扰计时。
    left = left.to(device)
    right = right.to(device)
    _ = left @ right  # 预热，排除首次调用的初始化耗时
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    started = time.perf_counter()
    result = left @ right
    for _ in range(repeats - 1):
        result = result + left @ right
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    return result, (time.perf_counter() - started) * 1000


def parse_args():
    parser = ArgumentParser(description="Compare one deterministic matrix workload on CPU and CUDA")
    parser.add_argument("--size", type=int, default=2048, help="square matrix dimension")
    parser.add_argument("--repeats", type=int, default=8, help="number of matrix multiplications")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.size <= 0 or args.repeats <= 0:
        raise SystemExit("--size and --repeats must be greater than zero")
    size, repeats = args.size, args.repeats
    # size 是方阵边长，repeats 是重复计算次数；两者越大，耗时和内存占用越高。
    print("torch:", torch.__version__)
    print("cuda runtime:", torch.version.cuda)
    print("cuda available:", torch.cuda.is_available())
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is unavailable; stop here and resolve the Day 3 install path.")
    gpu = torch.device("cuda:0")
    print("gpu:", torch.cuda.get_device_name(gpu))
    # 固定随机种子，让 CPU/GPU 使用完全相同的输入；否则误差和耗时差异
    # 可能来自不同数据，而不是来自计算设备本身。
    generator = torch.Generator(device="cpu").manual_seed(7)
    left = torch.randn((size, size), generator=generator)
    right = torch.randn((size, size), generator=generator)
    cpu_result, cpu_ms = timed_matmul(left, right, torch.device("cpu"), repeats)
    # CPU 和 GPU 使用同一组输入，最后比较结果误差和耗时。
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
