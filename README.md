# jetson-stu

Jetson AGX Thor 与具身智能学习项目。

本项目按照 12 周学习计划推进，目标是从 Jetson 端侧 AI 部署出发，逐步完成 ROS 2 感知流水线、机械臂运动规划，以及受约束的自然语言任务执行闭环。

## 测试设备

- NVIDIA Jetson AGX Thor Developer Kit 128GB（T5000）
- JetPack 7.2 / Jetson Linux 39.2
- Ubuntu 24.04 ARM64
- 1TB NVMe SSD

详细信息和验证状态见 [系统基线](docs/system-baseline.md)。

## 学习文档

- [Codex跨设备交接入口](AGENTS.md)
- [学习路线设计](docs/2026-08-03-jetson-embodied-ai-learning-design.md)
- [12周每日学习计划](docs/2026-08-03-jetson-embodied-ai-learning-plan.md)
- [系统基线](docs/system-baseline.md)

## 目录

```text
jetson-stu/
├── README.md             # 项目入口
├── docs/                 # 学习计划、笔记和报告
├── diagnostics/          # Jetson诊断与环境检查脚本
├── benchmarks/           # 延迟、吞吐、温度和功耗数据
├── perception/           # OpenCV、PyTorch、ONNX和TensorRT实验
├── ros2_ws/src/          # ROS 2 packages
├── robot_description/    # URDF/Xacro和机器人配置
├── task_planner/         # 语言任务、技能Schema和状态机
└── demo/                 # 演示配置、素材和说明
```

## 学习原则

1. 每天留下可检查的产物，而不是只看教程。
2. 先做确定性机器人技能，再接入LLM/VLM。
3. 实验必须记录软件版本、输入、延迟、温度和功耗。
4. 不把LLM直接接入电机控制；动作必须经过Schema、安全约束和规划器。
5. 当前没有机器人硬件，第一阶段使用图片、视频和仿真数据。

## 当前进度

- [x] 确认学习方向：纯Jetson起步，最终面向机械臂视觉抓取
- [x] 制定12周学习计划
- [x] Day 1：建立仓库和系统基线
- [x] Day 2：SSH、文件传输与终端效率
