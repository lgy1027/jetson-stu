# jetson-stu

Jetson AGX Thor 与具身智能学习项目。

本项目按照“Day 0 环境就绪 + 6 周、30 个主课日”的学习计划推进，目标是从 Jetson 端侧 AI 部署出发，尽快完成 ROS 2 感知流水线、机械臂运动规划，以及受约束的自然语言任务执行闭环。

## 测试设备

- NVIDIA Jetson AGX Thor Developer Kit 128GB（T5000）
- JetPack 7.2 / Jetson Linux 39.2
- Ubuntu 24.04 ARM64
- 1TB NVMe SSD

当前已验证的软件环境与操作规则见 [交接入口](AGENTS.md)。

## 学习文档

- [Codex跨设备交接入口](AGENTS.md)
- [课程入口](docs/README.md)
- [Day 0 + 30天实践计划](docs/course-plan.md)
- [每日课件](docs/course/README.md)
- [可点击课程工作台](course-app/README.md)

## 目录

```text
jetson-stu/
├── README.md             # 项目入口
├── docs/                 # 学习计划、笔记和报告
├── course-app/           # 可点击的课程、目标、教程和验收工作台
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

- [x] Day 0：环境与工作流就绪
- [ ] Day 1：第一张可复现的处理图片

## 版权与许可

Copyright © 2026 合肥枢维智能科技有限公司。项目采用 [Apache License 2.0](LICENSE)，其中包含明确的版权、专利授权与商标使用边界；归属声明见 [NOTICE](NOTICE)。
