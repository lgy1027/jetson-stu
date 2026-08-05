# Day 0：环境与工作流

> Day 0 只用一天。目标不是背版本号，而是证明你能从自己的电脑稳定进入 Jetson、恢复工作现场，并运行一次真实 GPU 计算。已完成本日的同学只需保留产物记录，不必重复执行。

## 今天的问题

如何建立可复现的 Jetson 开发方式，而不把环境检查扩展成多天任务？

## 你要掌握

- JetPack 是 Jetson 的兼容性基线；CUDA 是 GPU 计算平台；cuDNN 与 TensorRT 分别服务于深度学习算子和推理优化。
- `nvidia-smi` 的 CUDA 字段只反映驱动可报告的兼容能力；`nvcc` 与真实计算才构成开发/运行证据。
- SSH、tmux 与 Git 是让实验可恢复的工作流工具，不是本周单独学习的主题。

## 今天完成后你能做到什么

1. 从 Mac 免密 SSH 登录普通 Jetson 用户，并知道如何退出。
2. 断开后恢复 tmux 工作会话。
3. 在仓库中运行一次既有 CUDA 烟雾测试，保留 PASS 证据。
4. 知道后续安装只能由当天实践目标触发。

## 时间和产物

- 预计：2–3 小时；若 SSH 与 CUDA 已验证，30 分钟完成复盘即可。
- 产物：SSH 可用、tmux 会话、`diagnostics/day03-cuda-smoke-output.txt` 或等价终端记录。

## 操作教程

### 1. 从 Mac 连接（20 分钟）

在 Mac 终端执行，将占位符替换为你的普通 Jetson 用户和当前局域网地址；不要使用 root：

```bash
ssh <jetson-user>@<jetson-lan-ip>
whoami
hostname
```

预期：`whoami` 显示普通用户。首次连接可能询问主机指纹；只在确认是自己的 Jetson 后接受。若仍要求密码，检查 Mac 的 `~/.ssh` 私钥权限与 Jetson 的 `~/.ssh/authorized_keys`，不要关闭 SSH 的安全校验。

### 2. 建立可恢复终端（20 分钟）

在 Jetson 上执行：

```bash
if ! command -v tmux >/dev/null; then
  sudo apt update
  sudo apt install -y tmux
fi
tmux new -s jetson-study
pwd
```

在 tmux 中按 `Ctrl-b` 再按 `d` 断开会话；回到普通 shell 后执行：

```bash
tmux attach -t jetson-study
```

预期：你能看到之前的 `pwd`。以后网络临时断开时，实验不会丢失。

### 3. 只验证一次真实 CUDA 工作（35 分钟）

先阅读而不是直接运行：[展开 `day03_cuda_smoke.cu`](#course-file:diagnostics/day03_cuda_smoke.cu)。说明它为什么比“GPU 列表存在”更有力：它编译 CUDA 代码、执行核函数、把结果取回并检查数值。

在 Jetson 仓库根目录执行已有测试；若文件名已不同，使用你 Day 0 已验证的等价测试，不新建另一套：

```bash
cd ~/jetson-stu
nvcc diagnostics/day03_cuda_smoke.cu -o /tmp/day03_cuda_smoke
/tmp/day03_cuda_smoke | tee diagnostics/day03-cuda-smoke-output.txt
```

预期：有明确 `PASS` 或数值校验成功的结论。若 `nvcc` 不存在，停止在这里记录完整报错；不要根据 `nvidia-smi` 推测 Toolkit 已安装。

### 4. 建立每天的最小记录（20 分钟）

每次实践只记录四件事：输入、命令、原始输出、你的结论。Day 1 开始，代码都放在 `perception/`，结果放在被忽略的 `perception/outputs/`，不要把大图片、模型权重或 TensorRT 引擎直接提交到 Git。

## 实践

1. 完成一次 SSH 登录和一次 tmux 恢复。
2. 阅读 CUDA 烟雾测试，运行一次并保存原始输出。
3. 写下 JetPack、CUDA、cuDNN、TensorRT 各自的一句话职责。

## 产物与验收

- [ ] SSH 使用普通用户，未启用远程 root 登录。
- [ ] tmux 会话可从断连后恢复。
- [ ] 真实 CUDA 测试有可保存的 PASS 证据。
- [ ] 能解释“驱动可见 GPU”与“CUDA 程序可编译并正确计算”的区别。

## 复盘

为什么“驱动能看到 GPU”不等于“你的 CUDA 程序能编译并正确运行”？
