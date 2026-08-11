# Day 1：第一张可复现的处理图片

> 今天只做一件事：把一张图片稳定地变成一张“可检查的结果图片”。
>
> 不训练模型、不测 GPU、不安装一堆工具。你会建立后面所有感知实验都会复用的输入 → 处理 → 输出闭环。

## 今天的问题

如何把一张输入图片稳定地变成一张可检查的输出图片，并让错误输入清楚失败？

## 前置条件与边界

- Day 0 已完成，能够在 Jetson 终端进入课程仓库。
- 当前单元只需要 Python、OpenCV、NumPy 和普通文件系统，不需要 PyTorch、摄像头或 GPU 指标。
- 所有命令都从仓库根目录执行。示例中的 `~/jetson-stu` 应替换为 Jetson 上的真实仓库路径。
- `perception/inputs/` 与 `perception/outputs/` 被 Git 忽略；课程保留生成方法和证据，不强制提交生成图片。

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

## 本单元产物

- 本单元产物：两个输入图、两个输出图、脚本和一段错误输入日志。
- 成功标准：换一张图仍能运行；给错路径时能解释报错。

## 操作教程

### 0. 先理解今天的工程问题

一张图片在程序里不是“文件”，而是一个像素数组。程序要先把文件解码为数组，才能缩放、画字、保存。今天我们刻意把每一步写清楚：

```text
文件路径 → cv2.imread → 像素数组 → resize / annotate → cv2.imwrite → 结果文件
```

后续无论接摄像头、视频、PyTorch 还是 ROS 2，都会保留这条“输入是否有效、输出是否可检查”的边界。

### 1. 进入仓库并只检查今天需要的依赖

在 Jetson 终端执行。请逐块执行，不要整段粘贴后不看输出。

```bash
# 进入仓库、创建今天的输入输出目录，并确认 OpenCV 可导入。
cd ~/jetson-stu
mkdir -p perception/inputs perception/outputs
python3 -c 'import cv2; print("OpenCV:", cv2.__version__)'
```

预期：最后一行会显示类似 `OpenCV: 4.x.x`。

如果出现 `ModuleNotFoundError: No module named 'cv2'`，先不要继续；记录完整报错，然后只安装今天需要的包：

```bash
# 仅安装今天缺失的 OpenCV 运行依赖，然后再次验证导入。
sudo apt update
sudo apt install -y python3-opencv
python3 -c 'import cv2; print("OpenCV:", cv2.__version__)'
```

解释：这不是“环境巡检”。`cv2` 是今天读取、变换和保存图片的唯一运行依赖。

### 2. 生成两张确定的测试图片

真实图片来源不稳定：有时路径不对、有时颜色空间不同。先用程序生成两张输入图，保证每个人都有相同的起点。

创建 `perception/make_sample_images.py`：

完整文件：[展开 `make_sample_images.py`](#course-file:perception/make_sample_images.py)。展开后先通读，再亲手输入或粘贴到 Jetson 的同一路径。

运行并检查文件：

```bash
# 生成两张尺寸不同但内容确定的测试图片，并检查文件类型。
python3 perception/make_sample_images.py
file perception/inputs/wide.png perception/inputs/tall.png
```

预期：两个文件都应被识别为 `PNG image data`，且一个较宽、一个较高。

生成程序还会打印每张图的 shape 和 dtype。预期分别为 `(360, 640, 3)`、`(640, 360, 3)` 和 `uint8`；OpenCV 的 shape 顺序是高、宽、通道，不是宽、高、通道。

### 3. 编写可复现的图片处理程序

创建 `perception/image_pipeline.py`。先读代码，再亲手输入或粘贴；注意参数、错误处理和输出目录各自承担的职责。

完整文件：[查看 `image_pipeline.py`](#course-file:perception/image_pipeline.py)。请先通读源码，再按步骤运行和修改。

关键解释：

- `Path` 让路径处理跨目录时更可靠；
- `image is None` 区分“文件存在”与“图片可解码”；
- 新高度由原始宽高比推导，避免图片拉伸；
- `cv2.imwrite` 的返回值也要检查；
- 最外层把可预期的输入错误变成清楚的 `ERROR:` 和退出码 `2`。

### 4. 用两种输入验证它

先运行宽图：

```bash
# 用宽图验证缩放、标注和输出文件是否正常。
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
# 用高图验证程序能保持另一种宽高比，并检查两张结果图。
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

### 5. 故意走一次错误路径

工程程序是否可靠，不只看成功路径。运行一个不存在的文件：

```bash
# 传入不存在的输入，验证程序会返回清楚的错误和非零退出码。
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

再区分“文件不存在”和“文件存在但不是图片”：

```bash
printf 'this is not an image\n' > perception/inputs/not-an-image.png
python3 perception/image_pipeline.py \
  perception/inputs/not-an-image.png \
  perception/outputs/should-also-not-exist.png
echo "exit code: $?"
```

预期错误包含 `OpenCV could not decode image`，退出码仍为 `2`。这证明路径检查和解码检查解决的是两个不同问题。

### 6. 保存可复现证据

把成功与失败命令集中保存，不要只截一张终端图：

```bash
{
  python3 perception/image_pipeline.py perception/inputs/wide.png perception/outputs/wide_480.png --width 480
  python3 perception/image_pipeline.py perception/inputs/tall.png perception/outputs/tall_300.png --width 300
  python3 perception/image_pipeline.py perception/inputs/not-here.png perception/outputs/should-not-exist.png
} > diagnostics/day01-image-pipeline.txt 2>&1
```

最后一条命令预期失败，因此整个命令组可能返回非零；证据文件仍应包含前两次成功和最后一次失败。验收时同时查看文件内容和实际输出图。

## 常见问题与诊断顺序

| 现象 | 先检查什么 | 不要直接做什么 |
|---|---|---|
| `No module named cv2` | 当前 `python3` 路径与 `python3-opencv` 是否属于同一系统环境 | 不要随机安装 x86 wheel |
| 文件存在但 `imread` 返回空 | `file <path>`、扩展名是否伪装、文件是否损坏 | 不要删除解码检查 |
| 输出目录存在但没有图片 | `cv2.imwrite` 返回值、目录权限、磁盘空间 | 不要假设没有异常就是写入成功 |
| 图片被拉伸 | 新高度是否按原宽高比计算 | 不要硬编码宽高两个值 |
| 标注文字看不清 | 文字描边、图片尺寸、标注位置 | 不要把可视化当作唯一机器结果 |

## 实践

按顺序完成，不要跳过错误路径：

1. 生成宽图和高图，并用 `file` 检查两个输入。
2. 用两种不同宽高比的图片运行 `image_pipeline.py`。
3. 打开两张输出图，人工检查比例与左上角标注。
4. 用不存在的输入路径运行一次，记录 `ERROR:` 与退出码。
5. 用存在但不可解码的伪图片再验证一次错误边界。

## 产物与验收

全部满足后才标记 Day 1 完成：

- [ ] `make_sample_images.py` 生成了宽图和高图；
- [ ] `image_pipeline.py` 成功处理两张不同尺寸的图；
- [ ] 你亲眼检查过两张输出图片；
- [ ] 不存在的输入文件产生清楚的错误，并以退出码 2 结束；
- [ ] 存在但不可解码的文件不会产生输出图；
- [ ] `diagnostics/day01-image-pipeline.txt` 或等价记录包含成功和失败证据；
- [ ] 你能解释为什么只检查“文件存在”还不够。

## 与后续课程的连接

Day 2 会把这里的单一图片结果拆成人可读 PNG 和机器可读 JSON；Day 5 会把同样的读取、处理、写入和资源释放边界放进视频循环；Day 8 会把这些函数包装进 ROS 2 节点。

## 复盘

在当天笔记写下三句话：输入是什么、程序做了什么、错误如何被处理。为什么只检查“文件存在”还不够？明天会在这条稳定流水线上做图像变换与结果表达。
