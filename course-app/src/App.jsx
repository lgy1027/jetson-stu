import { useEffect, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  BookOpen, CaretDown, CaretRight, CheckCircle, Circle, Clock,
  CaretUp, Code, Compass, Cube, FileCode, ListChecks, PlayCircle, RocketLaunch, Target, WechatLogo,
} from '@phosphor-icons/react';
import { courseLessons, courseSourceFiles, foundationsMarkdown } from 'virtual:jetson-courseware';

const contactQrImage = `${import.meta.env.BASE_URL}assets/contact-wechat-qr.jpg`;

const weeks = [
  {
    name: 'Start', subtitle: '环境与工作流', color: 'lime',
    days: [['Day 0', '环境与工作流', '建立可复现的 Jetson 开发方式']],
  },
  {
    name: 'M1', subtitle: '可复现感知程序', color: 'lime',
    days: [
      ['Day 1', '图像进入 Jetson', '建立可复现的图像输入与输出'],
      ['Day 2', '图像操作实验室', '用 NumPy / OpenCV 看懂图像数据'],
      ['Day 3', 'GPU 张量与统一内存', '把同一任务放到 CPU 与 GPU 对比'],
      ['Day 4', '第一个视觉模型', '完成一次可解释的推理'],
      ['Day 5', '视频流推理', '让推理进入连续帧循环'],
    ],
  },
  {
    name: 'M2', subtitle: 'ROS 2 感知系统', color: 'cyan',
    days: [
      ['Day 06', 'ROS 2 工作空间', '创建、构建并运行第一个包'],
      ['Day 07', 'Topic 通信', '让节点稳定发布与订阅消息'],
      ['Day 08', '感知节点骨架', '把图像处理封装成 ROS 节点'],
      ['Day 09', '参数、Launch 与日志', '让节点可配置、可启动、可排查'],
      ['Day 10', 'Rosbag 回放', '录制、回放与复现实验输入'],
    ],
  },
  {
    name: 'M3', subtitle: '可验证部署后端', color: 'purple',
    days: [
      ['Day 11', 'ONNX 导出', '固定模型输入输出契约'],
      ['Day 12', 'ONNX Runtime 基线', '获得部署前的正确性与性能基线'],
      ['Day 13', 'TensorRT 构建', '在目标 Jetson 上生成并验证引擎'],
      ['Day 14', '性能与内存基准', '用延迟、吞吐、内存与稳定性做选择'],
      ['Day 15', '部署契约与接口冻结', '让 ROS 可调用稳定、可替换的推理接口'],
    ],
  },
  {
    name: 'M4', subtitle: '有物理含义的目标', color: 'orange',
    days: [
      ['Day 16', '坐标变换直觉', '掌握位置、朝向与参考系'],
      ['Day 17', '相机模型与三维点', '把像素和模拟深度还原到相机坐标'],
      ['Day 18', 'TF2 树', '查询和发布带时间条件的坐标变换'],
      ['Day 19', 'URDF 机器人模型', '描述连杆、关节与坐标系'],
      ['Day 20', 'MoveIt 配置', '加载规划组、运动学与碰撞模型'],
    ],
  },
  {
    name: 'M5', subtitle: '安全任务规划', color: 'pink',
    days: [
      ['Day 21', '合法运动规划', '生成并解释满足约束的轨迹'],
      ['Day 22', '确定性安全拒绝', '让非法目标在正确层停止'],
      ['Day 23', '受限任务 Schema', '把自然语言限制成可检查的目标'],
      ['Day 24', '状态机与恢复', '定义任务状态、超时和失败路径'],
      ['Day 25', '感知到任务', '保留视觉来源、不确定性和坐标条件'],
    ],
  },
  {
    name: 'M6', subtitle: '端到端作品', color: 'blue',
    days: [
      ['Day 26', 'MoveIt 任务接入', '把安全目标送进模拟规划器'],
      ['Day 27', '端到端闭环', '连通任务、感知、三维目标、TF 与规划'],
      ['Day 28', '失败案例矩阵', '为异常输入建立可复现测试'],
      ['Day 29', '可观测性与复现', '记录指标并从干净终端复现项目'],
      ['Day 30', '最终演示', '完成端到端演示与复盘'],
    ],
  },
];

const tabs = [
  { id: 'lesson', label: '任务卡', icon: BookOpen },
  { id: 'tutorial', label: '操作教程', icon: PlayCircle },
  { id: 'practice', label: '动手实践', icon: Code },
  { id: 'check', label: '验收', icon: ListChecks },
];

function buildLesson([day, title, goal], week) {
  const source = courseLessons.find((item) => item.day === day);
  return {
    day, title, goal, week,
    pace: '弹性实践单元',
    question: source?.question || goal,
    concepts: source?.concepts?.length ? source.concepts : ['先构建最小可运行闭环', '每一步留下可复现证据'],
    practice: source?.practice?.length ? source.practice : ['完成最小实验并记录原始输出。'],
    checks: source?.checks?.length ? source.checks : ['命令或程序能在 Jetson 上从头复现。'],
    reflection: source?.reflection || '用自己的话解释今天的关键决策。',
    outcomes: source?.outcomes?.length ? source.outcomes : source?.checks?.slice(0, 2) || [],
    tutorialMarkdown: source?.tutorialMarkdown || source?.markdown || `## 今天的问题\n\n${goal}`,
  };
}

const lessons = weeks.flatMap((week) => week.days.map((d) => buildLesson(d, week)));

function CourseMarkdown({ children, onOpenCode }) {
  return <ReactMarkdown components={{
    a: ({ href, children: linkChildren }) => href?.startsWith('#course-file:')
      ? <button className="source-link" onClick={() => onOpenCode(href.slice('#course-file:'.length))}><FileCode size={17} />{linkChildren}</button>
      : <a href={href} target="_blank" rel="noreferrer">{linkChildren}</a>,
  }} remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>;
}

function SourceDialog({ path, source, onClose }) {
  if (!path || !source) return null;
  return <div className="source-modal-backdrop" role="presentation" onMouseDown={onClose}>
    <section className="source-modal" role="dialog" aria-modal="true" aria-label={`源码：${path}`} onMouseDown={(event) => event.stopPropagation()}>
      <div className="source-file-head"><div><p className="eyebrow">COURSE SOURCE · LIVE FILE</p><h2><FileCode size={22} /> {path}</h2><p>这里显示课程实际使用的完整 Python 源码，包括中文注释。</p></div><button className="source-close" onClick={onClose}><CaretUp size={17} /> 收起代码</button></div>
      <pre><code>{source}</code></pre>
    </section>
  </div>;
}

export function App() {
  const [activeDay, setActiveDay] = useState('Day 0');
  const [activeTab, setActiveTab] = useState('lesson');
  const [openWeek, setOpenWeek] = useState(-1);
  const [viewingFoundations, setViewingFoundations] = useState(true);
  const [expandedCode, setExpandedCode] = useState(null);
  const [done, setDone] = useState(() => JSON.parse(localStorage.getItem('jetson-course-done') || '[]'));
  const lesson = lessons.find((item) => item.day === activeDay) || lessons[0];
  const lessonIndex = lessons.findIndex((item) => item.day === activeDay);
  const completed = useMemo(() => new Set(done), [done]);
  const completedMainDays = done.filter((day) => day !== 'Day 0').length;

  useEffect(() => localStorage.setItem('jetson-course-done', JSON.stringify(done)), [done]);
  useEffect(() => {
    const closeOnEscape = (event) => { if (event.key === 'Escape') setExpandedCode(null); };
    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, []);

  const chooseDay = (day, index) => {
    setActiveDay(day);
    setOpenWeek(index);
    setActiveTab('lesson');
    setViewingFoundations(false);
    setExpandedCode(null);
  };
  const toggleDone = (key) => setDone((current) => current.includes(key)
    ? current.filter((item) => item !== key) : [...current, key]);
  const go = (offset) => {
    const target = lessons[lessonIndex + offset];
    if (!target) return;
    setActiveDay(target.day);
    setOpenWeek(weeks.indexOf(target.week));
    setActiveTab('lesson');
    setViewingFoundations(false);
    setExpandedCode(null);
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Jetson Studio 首页"><Cube size={22} weight="fill" /> JETSON STUDIO</a>
        <div className="topbar-meta"><span className="online-dot" />学习路线已就绪 <span className="divider" /> Day 0 完成</div>
        <div className="contact-wrap"><button className="contact-button" aria-describedby="wechat-contact-card"><WechatLogo size={18} weight="fill" /> 联系我</button><div className="qr-popover" id="wechat-contact-card" role="tooltip"><img src={contactQrImage} alt="微信联系二维码" /><span>微信扫码联系我</span></div></div>
        <button className="outline-button" onClick={() => { setViewingFoundations(false); setActiveTab('check'); }}><ListChecks size={18} /> 学习进度 {completedMainDays}/30</button>
      </header>

      <div className="workspace" id="top">
        <aside className="roadmap">
          <div className="roadmap-head"><p className="eyebrow">DAY 0 + 30 UNITS / 6 MILESTONES</p><h2>学习路线</h2><p>Day 是稳定编号，不是完成时限；通过当前验收后再进入下一单元。</p></div>
          <button className={`foundations-button ${viewingFoundations ? 'active' : ''}`} onClick={() => { setViewingFoundations(true); setActiveTab('lesson'); }}>
            <Compass size={20} weight="duotone" /><span><b>入门必读</b><small>Jetson 概念地图 · Day 0 前阅读</small></span><CaretRight size={16} />
          </button>
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
          {viewingFoundations ? <>
            <div className="lesson-topline"><span className="status-pill lime">BEFORE DAY 0 · FOUNDATION</span><span><Clock size={16} /> 按需阅读</span></div>
            <h1>Jetson 概念地图</h1>
            <p className="lesson-goal"><Compass size={20} weight="fill" /> 先建立共同语言，再开始环境与实践。</p>
            <article className="content-card markdown-lesson foundations-lesson"><CourseMarkdown onOpenCode={setExpandedCode}>{foundationsMarkdown}</CourseMarkdown></article>
            <footer className="lesson-footer"><button onClick={() => chooseDay('Day 0', 0)}>进入 Day 0 →</button><span>这页不计入 30 个单元进度，但建议每位新同学先读完。</span><span /></footer>
          </> : <>
          <div className="lesson-topline"><span className={`status-pill ${lesson.week.color}`}>{lesson.week.name} · {lesson.day}</span><span><Clock size={16} /> {lesson.pace}</span></div>
          <h1>{lesson.title}</h1>
          <p className="lesson-goal"><Target size={20} weight="fill" /> {lesson.goal}</p>

          <div className="tab-row" role="tablist" aria-label="当天内容">
            {tabs.map(({ id, label, icon: Icon }) => <button role="tab" aria-selected={activeTab === id} className={activeTab === id ? 'selected' : ''} key={id} onClick={() => setActiveTab(id)}><Icon size={18} />{label}</button>)}
          </div>

          {activeTab === 'lesson' && <article className="content-card overview-card"><p className="eyebrow">TODAY'S MISSION</p><h2>今天先搞清楚什么？</h2><p>{lesson.question}</p><h3>完成后你应当拥有</h3><ul className="overview-list">{lesson.outcomes.map((item) => <li key={item}><CheckCircle size={18} weight="fill" />{item}</li>)}</ul><div className="concept-list">{lesson.concepts.map((item) => <span key={item}>{item}</span>)}</div></article>}

          {activeTab === 'tutorial' && <article className="content-card markdown-lesson"><CourseMarkdown onOpenCode={setExpandedCode}>{lesson.tutorialMarkdown}</CourseMarkdown></article>}
          {activeTab === 'practice' && <article className="content-card instruction-card"><p className="eyebrow">HANDS-ON LAB</p><h2>今天由你操作</h2><ol>{lesson.practice.map((step) => <li key={step}>{step}</li>)}</ol><div className="command-note"><Code size={20} /><span>需要命令时，课件会给出“复制 → 执行 → 观察 → 解释”的小批次，而不是一次性的大段检查。</span></div></article>}
          {activeTab === 'check' && <article className="content-card instruction-card"><p className="eyebrow">ACCEPTANCE</p><h2>完成标准</h2><ul className="check-list">{lesson.checks.map((item) => <li key={item}><CheckCircle size={19} weight="fill" />{item}</li>)}</ul><p className="artifact"><RocketLaunch size={19} /> 复盘问题：<b>{lesson.reflection}</b></p><button className={`complete-button ${completed.has(lesson.day) ? 'done' : ''}`} onClick={() => toggleDone(lesson.day)}>{completed.has(lesson.day) ? <CheckCircle size={19} weight="fill" /> : <Circle size={19} />}{completed.has(lesson.day) ? '已标记完成' : '完成本课后标记'}</button></article>}

          <footer className="lesson-footer"><button onClick={() => go(-1)} disabled={lessonIndex === 0}>← 上一课</button><span>你的节奏优先：产物与验收决定进度，不追赶固定日历。</span><button onClick={() => go(1)} disabled={lessonIndex === lessons.length - 1}>下一课 →</button></footer>
          </>}
        </section>

        <aside className="focus-panel"><p className="eyebrow">CURRENT / FOCUS</p><h2>学习不是“跑过命令”，而是留下证据。</h2><div className="focus-rule"><span>01</span><p>先看任务卡<br /><b>确认目标与概念</b></p></div><div className="focus-rule"><span>02</span><p>再读操作教程<br /><b>按小步骤理解与执行</b></p></div><div className="focus-rule"><span>03</span><p>最后实践与验收<br /><b>把结果变成能力</b></p></div><div className="progress-box"><div><span>主线进度</span><b>{Math.round(completedMainDays / 30 * 100)}%</b></div><div className="progress-track"><i style={{ width: `${completedMainDays / 30 * 100}%` }} /></div><small>{completedMainDays} / 30 个实践单元已完成</small><small>进度仅保存在当前浏览器，不会影响其他访问者。</small></div></aside>
      </div>
      <footer className="site-footer"><span>本项目属于 <b>合肥枢维智能科技有限公司</b></span><span>© 2026 · Apache-2.0 · 版权、专利与商标声明见 LICENSE / NOTICE</span></footer>
      <SourceDialog path={expandedCode} source={courseSourceFiles[expandedCode]} onClose={() => setExpandedCode(null)} />
    </main>
  );
}
