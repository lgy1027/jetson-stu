# Day 10：可回放的离线感知系统

> 今天把检测结果和状态录制为 rosbag，在感知节点停止后重新回放给下游节点。

## 今天的问题

如何保存一次 topic 数据流，让问题复现不再依赖原始感知节点仍在运行？

## 前置条件与边界

- Day 9 的 Launch 可以稳定运行；
- rosbag 目录可能较大，不提交 Git；
- bag 保存 topic 消息，不保存源码、参数文件、环境版本和进程内部状态。

## 你要掌握

- `ros2 bag record` 订阅并持久化指定 topic。
- `ros2 bag info` 查看时长、消息数和类型。
- `ros2 bag play` 重新发布消息，下游节点无需知道数据来自实时节点还是 bag。
- 回放时不能同时运行原发布者，否则 topic 会混入两路数据。

## 本单元产物

- `ros2_ws/bags/day10/` bag 目录；
- bag 信息和回放监听日志；
- M2 的构建、topic、参数、Launch、错误与回放证据。

## 操作教程

### 1. 创建本地目录

```bash
# bag 和诊断记录都保存在项目对应目录；这些生成物不会提交 Git。
cd ~/jetson-stu
mkdir -p ros2_ws/bags diagnostics/day10

# ros2 bag 不会覆盖同名目录；重复学习时先把旧证据改名保留。
if [ -d ros2_ws/bags/day10 ]; then
  mv ros2_ws/bags/day10 "ros2_ws/bags/day10.backup-$(date +%Y%m%d-%H%M%S)"
fi

source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
```

### 2. 启动数据源

终端 A：

```bash
# 启动 Day 9 的完整离线感知系统。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 launch jetson_perception offline_perception.launch.py
```

确认两个 topic 都在发布：

```bash
# 查看检测和状态 topic 的类型。
ros2 topic list -t | grep '/perception/'
```

### 3. 录制约 15 秒

终端 B：

```bash
# 只录制系统边界上的检测和状态，不使用 -a 录制所有无关 topic。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 bag record \
  -o ros2_ws/bags/day10 \
  /perception/detections \
  /perception/status
```

等待约 15 秒后按 `Ctrl+C`。不要在录制进程仍写盘时强制断电。

### 4. 检查 bag

```bash
# 保存 bag 的时长、消息数量、topic 和类型信息。
ros2 bag info ros2_ws/bags/day10 \
  | tee diagnostics/day10/bag-info.txt
```

检查：

- 包含两个 topic；
- `/perception/detections` 类型为 `jetson_interfaces/msg/Detection2DArray`；
- 每个 topic 都有多条消息；
- 时长接近实际录制时间。

### 5. 停止实时节点并回放

先停止终端 A，确保原感知节点不再发布。

终端 C 启动下游监听器：

```bash
# 只运行订阅者，证明下游可以消费回放数据。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run jetson_perception detection_listener \
  | tee diagnostics/day10/replay-listener.txt
```

终端 B 回放：

```bash
# 按录制时间重新发布消息；--clock 同时发布回放时钟。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 bag play ros2_ws/bags/day10 --clock
```

监听器应重新收到和录制阶段相同类型的检测结果。

`--clock` 会额外发布 `/clock`。本课监听器使用消息中已经录制的时间戳，不依赖仿真时间；后续节点若启用 `use_sim_time`，才会主动使用 `/clock`。

### 6. 验证回放边界

```bash
# 回放期间检查发布者来源和消息频率。
ros2 topic info /perception/detections --verbose
timeout 10 ros2 topic hz /perception/detections || true
```

回放可以复现消息内容和时间关系，但不会自动恢复：

- Git commit 和依赖版本；
- Launch/YAML 参数文件；
- 没有发布到 topic 的内部变量；
- 原始 GPU、CPU、温度和内存状态。

## 常见问题

| 现象 | 检查 |
|---|---|
| 输出目录已存在 | 删除或改名具体 bag 目录后重录，不要覆盖证据 |
| 回放时监听器无消息 | 是否 source 包含自定义消息的 workspace |
| 消息数比预期多 | 原发布者是否仍在运行，是否混入实时数据 |
| `unknown message type` | `jetson_interfaces` 是否已构建并 source |

## 实践

1. 录制两个关键 topic 约 15 秒。
2. 用 `ros2 bag info` 检查消息数和类型。
3. 停止实时感知节点。
4. 只启动监听器并回放 bag。
5. 写下 rosbag 能复现和不能复现的内容。

## 产物与验收

- [ ] bag 包含检测和状态两个 topic；
- [ ] 两个 topic 都有多条消息；
- [ ] 原发布者停止后，监听器仍能收到回放结果；
- [ ] 回放时没有混入实时发布者；
- [ ] bag 目录未进入 Git；
- [ ] 能说明 rosbag 不等于完整实验环境快照。

## M2 里程碑验收

- [ ] 两个 ROS package 可从干净终端构建；
- [ ] 自定义消息包含时间戳、坐标系和结构化检测字段；
- [ ] 离线图片节点有成功、阈值过滤和读取失败路径；
- [ ] YAML 与 Launch 能复现相同配置；
- [ ] rosbag 能在感知节点停止后驱动下游监听器。

## 复盘

为什么保存了 rosbag，仍然需要保存 Git commit、参数文件和软件版本？
