# Jetson 具身智能学习路线设计

**目标：** 用 12 周把现有的大模型应用开发能力，扩展为可在 Jetson AGX Thor 上完成感知、ROS 2 通信、任务规划与仿真机械臂执行的具身智能工程能力。

**当前条件：**

- NVIDIA Jetson AGX Thor Developer Kit 128GB
- JetPack 7.2 / Jetson Linux 39.2 / Ubuntu 24.04 ARM64
- 每天可投入 3～4 小时
- 已具备 Python、深度学习和大模型应用开发基础
- 暂无摄像头、机械臂、底盘等机器人硬件

## 路线选择

采用“纯 Jetson 与离线数据起步，最终面向机械臂视觉抓取”的路线。

前 12 周不依赖真机，使用图片、视频、ROS 2 测试消息、URDF 和 MoveIt 仿真完成软件闭环：

```text
自然语言目标
    ↓
结构化任务与安全约束
    ↓
图像/视频感知
    ↓
ROS 2 消息与 TF 坐标变换
    ↓
仿真机械臂运动规划
    ↓
执行结果与性能评估
```

## 为什么选择这条路线

1. 最大限度复用现有的 LLM/VLM 应用能力。
2. 在购买硬件前验证自己是否真正喜欢机器人系统开发。
3. ROS 2、TF2、URDF、MoveIt、TensorRT 都可迁移到后续真机。
4. 避免一开始同时处理电机、供电、通信、标定和模型兼容问题。
5. 先建立确定性机器人技能，再把大模型放在任务理解和技能选择层。

## 12 周阶段划分

| 阶段 | 周数 | 重点 | 阶段成果 |
|---|---:|---|---|
| Jetson AI 基线 | 1～3 | 系统、容器、视觉推理、ONNX、TensorRT | 一份可复现的模型推理基准报告 |
| ROS 2 工程基础 | 4～6 | Node、Topic、Service、Action、Launch、TF2、rosbag | 视频感知 ROS 2 流水线 |
| 机器人学与规划 | 7～8 | 坐标变换、URDF、关节、MoveIt | 仿真机械臂可执行目标位姿 |
| 具身闭环项目 | 9～12 | 语言任务、感知、抓取位姿、状态机、安全和评测 | 端到端仿真抓取演示项目 |

## 每日学习结构

每天 3～4 小时采用固定节奏：

- 30～45 分钟：阅读官方文档或核心理论
- 90～120 分钟：动手实现当天最小功能
- 30～45 分钟：测试、性能记录和故障定位
- 20～30 分钟：整理笔记、更新 README 和打卡

每周学习 6 天，第 7 天只复盘、补缺或休息。连续两天卡在同一问题时，先记录最小复现，再与 Codex 一起诊断，不靠反复重装解决。

## 技术边界

- 第一阶段使用 ROS 2 Jazzy。官方支持 Ubuntu 24.04 的 ARM64。
- JetPack 7.2 当前包含 CUDA 13.2.1、cuDNN 9.20 和 TensorRT 10.16.2。
- 在 NVIDIA 正式宣布 JetPack 7.2 兼容前，不混装面向 JetPack 7.1 的 Isaac ROS 包。
- 不把 Isaac Sim 作为 Jetson 本机第一阶段的必需项；优先使用 ROS 2、RViz、MoveIt 和可用的轻量仿真。
- LLM/VLM 只负责语义理解、任务拆分和技能选择；轨迹、安全约束及底层控制保持确定性。

## 12 周验收标准

完成时应能够独立解释并演示：

1. JetPack、CUDA、cuDNN、TensorRT、PyTorch和ROS 2之间的关系。
2. 同一视觉模型在PyTorch、ONNX Runtime和TensorRT下的延迟、吞吐、温度和功耗差异。
3. ROS 2 Topic、Service、Action、TF2、Launch和rosbag的使用场景。
4. 从相机坐标到机器人基坐标的变换过程。
5. URDF如何描述机械臂，MoveIt如何完成规划和碰撞检查。
6. 如何把自然语言任务约束为允许执行的机器人技能序列。
7. 端到端系统在异常输入、目标丢失和规划失败时如何安全退出。

## 第一阶段作品集

最终仓库至少包含：

```text
jetson-embodied-lab/
├── README.md
├── docs/
├── diagnostics/
├── benchmarks/
├── perception/
├── ros2_ws/src/
├── robot_description/
├── task_planner/
└── demo/
```

作品集需要有架构图、安装步骤、可复现实验、性能表格、演示视频、失败案例和下一步真机迁移方案。

## 参考入口

- JetPack 7.2：https://developer.nvidia.com/embedded/jetpack/downloads
- Jetson Thor 教程：https://www.jetson-ai-lab.com/tutorials/gtc26/
- ROS 2 Jazzy：https://docs.ros.org/en/jazzy/
- MoveIt 2：https://moveit.picknik.ai/
- Isaac ROS 支持表：https://nvidia-isaac-ros.github.io/getting_started/index.html
- Isaac Lab：https://isaac-sim.github.io/IsaacLab/
- LeRobot：https://huggingface.co/docs/lerobot/
