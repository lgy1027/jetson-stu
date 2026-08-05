# Day 3：让 PyTorch 真正使用 Thor GPU

> 今天第一次在真实工作负载中使用 PyTorch GPU。监控只在计算发生时采一次；不要把它变成独立的“看数字练习”。

## 今天的问题

如何证明 PyTorch 在 GPU 上计算，而不是程序启动了却悄悄回退到 CPU？

## 你要掌握

- `torch.cuda.is_available()` 是前置条件，不是完整证据；设备名、张量设备、同步计时和数值比较要一起看。
- CUDA 计算通常异步排队；没有 `torch.cuda.synchronize()` 的 wall-clock 时间常常低估 GPU 真实耗时。
- CPU/GPU 的绝对耗时会受矩阵尺寸、启动开销、功耗模式和内存传输影响；今天先保证测量正确。

## 今天完成后你能做到什么

1. 在当前 JetPack/Ubuntu/ARM64 组合上确认一个兼容的 PyTorch 安装路径。
2. 用同一矩阵工作负载得到 CPU 与 GPU 结果，比较最大绝对误差。
3. 输出 GPU 名称、CUDA runtime、同步后的耗时和加速比。

## 时间和产物

- 预计：3–4 小时；首次安装 PyTorch 时可能更久。
- 产物：`perception/day03_torch_gpu.py`、一次完整原始输出、计算期间的一小段 `tegrastats` 记录。

## 操作教程

### 1. 只为今天确认 PyTorch 路径（30–60 分钟）

先检查有没有可用 PyTorch：

```bash
python3 -c 'import torch; print(torch.__version__, torch.cuda.is_available(), torch.version.cuda)'
```

如果导入失败或 CUDA 为 `False`，不要安装 x86/PC 教程里的随机 wheel。记录 JetPack、Ubuntu 24.04、ARM64 和 Python 版本，查 NVIDIA 针对当前 JetPack 的官方兼容安装说明后再安装。把实际使用的安装命令和版本写入当天记录；这一步的目标是兼容性，不是“装最新版”。

### 2. 阅读并运行矩阵工作负载（45 分钟）

完整文件：[展开 `day03_torch_gpu.py`](#course-file:perception/day03_torch_gpu.py)。先找出四处关键证据：同一对 CPU 随机输入被复制到两种设备、`cuda:0`、两次同步、`max_abs_error`。

```bash
cd ~/jetson-stu
python3 perception/day03_torch_gpu.py | tee diagnostics/day03-torch-gpu-output.txt
```

预期：输出 `cuda available: True`、GPU 名称、CPU/GPU 耗时与很小的误差。浮点误差不一定为零；如果误差异常大，先停止并检查随机数、dtype 和累加顺序。

### 3. 在真实计算期间取一小段资源证据（15 分钟）

打开第二个 tmux pane，在第一次命令运行的同时执行：

```bash
tegrastats --interval 1000 | tee diagnostics/day03-tegrastats.log
```

采 10 秒后 `Ctrl-c` 停止。你只需确认 GPU/内存活动和负载在计算期有变化；不要将空闲状态的读数当作结论。

### 4. 改一个工作负载变量（30 分钟）

把 `size` 从 `2048` 改为 `1024` 或 `3072`（内存允许时），再次运行。记录：矩阵尺寸、CPU ms、GPU ms、加速比。不要跨两次不同设置直接比较“谁更快”。

## 实践

1. 留下兼容 PyTorch 版本和 CUDA 可用性证据。
2. 运行 CPU/GPU 同一矩阵工作负载。
3. 保存同步后的耗时、最大误差与 10 秒计算期监控片段。
4. 只改变一个矩阵尺寸后重跑一次。

## 产物与验收

- [ ] 脚本打印出 CUDA runtime、设备名与 `cuda available: True`。
- [ ] CPU/GPU 都完成相同工作，`max_abs_error` 合理且可解释。
- [ ] 两次测试各自有尺寸和耗时记录。
- [ ] 监控证据来自真实计算期间。

## 复盘

为什么只在 GPU 上创建一个张量，不能证明实际计算发生在 GPU？
