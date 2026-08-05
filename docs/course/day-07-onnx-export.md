# Day 11：导出 ONNX

## 今天的问题

怎样将 PyTorch 模型转换为独立于 PyTorch 的推理表示，并保证语义不变？

## 你要掌握

- ONNX 是模型计算图交换格式，不是自动加速器。
- 导出时必须固定输入 shape、opset、动态维策略和模型 eval 状态。

## 实践

1. 将 Week 1 模型切换到 `eval()`，固定一份代表性输入。
2. 导出 ONNX，保存输入/输出名称、shape、opset 与模型来源。
3. 用 ONNX checker 验证图合法性。
4. 比较 PyTorch 与 ONNX 输出的 shape、前几个值和最大误差。

## 产物与验收

- `perception/export_onnx.py` 与导出说明。
- 正确性对比脚本；误差在模型/精度允许范围内。
- 不提交大型 ONNX 文件，记录可再生成命令。

## 复盘

为什么“成功生成 .onnx 文件”仍不足以证明可以部署？
