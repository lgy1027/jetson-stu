# Day 2：图像变换与结果表达

> 今天把 Day 1 的“能处理图片”升级为“结果对人和程序都可用”。不接模型，不追求炫酷效果；重点是让每次变换留下可检查的证据。

## 今天的问题

如何把原始像素转换为模型和人都能可靠使用的数据，并让结果能被下游程序读取？

## 你要掌握

- OpenCV 默认读取的是 BGR；许多模型与 PIL 工具使用 RGB。颜色顺序错了，图像看起来仍“正常”，模型输入却已经变了。
- resize、crop 与 normalize 都是数据契约的一部分；必须把参数写入结构化结果。
- 图片适合人检查，JSON 适合程序检查；二者应对应同一次处理。

## 今天完成后你能做到什么

1. 使用可复用函数做等比例缩放、中心裁剪和 BGR→归一化 RGB 转换。
2. 生成一张带模拟检测框的图片和与之对应的 JSON。
3. 为形状正确、越界裁剪失败这两类情况留下自动化证据。

## 时间和产物

- 预计：3–3.5 小时。
- 输入：Day 1 生成的 `wide.png`。
- 产物：`perception/image_ops.py`、`perception/test_image_ops.py`、一张标注图和一个 JSON。

## 操作教程

### 1. 先读数据流（15 分钟）

今天的同一份输入会产生两类输出：

```text
输入 BGR 图像 → resize → center crop → annotate → PNG（给人）
                                      └──────────────→ JSON（给程序）
```

不要把归一化后的浮点 RGB 数组直接写成普通 PNG。它是给模型用的数值输入；给人检查的图片保持 BGR/uint8 更清晰。

### 2. 阅读并运行真实源码（45 分钟）

完整文件：[展开 `image_ops.py`](#course-file:perception/image_ops.py)。先看四个函数各自的输入与输出，再运行：

```bash
cd ~/jetson-stu
python3 perception/image_ops.py
file perception/outputs/day02/wide_annotated.png
python3 -m json.tool perception/outputs/day02/wide_annotated.json
```

预期：PNG 中有绿色框和 `demo-object 0.87`；JSON 中有 `image_size`、`transform` 与 `detections` 三个顶层字段。

### 3. 逐项核对 JSON 与图片（30 分钟）

打开 PNG，同时阅读 JSON，回答：

1. JSON 的宽高是否等于输出图片实际尺寸？
2. `bbox_xyxy` 的四个数分别代表什么？
3. 为什么 `score` 是机器可读的数值，而不是画在图片上的文字？

然后把 `detections` 里的 `score` 改为 `0.42`，再运行一次。确认图片文字和 JSON 都变了，理解它们来自同一份结构化数据。

### 4. 运行边界测试（30 分钟）

完整文件：[展开 `test_image_ops.py`](#course-file:perception/test_image_ops.py)。运行：

```bash
python3 -m pytest -q perception/test_image_ops.py
```

如果没有 `pytest`，当天只安装这个测试工具。Ubuntu 24.04 的系统 Python 通常不允许直接用 pip 改系统环境，因此使用发行版包：

```bash
sudo apt update
sudo apt install -y python3-pytest
python3 -m pytest -q perception/test_image_ops.py
```

预期：三个测试全部通过。重点不是测试框架，而是“无效 crop 必须明确失败”，不能悄悄返回一张尺寸错误的图。

### 5. 做一个自己的小改动（30 分钟）

把 `main()` 中的 crop 从 `360x240` 改为你选择的、仍能容纳在缩放图中的尺寸；重新运行并记录：输入尺寸、缩放尺寸、裁剪尺寸、输出尺寸。不要修改函数名或删除错误检查。

## 实践

1. 运行 `image_ops.py`，保存 PNG 与 JSON。
2. 用 JSON 工具检查字段，不只看图片。
3. 运行三个自动化测试。
4. 改一次合法裁剪尺寸，并说明输出为什么变化。

## 产物与验收

- [ ] `wide_annotated.png` 与 `wide_annotated.json` 同时存在。
- [ ] 图片中的框、类别和分数与 JSON 的检测项一致。
- [ ] 三个测试通过；越界裁剪的错误能解释。
- [ ] 你能说出 BGR、RGB、归一化数组各自适合在哪里使用。

## 复盘

为什么视觉结果不能只保存在一张画了框的图片里？
