# Day 4：第一批真实模型结果

> 今天把图片管线接到一个小型预训练分类模型。分类不是机械臂感知的最终形态，但它足够轻量，能把预处理、GPU 推理、后处理、可视化和结构化记录完整串起来。

## 今天的问题

如何把图像管线连接到一个足够轻量、可解释的视觉模型，并诚实保存模型输出？

## 前置条件与边界

- Day 3 的 PyTorch 环境已经在 `cuda:0` 完成真实计算；Day 4/5 必须继续使用同一个解释器、虚拟环境或容器。
- `torchvision` 必须与 PyTorch 匹配，不能看到缺包就从另一个 JetPack 或 Python ABI 随机安装。
- MobileNet V3 Small 是用来教授完整推理契约的轻量分类模型，不是最终机械臂检测器。
- 分类标签来自预训练权重的类别空间。分类结果没有二维位置、深度或抓取姿态，不能直接成为机器人动作目标。

## 你要掌握

- 一次推理分为预处理、前向计算与后处理；模型的输入尺寸、颜色和归一化方式不能凭感觉修改。
- `score` 表示模型在其类别空间内的相对置信度，不等于现实世界正确率，更不等于机器人获准执行动作。
- 每个结果至少要留原图、标注图、结构化 JSON、模型名和延迟。

## 今天完成后你能做到什么

1. 对一个目录的图片运行 MobileNet V3 Small，并保存 top-k 分类结果。
2. 为每张可读图片保存标注图；为整个批次保存 `results.json`。
3. 人工找出一个可信样例和一个不可信样例，不用调阈值掩盖失败。

## 本单元产物

- 前置：Day 3 的 GPU PyTorch 可用；还需要匹配的 `torchvision` 与 Pillow。
- 产物：`perception/infer_images.py`、至少 10 张输入图、对应标注图和 `results.json`。

## 操作教程

### 1. 准备十张有来源的图片

创建目录并放入至少 10 张你有权使用的 JPG/PNG。来源可为自己拍摄、公开许可素材或你已拥有的数据；在 `source-notes.txt` 记录来源和许可。当前没有相机时，优先使用公开许可、内容多样的静态图片。

```bash
cd ~/jetson-stu
mkdir -p perception/inputs/day04 perception/outputs/day04
find perception/inputs/day04 -type f | wc -l
```

不要把大型数据集、权重文件或受限图片提交到 Git。只保留来源说明和小型、许可明确的课程样本。

为实际输入生成可复现清单：

```bash
find perception/inputs/day04 -maxdepth 1 -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) \
  -print0 | sort -z | xargs -0 sha256sum \
  > diagnostics/day04-input-sha256.txt
```

哈希不替代许可说明；它用于确认以后复测时是不是同一批字节输入。

### 2. 确认 Python 运行时

```bash
python3 -c 'import torch, torchvision, PIL; print(torch.__version__, torchvision.__version__, torch.cuda.is_available())'
```

如果 `torchvision` 不存在或与 Day 3 的 PyTorch 不匹配，停止并使用同一 NVIDIA/JetPack 兼容渠道补齐它；不要混用来自不同 CUDA/ARM64 组合的 wheel。第一次加载预训练权重可能下载文件，确保网络可用并在记录中写下模型与权重来源。

第一次下载完成后记录缓存是否存在。后续离线复现必须明确依赖已经缓存的权重，不能把“网络刚好可用”当成系统前提。

### 3. 阅读批量推理程序

完整文件：[展开 `infer_images.py`](#course-file:perception/infer_images.py)。重点找到：

- `weights.transforms()`：权重附带的预处理契约；
- `torch.inference_mode()`：推理时关闭梯度记录；
- `torch.cuda.synchronize()`：只包住前向计算的可靠 GPU 计时；
- `results.json`：给后续程序读取的结果，而不依赖 OCR 图片文字。

程序对显式 `--device cuda:0` 不会静默回退到 CPU；CUDA 不可用时会明确失败。不可解码图片会进入 `skipped` 列表，而不是伪造预测。

### 4. 运行并检查批量结果

```bash
python3 perception/infer_images.py \
  perception/inputs/day04 \
  perception/outputs/day04 \
  --device cuda:0 \
  --top-k 3 | tee diagnostics/day04-infer-images-output.txt
python3 -m json.tool perception/outputs/day04/results.json | head -80
```

预期：每个可读输入都有 `_annotated.jpg`，终端每行显示 top-1 类别和推理毫秒数。JSON 顶层记录 `model`、`weights`、`device`、`top_k`、成功/跳过数量；`records` 中记录每张输入、输出、延迟与 top-k 预测。

用程序检查结构化契约，而不只是滚动阅读 JSON：

```bash
python3 - <<'PY'
import json
from pathlib import Path

data = json.loads(Path('perception/outputs/day04/results.json').read_text())
assert data['device'] == 'cuda:0', data['device']
assert data['processed_count'] == len(data['records'])
assert data['processed_count'] >= 10
assert all(len(item['predictions']) == data['top_k'] for item in data['records'])
print('PASS:', data['model'], data['weights'], data['processed_count'], 'images')
PY
```

### 5. 进行人工审阅

随机打开至少 10 张标注图，选两张写进当天笔记：

1. 一个 top-1 看起来可信的样例：模型为何可能做对？
2. 一个不可信、太泛化或根本不对应你关心对象的样例：输入有什么歧义？

不要把不喜欢的结果删除。失败样例将成为后续安全与评估课程的输入。

### 6. 验证错误路径

错误输入也属于教程：

```bash
python3 perception/infer_images.py \
  perception/inputs/not-a-directory \
  perception/outputs/day04-invalid \
  --device cuda:0
echo "exit code: $?"

python3 perception/infer_images.py \
  perception/inputs/day04 \
  perception/outputs/day04-invalid-topk \
  --device cuda:0 \
  --top-k 0
echo "exit code: $?"
```

两次都必须非零退出，并明确指出输入目录或 `top-k` 错误。不要为了通过演示捕获所有异常后返回成功退出码。

## 常见问题与诊断顺序

| 现象 | 先检查什么 |
|---|---|
| 第一次运行停在下载 | 网络、权重缓存目录和磁盘空间；不要误判为 GPU 卡死 |
| `torchvision` 导入或算子错误 | PyTorch/torchvision 版本、安装来源和 Python ABI |
| 显式 CUDA 请求失败 | 回到 Day 3，不能改成 `auto` 隐藏问题 |
| 所有图片都被跳过 | 用 `file` 和 OpenCV 单独解码输入，检查扩展名与真实格式 |
| 结果明显不符合任务语义 | 检查权重类别空间和预处理，不用调高分数伪装正确 |
| 标注图缺失但 JSON 存在 | 检查输出权限、磁盘空间和 `imwrite` 错误 |

## 实践

1. 准备十张许可清楚、内容多样的输入图。
2. 对整个目录运行一次 GPU 推理。
3. 保存标注图、`results.json` 与终端原始输出。
4. 记录一个可信样例和一个不可信样例。
5. 验证不存在目录和非法 `top-k` 两条错误路径。

## 产物与验收

- [ ] 输入目录至少有 10 张可读图片和来源说明。
- [ ] 每张成功输入都有对应标注图；`results.json` 能被 `python3 -m json.tool` 读取。
- [ ] 结果包含模型、权重、实际设备、预测和延迟，不只是一张图片。
- [ ] 输入哈希和图片来源说明都已保存。
- [ ] 笔记中保留一个成功与一个失败/不确定样例。
- [ ] 两条错误路径均非零退出，没有生成伪成功结果。

## 与后续课程的连接

Day 5 复用同一个 `ImageClassifier` 进入视频循环；Day 8 会把后端包装进 ROS 2；Day 11 会冻结输入输出并导出 ONNX。这里保留的不可信样例会进入后续失败分类和安全拒绝测试。

## 复盘

模型输出的置信度与机器人是否应当执行动作，为什么不是同一个问题？
