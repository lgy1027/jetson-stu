# 每日课件目录

这套课件按“先做可见结果，再接入机器人系统；先仿真验证，再谈真实硬件”组织。每周学习 5 天，第 6 天只用于补实验、复盘或休息。

| 周次 | 目标 | 每日课件 |
|---|---|---|
| Day 0 | 环境与工作方式就绪 | [Day 0：环境与工作流](day-00-environment.md) |
| Week 1 | 建立可复现的视觉输入、处理与推理闭环 | [Day 1：处理图片](day-01-image-pipeline.md) · [Day 2：图像变换](day-02-image-ops.md) · [Day 3：GPU 张量](day-03-gpu-tensors.md) · [Day 4：模型推理](day-04-model-inference.md) · [Day 5：视频推理](day-05-video-inference.md) |
| Week 2 | 尽早拥有 ROS 2 的可运行骨架 | [Day 6：工作空间](day-13-ros2-workspace.md) · [Day 7：Topic 契约](day-14-ros2-topics.md) · [Day 8：感知节点](day-15-perception-node.md) · [Day 9：参数与 Launch](day-16-parameters-launch.md) · [Day 10：Rosbag 回放](day-18-rosbag-integration.md) |
| Week 3 | 为已运行的感知系统选择可验证的部署后端 | [Day 11：ONNX](day-07-onnx-export.md) · [Day 12：ONNX Runtime](day-08-onnx-runtime.md) · [Day 13：TensorRT](day-09-tensorrt-build.md) · [Day 14：公平基准](day-10-backend-benchmark.md) · [Day 15：部署契约](day-12-deployment-review.md) |
| Week 4 | 让视觉结果在机器人坐标系和仿真中有物理含义 | [Day 16：坐标数学](day-19-coordinate-math.md) · [Day 17：TF2](day-20-tf2.md) · [Day 18：URDF](day-21-urdf.md) · [Day 19：MoveIt 配置](day-22-moveit-setup.md) · [Day 20：合法轨迹](day-23-motion-planning.md) |
| Week 5 | 明确安全边界，并把感知输入变成受约束任务 | [Day 21：安全拒绝](day-24-safety-rejection.md) · [Day 22：任务 Schema](day-25-task-schema.md) · [Day 23：状态机](day-26-state-machine.md) · [Day 24：感知到任务](day-27-perception-to-task.md) · [Day 25：端到端骨架](day-28-end-to-end.md) |
| Week 6 | 集成、失败测试、指标与最终作品集 | [Day 26：MoveIt 集成](day-26-moveit-task-integration.md) · [Day 27：失败案例](day-29-failure-cases.md) · [Day 28：可观测性](day-28-observability.md) · [Day 29：项目复现](day-30-portfolio.md) · [Day 30：最终演示](day-30-final-demo.md) |

## 使用方式

1. 只打开当天课件；不要预先批量执行后续命令。
2. 你亲手执行；每个小批次都先观察、解释，再继续。
3. 把命令、原始输出和你的结论保存为当天产物。
4. 只有完成验收条件，才标记该课程日完成。

从 [Day 1：第一张可复现的处理图片](day-01-image-pipeline.md) 开始。

## 可选加深（不计入 30 天主线）

当对应主线已完成、且第 6 天仍有精力时再阅读：视觉性能与可靠性、部署可靠性、ROS Service / Action。这三项不会阻塞后续课程。
