# Day 3：让 PyTorch 真正使用 GPU

> 今天第一次在真实工作负载中使用 PyTorch GPU。监控只在计算发生时采一次；不要把它变成独立的“看数字练习”。

## 今天的问题

如何证明 PyTorch 在 GPU 上计算，而不是程序启动了却悄悄回退到 CPU？

## 前置条件与兼容性边界

- Day 0 已证明 CUDA Toolkit 可以编译并执行真实 kernel；今天验证的是 PyTorch 自己是否与当前 CUDA/JetPack 组合兼容。
- PyTorch 必须同时匹配 JetPack、CUDA、ARM64 架构和 Python ABI。不要使用为其他 JetPack、x86_64 或其他 Python 版本构建的 wheel。
- 安装前先查阅 [NVIDIA PyTorch for Jetson 兼容矩阵](https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform-release-notes/pytorch-jetson-rel.html) 和 [Jetson PyTorch 安装说明](https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform/index.html)，确认当前设备有明确支持的安装路径。
- 如果设备已有 CUDA 可用的 PyTorch，先记录来源并验证；如果没有明确兼容路径，暂停安装并记录原因，不要用未经验证的旧版本反复尝试。

## 你要掌握

- `torch.cuda.is_available()` 是前置条件，不是完整证据；设备名、张量设备、同步计时和数值比较要一起看。
- CUDA 计算通常异步排队；没有 `torch.cuda.synchronize()` 的 wall-clock 时间常常低估 GPU 真实耗时。
- CPU/GPU 的绝对耗时会受矩阵尺寸、启动开销、功耗模式和内存传输影响；今天先保证测量正确。

## 今天完成后你能做到什么

1. 在当前 JetPack/Ubuntu/ARM64 组合上确认一个兼容的 PyTorch 安装路径。
2. 用同一矩阵工作负载得到 CPU 与 GPU 结果，比较最大绝对误差。
3. 输出 GPU 名称、CUDA runtime、同步后的耗时和加速比。

## 本单元产物

- 产物：`perception/day03_gpu_tensors.py`、一次完整原始输出、计算期间的一小段 `tegrastats` 记录。

## 操作教程

### 1. 只为今天确认 PyTorch 路径

先检查有没有可用 PyTorch：

```bash
# 检查 PyTorch 版本、CUDA 是否可用，以及它使用的 CUDA 版本。
python3 -c 'import torch; print(torch.__version__, torch.cuda.is_available(), torch.version.cuda)'
```

同时记录解释器与平台，防止 wheel 的架构和 Python ABI 对不上：

```bash
# 记录 Python、系统和 CPU 架构，排查 ARM64 与 Python ABI 不匹配。
python3 - <<'PY'
import platform, sys
print("python:", sys.version)
print("executable:", sys.executable)
print("machine:", platform.machine())
PY
```

如果导入失败或 CUDA 为 `False`，按以下顺序决策：

1. 查 [NVIDIA PyTorch for Jetson 兼容矩阵](https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform-release-notes/pytorch-jetson-rel.html)，寻找明确对应当前 JetPack 的版本；
2. 查 [NVIDIA Jetson PyTorch 安装说明](https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform/index.html)，确认采用 wheel、容器还是其他官方路径；
3. 核对 Python ABI、ARM64、CUDA 和 cuDNN 要求；
4. 把候选方案、来源 URL 和选择理由写入 `diagnostics/day03-pytorch-install-decision.md`；
5. 只有兼容关系明确后才安装并继续。

不要使用 `sudo pip`，也不要把 `--break-system-packages` 当作默认解法。若使用虚拟环境或容器，后面的 Day 4/5 必须继续使用同一个运行环境。

### 2. 阅读并运行矩阵工作负载

完整文件：[展开 `day03_gpu_tensors.py`](#course-file:perception/day03_gpu_tensors.py)。先找出四处关键证据：同一对 CPU 随机输入被复制到两种设备、`cuda:0`、两次同步、`max_abs_error`。

```bash
# 从仓库根目录运行 CPU/GPU 张量对照实验，并保存输出。
cd ~/jetson-stu
python3 perception/day03_gpu_tensors.py | tee diagnostics/gpu-tensors-output.txt
```

脚本会在计时前执行一次不计时的预热，然后同步 CUDA。预期输出 `cuda available: True`、GPU 名称、CPU/GPU 结果设备、耗时、加速比与很小的误差。浮点误差不一定为零；如果误差异常大，先停止并检查随机数、dtype 和累加顺序。

### 3. 在真实计算期间取一小段资源证据

打开第二个 tmux pane，在第一次命令运行的同时执行：

```bash
# 每秒采样 Jetson 的 GPU、CPU 和内存活动，观察真实计算期间的负载。
tegrastats --interval 1000 | tee diagnostics/gpu-tensors-tegrastats.log
```

矩阵脚本结束后停止 `tegrastats`。你只需确认 GPU/内存活动和负载在计算期有变化；不要将空闲状态的读数当作结论。如果默认负载结束太快，可提高 `--size` 或 `--repeats`，但必须避免让系统进入不可响应状态。

### 4. 改一个工作负载变量

不要修改源码，通过参数只改变矩阵尺寸：

```bash
# 只改变矩阵规模，分别保存两次可比较的性能结果。
python3 perception/day03_gpu_tensors.py --size 1024 --repeats 8 \
  | tee diagnostics/gpu-tensors-1024.txt
python3 perception/day03_gpu_tensors.py --size 2048 --repeats 8 \
  | tee diagnostics/gpu-tensors-2048.txt
```

记录矩阵尺寸、重复次数、CPU ms、GPU ms、加速比和最大误差。规模不同的两次运行用于观察趋势，不用于宣称某个固定加速比。

## 如何解释输出

- `torch.version.cuda` 是该 PyTorch 构建所针对的 CUDA runtime 信息，不等于 `nvcc --version`。
- `gpu result device: cuda:0` 证明结果张量位于 GPU；配合同步计时和 `tegrastats` 才形成完整证据。
- 小矩阵可能因为调度开销而不比 CPU 快，这不是 GPU 未工作。
- 加速比只对当前 dtype、尺寸、重复次数、功耗模式和软件版本成立。
- Jetson 使用统一物理内存并不意味着 CPU/GPU 张量对象完全没有迁移或同步成本。

## 常见失败与处理

| 现象 | 含义与下一步 |
|---|---|
| `import torch` 失败 | 先核对解释器和安装来源，不继续 Day 4 |
| `cuda available: False` | 当前 PyTorch 没有可用 CUDA 后端；不要偷偷改成 CPU 通过验收 |
| `no kernel image` / 动态库错误 | 构建与 GPU/CUDA 栈不匹配，保存完整错误并回到兼容性决策 |
| GPU 时间异常小 | 检查同步是否仍在计时边界两侧 |
| GPU 时间异常大 | 记录首次运行、功耗模式、温度、后台负载和矩阵规模，再复测 |
| 系统内存压力过高 | 降低 `--size`；不要先用 Swap 掩盖不合理工作负载 |

## 实践

1. 留下兼容 PyTorch 版本和 CUDA 可用性证据。
2. 运行 CPU/GPU 同一矩阵工作负载。
3. 保存同步后的耗时、最大误差与计算期监控片段。
4. 通过 `--size` 只改变一个变量后重跑一次。

## 产物与验收

- [ ] 脚本打印出 CUDA runtime、设备名与 `cuda available: True`。
- [ ] CPU/GPU 都完成相同工作，`max_abs_error` 合理且可解释。
- [ ] 两次测试各自有尺寸和耗时记录。
- [ ] 监控证据来自真实计算期间。
- [ ] 安装来源或兼容性决策被记录，且没有混用其他 JetPack 的 wheel。

## 与后续课程的连接

Day 4 会继续使用同一个 PyTorch 环境和 CUDA 计时边界；Day 11 会从同一模型导出 ONNX；Day 14 会把这里的单次矩阵实验升级为统一的推理延迟、吞吐和内存基准。

## 复盘

为什么只在 GPU 上创建一个张量，不能证明实际计算发生在 GPU？
