# Day 12：ONNX Runtime 推理

## 今天的问题

如何让同一个 ONNX 模型在独立 runtime 中正确运行，并定位输出差异？

## 你要掌握

- Provider 决定 ONNX Runtime 使用 CPU、CUDA 或其他执行后端。
- 前处理、dtype、layout、动态 shape 都可能造成“模型相同、结果不同”。

## 实践

1. 安装或确认适用于当前 ARM64/JetPack 的 ONNX Runtime 路径，只解决本日阻塞。
2. 打印可用 execution providers 和实际选用 provider。
3. 对 Day 11 的固定输入运行 ONNX Runtime。
4. 比较 PyTorch/ONNX Runtime 后处理前的原始输出。

## 产物与验收

- `perception/infer_onnx.py`。
- provider、输入输出 metadata、最大误差和一次正确推理记录。

## 复盘

当 ONNX Runtime 的输出不同，你会先检查模型、provider 还是前处理？为什么？
