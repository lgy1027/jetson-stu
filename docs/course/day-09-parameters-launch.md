# Day 9：参数、YAML 与 Launch

> 今天把长命令中的配置移到 YAML，并用一条 Launch 命令启动完整离线感知路径。

## 今天的问题

怎样在不修改源码的情况下切换输入、阈值、坐标系和处理周期？

## 前置条件

- Day 8 节点可以独立运行；
- `wide.png` 输入仍然存在；
- 已重新构建最新的 `jetson_perception` 包。

## 你要掌握

- ROS 参数改变节点行为，YAML 保存一组可复现配置。
- Launch 负责组合节点、参数和启动边界。
- 节点名必须和 YAML 顶层键匹配，否则参数不会加载。
- 相对路径相对于启动命令的当前目录，不是 Launch 文件目录。

## 本单元产物

- `offline_perception.yaml`；
- `offline_perception.launch.py`；
- 一条命令启动感知节点和检测监听器。

## 操作教程

### 1. 阅读配置和 Launch

- [查看 `offline_perception.yaml`](#course-file:ros2_ws/src/jetson_perception/config/offline_perception.yaml)
- [查看 `offline_perception.launch.py`](#course-file:ros2_ws/src/jetson_perception/launch/offline_perception.launch.py)
- [查看 `setup.py` 的安装配置](#course-file:ros2_ws/src/jetson_perception/setup.py)

`setup.py` 必须安装 `launch/` 和 `config/`，否则源码目录存在文件，`ros2 launch` 仍然找不到。

### 2. 构建并确认安装结果

```bash
# 重新构建后，检查 Launch 和 YAML 是否进入 install 目录。
cd ~/jetson-stu/ros2_ws
source /opt/ros/jazzy/setup.bash
mkdir -p ../diagnostics/day09
colcon build --symlink-install --packages-select jetson_interfaces jetson_perception \
  | tee ../diagnostics/day09/build.txt
source install/setup.bash
find install/jetson_perception/share/jetson_perception -maxdepth 2 -type f | sort
```

应能看到 `config/offline_perception.yaml` 和 `launch/offline_perception.launch.py`。

### 3. 一条命令启动系统

```bash
# 从仓库根启动，Launch 会同时运行感知节点和检测监听器。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 launch jetson_perception offline_perception.launch.py \
  | tee diagnostics/day09/launch.txt
```

终端应同时出现两个节点的日志。另开终端检查：

```bash
# 查看节点、参数值和两个输出 topic。
source /opt/ros/jazzy/setup.bash
source ~/jetson-stu/ros2_ws/install/setup.bash
ros2 node list
ros2 param list /image_perception
ros2 param get /image_perception score_threshold
ros2 topic list -t | grep perception
```

### 4. 运行时修改参数

```bash
# 把阈值改为 0.9；固定结果分数为 0.87，因此检测数组应变为空。
ros2 param set /image_perception score_threshold 0.9
ros2 topic echo /perception/detections --once

# 恢复阈值，下一帧应重新出现检测结果。
ros2 param set /image_perception score_threshold 0.5
ros2 topic echo /perception/detections --once
```

参数修改只影响当前进程；下次 Launch 仍从 YAML 加载 `0.5`。

### 5. 验证非法参数

停止 Launch 后执行：

```bash
# 阈值超出 0~1，节点应在启动时明确失败。
ros2 run jetson_perception image_perception --ros-args \
  -p score_threshold:=1.5
echo "exit code: $?"
```

预期非零退出，并提示 `score_threshold 必须在 0 到 1 之间`。

### 6. 运行配置文件测试

[查看 `test_package_files.py`](#course-file:ros2_ws/src/jetson_perception/test/test_package_files.py)

```bash
# 用 colcon 执行包测试并查看详细结果。
cd ~/jetson-stu/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon test --packages-select jetson_perception
colcon test-result --verbose
```

## 常见问题

| 现象 | 检查 |
|---|---|
| Launch 文件找不到 | `setup.py` data_files、重新构建和重新 source |
| YAML 没生效 | 顶层节点名是否为 `image_perception` |
| 相对路径读取失败 | 是否从仓库根执行 `ros2 launch` |
| 修改 YAML 后仍是旧值 | 是否重新构建并重新 source install |

## 实践

1. 用一条 Launch 命令启动两个节点。
2. 查看五个参数的当前值。
3. 运行时修改阈值并观察检测数组变化。
4. 验证非法阈值会失败。
5. 运行 package 测试。

## 产物与验收

- [ ] Launch 一次启动两个节点；
- [ ] YAML 中五个参数全部生效；
- [ ] 阈值修改会改变检测数组；
- [ ] 非法阈值明确失败；
- [ ] `colcon test-result` 无失败项。

## 复盘

哪些配置适合放在参数中，哪些内容应由代码和版本控制固定？
