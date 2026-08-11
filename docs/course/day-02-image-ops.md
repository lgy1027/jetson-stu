# Day 2：图像变换与结果表达

> 今天把 Day 1 的“能处理图片”升级为“结果对人和程序都可用”。不接模型，不追求炫酷效果；重点是让每次变换留下可检查的证据。

## 今天的问题

如何把原始像素转换为模型和人都能可靠使用的数据，并让结果能被下游程序读取？

## 前置条件与边界

- Day 1 的 `perception/inputs/wide.png` 可以被 OpenCV 解码。
- 所有变换函数接收内存中的 NumPy 数组，不负责寻找输入文件。
- 今天的检测框是固定模拟数据，用于练习结果契约，不代表模型已经完成检测。
- PNG 用于视觉审阅，JSON 用于程序消费；任何一方都不能悄悄表达另一套结果。

## 你要掌握

- OpenCV 默认读取的是 BGR；许多模型与 PIL 工具使用 RGB。颜色顺序错了，图像看起来仍“正常”，模型输入却已经变了。
- resize、crop 与 normalize 都是数据契约的一部分；必须把参数写入结构化结果。
- 图片适合人检查，JSON 适合程序检查；二者应对应同一次处理。

## 今天完成后你能做到什么

1. 使用可复用函数做等比例缩放、中心裁剪和 BGR→归一化 RGB 转换。
2. 生成一张带模拟检测框的图片和与之对应的 JSON。
3. 为形状正确、越界裁剪失败这两类情况留下自动化证据。

## 本单元产物

- 输入：Day 1 生成的 `wide.png`。
- 产物：`perception/image_ops.py`、`perception/test_image_ops.py`、一张标注图和一个 JSON。

## 操作教程

### 1. 先读数据流

今天的同一份输入会产生两类输出：

```text
输入 BGR 图像 → resize → center crop → annotate → PNG（给人）
                                      └──────────────→ JSON（给程序）
```

不要把归一化后的浮点 RGB 数组直接写成普通 PNG。它是给模型用的数值输入；给人检查的图片保持 BGR/uint8 更清晰。

### 2. 阅读并运行真实源码

完整文件：[展开 `image_ops.py`](#course-file:perception/image_ops.py)。先看四个函数各自的输入与输出，再运行：

```bash
# 创建证据目录，运行图像变换程序，并检查标注图片和结构化 JSON 输出。
cd ~/jetson-stu
mkdir -p diagnostics/day02
python3 perception/image_ops.py
file perception/outputs/day02/wide_annotated.png
python3 -m json.tool perception/outputs/day02/wide_annotated.json
```

预期：PNG 中有绿色框和 `demo-object 0.87`；JSON 中有 `image_size`、`transform` 与 `detections` 三个顶层字段。

### 3. 逐项核对 JSON 与图片

打开 PNG，同时阅读 JSON，回答：

1. JSON 的宽高是否等于输出图片实际尺寸？
2. `bbox_xyxy` 的四个数分别代表什么？
3. 为什么 `score` 是机器可读的数值，而不是画在图片上的文字？

然后把 `image_ops.py` 的 `detections` 中 `score` 改为 `0.42`，再运行一次。确认图片文字和 JSON 都变了，理解它们来自同一份结构化数据。观察完成后将值改回 `0.87`，保持示例源码与预期输出一致。

### 4. 运行边界测试

完整文件：[展开 `test_image_ops.py`](#course-file:perception/test_image_ops.py)。运行：

```bash
# 执行边界测试，验证裁剪、缩放、颜色转换和错误输入契约。
python3 -m pytest -q perception/test_image_ops.py
```

如果没有 `pytest`，当天只安装这个测试工具。现代 Ubuntu 的系统 Python 通常不允许直接用 pip 改系统环境，因此使用发行版包：

```bash
# 仅安装本课需要的 pytest 测试工具，然后重新执行测试。
sudo apt update
sudo apt install -y python3-pytest
python3 -m pytest -q perception/test_image_ops.py
```

预期：六个测试全部通过。它们分别覆盖裁剪尺寸、越界裁剪、等比例缩放、BGR→RGB 数值、错误 dtype 和标注不修改原输入。重点不是测试框架，而是变换契约和错误边界都能自动验证。

### 5. 做一个自己的小改动

把 `main()` 中的 crop 从 `360x240` 改为你选择的、仍能容纳在缩放图中的尺寸；重新运行并记录：输入尺寸、缩放尺寸、裁剪尺寸、输出尺寸。不要修改函数名或删除错误检查。

### 6. 保存本单元证据

```bash
# 保存程序、测试和 JSON 校验的原始输出，作为本单元验收证据。
python3 perception/image_ops.py | tee diagnostics/day02/image-ops.txt
python3 -m pytest -q perception/test_image_ops.py | tee diagnostics/day02/image-ops-tests.txt
python3 -m json.tool perception/outputs/day02/wide_annotated.json > /dev/null \
  && echo "PASS: valid JSON"
```

输出图片不提交 Git 时，至少保留生成命令、JSON 字段说明和测试输出。

## 常见问题与诊断顺序

- 颜色整体异常：先核对 BGR/RGB 转换位置，不要调模型阈值。
- crop 报越界：先打印 resize 后尺寸，再判断 crop 是否合理。
- 图片变了但 JSON 没变：检查可视化是否直接使用同一份 `detections`。
- 测试导入失败：确认从仓库根运行 `python3 -m pytest`，不要从 `perception/` 子目录改变导入语义。
- 浮点归一化超出 `[0, 1]`：检查输入是否真是 `uint8`，不要对已经归一化的数据再次除以 255。

## 实践

1. 运行 `image_ops.py`，保存 PNG 与 JSON。
2. 用 JSON 工具检查字段，不只看图片。
3. 运行三个自动化测试。
4. 改一次合法裁剪尺寸，并说明输出为什么变化。

## 产物与验收

- [ ] `wide_annotated.png` 与 `wide_annotated.json` 同时存在。
- [ ] 图片中的框、类别和分数与 JSON 的检测项一致。
- [ ] 六个测试通过；越界、dtype 和非原地修改行为都符合契约。
- [ ] 你能说出 BGR、RGB、归一化数组各自适合在哪里使用。

## 与后续课程的连接

Day 4 会用预训练权重自带的 transform 取代手写模型预处理，但今天学到的颜色、dtype、shape 和结构化结果契约仍然有效。Day 7 会把类似字段提升为 ROS 2 消息契约。

## 复盘

为什么视觉结果不能只保存在一张画了框的图片里？
