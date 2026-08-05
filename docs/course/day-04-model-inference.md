# Day 4：第一批真实模型结果

> 今天把图片管线接到一个小型预训练分类模型。分类不是机械臂感知的最终形态，但它足够轻量，能把预处理、GPU 推理、后处理、可视化和结构化记录完整串起来。

## 今天的问题

如何把图像管线连接到一个足够轻量、可解释的视觉模型，并诚实保存模型输出？

## 你要掌握

- 一次推理分为预处理、前向计算与后处理；模型的输入尺寸、颜色和归一化方式不能凭感觉修改。
- `score` 表示模型在其类别空间内的相对置信度，不等于现实世界正确率，更不等于机器人获准执行动作。
- 每个结果至少要留原图、标注图、结构化 JSON、模型名和延迟。

## 今天完成后你能做到什么

1. 对一个目录的图片运行 MobileNet V3 Small，并保存 top-k 分类结果。
2. 为每张可读图片保存标注图；为整个批次保存 `results.json`。
3. 人工找出一个可信样例和一个不可信样例，不用调阈值掩盖失败。

## 时间和产物

- 预计：3–4 小时。
- 前置：Day 3 的 GPU PyTorch 可用；还需要匹配的 `torchvision` 与 Pillow。
- 产物：`perception/infer_images.py`、至少 10 张输入图、对应标注图和 `results.json`。

## 操作教程

### 1. 准备十张有来源的图片（30 分钟）

创建目录并放入至少 10 张你有权使用的 JPG/PNG。来源可为自己拍摄、公开许可素材或你已拥有的数据；在 `source-notes.txt` 记录来源和许可。当前没有相机时，优先使用公开许可、内容多样的静态图片。

```bash
cd ~/jetson-stu
mkdir -p perception/inputs/day04 perception/outputs/day04
find perception/inputs/day04 -type f | wc -l
```

不要把大型数据集、权重文件或受限图片提交到 Git。只保留来源说明和小型、许可明确的课程样本。

### 2. 确认 Python 运行时（20 分钟）

```bash
python3 -c 'import torch, torchvision, PIL; print(torch.__version__, torchvision.__version__, torch.cuda.is_available())'
```

如果 `torchvision` 不存在或与 Day 3 的 PyTorch 不匹配，停止并使用同一 NVIDIA/JetPack 兼容渠道补齐它；不要混用来自不同 CUDA/ARM64 组合的 wheel。第一次加载预训练权重可能下载文件，确保网络可用并在记录中写下模型与权重来源。

### 3. 阅读批量推理程序（45 分钟）

完整文件：[展开 `infer_images.py`](#course-file:perception/infer_images.py)。重点找到：

- `weights.transforms()`：权重附带的预处理契约；
- `torch.inference_mode()`：推理时关闭梯度记录；
- `torch.cuda.synchronize()`：只包住前向计算的可靠 GPU 计时；
- `results.json`：给后续程序读取的结果，而不依赖 OCR 图片文字。

### 4. 运行并检查批量结果（45 分钟）

```bash
python3 perception/infer_images.py \
  perception/inputs/day04 \
  perception/outputs/day04 \
  --device cuda:0 \
  --top-k 3 | tee diagnostics/day04-infer-images-output.txt
python3 -m json.tool perception/outputs/day04/results.json | head -80
```

预期：每个可读输入都有 `_annotated.jpg`，终端每行显示 top-1 类别和推理毫秒数，JSON 记录输入、输出、延迟与 top-k 预测。

### 5. 进行人工审阅（35 分钟）

随机打开至少 10 张标注图，选两张写进当天笔记：

1. 一个 top-1 看起来可信的样例：模型为何可能做对？
2. 一个不可信、太泛化或根本不对应你关心对象的样例：输入有什么歧义？

不要把不喜欢的结果删除。失败样例将成为后续安全与评估课程的输入。

## 实践

1. 准备十张许可清楚、内容多样的输入图。
2. 对整个目录运行一次 GPU 推理。
3. 保存标注图、`results.json` 与终端原始输出。
4. 记录一个可信样例和一个不可信样例。

## 产物与验收

- [ ] 输入目录至少有 10 张可读图片和来源说明。
- [ ] 每张成功输入都有对应标注图；`results.json` 能被 `python3 -m json.tool` 读取。
- [ ] 结果包含模型预测和延迟，不只是一张图片。
- [ ] 笔记中保留一个成功与一个失败/不确定样例。

## 复盘

模型输出的置信度与机器人是否应当执行动作，为什么不是同一个问题？
