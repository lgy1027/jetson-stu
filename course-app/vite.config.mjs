import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync } from "node:fs";
import path from "node:path";

const courseOrder = [
  { day: 'Day 00', file: 'day-00-environment.md' },
  { day: 'Day 01', file: 'day-01-image-pipeline.md' }, { day: 'Day 02', file: 'day-02-image-ops.md' }, { day: 'Day 03', file: 'day-03-gpu-tensors.md' }, { day: 'Day 04', file: 'day-04-model-inference.md' }, { day: 'Day 05', file: 'day-05-video-inference.md' },
  'day-13-ros2-workspace.md', 'day-14-ros2-topics.md', 'day-15-perception-node.md', 'day-16-parameters-launch.md', 'day-18-rosbag-integration.md',
  'day-07-onnx-export.md', 'day-08-onnx-runtime.md', 'day-09-tensorrt-build.md', 'day-10-backend-benchmark.md', 'day-12-deployment-review.md',
  'day-19-coordinate-math.md', 'day-17-camera-geometry.md', 'day-20-tf2.md', 'day-21-urdf.md', 'day-22-moveit-setup.md',
  'day-23-motion-planning.md', 'day-24-safety-rejection.md', 'day-25-task-schema.md', 'day-26-state-machine.md', 'day-27-perception-to-task.md',
  'day-26-moveit-task-integration.md', 'day-28-end-to-end.md', 'day-29-failure-cases.md', 'day-28-observability.md', 'day-30-final-demo.md',
].map((item) => typeof item === 'string' ? { day: null, file: item } : item);
const courseDir = path.resolve(import.meta.dirname, '../docs/course');
const repositoryRoot = path.resolve(import.meta.dirname, '..');
const virtualCoursewareId = 'virtual:jetson-courseware';
const resolvedVirtualCoursewareId = `\0${virtualCoursewareId}`;

function clean(text) {
  return text.replace(/`/g, '').replace(/\*\*/g, '').replace(/\n+/g, ' ').trim();
}

function section(markdown, heading) {
  const match = markdown.match(new RegExp(`## ${heading}\\n([\\s\\S]*?)(?=\\n## |$)`));
  return match ? match[1].trim() : '';
}

function afterHeading(markdown, heading) {
  const marker = `## ${heading}`;
  const start = markdown.indexOf(marker);
  if (start === -1) return markdown;
  const body = markdown.slice(start + marker.length).replace(/^\s+/, '');
  const end = body.search(/\n## (?:实践|产物与验收|复盘)\n/);
  return (end === -1 ? body : body.slice(0, end)).trim();
}

function list(markdown) {
  return markdown.split('\n').map((line) => line.replace(/^[-*]|^\d+\.\s*/, '').trim()).filter(Boolean).map(clean);
}

function parseCourseware({ file, day }, index) {
  const markdown = readFileSync(path.join(courseDir, file), 'utf8');
  const heading = markdown.match(/^#\s+(.+)$/m)?.[1] || `Day ${index + 1}`;
  const title = heading.replace(/^Day\s+\d+：/, '');
  const question = clean(section(markdown, '今天的问题'));
  const concepts = list(section(markdown, '你要掌握'));
  const practice = list(section(markdown, '实践'));
  const guidedSteps = [...markdown.matchAll(/^##\s+\d+\.\s*(.+)$/gm)].map((match) => clean(match[1]));
  const outcomes = list(section(markdown, '今天完成后你能做到什么'));
  const checks = list(section(markdown, '产物与验收'));
  const reflection = clean(section(markdown, '复盘'));
  const tutorialMarkdown = afterHeading(markdown, '操作教程');
  return {
    day: day || `Day ${String(index).padStart(2, '0')}`,
    title, question, concepts, practice: practice.length ? practice : guidedSteps, outcomes, checks, reflection, source: file,
    markdown: markdown.replace(/^#\s+.+$/m, '').trim(), tutorialMarkdown,
  };
}

function sourceFiles(lessons) {
  const paths = new Set(lessons.flatMap((lesson) => [...lesson.markdown.matchAll(/#course-file:([^\s)]+)/g)]).map((match) => match[1]));
  return Object.fromEntries([...paths].map((relativePath) => {
    const absolutePath = path.resolve(repositoryRoot, relativePath);
    if (!absolutePath.startsWith(`${repositoryRoot}${path.sep}`)) {
      throw new Error(`Course source path escapes repository: ${relativePath}`);
    }
    return [relativePath, readFileSync(absolutePath, 'utf8')];
  }));
}

function coursewarePlugin() {
  return {
    name: 'jetson-courseware',
    resolveId(id) { return id === virtualCoursewareId ? resolvedVirtualCoursewareId : null; },
    load(id) {
      if (id !== resolvedVirtualCoursewareId) return null;
      const foundations = readFileSync(path.join(courseDir, 'foundations.md'), 'utf8')
        .replace(/^#\s+.+$/m, '').trim();
      const lessons = courseOrder.map(parseCourseware);
      return `export const courseLessons = ${JSON.stringify(lessons)};\nexport const courseSourceFiles = ${JSON.stringify(sourceFiles(lessons))};\nexport const foundationsMarkdown = ${JSON.stringify(foundations)};`;
    },
    configureServer(server) {
      server.watcher.add(courseDir);
      server.watcher.add(path.join(repositoryRoot, 'perception'));
    },
    handleHotUpdate({ file, server }) {
      if (!file.startsWith(courseDir) && !file.startsWith(path.join(repositoryRoot, 'perception'))) return;
      const module = server.moduleGraph.getModuleById(resolvedVirtualCoursewareId);
      if (module) server.moduleGraph.invalidateModule(module);
      server.ws.send({ type: 'full-reload' });
      return [];
    },
  };
}

export default defineConfig({
  base: process.env.VITE_BASE_PATH || '/',
  build: {
    outDir: "dist/client",
  },
  optimizeDeps: {
    include: ["react", "react-dom/client"],
  },
  server: {
    host: "0.0.0.0",
    allowedHosts: ["terminal.local"],
    warmup: {
      clientFiles: ["./src/main.jsx"],
    },
  },
  plugins: [coursewarePlugin(), react()],
});
