# 每日课件目录

这套课程包含 Day 0 和 30 个实践单元。Day 是稳定编号，不是完成时限；一个复杂单元可以跨多次学习会话。学习进度由产物和验收决定。

## 课程入口

- [入门必读：Jetson 概念地图](foundations.md)
- [课程总计划、里程碑与完成定义](../course-plan.md)
- [Day 0：环境与工作流](day-00-environment.md)

## M1：可复现感知程序

目标：在 Jetson 上建立从文件输入到 GPU 模型和视频输出的第一条可复现感知链路。

1. [Day 1：第一张可复现的处理图片](day-01-image-pipeline.md)
2. [Day 2：图像变换与结果表达](day-02-image-ops.md)
3. [Day 3：让 PyTorch 真正使用 GPU](day-03-gpu-tensors.md)
4. [Day 4：第一批真实模型结果](day-04-model-inference.md)
5. [Day 5：从单图到视频](day-05-video-inference.md)

里程碑验收：图像与视频输出可检查，推理结果有结构化记录，GPU 计算有正确性和同步计时证据。

## M2：ROS 2 感知系统

目标：把已经验证的处理逻辑变成可发现、可配置、可回放的机器人软件组件。

6. [Day 6：第一个 ROS 2 包](day-06-ros2-workspace.md)
7. [Day 7：Topic 与消息契约](day-07-ros2-topics.md)
8. [Day 8：把感知逻辑接入 ROS 2](day-08-perception-node.md)
9. [Day 9：参数与 Launch](day-09-parameters-launch.md)
10. [Day 10：可回放的离线感知系统](day-10-rosbag-integration.md)

里程碑验收：一条 launch 命令可启动离线感知路径，关键消息可被录制、回放和复现。

## M3：可验证部署后端

目标：在同一输入和数据边界下验证 ONNX、ONNX Runtime 与 TensorRT，并形成上层可替换的后端接口。

11. [Day 11：导出 ONNX](day-11-onnx-export.md)
12. [Day 12：ONNX Runtime 基线](day-12-onnx-runtime.md)
13. [Day 13：在目标 Jetson 构建 TensorRT Engine](day-13-tensorrt-build.md)
14. [Day 14：三后端公平性能与内存基准](day-14-backend-benchmark.md)
15. [Day 15：部署选择与接口冻结](day-15-deployment-review.md)

里程碑验收：默认后端的正确性、延迟、吞吐、峰值内存和失败行为都有证据，上层只依赖稳定推理接口。

## M4：有物理含义的机器人目标

目标：把视觉像素变成带坐标系和时间条件的三维目标，并建立机器人模型与规划配置。

16. [Day 16：坐标变换的数学基础](day-16-coordinate-math.md)
17. [Day 17：相机模型、深度与三维点](day-17-camera-geometry.md)
18. [Day 18：把坐标关系放入 TF2](day-18-tf2.md)
19. [Day 19：用 URDF/Xacro 描述机械臂](day-19-urdf.md)
20. [Day 20：MoveIt 2 仿真配置](day-20-moveit-setup.md)

里程碑验收：固定像素和模拟深度能转换到 `base_link`，错误的深度、时间戳和 frame 被拒绝；机器人模型与规划组可加载。

## M5：安全任务规划

目标：只允许经过确定性检查的目标进入运动规划，并让失败成为结构化、可测试的正常结果。

21. [Day 21：规划一个合法目标](day-21-motion-planning.md)
22. [Day 22：让非法目标被拒绝](day-22-safety-rejection.md)
23. [Day 23：任务 Schema 与技能白名单](day-23-task-schema.md)
24. [Day 24：确定性任务状态机](day-24-state-machine.md)
25. [Day 25：感知结果成为候选任务目标](day-25-perception-to-task.md)

里程碑验收：合法目标产生规划轨迹；越界、碰撞、不可达、低置信度、过期与 TF 错误在正确层停止。

## M6：端到端作品

目标：集成已经独立验证的模块，完成成功、拒绝、指标、复现和最终边界说明。

26. [Day 26：把安全任务接入 MoveIt 仿真](day-26-moveit-task-integration.md)
27. [Day 27：第一次端到端闭环](day-27-end-to-end.md)
28. [Day 28：失败案例是安全功能](day-28-failure-cases.md)
29. [Day 29：可观测性、指标与项目复现](day-29-observability.md)
30. [Day 30：最终演示与下一阶段边界](day-30-final-demo.md)

里程碑验收：从干净终端可复现成功路径和至少五类安全拒绝；每次运行有 trace、阶段指标和结构化结果；README 能支持他人复现。

## 可选加深

这些内容不阻塞 30 个核心单元，只有主线需要时再学习：

- [视觉流水线的性能与可靠性](optional-vision-review.md)
- [部署失败不应悄悄发生](optional-deployment-reliability.md)
- [ROS 2 Service 与 Action](optional-ros2-services-actions.md)
- 本地 LLM/VLM、FP16/INT8、DeepStream 和真实硬件迁移将在核心课完成后形成独立进阶路线。

## 使用规则

1. 每次只推进当前单元能够验证的一小批内容。
2. 保存输入、命令、原始输出、配置和自己的结论。
3. 熟悉的概念可以快速阅读，但必须完成验收。
4. 安装、编译和下载耗时不等于学习进度，不需要追赶固定日历。
5. 当前单元的验收没有证据时，不标记完成。

从 [Day 1：第一张可复现的处理图片](day-01-image-pipeline.md) 开始。
