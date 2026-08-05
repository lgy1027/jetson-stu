# Jetson Studio 课程工作台

本目录是课程的 Vite + React 前端。课程正文来自仓库根目录的 `docs/course/`，不会在前端复制一份内容。

## 本地运行

```bash
cd course-app
npm install
npm run dev
```

浏览器打开终端显示的本地地址。页面提供 6 周、30 个课程日的展开导航，以及课件、教程、实践、验收和本地完成进度。

## 生产构建

```bash
npm run build
```

## GitHub Pages

根目录的 `.github/workflows/deploy-course.yml` 会在 `main` 分支的课程内容或前端变更推送后构建并发布。它会根据仓库名设置 Vite 的资源路径，因此可部署到 `https://<owner>.github.io/<repo>/` 这种项目站点路径。

首次发布前，在 GitHub 仓库的 **Settings → Pages** 中将 Source 设为 **GitHub Actions**。推送工作流后，在 Actions 中查看部署结果；仓库为私有时，还需要你的 GitHub 方案支持私有仓库 Pages 访问。
