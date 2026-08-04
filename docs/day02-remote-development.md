# Day 2：SSH、文件传输与终端效率

## 当前连接信息

- Windows客户端：OpenSSH for Windows 9.5p2
- Jetson普通用户：`lcfc`
- Jetson局域网地址：`10.159.134.94`
- SSH服务：enabled / active，监听TCP 22端口
- 认证方式：Windows现有RSA密钥
- root SSH：不启用；需要系统权限时使用 `sudo`

局域网IP可能在重新联网后变化。如果连接失败，先在Jetson执行 `hostname -I`，不要直接删除 `known_hosts` 或重新生成密钥。

## SSH

登录：

```powershell
ssh lcfc@10.159.134.94
```

强制使用当前学习环境的密钥进行诊断：

```powershell
ssh -o IdentitiesOnly=yes `
  -i "$env:USERPROFILE\.ssh\id_rsa" `
  lcfc@10.159.134.94
```

密钥认证的意义是客户端用私钥签名，服务端用 `authorized_keys` 中的公钥验证。私钥始终保留在Windows，不能上传、提交Git或发到聊天中。

## scp

Windows发送文件到Jetson：

```powershell
scp .\README.md lcfc@10.159.134.94:~/jetson-stu/
```

从Jetson取回文件：

```powershell
scp lcfc@10.159.134.94:~/jetson-stu/README.md .\README.from-jetson.md
```

目录传输可使用 `scp -r`，但项目日常同步更适合Git；大模型、数据集和生成视频不应直接提交仓库。

## tmux

`tmux`在Jetson上创建独立于SSH连接的终端会话。SSH断开时，tmux里的进程继续运行。

```bash
# 新建会话
tmux new -s jetson-day02

# 临时离开会话：先按Ctrl+b，松开，再按d

# 查看会话
tmux ls

# 恢复会话
tmux attach -t jetson-day02

# 确认不再需要后结束会话
tmux kill-session -t jetson-day02
```

不要在任务仍需要运行时用 `tmux kill-server`，它会结束当前用户的全部tmux会话。

## htop

`htop`用于交互查看CPU、内存、负载和进程：

```bash
htop
```

- `F3`：搜索进程
- `F4`：过滤进程
- `F6`：选择排序字段
- `F9`：发送信号，使用前确认进程
- `q`：退出

Jetson GPU、温度和功耗仍应结合 `tegrastats` 或 `jtop` 查看。

## systemctl

`systemctl`管理systemd服务。Day 2只进行只读查看：

```bash
systemctl is-active ssh
systemctl status ssh --no-pager
systemctl list-units --type=service --state=running --no-pager
```

在不理解服务用途前，不执行 `disable`、`mask` 或随意停止服务。

## journalctl

`journalctl`查看systemd日志：

```bash
journalctl -u ssh -n 20 --no-pager
journalctl -u ssh --since "10 minutes ago" --no-pager
journalctl -p warning -b --no-pager
```

- `-u ssh`：只看SSH服务
- `-n 20`：最后20行
- `--since`：指定时间范围
- `-b`：当前启动周期
- `-p warning`：warning及更高优先级

## Day 2验收

1. Windows无需密码登录普通用户 `lcfc`。
2. 使用scp传输测试脚本，本地与远端SHA-256一致。
3. 在tmux中启动持续任务。
4. 关闭原SSH连接后，新建SSH连接仍能看到同一任务继续输出。
5. 能解释 `htop`、`systemctl` 与 `journalctl` 分别解决什么问题。

## 2026-08-04实测记录

- 免密登录：PASS，服务端接受用户 `lcfc` 的RSA公钥。
- tmux版本：3.4。
- htop版本：3.3.0。
- SSH服务：active。
- scp测试文件：`diagnostics/day02_tmux_test.sh`。
- 本地SHA-256：`48ec41e5a5a00a4d72f706bb16b321e1386bf23f7dcb6ffe6f330f0e10e09b57`。
- 远端SHA-256：`48ec41e5a5a00a4d72f706bb16b321e1386bf23f7dcb6ffe6f330f0e10e09b57`。
- 断线恢复：PASS。首次连接启动会话后结束；第二个独立SSH连接捕获到tick持续从001增长到013，会话状态为running。
- 本人交互练习：PASS。已完成attach、detach、reattach、查看工具及kill session。
- 最终远程复核：`jetson-day02`会话已关闭；日志保留128条持续输出记录。
- 本地验收日志：`diagnostics/day02-tmux-output.log`。

### 本次排障记录

最初使用Windows PowerShell管道把公钥直接传给SSH。Windows PowerShell的原生程序管道编码导致远端 `authorized_keys` 不是有效公钥文件。通过scp按原文件传输、移除CRLF并重新安装公钥后解决。

经验：跨Windows/Linux传输密钥、模型和二进制文件时优先使用scp、Git或明确的字节传输方式，不假设Shell文本管道会保持编码和换行不变。
