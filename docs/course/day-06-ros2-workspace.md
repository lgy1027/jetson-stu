# Day 6：第一个 ROS 2 包

> 今天把普通 Python 程序放进 ROS 2 workspace，完成第一个可发现、可构建、可通信的包。

## 今天的问题

如何把 Python 程序变成 ROS 2 能发现、运行和组合的节点？

## 前置条件与边界

- Ubuntu 24.04 ARM64 对应 ROS 2 Jazzy；先确认实际系统版本，不要在其他 Ubuntu 版本上照搬发行版名称。
- ROS 2 的二进制包依赖系统 Python。若正在使用 uv/Conda 环境，先 `deactivate`，再使用 `/usr/bin/python3` 构建本阶段包。
- 今天只使用 `rclpy`、`std_msgs` 和 `colcon`，不安装 Isaac ROS。

## 你要掌握

- package 保存源码、依赖和可执行入口；workspace 管理一组 package。
- `src/` 是源码，`build/`、`install/`、`log/` 是构建产物。
- 每个新终端都要先 source ROS，再 source 当前 workspace。
- topic 是发布者和订阅者之间的异步数据通道。

## 本单元产物

- `jetson_perception` Python package；
- `hello_publisher` 与 `hello_subscriber` 两个节点；
- 至少 10 条成功收发消息的日志。

## 操作教程

下面使用 `~/jetson-stu` 表示仓库根目录；如果你的仓库位于其他位置，请替换为实际路径。

### 1. 确认系统和 ROS 2

```bash
# 回到系统 Python，确认 Ubuntu、CPU 架构和 ROS 2 发行版。
deactivate 2>/dev/null || true
cat /etc/os-release | grep -E '^(NAME|VERSION_ID|VERSION_CODENAME)='
uname -m
command -v ros2 || true
```

在 Ubuntu 24.04 ARM64 上，本课程使用 ROS 2 Jazzy。若 `ros2` 不存在，先按 [ROS 2 Jazzy Ubuntu 安装说明](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html) 配置官方软件源，再安装开发所需组件：

```bash
# 软件源配置完成后，安装 ROS Base 和构建工具。
sudo apt update
sudo apt install -y ros-jazzy-ros-base ros-dev-tools python3-colcon-common-extensions
```

然后加载 ROS 环境并检查：

```bash
# setup.bash 将 ros2、rclpy 和 Jazzy 包加入当前终端环境。
source /opt/ros/jazzy/setup.bash
echo "ROS_DISTRO=$ROS_DISTRO"
which python3
python3 -c 'import rclpy; print("rclpy: OK")'
```

预期 `ROS_DISTRO=jazzy`，Python 应来自系统路径，而不是 Conda 环境。

### 2. 认识包结构

课程已经提供完整包，不需要重新运行 `ros2 pkg create`。先查看关键文件：

- [查看 `package.xml`](#course-file:ros2_ws/src/jetson_perception/package.xml)
- [查看 `setup.py`](#course-file:ros2_ws/src/jetson_perception/setup.py)
- [查看 `hello_publisher.py`](#course-file:ros2_ws/src/jetson_perception/jetson_perception/hello_publisher.py)
- [查看 `hello_subscriber.py`](#course-file:ros2_ws/src/jetson_perception/jetson_perception/hello_subscriber.py)

`package.xml` 声明 ROS 依赖；`setup.py` 把 Python 函数注册为 `ros2 run` 可调用的入口。

### 3. 安装依赖并构建

```bash
# 从 workspace 根目录安装声明的依赖，并只构建课程的两个包。
cd ~/jetson-stu/ros2_ws
mkdir -p ../diagnostics/day06
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select jetson_interfaces jetson_perception \
  | tee ../diagnostics/day06/build.txt
```

`--symlink-install` 让 Python 源码修改后无需每次复制安装；修改消息定义或 `setup.py` 后仍需重新构建。

### 4. 运行发布者和订阅者

终端 A：

```bash
# 每个新终端都加载系统 ROS 和当前 workspace。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run jetson_perception hello_publisher
```

终端 B：

```bash
# 启动订阅者，并把收到的前 10 条以上消息保存为证据。
cd ~/jetson-stu
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run jetson_perception hello_subscriber \
  | tee diagnostics/day06/subscriber.txt
```

订阅者应持续打印 `收到第 N 条`。按 `Ctrl+C` 停止两个节点。

### 5. 用 ROS 2 命令检查系统

```bash
# 发布者运行时，检查节点、topic、消息类型和发布频率。
ros2 node list
ros2 topic list -t
ros2 topic info /course/hello --verbose
ros2 topic hz /course/hello
```

预期 `/course/hello` 类型为 `std_msgs/msg/String`，频率约 2 Hz。

## 常见问题

| 现象 | 检查 |
|---|---|
| `ros2: command not found` | 是否 source `/opt/ros/jazzy/setup.bash` |
| 找不到 `jetson_perception` | 是否构建成功并 source `ros2_ws/install/setup.bash` |
| `rclpy` 导入失败 | 是否误用了 Conda/uv 中不兼容的 Python |
| `rosdep` 尚未初始化 | 首次执行 `sudo rosdep init`，然后执行 `rosdep update` |
| 两个节点看不到彼此 | `ROS_DOMAIN_ID`、RMW 配置和两个终端的环境是否一致 |

## 实践

1. 构建两个课程包。
2. 启动发布者和订阅者，观察至少 10 条消息。
3. 用 `ros2 topic info` 和 `ros2 topic hz` 检查 topic。
4. 解释 `src`、`build`、`install`、`log` 的用途。

## 产物与验收

- [ ] `colcon build` 成功；
- [ ] `ros2 pkg executables jetson_perception` 能看到两个 hello 节点；
- [ ] 订阅者收到至少 10 条消息；
- [ ] `/course/hello` 频率约为 2 Hz；
- [ ] `build/`、`install/`、`log/` 没有进入 Git。

## 复盘

为什么 ROS 2 节点不应依赖启动终端的随意工作目录？
