# Day 5：从单图到视频

> 今天将 Day 4 的分类器接入视频帧循环，产出可播放的视频与统计 JSON。重点是资源释放、帧率解释与“每 N 帧推理一次”的工程取舍，不是追求最高 FPS。

## 今天的问题

如何持续处理视频帧，并留下可回放、可解释的推理结果？

## 你要掌握

- 输入 FPS、模型推理 FPS、端到端处理 FPS 和输出编码 FPS 是不同指标。
- 视频不应把每帧都当成孤立离线图片；可以在相邻帧之间复用最近一次预测。
- `VideoCapture` 和 `VideoWriter` 无论成功或失败都必须释放，输出视频还要实际播放检查。

## 今天完成后你能做到什么

1. 读取一个视频，按固定间隔调用 Day 4 分类器，写出标注 MP4。
2. 在画面中显示帧号与端到端 FPS，并保存 JSON 统计。
3. 解释为什么推理单帧很快，不代表输出视频就有同样高的端到端 FPS。

## 时间和产物

- 预计：3–4 小时。
- 前置：Day 4 模型能运行；一个你有权使用的短视频。没有摄像头不影响本课。
- 产物：`perception/infer_video.py`、标注 MP4、同名 JSON 与一次播放检查记录。

## 操作教程

### 1. 准备可复现输入（20 分钟）

把一个许可明确的视频放到 `perception/inputs/day05/`，先查看容器信息：

```bash
cd ~/jetson-stu
mkdir -p perception/inputs/day05 perception/outputs/day05
ffprobe -hide_banner perception/inputs/day05/<your-video>.mp4 2>&1 | head -30
```

如果没有 `ffprobe`，使用系统的视频信息工具或 OpenCV 稍后打印的 FPS/尺寸。建议先用 30–90 秒短片，而不是直接处理大文件。

### 2. 阅读视频循环（40 分钟）

完整文件：[展开 `infer_video.py`](#course-file:perception/infer_video.py)。关注四点：

1. `--every 5` 意味着每 5 帧做一次推理，其他帧复用最新预测；
2. writer 使用原始 FPS 和尺寸，以保证播放器可正确解码；
3. `try/finally` 保证输入和输出句柄关闭；
4. JSON 记录帧数、时长、推理次数、wall time，而非只报一个“FPS”。

### 3. 运行最小视频实验（50 分钟）

```bash
python3 perception/infer_video.py \
  perception/inputs/day05/<your-video>.mp4 \
  perception/outputs/day05/annotated.mp4 \
  --device cuda:0 \
  --every 5 | tee diagnostics/day05-video-output.txt
python3 -m json.tool perception/outputs/day05/annotated.json
```

预期：程序结束后有 MP4 和 JSON；JSON 的 `frames / input_fps` 应大致等于视频时长，`inference_count` 应约等于 `frames / every`。

### 4. 必须播放检查（25 分钟）

打开输出 MP4，随机检查开头、中段、结尾：画面可播放、帧号递增、预测文字没有漂出画面、视频没有在最后几帧损坏。若无法播放，记录编解码器、输入容器、输出容器和完整报错，不要先猜是 GPU 问题。

### 5. 做一个受控对比（30 分钟）

只改变 `--every`：一次设为 `1`，一次设为 `5`。比较 JSON 中的推理次数与 wall time，并解释画面标签更新频率为何不同。输入视频、模型和设备必须保持不变。

## 实践

1. 准备一个 30–90 秒、许可明确的视频并记录其基本信息。
2. 生成可播放的标注 MP4 与 JSON。
3. 实际播放检查三个时间点。
4. 对比 `--every 1` 和 `--every 5` 的统计结果。

## 产物与验收

- [ ] 输出 MP4 能完整播放，帧号与标签可见。
- [ ] JSON 包含输入 FPS、帧数、时长、推理间隔、推理次数和 wall time。
- [ ] 两次间隔实验只改变一个变量，并有对比结论。
- [ ] 能解释输入 FPS、推理 FPS 与端到端 FPS 的区别。

## 复盘

为什么“推理很快”不必然意味着端到端视频 FPS 很高？
