# Day 3：让 PyTorch 真正使用 Thor GPU

## 今天的问题

如何在真实工作负载中验证 PyTorch 使用的是 GPU，而不是悄悄回退到 CPU？

## 你要掌握

- `torch.cuda.is_available()` 是前置条件；设备名、张量 `.device` 和 GPU 计时共同构成证据。
- GPU 异步执行，计时前后需要正确同步。

## 实践

1. 为当前 JetPack / ARM64 选择兼容 PyTorch 路径；只在本日需要时安装。
2. 编写 GPU 张量矩阵运算，与 CPU 结果比较正确性。
3. 用同步后的计时记录 CPU 与 GPU 的运行时间。
4. 在这次真实计算期间采集一小段 `tegrastats`，而不是单独做监控练习。

## 产物与验收

- `perception/day03_torch_gpu.py`。
- 输出 Python、PyTorch、CUDA runtime、设备名、CPU/GPU 耗时和数值误差。
- GPU 可用且结果一致。

## 复盘

为什么在 GPU 上仅创建一个张量不能证明实际计算发生在 GPU？
