# Day 5：从单图到视频

> 今天将 Day 4 的分类器接入视频帧循环，产出可播放的视频与统计 JSON。重点是资源释放、帧率解释与“每 N 帧推理一次”的工程取舍，不是追求最高 FPS。

## 今天的问题

如何持续处理视频帧，并留下可回放、可解释的推理结果？

## 前置条件与边界

- Day 4 的 `ImageClassifier` 能在同一 Python 环境中使用 `cuda:0`。
- 当前没有摄像头，因此主路径从 Day 4 的许可图片生成确定性短视频；也可以额外使用自有视频做泛化验证。
- 本单元仍是图像分类随时间采样，不进行目标跟踪，也不把相邻帧标签当成真实轨迹。
- 输出 MP4 能被写出不等于能被播放器完整解码，人工播放检查是验收的一部分。

## 你要掌握

- 输入 FPS、模型推理 FPS、端到端处理 FPS 和输出编码 FPS 是不同指标。
- 视频不应把每帧都当成孤立离线图片；可以在相邻帧之间复用最近一次预测。
- `VideoCapture` 和 `VideoWriter` 无论成功或失败都必须释放，输出视频还要实际播放检查。

## 今天完成后你能做到什么

1. 读取一个视频，按固定间隔调用 Day 4 分类器，写出标注 MP4。
2. 在画面中显示帧号与端到端 FPS，并保存 JSON 统计。
3. 解释为什么推理单帧很快，不代表输出视频就有同样高的端到端 FPS。

## 本单元产物

- 前置：Day 4 模型能运行；一个你有权使用的短视频。没有摄像头不影响本课。
- 产物：`perception/day05_infer_video.py`、标注 MP4、同名 JSON 与一次播放检查记录。

## 操作教程

### 1. 准备可复现输入

优先复用 Day 4 的许可图片生成确定性输入视频。完整文件：[展开 `day05_make_sample_video.py`](#course-file:perception/day05_make_sample_video.py)。

```bash
cd ~/jetson-stu
mkdir -p perception/inputs/day05 perception/outputs/day05
python3 perception/day05_make_sample_video.py \
  perception/inputs/day04 \
  perception/inputs/day05/day04-slideshow.mp4 \
  --fps 10 \
  --frames-per-image 10
```

程序会打印帧数、FPS 和计算得到的时长。这样 Day 4 的输入来源、哈希和许可继续适用于视频内容。

也可以把一个许可明确的自有视频放到 `perception/inputs/day05/` 做第二次验证。查看容器信息：

```bash
ffprobe -hide_banner perception/inputs/day05/day04-slideshow.mp4 2>&1 | head -30
```

如果没有 `ffprobe`，不必为了本课安装完整 FFmpeg；使用 OpenCV 稍后写入 JSON 的 FPS、帧数和时长。处理自有素材时先选短片，不要直接使用大型视频。

### 2. 阅读视频循环

完整文件：[展开 `day05_infer_video.py`](#course-file:perception/day05_infer_video.py)。关注四点：

1. `--every 5` 意味着每 5 帧做一次推理，其他帧复用最新预测；
2. writer 使用原始 FPS 和尺寸，以保证播放器可正确解码；
3. `try/finally` 保证输入和输出句柄关闭；
4. JSON 记录帧数、时长、推理次数、wall time，而非只报一个“FPS”。

### 3. 运行最小视频实验

```bash
python3 perception/day05_infer_video.py \
  perception/inputs/day05/day04-slideshow.mp4 \
  perception/outputs/day05/annotated-every5.mp4 \
  --device cuda:0 \
  --every 5 | tee diagnostics/day05-video-inference-output.txt
python3 -m json.tool perception/outputs/day05/annotated-every5.json
```

预期：程序结束后有 MP4 和 JSON；JSON 记录模型、权重、实际设备、输入 FPS、帧数、时长、平均推理延迟和端到端 FPS。`frames / input_fps` 应等于记录的视频时长，`inference_count` 应约等于 `ceil(frames / every)`。

### 4. 必须播放检查

打开输出 MP4，随机检查开头、中段、结尾：画面可播放、帧号递增、预测文字没有漂出画面、视频没有在最后几帧损坏。若无法播放，记录编解码器、输入容器、输出容器和完整报错，不要先猜是 GPU 问题。

### 5. 做一个受控对比

只改变 `--every`，并使用不同输出名避免覆盖第一次证据：

```bash
python3 perception/day05_infer_video.py \
  perception/inputs/day05/day04-slideshow.mp4 \
  perception/outputs/day05/annotated-every1.mp4 \
  --device cuda:0 --every 1 \
  | tee diagnostics/day05-video-every1-output.txt
```

比较 `annotated-every1.json` 与 `annotated-every5.json` 中的推理次数、平均推理延迟、wall time 和端到端 FPS，并解释画面标签更新频率为何不同。输入视频、模型、权重和设备必须保持不变。

### 6. 验证错误和资源边界

```bash
python3 perception/day05_infer_video.py \
  perception/inputs/day05/not-here.mp4 \
  perception/outputs/day05/invalid.mp4 \
  --device cuda:0
echo "exit code: $?"

python3 perception/day05_infer_video.py \
  perception/inputs/day05/day04-slideshow.mp4 \
  perception/outputs/day05/invalid-every.mp4 \
  --device cuda:0 --every 0
echo "exit code: $?"
```

两次都必须失败。源码把分类器初始化和帧循环放在资源释放边界内，即使模型初始化或中途推理失败，也会释放 `VideoCapture` 和 `VideoWriter`。

## 常见问题与诊断顺序

- `cannot open video`：先用 `file`/`ffprobe` 检查输入，再检查 OpenCV 编解码支持。
- `cannot create output video`：检查输出后缀、父目录权限、磁盘空间和 MP4 编码器。
- MP4 存在但不能播：不要先归因 GPU；检查 writer 是否释放、帧尺寸是否始终一致、播放器是否支持 `mp4v`。
- 输出速度低于输入 FPS：区分离线 wall time 和媒体时间，不要把它描述成“丢帧”。
- 标签更新跳跃：这是 `--every` 的预期结果，不是跟踪器错误；本课没有跟踪器。
- 末尾文件损坏：检查程序是否异常退出以及 `finally` 是否执行。

## 实践

1. 从 Day 4 图片生成确定性短视频，并记录其基本信息。
2. 生成可播放的标注 MP4 与 JSON。
3. 实际播放检查三个时间点。
4. 对比 `--every 1` 和 `--every 5` 的统计结果。
5. 验证不存在视频和非法推理间隔两条错误路径。

## 产物与验收

- [ ] 输出 MP4 能完整播放，帧号与标签可见。
- [ ] JSON 包含模型、权重、设备、输入 FPS、帧数、时长、推理间隔、平均推理延迟、wall time 和端到端 FPS。
- [ ] 两次间隔实验只改变一个变量，并有对比结论。
- [ ] 两条错误路径均非零退出，失败后输出资源可被再次创建或覆盖。
- [ ] 能解释输入 FPS、推理 FPS 与端到端 FPS 的区别。

## M1 里程碑验收

完成 Day 5 后，不只检查本课文件，还要回看 Day 1–5：

- 文件输入、图像解码、输出写入和错误退出都有明确边界；
- 图像变换同时留下人可读与机器可读结果；
- PyTorch CUDA 有设备、同步计时、数值误差和运行期监控证据；
- 模型结果记录权重、设备、延迟、成功与跳过项；
- 视频可以重放，并能解释采样推理与端到端性能；
- 所有不可信预测都保留为后续安全测试素材。

这些证据齐全后，才进入 M2 的 ROS 2 感知系统。

## 复盘

为什么“推理很快”不必然意味着端到端视频 FPS 很高？
