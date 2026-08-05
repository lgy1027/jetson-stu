# Day 1：第一张可复现的处理图片

> 今天只做一件事：把一张图片稳定地变成一张“可检查的结果图片”。
>
> 不训练模型、不测 GPU、不安装一堆工具。你会建立后面所有感知实验都会复用的输入 → 处理 → 输出闭环。

## 今天的问题

如何把一张输入图片稳定地变成一张可检查的输出图片，并让错误输入清楚失败？

## 你要掌握

- 图片文件必须先被解码为像素数组，才能缩放、标注和保存。
- 输入存在、可被 OpenCV 解码、输出可被写入，是三个不同的检查点。
- 先建立文件输入→处理→结果文件的最小闭环，再接摄像头、模型和 ROS 2。

## 今天完成后你能做到什么

你会有一个 `perception/image_pipeline.py`，它能够：

1. 检查输入文件是否存在、是否能被读取；
2. 将图片缩放到指定宽度；
3. 在图片上写入处理信息；
4. 保存输出图片；
5. 在错误输入时清楚地失败，而不是产生空文件或难懂的栈追踪。

## 时间和产物

- 预计：2.5–3.5 小时。
- 你今天提交/保留：两个输入图、两个输出图、脚本和一段错误输入日志。
- 成功标准：换一张图仍能运行；给错路径时能解释报错。

## 操作教程

### 0. 先理解今天的工程问题（10 分钟）

一张图片在程序里不是“文件”，而是一个像素数组。程序要先把文件解码为数组，才能缩放、画字、保存。今天我们刻意把每一步写清楚：

```text
文件路径 → cv2.imread → 像素数组 → resize / annotate → cv2.imwrite → 结果文件
```

后续无论接摄像头、视频、PyTorch 还是 ROS 2，都会保留这条“输入是否有效、输出是否可检查”的边界。

### 1. 进入仓库并只检查今天需要的依赖（10 分钟）

在 Jetson 终端执行。请逐块执行，不要整段粘贴后不看输出。

```bash
cd ~/jetson-stu
mkdir -p perception/inputs perception/outputs
python3 -c 'import cv2; print("OpenCV:", cv2.__version__)'
```

预期：最后一行会显示类似 `OpenCV: 4.x.x`。

如果出现 `ModuleNotFoundError: No module named 'cv2'`，先不要继续；记录完整报错，然后只安装今天需要的包：

```bash
sudo apt update
sudo apt install -y python3-opencv
python3 -c 'import cv2; print("OpenCV:", cv2.__version__)'
```

解释：这不是“环境巡检”。`cv2` 是今天读取、变换和保存图片的唯一运行依赖。

### 2. 生成两张确定的测试图片（20 分钟）

真实图片来源不稳定：有时路径不对、有时颜色空间不同。先用程序生成两张输入图，保证每个人都有相同的起点。

创建 `perception/make_sample_images.py`：

完整文件：[展开 `make_sample_images.py`](#course-file:perception/make_sample_images.py)。展开后先通读，再亲手输入或粘贴到 Jetson 的同一路径。

运行并检查文件：

```bash
python3 perception/make_sample_images.py
file perception/inputs/wide.png perception/inputs/tall.png
```

预期：两个文件都应被识别为 `PNG image data`，且一个较宽、一个较高。

### 3. 编写可复现的图片处理程序（60 分钟）

创建 `perception/image_pipeline.py`。先读代码，再亲手输入或粘贴；注意参数、错误处理和输出目录各自承担的职责。

完整文件：[展开 `image_pipeline.py`](#course-file:perception/image_pipeline.py)。它就是当天应保留的真实源码，前端显示的内容会随该文件同步更新。

关键解释：

- `Path` 让路径处理跨目录时更可靠；
- `image is None` 区分“文件存在”与“图片可解码”；
- 新高度由原始宽高比推导，避免图片拉伸；
- `cv2.imwrite` 的返回值也要检查；
- 最外层把可预期的输入错误变成清楚的 `ERROR:` 和退出码 `2`。

### 4. 用两种输入验证它（25 分钟）

先运行宽图：

```bash
python3 perception/image_pipeline.py \
  perception/inputs/wide.png \
  perception/outputs/wide_480.png \
  --width 480
```

预期终端包含：

```text
input: perception/inputs/wide.png
output: perception/outputs/wide_480.png
shape: (360, 640, 3) -> (270, 480, 3)
```

再用高图验证“不是只为一个尺寸写的程序”：

```bash
python3 perception/image_pipeline.py \
  perception/inputs/tall.png \
  perception/outputs/tall_300.png \
  --width 300
file perception/outputs/wide_480.png perception/outputs/tall_300.png
```

现在在桌面文件管理器中打开两张输出图，或使用你习惯的图片查看器。必须确认：

1. 图片没有被拉伸；
2. 左上角有输入名和尺寸变化；
3. 两张输出图的尺寸不同，但都保持原比例。

### 5. 故意走一次错误路径（15 分钟）

工程程序是否可靠，不只看成功路径。运行一个不存在的文件：

```bash
python3 perception/image_pipeline.py \
  perception/inputs/not-here.png \
  perception/outputs/should-not-exist.png
echo "exit code: $?"
```

预期：

```text
ERROR: input image does not exist: perception/inputs/not-here.png
exit code: 2
```

并确认没有产生 `should-not-exist.png`：

```bash
test ! -e perception/outputs/should-not-exist.png && echo "PASS: no bogus output"
```

## 实践

按顺序完成，不要跳过错误路径：

1. 生成宽图和高图，并用 `file` 检查两个输入。
2. 用两种不同宽高比的图片运行 `image_pipeline.py`。
3. 打开两张输出图，人工检查比例与左上角标注。
4. 用不存在的输入路径运行一次，记录 `ERROR:` 与退出码。

## 产物与验收

全部满足后才标记 Day 1 完成：

- [ ] `make_sample_images.py` 生成了宽图和高图；
- [ ] `image_pipeline.py` 成功处理两张不同尺寸的图；
- [ ] 你亲眼检查过两张输出图片；
- [ ] 不存在的输入文件产生清楚的错误，并以退出码 2 结束；
- [ ] 你能解释为什么只检查“文件存在”还不够。

## 复盘

在当天笔记写下三句话：输入是什么、程序做了什么、错误如何被处理。为什么只检查“文件存在”还不够？明天会在这条稳定流水线上做图像变换与结果表达。
