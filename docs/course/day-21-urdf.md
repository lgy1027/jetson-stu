# Day 18：用 URDF 描述机械臂

## 今天的问题

怎样让软件知道机械臂有哪些连杆、关节、限制和坐标系？

## 你要掌握

- URDF 描述 link、joint、惯性、视觉和碰撞几何。
- joint limit 是安全约束的一部分，而不是 UI 提示。

## 实践

1. 选择教学用机械臂模型或创建最小两/六关节 URDF。
2. 用 Xacro 参数化长度、关节名称和限制。
3. 在 RViz 显示 `robot_state_publisher` 的模型。
4. 改变关节状态，观察 TF 与模型姿态。

## 产物与验收

- `robot_description/` 中的 URDF/Xacro。
- RViz 截图或录屏，展示关节变化与坐标系。

## 复盘

视觉几何和碰撞几何为什么可能不一样？
