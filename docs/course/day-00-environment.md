# Day 0：环境与工作流

## 今天的问题

如何确认 Jetson 能稳定用于后续实践，而不把环境检查扩展成多天任务？

## 你要掌握

- JetPack 是 Jetson 的系统与 AI 开发套件；CUDA 是 GPU 通用计算基础；cuDNN 和 TensorRT 分别服务于深度学习算子与推理优化。
- `nvidia-smi` 的 CUDA 字段不是 Toolkit 安装证明；真实 CUDA 编译/计算才是证据。
- SSH、tmux 和 Git 是远程实践的工作流工具，不是课程主题。

## 实践

1. 用普通用户通过 SSH 登录 Jetson；创建或恢复一个 `tmux` 会话。
2. 阅读 `diagnostics/day03_cuda_smoke.cu`，用自己的话说明它怎样证明 GPU 真正计算。
3. 运行已有 CUDA 烟雾测试或同等的最小 GPU 运算；只记录一次结果。
4. 确认 `~/jetson-stu` 是工作目录，并在其中创建当天的分支/工作区习惯。

## 产物与验收

- 能解释 JetPack、CUDA、cuDNN、TensorRT 的关系。
- 能在 Jetson 上运行一次真实 GPU 计算，并看到 PASS。
- 能从断开的 SSH 会话恢复 tmux。

## 复盘

为什么“驱动能看到 GPU”不等于“你的 CUDA 程序能编译并正确运行”？
