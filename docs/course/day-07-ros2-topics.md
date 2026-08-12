# Day 7：Topic 与消息契约

> 今天把“检测到一个物体”拆成下游程序真正能检查的字段。

## 今天的问题

视觉节点应发布哪些信息，才能让下游节点不依赖模型内部实现？

## 前置条件

- Day 6 的两个包可以构建；
- 当前终端已 source ROS 2 Jazzy 和 `ros2_ws/install/setup.bash`；
- 今天使用模拟检测结果，只学习消息边界，不运行模型。

## 你要掌握

- ROS 2 消息定义是跨节点接口，不是随意打印的文本。
- `stamp` 表示数据产生时间，`frame_id` 表示坐标参考系。
- 检测框使用 `xyxy`：左上角 `(x_min, y_min)` 到右下角 `(x_max, y_max)`。
- 消息定义改变后必须重新构建并重新 source workspace。

## 本单元产物

- `Detection2D.msg` 与 `Detection2DArray.msg`；
- 模拟检测发布者和结果监听器；
- topic 类型、内容与频率检查记录。

## 操作教程

### 1. 阅读消息定义

- [查看 `Detection2D.msg`](#course-file:ros2_ws/src/jetson_interfaces/msg/Detection2D.msg)
- [查看 `Detection2DArray.msg`](#course-file:ros2_ws/src/jetson_interfaces/msg/Detection2DArray.msg)

一帧结果包含：时间戳、`frame_id`、输入来源和检测数组；每个检测包含类别、分数和二维框。

| 字段 | 作用 |
|---|---|
| `header.stamp` | 标记这一帧数据产生的 ROS 时间，便于同步和判断数据是否过期 |
| `header.frame_id` | 指明检测结果所属坐标系，本阶段固定为 `camera` |
| `source_image` | 保留输入来源，回查结果时能找到对应图片 |
| `detections` | 一帧中的零个或多个检测结果 |
| `label` / `score` | 类别名和置信度，阈值过滤会使用 `score` |
| `x_min`～`y_max` | 图像像素坐标中的二维框，原点位于左上角 |

### 2. 重新构建消息和节点

```bash
# 消息定义由 rosidl 生成代码，修改后必须重新构建。
cd ~/jetson-stu/ros2_ws
source /opt/ros/jazzy/setup.bash
mkdir -p ../diagnostics/day07
colcon build --symlink-install --packages-select jetson_interfaces jetson_perception \
  | tee ../diagnostics/day07/build.txt
source install/setup.bash
```

检查生成后的接口：

```bash
# 查看 ROS 2 实际识别到的字段，不只阅读源码文件。
ros2 interface show jetson_interfaces/msg/Detection2D
ros2 interface show jetson_interfaces/msg/Detection2DArray
```

### 3. 运行模拟发布者

完整源码：

- [查看 `detection_publisher.py`](#course-file:ros2_ws/src/jetson_perception/jetson_perception/detection_publisher.py)
- [查看 `detection_listener.py`](#course-file:ros2_ws/src/jetson_perception/jetson_perception/detection_listener.py)

终端 A：

```bash
# 以 camera 作为坐标系，每 0.5 秒发布一帧模拟结果。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run jetson_perception detection_publisher --ros-args \
  -p frame_id:=camera -p publish_period:=0.5
```

终端 B：

```bash
# 监听结构化消息，并保存前几帧日志。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run jetson_perception detection_listener \
  | tee diagnostics/day07/listener.txt
```

### 4. 检查消息契约

终端 C：

```bash
# 查看一条完整消息、消息频率和发布订阅关系。
source /opt/ros/jazzy/setup.bash
source ~/jetson-stu/ros2_ws/install/setup.bash
ros2 topic echo /perception/detections --once
ros2 topic hz /perception/detections
ros2 topic info /perception/detections --verbose
```

重点检查：

1. `header.stamp` 不是全零；
2. `header.frame_id` 是 `camera`；
3. `source_image` 是 `simulated`；
4. 检测结果包含类别、分数和四个框坐标。

### 5. 验证参数错误

停止终端 A 的模拟发布者，再在同一终端执行：

```bash
# publish_period 小于等于 0 时，节点必须明确失败。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run jetson_perception detection_publisher --ros-args \
  -p publish_period:=0.0
echo "exit code: $?"
```

预期节点非零退出，并提示 `publish_period 必须大于 0`。

## 常见问题

| 现象 | 检查 |
|---|---|
| `The passed message type is invalid` | 消息包是否重新构建并重新 source |
| `frame_id` 为空 | 参数名和发布时赋值位置 |
| `topic hz` 无输出 | 发布者是否仍在运行，topic 名是否一致 |
| 修改 `.msg` 后字段没变化 | 删除旧终端环境，重新构建并打开新终端 |

## 实践

1. 查看两个接口的实际字段。
2. 发布并监听至少 10 帧结构化结果。
3. 用 `echo --once` 找到时间戳、坐标系、来源和检测框。
4. 用非法周期验证参数边界。

## 产物与验收

- [ ] 两个自定义接口可被 `ros2 interface show` 找到；
- [ ] `/perception/detections` 类型正确；
- [ ] 时间戳、`frame_id`、来源、类别、分数和框坐标完整；
- [ ] 发布频率约 2 Hz；
- [ ] 非法周期导致明确失败。

## 复盘

为什么只发布“检测到杯子”无法支持坐标转换、时效检查和安全规划？
