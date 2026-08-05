import { useEffect, useMemo, useState } from 'react';
import {
  BookOpen, CaretDown, CaretRight, CheckCircle, Circle, Clock,
  Code, Cube, ListChecks, PlayCircle, RocketLaunch, Target,
} from '@phosphor-icons/react';

const weeks = [
  {
    name: 'Week 01', subtitle: '视觉与 GPU 基础', color: 'lime',
    days: [
      ['Day 01', '图像进入 Jetson', '建立可复现的图像输入与输出'],
      ['Day 02', '图像操作实验室', '用 NumPy / OpenCV 看懂图像数据'],
      ['Day 03', 'GPU 张量与统一内存', '把同一任务放到 CPU 与 GPU 对比'],
      ['Day 04', '第一个视觉模型', '完成一次可解释的推理'],
      ['Day 05', '视频流推理', '让推理进入连续帧循环'],
    ],
  },
  {
    name: 'Week 02', subtitle: 'ROS 2 尽早上手', color: 'cyan',
    days: [
      ['Day 06', 'ROS 2 工作空间', '创建、构建并运行第一个包'],
      ['Day 07', 'Topic 通信', '让节点稳定发布与订阅消息'],
      ['Day 08', '感知节点骨架', '把图像处理封装成 ROS 节点'],
      ['Day 09', '参数、Launch 与日志', '让节点可配置、可启动、可排查'],
      ['Day 10', 'Rosbag 回放', '录制、回放与复现实验输入'],
    ],
  },
  {
    name: 'Week 03', subtitle: '模型部署与感知接口', color: 'purple',
    days: [
      ['Day 11', 'ONNX 导出', '固定模型输入输出契约'],
      ['Day 12', 'ONNX Runtime 基线', '获得部署前的正确性与性能基线'],
      ['Day 13', 'TensorRT 构建', '在目标 Jetson 上生成并验证引擎'],
      ['Day 14', '推理基准', '用延迟、吞吐与稳定性做选择'],
      ['Day 15', '部署契约与接口冻结', '让 ROS 可调用稳定、可替换的推理接口'],
    ],
  },
  {
    name: 'Week 04', subtitle: '坐标、TF 与机器人描述', color: 'orange',
    days: [
      ['Day 16', '坐标变换直觉', '掌握位置、朝向与参考系'],
      ['Day 17', 'TF2 树', '查询和发布正确的坐标变换'],
      ['Day 18', 'URDF 机器人模型', '描述连杆、关节与坐标系'],
      ['Day 19', 'MoveIt 配置', '在仿真中加载机械臂'],
      ['Day 20', '合法运动规划', '生成并解释可行轨迹'],
    ],
  },
  {
    name: 'Week 05', subtitle: '安全约束与任务结构', color: 'pink',
    days: [
      ['Day 21', '确定性安全拒绝', '先验证，再规划，再执行'],
      ['Day 22', '受限任务 Schema', '把自然语言限制成可检查的目标'],
      ['Day 23', '状态机与恢复', '定义任务状态、超时和失败路径'],
      ['Day 24', '感知到任务', '把视觉结果接入任务输入'],
      ['Day 25', '端到端骨架', '连通解释、检查、规划与反馈'],
    ],
  },
  {
    name: 'Week 06', subtitle: '集成、评估与作品集', color: 'blue',
    days: [
      ['Day 26', 'MoveIt 任务接入', '把安全目标送进模拟规划器'],
      ['Day 27', '失败案例', '为异常输入建立可复现测试'],
      ['Day 28', '可观测性与基准', '记录延迟、结果与资源使用'],
      ['Day 29', '项目复现与作品集', '让仓库可以被别人复现和阅读'],
      ['Day 30', '最终演示', '完成端到端演示与复盘'],
    ],
  },
];

const tabs = [
  { id: 'lesson', label: '课件', icon: BookOpen },
  { id: 'tutorial', label: '教程', icon: PlayCircle },
  { id: 'practice', label: '实践', icon: Code },
  { id: 'check', label: '验收', icon: ListChecks },
];

function buildLesson([day, title, goal], week) {
  const n = Number(day.slice(-2));
  return {
    day, title, goal, week,
    time: '3–4 小时',
    concepts: ['先构建最小可运行闭环', '每一步留下可复现证据', '把安全边界写成代码'],
    tutorial: [
      `先阅读本节的目标，写下你认为「${title}」的输入与输出。`,
      '按课件拆成最小步骤；每执行一条命令，观察并解释输出。',
      '遇到错误先保存完整报错，再用假设—验证的方式定位。',
      '将命令、结果与结论写进当天笔记，形成自己的排障资料库。',
    ],
    practice: [
      `完成一个围绕「${title}」的最小实验，不追求功能堆叠。`,
      '为实验设置一个能被验证的输入，并保留原始输出。',
      '故意修改一个条件，比较预期与实际结果。',
      '提交或保存当天的源代码、命令记录和 3 句话结论。',
    ],
    checks: [
      '命令或程序能在 Jetson 上从头复现。',
      '能用自己的话解释输入、处理和输出。',
      '关键结果已记录，没有只靠“看起来能跑”。',
    ],
    artifact: `day-${String(n).padStart(2, '0')} 的实验记录`,
  };
}

const lessons = weeks.flatMap((week) => week.days.map((d) => buildLesson(d, week)));

export function App() {
  const [activeDay, setActiveDay] = useState('Day 01');
  const [activeTab, setActiveTab] = useState('lesson');
  const [openWeek, setOpenWeek] = useState(0);
  const [done, setDone] = useState(() => JSON.parse(localStorage.getItem('jetson-course-done') || '[]'));
  const lesson = lessons.find((item) => item.day === activeDay) || lessons[0];
  const lessonIndex = lessons.findIndex((item) => item.day === activeDay);
  const completed = useMemo(() => new Set(done), [done]);

  useEffect(() => localStorage.setItem('jetson-course-done', JSON.stringify(done)), [done]);

  const chooseDay = (day, index) => {
    setActiveDay(day);
    setOpenWeek(index);
    setActiveTab('lesson');
  };
  const toggleDone = (key) => setDone((current) => current.includes(key)
    ? current.filter((item) => item !== key) : [...current, key]);
  const go = (offset) => {
    const target = lessons[lessonIndex + offset];
    if (!target) return;
    setActiveDay(target.day);
    setOpenWeek(weeks.indexOf(target.week));
    setActiveTab('lesson');
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Jetson Studio 首页"><Cube size={22} weight="fill" /> JETSON STUDIO</a>
        <div className="topbar-meta"><span className="online-dot" />学习路线已就绪 <span className="divider" /> Day 0 完成</div>
        <button className="outline-button" onClick={() => setActiveTab('check')}><ListChecks size={18} /> 学习进度 {done.length}/30</button>
      </header>

      <div className="workspace" id="top">
        <aside className="roadmap">
          <div className="roadmap-head"><p className="eyebrow">30 DAYS / 6 WEEKS</p><h2>学习路线</h2><p>每周 5 天主课，第 6 天用于复盘、补实验或休息。</p></div>
          <nav aria-label="课程周次">
            {weeks.map((week, wi) => (
              <section className={`week-block ${openWeek === wi ? 'is-open' : ''}`} key={week.name}>
                <button className="week-button" onClick={() => setOpenWeek(openWeek === wi ? -1 : wi)}>
                  <span className={`week-swatch ${week.color}`} /><span><b>{week.name}</b><small>{week.subtitle}</small></span>
                  {openWeek === wi ? <CaretDown size={16} /> : <CaretRight size={16} />}
                </button>
                {openWeek === wi && <div className="day-list">
                  {week.days.map(([day, title]) => <button key={day} className={`day-button ${activeDay === day ? 'active' : ''}`} onClick={() => chooseDay(day, wi)}>
                    {completed.has(day) ? <CheckCircle size={16} weight="fill" /> : <Circle size={16} />}<span><b>{day}</b>{title}</span>
                  </button>)}
                </div>}
              </section>
            ))}
          </nav>
        </aside>

        <section className="lesson-panel">
          <div className="lesson-topline"><span className={`status-pill ${lesson.week.color}`}>{lesson.week.name} · {lesson.day}</span><span><Clock size={16} /> {lesson.time}</span></div>
          <h1>{lesson.title}</h1>
          <p className="lesson-goal"><Target size={20} weight="fill" /> {lesson.goal}</p>

          <div className="tab-row" role="tablist" aria-label="当天内容">
            {tabs.map(({ id, label, icon: Icon }) => <button role="tab" aria-selected={activeTab === id} className={activeTab === id ? 'selected' : ''} key={id} onClick={() => setActiveTab(id)}><Icon size={18} />{label}</button>)}
          </div>

          {activeTab === 'lesson' && <div className="content-grid">
            <article className="content-card overview-card"><p className="eyebrow">TODAY'S MISSION</p><h2>先理解闭环，再写代码。</h2><p>今天不做无目的的命令巡检。我们只为一个明确问题搭建最小实验：{lesson.goal}</p><div className="concept-list">{lesson.concepts.map((item) => <span key={item}>{item}</span>)}</div></article>
            <article className="hero-card"><img src="/assets/vision-pipeline-hero.png" alt="Jetson 上的视觉计算流程" /><div><p>FROM INPUT TO EVIDENCE</p><b>输入 → 处理 → 证据</b></div></article>
          </div>}

          {activeTab === 'tutorial' && <article className="content-card instruction-card"><p className="eyebrow">GUIDED TUTORIAL</p><h2>执行节奏</h2><ol>{lesson.tutorial.map((step) => <li key={step}>{step}</li>)}</ol></article>}
          {activeTab === 'practice' && <article className="content-card instruction-card"><p className="eyebrow">HANDS-ON LAB</p><h2>今天由你操作</h2><ol>{lesson.practice.map((step) => <li key={step}>{step}</li>)}</ol><div className="command-note"><Code size={20} /><span>需要命令时，课件会给出“复制 → 执行 → 观察 → 解释”的小批次，而不是一次性的大段检查。</span></div></article>}
          {activeTab === 'check' && <article className="content-card instruction-card"><p className="eyebrow">ACCEPTANCE</p><h2>完成标准</h2><ul className="check-list">{lesson.checks.map((item) => <li key={item}><CheckCircle size={19} weight="fill" />{item}</li>)}</ul><p className="artifact"><RocketLaunch size={19} /> 当日产物：<b>{lesson.artifact}</b></p><button className={`complete-button ${completed.has(lesson.day) ? 'done' : ''}`} onClick={() => toggleDone(lesson.day)}>{completed.has(lesson.day) ? <CheckCircle size={19} weight="fill" /> : <Circle size={19} />}{completed.has(lesson.day) ? '已标记完成' : '完成本课后标记'}</button></article>}

          <footer className="lesson-footer"><button onClick={() => go(-1)} disabled={lessonIndex === 0}>← 上一课</button><span>你的节奏优先：第 6 天留作机动，不强行赶进度。</span><button onClick={() => go(1)} disabled={lessonIndex === lessons.length - 1}>下一课 →</button></footer>
        </section>

        <aside className="focus-panel"><p className="eyebrow">TODAY / FOCUS</p><h2>学习不是“跑过命令”，而是留下证据。</h2><div className="focus-rule"><span>01</span><p>你执行<br /><b>我解释与导航</b></p></div><div className="focus-rule"><span>02</span><p>小批次操作<br /><b>每次都验证结果</b></p></div><div className="focus-rule"><span>03</span><p>记录失败<br /><b>把它变成能力</b></p></div><div className="progress-box"><div><span>总进度</span><b>{Math.round(done.length / 30 * 100)}%</b></div><div className="progress-track"><i style={{ width: `${done.length / 30 * 100}%` }} /></div><small>{done.length} / 30 个课程日已完成</small></div></aside>
      </div>
    </main>
  );
}
