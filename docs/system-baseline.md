# Jetson AGX Thor 系统基线

## 文档状态

- 原始报告采集时间：2026-07-31 09:49:24 CST
- 文档整理时间：2026-08-04
- 设备：NVIDIA Jetson AGX Thor Developer Kit
- 安装后复核时间：2026-08-04 12:37:29 CST
- 状态：硬件、Jetson Linux及JetPack开发组件均已确认

这份基线用于复现实验环境。原始报告是在安装完整 `nvidia-jetpack` 之前采集的；2026-08-04已完成安装后的实时复核，确认CUDA开发工具、cuDNN和TensorRT均可用。

## 硬件配置

| 项目 | 已观测值 | 证据/说明 |
|---|---|---|
| 开发套件 | NVIDIA Jetson AGX Thor Developer Kit | `/proc/device-tree/model` |
| 模组 | Jetson T5000 128GB | 板号 `P3834-0008`，报告识别内存约122GiB |
| 载板 | P4071-0000 | compatible字符串 `nvidia,p4071-0000+p3834-0008` |
| SoC | Tegra 264 / NVIDIA Thor | `nvidia,tegra264`，`nvidia-smi`显示NVIDIA Thor |
| CPU | 14核ARM64 | `lscpu`显示14个在线CPU，最高2601MHz |
| 内存 | 128GB统一内存 | Linux可见约122GiB；CPU与集成GPU共享 |
| 系统盘 | WD PC SN5000S 1TB NVMe | 设备容量953.9G |
| 根分区 | ext4，约936G | 已用54G，可用835G，使用率7%（采集时） |

## 软件配置

| 项目 | 版本/状态 | 验证方式 |
|---|---|---|
| Ubuntu | 24.04.4 LTS Noble | `/etc/os-release` |
| 架构 | aarch64 / ARM64 | `uname -m`、`lscpu` |
| Jetson Linux / L4T | R39.2.0 | `/etc/nv_tegra_release`、`nvidia-l4t-core` |
| JetPack | 7.2-b187 | `dpkg-query -W nvidia-jetpack`，2026-08-04实测 |
| 内核 | 6.8.12-1021-tegra | `uname -a` |
| NVIDIA驱动 | 595.78 | `nvidia-smi`（采集时） |
| 驱动报告的CUDA兼容版本 | 13.2 | `nvidia-smi`；不等于已安装CUDA Toolkit |
| CUDA Toolkit / nvcc | CUDA 13.2，nvcc 13.2.78 | `/usr/local/cuda/bin/nvcc`，2026-08-04实测 |
| cuDNN | 9.20.0.46-1（CUDA 13） | runtime、dev、headers和samples均已安装 |
| TensorRT | 10.16.2.10-1+cuda13.2 | runtime、dev、工具及Python绑定均已安装 |
| 功耗模式 | MAXN | `sudo nvpmodel -q` |

## 采集时运行状态

| 指标 | 结果 | 判断 |
|---|---:|---|
| 内存使用 | 约3.8～4.5GiB / 125809MiB | 空闲充足 |
| Swap | 0 / 2GiB | 正常 |
| CPU负载 | 基本0% | 空闲状态 |
| GPU利用率 | 0% | 空闲状态 |
| CPU/GPU/SoC温度 | 约35～36℃ | 正常空闲温度 |
| 整机输入功耗VIN | 约18.8～19.0W瞬时值 | 空闲样本，不代表满载功耗 |
| GPU功耗 | 约2.0W | 空闲样本 |

采样仅持续约两秒，只能说明当时没有明显过热或异常负载，不能替代长时间压力测试。

## 组件关系：用自己的语言解释

### JetPack

JetPack是Jetson的软件发行套装和SDK集合。它把适配Jetson硬件的Linux、驱动、CUDA、cuDNN、TensorRT、多媒体组件和开发工具组合到一起。安装JetPack不是安装“一个AI框架”，而是建立Jetson端开发与部署的基础环境。

### CUDA

CUDA是NVIDIA GPU通用计算平台。上层框架通过CUDA runtime、驱动和计算库把张量或并行任务交给GPU执行。`nvidia-smi`显示的CUDA版本主要代表驱动兼容能力，不足以证明开发工具已安装。

### nvcc

`nvcc`是CUDA C/C++编译器驱动，用来编译 `.cu` 源码和CUDA扩展。运行PyTorch预编译包不一定直接调用它，但编译自定义CUDA算子、CUDA样例或部分第三方项目时需要。判断CUDA Toolkit是否可开发，应检查 `nvcc --version`，不能只看 `nvidia-smi`。

### cuDNN

cuDNN是在CUDA之上针对深度神经网络算子优化的库。PyTorch等框架通常自动调用它完成卷积、归一化、注意力相关计算等操作。开发者多数时候不直接写cuDNN代码，但其版本会影响框架兼容性和性能。

### TensorRT

TensorRT是训练后推理优化器和运行时。它读取ONNX等模型表示，执行层融合、精度选择和内核优化，并生成面向当前GPU与软件环境的Engine。它的主要目标是降低延迟、提高吞吐，而不是训练模型。

### 整体关系

```text
JetPack（整套Jetson软件环境）
├── NVIDIA驱动与Jetson Linux
├── CUDA（GPU通用计算基础）
│   └── nvcc（CUDA C/C++编译工具）
├── cuDNN（神经网络基础算子加速）
└── TensorRT（训练后模型优化与推理）
```

## 安装JetPack后的实时复核

复核结果：**PASS**。

- `nvidia-jetpack`：7.2-b187
- `nvcc`：13.2.78
- NVIDIA驱动：595.78
- cuDNN：9.20.0.46-1
- TensorRT：10.16.2.10
- TensorRT Python绑定：导入成功，版本10.16.2.10
- GPU：NVIDIA Thor，复核时38℃、0%利用率

原始实测摘要保存在：`diagnostics/day01-live-verification.txt`。

以下命令用于未来升级后的再次复核：

在Jetson终端执行以下整段命令，把输出保存为 `day01-live-verification.txt`：

```bash
{
  echo "===== TIME ====="
  date

  echo "===== MODEL ====="
  tr -d '\0' </proc/device-tree/model

  echo "===== OS / L4T / KERNEL ====="
  cat /etc/os-release
  cat /etc/nv_tegra_release
  uname -a

  echo "===== JETPACK ====="
  dpkg-query -W nvidia-jetpack 2>&1

  echo "===== CUDA / NVCC ====="
  command -v nvcc
  nvcc --version
  nvidia-smi

  echo "===== CUDNN ====="
  dpkg-query -W 'libcudnn*' 2>&1

  echo "===== TENSORRT ====="
  dpkg-query -W 'libnvinfer*' 'tensorrt*' 2>&1
  python3 -c "import tensorrt as trt; print('TensorRT Python:', trt.__version__)"

  echo "===== STORAGE / MEMORY / POWER ====="
  free -h
  lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL
  df -hT /
  nvpmodel -q
} 2>&1 | tee "$HOME/day01-live-verification.txt"
```

把生成的文件复制到：

```text
diagnostics/day01-live-verification.txt
```

升级JetPack或CUDA组件后，应重新运行并更新版本基线。

## 复现原则

1. 所有性能实验必须注明JetPack/L4T、模型、输入尺寸、精度和功耗模式。
2. 记录测试前是否执行过 `jetson_clocks`，MAXN本身不代表频率始终锁定最高值。
3. TensorRT Engine原则上在目标Jetson和目标软件版本上重新构建。
4. 不安装Ubuntu仓库的 `nvidia-cuda-toolkit` 替代Jetson适配包。
5. 不把账号、IP、MAC、序列号、SSH密钥写入公开报告。

## 官方参考

- JetPack 7.2：https://developer.nvidia.com/embedded/jetpack/downloads
- Jetson AGX Thor User Guide：https://docs.nvidia.com/jetson/agx-thor-devkit/user-guide/latest/
- CUDA Setup：https://docs.nvidia.com/jetson/agx-thor-devkit/user-guide/latest/setup_cuda.html
