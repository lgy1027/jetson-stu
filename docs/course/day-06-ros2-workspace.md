# Day 6：第一个 ROS 2 包

## 今天的问题

如何把一个 Python 程序变成可被机器人系统发现、运行和组合的 ROS 2 节点？

## 你要掌握

- ROS 2 package 是代码、依赖和入口点的可分发单元。
- workspace 的 `src`、`build`、`install`、`log` 有不同职责；只提交 `src`。

## 实践

1. 核对 ROS 2 发行版与当前系统、CPU 架构的兼容路径；仅在缺失时安装必要组件。
2. 创建 `ros2_ws/src` 下的 Python package。
3. 编写最小 publisher 和 subscriber，使用自定义节点名与 topic 名。
4. 用 `colcon build` 构建、source workspace 后运行两个节点。

## 产物与验收

- 一个可构建 ROS 2 Python package。
- publisher/subscriber 能交换至少 10 条消息。
- `ros2_ws/build`、`install`、`log` 不进入 Git。

## 复盘

为什么 ROS 2 节点不应依赖当前 shell 的随意工作目录？
