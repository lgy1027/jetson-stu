# Jetson 具身智能实战课程

面向有 Python、深度学习或大模型基础的学习者，系统学习 Jetson 端侧 AI 与具身智能工程。

课程采用“Day 0 环境就绪 + 6 个里程碑 + 30 个弹性实践单元”的路线，目标是完成从图像感知、CUDA/TensorRT 加速、ROS 2 通信、三维坐标变换，到机械臂仿真规划和安全任务执行的完整闭环。Day 是稳定编号，不是日历期限；每个单元以可运行产物和验收证据为完成标准。

线上课程：[lgy1027.github.io/jetson-stu](https://lgy1027.github.io/jetson-stu/)

## 测试设备

- NVIDIA Jetson AGX Thor Developer Kit 128GB（T5000）
- JetPack 7.2 / Jetson Linux 39.2
- Ubuntu 24.04 ARM64
- 1TB NVMe SSD

课程会在需要时记录具体软件版本和兼容性要求；学习者应以自己 Jetson 上的现场检查结果为准。

## 学习文档

- [课程入口](docs/README.md)
- [Day 0 + 30 个实践单元](docs/course-plan.md)
- [每日课件](docs/course/README.md)
- [可点击课程工作台](course-app/README.md)

## 目录

```text
jetson-stu/
├── README.md             # 项目入口
├── docs/                 # 学习计划、笔记和报告
├── course-app/           # 可点击的课程、目标、教程和验收工作台
├── diagnostics/          # CUDA、容器和环境检查工具
├── benchmarks/           # 延迟、吞吐、温度和功耗数据
├── perception/           # OpenCV、PyTorch、ONNX 和 TensorRT 实验
├── ros2_ws/src/          # ROS 2 packages
├── robot_description/    # URDF/Xacro 和机器人配置
├── task_planner/         # 语言任务、技能 Schema 和状态机
└── demo/                 # 演示配置、素材和说明
```

## 学习原则

1. 每个单元留下可检查的产物，而不是只看教程。
2. 先做确定性机器人技能，再接入 LLM/VLM。
3. 实验记录软件版本、输入、延迟、温度和功耗。
4. 不把 LLM 直接接入电机控制；动作必须经过 Schema、安全约束和规划器。
5. 当前没有机器人硬件，第一阶段使用图片、视频和仿真数据。

## 当前进度

- [x] Day 0：环境与工作流
- [ ] Day 1：第一张可复现的处理图片（下一单元）

## 版权与许可

Copyright © 2026 合肥枢维智能科技有限公司。项目采用 [Apache License 2.0](LICENSE)，其中包含明确的版权、专利授权与商标使用边界；归属声明见 [NOTICE](NOTICE)。
