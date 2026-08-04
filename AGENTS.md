# jetson-stu Codex Handoff

This file is the entry point for any Codex instance working in this repository. Read it before making changes.

## What we are doing

The user is transitioning from LLM application engineering into Jetson and embodied-intelligence engineering. This repository tracks a structured 12-week, 84-day learning program and contains the exercises, diagnostics, benchmarks, ROS 2 packages, robot descriptions, task-planning code, and final portfolio project.

The first-stage capstone is:

```text
natural-language goal
    -> constrained task schema and safety checks
    -> image/video perception on Jetson
    -> ROS 2 messages and TF transforms
    -> simulated robot-arm motion planning
    -> execution result and performance evaluation
```

LLMs/VLMs may perform semantic interpretation, task decomposition, and skill selection. They must not directly generate motor current, PWM, or unchecked joint commands. Motion, workspace limits, collision checks, and execution safety remain deterministic.

## User and available hardware

- User background: professional LLM application developer; already comfortable with Python, deep learning, and model applications.
- Study time: about 3-4 hours per day.
- Current hardware: NVIDIA Jetson AGX Thor Developer Kit 128GB (T5000), with no camera, robot arm, mobile base, or other robot hardware yet.
- Initial direction: use files and simulation first; eventually build toward vision-guided robot-arm manipulation.

## Confirmed Jetson environment

- JetPack 7.2-b187
- Jetson Linux / L4T R39.2
- Ubuntu 24.04 ARM64
- CUDA Toolkit 13.2; nvcc 13.2.78
- NVIDIA driver 595.78
- cuDNN 9.20.0.46
- TensorRT 10.16.2.10, including working Python bindings
- 14-core ARM CPU, 128GB unified memory, 1TB NVMe
- Power mode observed as MAXN

Use `docs/system-baseline.md` as the authoritative environment record. Do not treat the CUDA version shown by `nvidia-smi` as proof that nvcc or the CUDA development toolkit is installed; validate them separately.

## Current progress

- [x] Learning direction and 12-week design completed.
- [x] Day 1 completed: repository structure, system baseline, and NVIDIA stack concepts.
- [x] Day 2 completed: ordinary-user SSH key authentication, scp, tmux persistence, htop, systemctl, and journalctl.
- [ ] Day 3 is next: validate CUDA and AI components with an actual GPU computation/deviceQuery-style test, then document GPU architecture and unified memory behavior.

Last updated: 2026-08-04.

## Authoritative documents

Read these in order:

1. `AGENTS.md` — current handoff and operating rules.
2. `README.md` — repository overview and visible progress.
3. `docs/2026-08-03-jetson-embodied-ai-learning-design.md` — goals and architecture of the learning path.
4. `docs/2026-08-03-jetson-embodied-ai-learning-plan.md` — authoritative daily checklist.
5. `docs/system-baseline.md` — hardware and software baseline.
6. The latest `docs/dayNN-*.md` file — detailed notes from the most recently completed day.

If these files disagree, pause and reconcile them rather than silently choosing one.

## How to continue a study day

1. Read the relevant Day section from the 12-week plan.
2. Review it critically for compatibility with the current JetPack and ARM64 environment.
3. Tell the user what will be done and what requires interaction on the Jetson.
4. Prefer read-only checks before installing or changing system configuration.
5. Execute the day in small batches with explicit verification.
6. Do not mark a checkbox complete until its acceptance condition has evidence.
7. Save commands, logs, versions, measurements, and conclusions in this repository.
8. At the end of the day, update all three:
   - the Day checklist in the 12-week plan;
   - progress in `README.md`;
   - `Current progress`, `Day N is next`, and `Last updated` in this file.

## Immediate next task: Day 3

The Day 3 plan requires:

1. Verify `nvcc --version`, `nvidia-smi`, cuDNN packages, and TensorRT packages. The package-level checks already passed on Day 1; reuse that evidence instead of repeating unnecessary installation.
2. Compile and run a minimal CUDA program or an official `deviceQuery` equivalent that performs real GPU work.
3. Record GPU name, Compute Capability, unified-memory capacity/behavior, compiler/runtime versions, and PASS/FAIL output.
4. Save the source and reproducible command under `diagnostics/` or an appropriate CUDA learning directory.
5. Create a Day 3 note and update the learning checklist only after the test passes or a reproducible failure is documented.

Do not begin Day 4 until Day 3 evidence is saved.

## Repository and security rules

- Use the ordinary Jetson user for SSH and development; elevate individual commands with `sudo` when needed.
- Do not enable remote root login.
- Never commit private keys, passwords, API keys, tokens, `.env` files, Wi-Fi credentials, serial numbers, or public WAN addresses.
- Private SSH public keys and fingerprints are not secret, but avoid storing them unless needed for a diagnostic record.
- Local/LAN addresses may change. Diagnose with `hostname -I`; do not assume an old address is permanent.
- Do not commit model weights, datasets, large videos, TensorRT engines, ROS build outputs, or generated caches. The root `.gitignore` covers common cases.
- TensorRT engines should normally be rebuilt on the target Jetson and matching software stack.
- Preserve user changes. Never use destructive Git commands such as `git reset --hard` without explicit authorization.
- Before installing robotics packages, verify JetPack, Ubuntu ARM64, and ROS distribution compatibility from current official documentation.
- JetPack 7.2 support must be checked before installing Isaac ROS packages; do not mix packages intended for another JetPack release.

## Expected repository structure

```text
jetson-stu/
├── AGENTS.md
├── README.md
├── docs/
├── diagnostics/
├── benchmarks/
├── perception/
├── ros2_ws/src/
├── robot_description/
├── task_planner/
└── demo/
```

The repository may be checked out at a different filesystem path on another device. Never rely on the original Windows absolute path; resolve files from the repository root.
