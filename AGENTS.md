# jetson-stu Codex Handoff

This file is the entry point for any Codex instance working in this repository. Read it before making changes.

## What we are doing

The user is transitioning from LLM application engineering into Jetson and embodied-intelligence engineering. This repository tracks a Day 0 environment setup plus 30 practice-day learning program and contains the exercises, diagnostics, benchmarks, ROS 2 packages, robot descriptions, task-planning code, and final portfolio project.

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

Treat this file and the checked-in diagnostics as the current environment record. Do not treat the CUDA version shown by `nvidia-smi` as proof that nvcc or the CUDA development toolkit is installed; validate them separately.

## Current progress

- [x] Day 0 completed: system baseline, SSH, CUDA real computation, and Docker GPU container validation.
- [ ] Day 1 is next: build the first reproducible image-processing program.

Last updated: 2026-08-05.

## Authoritative documents

Read these in order:

1. `AGENTS.md` — current handoff and operating rules.
2. `README.md` — repository overview and visible progress.
3. `docs/README.md` — course entry point.
4. `docs/course-plan.md` — authoritative Day 0 + 30-day practice plan.
5. `docs/course/README.md` — daily lesson index.
6. The current day's `docs/course/day-NN-*.md` courseware.

If these files disagree, pause and reconcile them rather than silently choosing one.

## How to continue a study session

1. Read the current day's courseware and its acceptance criteria.
2. Review it critically for compatibility with the current JetPack and ARM64 environment.
3. Tell the user what will be done and what requires interaction on the Jetson.
4. Limit environment checks to those needed to unblock the current implementation; do not repeat already verified checks.
5. Let the user execute experiments by default. Use remote execution only when explicitly asked.
6. Execute the session in small batches with explicit verification.
7. Do not mark a day complete until its acceptance condition has evidence.
8. Save commands, logs, versions, measurements, and conclusions in this repository.
9. At the end of a day, update all three:
   - the course plan's progress;
   - progress in `README.md`;
   - `Current progress`, the next milestone, and `Last updated` in this file.

## Immediate next task: Day 1 — First reproducible processed image

The lesson requires:

1. Create `perception/image_pipeline.py` to read an image, resize it, annotate it, and save an output image.
2. Run it against two input images and inspect the saved results.
3. Implement a clear error path for an invalid input file.
4. Do not install PyTorch or collect GPU metrics today; those belong to the later lessons that need them.

Do not spend a separate session on generic monitoring checks; instrument the next real compute workload instead.

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
