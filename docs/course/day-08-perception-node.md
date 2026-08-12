# Day 8：把离线感知接入 ROS 2

> 今天把 Day 1–2 的文件输入、错误检查和标注输出包装成 ROS 2 节点。

## 今天的问题

如何让离线图片持续产生结构化检测消息，同时让读取和写入错误可观察？

## 前置条件与边界

- Day 1 已生成 `perception/inputs/wide.png`；
- Day 7 的自定义消息可以构建和查看；
- 今天使用固定模拟检测框，真实 PyTorch/ONNX/TensorRT 后端在 M3 完成后接入；
- 节点从仓库根目录启动，YAML 中的相对路径才有一致含义。

## 你要掌握

- ROS 节点负责参数、定时器、输入输出和错误状态。
- 固定检测器只是替身；消息契约以后不随推理后端改变。
- 文件读取失败应发布状态，不应伪造空白成功结果。
- 处理周期由定时器控制，回调中不能无限等待。

## 本单元产物

- `image_perception` 节点；
- `/perception/detections` 与 `/perception/status` 两个 topic；
- 标注图片 `perception/outputs/ros2/annotated.png`。

## 操作教程

### 1. 准备输入并构建

如果 Day 1 输入不存在，先生成：

```bash
# 使用当前 Python 环境生成固定的宽图和高图。
cd ~/jetson-stu
python3 perception/make_sample_images.py
file perception/inputs/wide.png
```

构建 ROS 2 包：

```bash
# 使用系统 ROS Python 构建节点，并创建本日证据目录。
deactivate 2>/dev/null || true
cd ~/jetson-stu/ros2_ws
source /opt/ros/jazzy/setup.bash
mkdir -p ../diagnostics/day08
colcon build --symlink-install --packages-select jetson_interfaces jetson_perception \
  | tee ../diagnostics/day08/build.txt
```

### 2. 阅读节点源码

[查看 `image_perception_node.py`](#course-file:ros2_ws/src/jetson_perception/jetson_perception/image_perception_node.py)

重点找到：

- 五个参数及其默认值；
- `cv2.imread` 的失败分支；
- `score_threshold` 如何决定是否发布检测；
- 输出目录创建和 `cv2.imwrite` 检查；
- 状态 topic 的 JSON 内容。

### 3. 启动离线感知节点

终端 A：

```bash
# 从仓库根启动，确保相对输入路径指向课程文件。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run jetson_perception image_perception --ros-args \
  -p input_path:=perception/inputs/wide.png \
  -p output_path:=perception/outputs/ros2/annotated.png \
  -p frame_id:=camera \
  -p score_threshold:=0.5 \
  -p publish_period:=1.0
```

终端 B：

```bash
# 检查一帧检测结果和一条状态消息。
source /opt/ros/jazzy/setup.bash
source ~/jetson-stu/ros2_ws/install/setup.bash
ros2 topic echo /perception/detections --once
ros2 topic echo /perception/status --once
```

预期状态包含 `"level": "ok"`，检测结果包含一个 `demo-object`。

### 4. 检查输出和持续发布

```bash
# 确认标注图片存在，并观察 10 秒内的发布频率。
cd ~/jetson-stu
file perception/outputs/ros2/annotated.png
timeout 10 ros2 topic hz /perception/detections \
  | tee diagnostics/day08/topic-hz.txt || true
```

频率应接近 1 Hz。打开输出图，确认中央有绿色框。

### 5. 验证错误输入

停止终端 A 后执行：

```bash
# 使用不存在的图片，节点应发布 error 状态，而不是发布伪检测。
ros2 run jetson_perception image_perception --ros-args \
  -p input_path:=perception/inputs/not-here.png \
  -p publish_period:=1.0
```

另一个终端查看：

```bash
# 只取一条错误状态。
ros2 topic echo /perception/status --once
```

预期 `level` 为 `error`，详情说明无法读取图片。

## 常见问题

| 现象 | 检查 |
|---|---|
| 节点持续报无法读取 | 是否从仓库根启动，相对路径是否存在 |
| `cv2` 导入失败 | 系统是否安装 `python3-opencv`，ROS 是否使用系统 Python |
| topic 有数据但图片不存在 | 输出目录权限和 `cv2.imwrite` 返回值 |
| 分数阈值改高后无检测 | 这是预期过滤结果，检查 status 是否仍为 ok |

## 实践

1. 运行节点并取得一帧检测和状态消息。
2. 打开标注输出图片。
3. 测量约 10 秒的 topic 频率。
4. 用不存在的输入验证错误状态。
5. 把阈值改为 `0.9`，解释检测数组为何为空。

## 产物与验收

- [ ] 节点持续发布约 1 Hz 的检测消息；
- [ ] 消息带当前时间戳、`camera` 和输入路径；
- [ ] 标注图片可打开；
- [ ] 输入不存在时发布 error 状态；
- [ ] 阈值 `0.9` 时不发布低于阈值的检测项。

## 复盘

为什么节点的消息接口不应随着 PyTorch、ONNX 或 TensorRT 后端变化？
