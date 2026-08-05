# Day 13：在目标 Jetson 构建 TensorRT Engine

## 今天的问题

如何让 TensorRT 针对当前 Thor、CUDA 和 TensorRT 版本优化 ONNX 模型？

## 你要掌握

- TensorRT engine 与 GPU、TensorRT、驱动和构建参数强相关。
- engine 是部署产物，不应跨设备盲目复制，也不提交到 Git。

## 实践

1. 阅读 ONNX 模型输入/输出和动态 shape。
2. 在 Jetson 用 TensorRT 工具或 Python API 构建 FP32 engine；记录命令、workspace 和 profile。
3. 保存 builder 日志，确认没有 silently fallback 的 layer。
4. 用固定输入运行一次 engine，并与 Day 11 输出比较。

## 产物与验收

- 可复现 engine 构建命令或 `perception/build_trt_engine.py`。
- 构建日志和正确性比较结果。
- engine 文件只保留在本机并被 `.gitignore` 忽略。

## 复盘

为什么 TensorRT engine 应在目标 Jetson 重新构建？
