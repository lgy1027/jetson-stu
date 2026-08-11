# Day 0：环境与工作流

> Day 0 建立 Jetson 软件栈和实验记录基线。目标不是背诵版本号，而是证明当前设备能够编译并执行一次真实 CUDA 计算，并且后续实验有统一的记录边界。

## 今天的问题

如何建立可复现的 Jetson 开发方式，而不把环境检查扩展成多天任务？

## 你要掌握

- JetPack 是 Jetson 的兼容性基线；CUDA 是 GPU 计算平台；cuDNN 与 TensorRT 分别服务于深度学习算子和推理优化。
- `nvidia-smi` 的 CUDA 字段只反映驱动可报告的兼容能力；`nvcc` 与真实计算才构成开发和运行证据。
- 安装、版本和实验输出必须与具体实践关联，不能用一份模糊的“环境正常”替代证据。

## 今天完成后你能做到什么

1. 读取并记录 JetPack、L4T、CUDA、cuDNN 和 TensorRT 的当前版本。
2. 编译并运行一次 CUDA 烟雾测试，确认数值结果正确。
3. 在当前设备上验证 Docker GPU 运行时，确认容器能够访问 GPU。
4. 建立后续课程统一使用的实验记录格式。

## 本单元产物

- `$HOME/jetson-stu-day00/environment-components.txt` 与 `tensorrt-python.txt`；
- `$HOME/jetson-stu-day00/cuda-smoke-output.txt`；
- `$HOME/jetson-stu-day00/container-runtime.txt` 与 `container-gpu.txt`；
- 一段说明 JetPack、CUDA、cuDNN、TensorRT 职责的个人笔记。

以下命令会把本次结果保存到 `$HOME/jetson-stu-day00/`。这些记录用于本次学习和后续排查，不需要上传到远端。

## 操作教程

### 1. 确认仓库和当前用户

在 Jetson 的普通开发用户终端执行：

```bash
# 进入课程仓库，确认当前用户和实际工作目录。
cd ~/jetson-stu
pwd
whoami
hostname
```

`whoami` 不应显示 `root`。仓库路径以设备上的实际路径为准；后续命令均从仓库根目录执行。

### 2. 现场记录 Jetson 软件栈

在当前 Jetson 上采集实时信息，并把原始输出保存到本机：

```bash
# 采集本机时间、用户、系统、L4T、CUDA Toolkit、Python 和驱动信息。
mkdir -p "$HOME/jetson-stu-day00"
{
  echo "timestamp=$(date --iso-8601=seconds)"
  echo "user=$(whoami)"
  echo "hostname=$(hostname)"
  echo "kernel=$(uname -a)"
  cat /etc/nv_tegra_release
  nvcc --version
  python3 --version
  command -v nvidia-smi >/dev/null && nvidia-smi || true
} 2>&1 | tee "$HOME/jetson-stu-day00/environment-components.txt"

# 单独确认当前 Python 能加载 TensorRT，并记录绑定版本。
python3 -c 'import tensorrt as trt; print("TensorRT:", trt.__version__)' \
  | tee "$HOME/jetson-stu-day00/tensorrt-python.txt"
```

不要把 `nvidia-smi` 显示的 CUDA 版本当作 Toolkit 已安装的证明。不同设备的版本可能不同，以本次命令输出为准。

### 3. 编译并运行真实 CUDA 计算

烟雾测试会编译 CUDA 源码、执行 kernel、取回结果并进行数值校验：

```bash
# 编译仓库中的 CUDA 烟雾测试，并把本机运行结果保存到用户目录。
nvcc diagnostics/cuda_smoke.cu -o /tmp/jetson-stu-cuda-smoke
/tmp/jetson-stu-cuda-smoke | tee "$HOME/jetson-stu-day00/cuda-smoke-output.txt"
```

预期输出包含明确的 `PASS` 或数值校验成功结论。如果 `nvcc` 不存在，保留完整报错并停止在这里；不要根据驱动信息推测 Toolkit 已安装。

### 4. 现场验证 Docker GPU 运行时

先检查当前 Docker 是否注册 NVIDIA runtime，再运行一个 ARM64 基础容器确认 GPU 设备能够传入：

```bash
# 查看当前 Docker 的运行时配置。
docker info --format 'server={{.ServerVersion}} runtimes={{json .Runtimes}} default={{.DefaultRuntime}}' \
  | tee "$HOME/jetson-stu-day00/container-runtime.txt"

# 使用 ARM64 Ubuntu 容器检查 Jetson GPU 设备节点是否可见。
docker run --rm --runtime=nvidia --gpus all ubuntu:24.04 \
  bash -lc 'uname -m; ls -l /dev/nvhost-ctrl-gpu /dev/nvmap 2>/dev/null' \
  2>&1 | tee "$HOME/jetson-stu-day00/container-gpu.txt"
```

如果镜像首次下载耗时较长属于正常现象；如果当前 JetPack 对 `ubuntu:24.04` 的 GPU 运行时有兼容性限制，记录完整报错，并改用 NVIDIA 为当前 JetPack 提供的 ARM64 基础镜像。不要为了 Day 0 安装 PyTorch、ROS 2、Isaac ROS 或完整 DeepStream 环境。

### 5. 建立实验记录格式

每个后续实践至少记录四项：

```text
输入：文件、模型、参数或数据范围
命令：实际执行的命令和配置
原始输出：终端、JSON、图片、视频或测试结果
结论：成功条件、异常、版本和下一步
```

代码放在对应的 `perception/`、`ros2_ws/src/`、`robot_description/` 或 `task_planner/` 目录；生成图片、视频、模型和 TensorRT engine 遵循 `.gitignore` 规则，不直接提交到 Git。

## 常见问题与诊断顺序

| 现象 | 先检查什么 | 结论 |
|---|---|---|
| `nvcc: command not found` | CUDA Toolkit 是否安装，PATH 是否正确 | 不能声称开发工具链可用 |
| 驱动能看到 GPU，但编译失败 | `nvcc`、头文件、库路径和 JetPack 版本 | 驱动可见不等于 Toolkit 可用 |
| CUDA 程序运行但数值错误 | kernel、内存拷贝和校验逻辑 | 不能只看进程退出码 |
| TensorRT Python 导入失败 | 绑定是否由当前 JetPack 提供 | 不要从普通 x86 Python 环境复制包 |
| Docker 容器不能访问 GPU | NVIDIA Container Runtime 记录和容器参数 | 不要把宿主机 CUDA 路径硬挂载到任意镜像 |

## 实践

1. 在普通用户终端进入仓库并现场记录主机和软件栈。
2. 编译、运行 CUDA 烟雾测试并保存原始输出。
3. 现场验证 Docker GPU 运行时并保存原始输出。
4. 写下四项组件职责和当前环境与课程的兼容性结论。

## 产物与验收

- [ ] 当前用户不是 `root`，仓库路径正确。
- [ ] JetPack/L4T、CUDA Toolkit、Python 和 TensorRT 版本有记录。
- [ ] CUDA 测试有可保存的 PASS 或数值校验证据。
- [ ] 已理解驱动可见 GPU、`nvcc` 可用和 CUDA 程序正确计算是三件不同的事。
- [ ] 已建立后续实践使用的输入、命令、输出、结论记录格式。

## 复盘

为什么“驱动能看到 GPU”不等于“你的 CUDA 程序能编译并正确运行”？

Day 0 完成后，从 [Day 1：第一张可复现的处理图片](day-01-image-pipeline.md) 开始；不在 Day 0 预装后续所有框架。
