---
name: pdf-to-html-deck
description: 把一本 PDF 书籍/手册/长报告做成「按章节、图文并茂、带动画」的单文件 HTML 演示站点,并用 GitHub Actions 部署到 GitHub Pages。凡用户想"把这本书/PDF/文档做成网页、演示、幻灯片、阅读笔记站、章节导览页",或要复用夜航图(Night Chart)演示管线,或提到 PDF→HTML/PPT 式页面/上线 GitHub Pages——即使只丢来一个 PDF 文件——都必须使用本 skill。
---

# PDF → 单文件 HTML 演示站点(章节式 · 图文 · 动画 · GitHub Pages)

把一本书变成一个 `index.html`:按书的「部分/章」组织成幻灯片,每章提炼 1-3 页概念页(手绘 SVG 图+表格+数字),书中有真实代码的章节加「代码讲解页」,单文件零依赖,浏览器直开,可推上 GitHub Pages。

全流程七个阶段。**先读本文件通读一遍再动手**;阶段 2/5/6 的细节按需读 references/。

## 阶段 0:盘点输入

```
python3 <skill>/scripts/extract_pdf.py <book.pdf> -o work/text
```

输出 `work/text/chNN.txt`(每章全文,页首带 `[pN]` 页码)+ `work/manifest.json`(章号/标题/部分/页码范围/字数)。
- 依赖书签(PDF outline);无书签的 PDF 会直接报错——告知用户先加书签,或按页码区间手工分章(把文本切块写成 chNN.txt + 自写 manifest.json,后续阶段不变)。
- 抽查 1-2 个 chNN.txt 确认中文/代码提取质量。代码缩进会被拍平属正常,代码页阶段按语法重排。
- 用 manifest 规划页面:<3000 字的章并页或跳过;大章(正文 >15K 字)拆 2-3 页;含代码 Listing 的章登记为代码页。
- 目标规模:每 10 章书 ≈ 15-20 页概念页;全书含封面/目录/扉页/尾页约 40-70 页。

## 阶段 1:搭壳(选主题)

1. `cp <skill>/assets/shell.template.html work/shell.html`
2. 替换占位符:`{{DECK_TITLE}}`(书名+风格名)、`{{CORNER_TL_A/B}}`、`{{CORNER_BR_A/B}}`(四角装饰小字)。

**主题预设库**(皮肤可换、骨架与片段契约不变):

| 主题名 | 风格 | 适配 |
|---|---|---|
| *(默认)* | 夜航图 Night Chart:深靛蓝+网格+宋体+三色信标 | 技术/工程书 |
| `apple-light` | 白色简约苹果风:白底、SF 字体、克制蓝、代码块深色 | 通用、产品向 |
| `papercut-vox` | Vox 剪纸风:米纸底、墨色硬边框+错位实体阴影、海报感 | 人文/科普/大众读物 |
| `chalkboard` | 黑板粉笔:墨绿板、粉笔白、虚线手绘框 | 教学/课程 |
| `pixel-blue` | 深蓝像素:深夜蓝、霓虹青/街机黄、等宽、直角+扫描线 | 游戏/极客向 |

```
python3 <skill>/scripts/build.py --theme apple-light   # 应用并记入 work/theme.txt
python3 <skill>/scripts/build.py --theme none          # 解除
```
不带 `--theme` 时沿用 `work/theme.txt`,重复构建幂等;自定义主题把 `NAME.css` 放 `work/themes/` 即可被 `--theme NAME` 找到。

**自建主题须知**(照抄内置主题文件的结构):① 重定义 `:root` 全部 tokens;② 覆写 shell 里硬编码 rgba 的选择器(`body::before/::after`、`.stage`、`.k-card` 及其角标、`.fig`、`.k-code pre` 底/字色、`.k-callout`、`.k-tag` 变体、`.div-num`、`#toc/#hud/#rail` 等);③ 浅色主题必须加两条 SVG 修正:`.fig [fill="var(--ink0)"]{…浅色…}`(否则结构块变黑块吞标签)与 `.fig [stroke^="rgba(78,201"]{…}`(硬编码青连线换主题色);④ 保证二级文字(=muted/faint)对底色对比度 ≥4:1。注入原理:build 把主题 css 作为 `<style data-theme>` 追加在 `</head>` 前,同特异性下后写胜出。

3. (可选)深度定制:改 shell 顶部 tokens 与组件 CSS,**类名与结构不动**——规范、脚本、子代理模板都依赖类名。

壳已含:1280×720 舞台居中缩放、←→/空格翻页、T 目录浮层、F 全屏、hash 定位(`#/页码`)、进度轨、打印导出(每页一纸)、prefers-reduced-motion 适配。

## 阶段 2:定规范 + 金标准

1. `cp <skill>/references/design-spec.md work/SPEC.md`,按书微调(页码引用、示例)。
2. **主代理亲写金标准示范页 1 张**(挑中等篇幅、有数字有结构图的一章)到 `work/fragments/`。这张页是全卷质量天花板,子代理以其为范本。
3. 建 `work/order.txt`(片段顺序表,见阶段 4)。

## 阶段 3:并行产出片段

按 `references/authoring-prompts.md` 的模板派子代理(要点:后台并发 ≤2,可 2 后台+1 前台流水线;模板必须自包含绝对路径与产出清单;「整页放得下」是硬约束)。

- **主代理自写框架页**:封面、总目录/航线图、各部分扉页(章列表+书页码)、尾页(阅读路径)。
- **子代理写概念页与代码页**:每组任务带三件套——SPEC + 金标准 + 章节原文绝对路径。
- 每完成一批:更新 `work/order.txt`、跑 build、抽查渲染,再补发下一组。

## 阶段 4:组装

```
python3 <skill>/scripts/build.py            # 读 work/shell.html + order.txt + fragments/ → index.html
```

校验片段 id 唯一、必备 data-* 属性、无外部 URL/script/style;缺文件退出非零并列名。
**id 撞名是最大坑**:片段 id 不得用 `toc/cover/rail/hud/…`(壳已占用,见 design-spec)。

## 阶段 5:QA 循环

按 `references/qa.md` 执行,顺序固定:
1. DOM 精确审计(全卷一次 evaluate:正文溢出/代码末行裁切/横幅叠压);
2. 逐页截图存 `work/render/pNN.png`(整视口、强制重绘、体积>60KB 判有效);
3. visual-judge 子代理分批验收(18 页/个),fail 项亲自复核后修复;
4. 修复 → build → 重渲受影响页,直到清零。

## 阶段 6:部署

按 `references/deployment.md`:加 `.github/workflows/deploy.yml`(单文件静态,upload+deploy-pages 两步),git init/push,仓库 Settings → Pages → Source: GitHub Actions。可选在 CI 里跑 build 从片段自动组装。

## 节奏与预算参考(实战值)

| 环节 | 一本 600 页/30 章的书 |
|---|---|
| 提取+规划 | ~2 分钟 |
| 壳+规范+金标准 | 主代理 1-2 轮 |
| 50-65 页片段 | 15-20 个子代理任务(并发 2-3,数小时) |
| QA+修复 | 3 轮验收,首轮通常 85-90% pass |
| 部署 | workflow 一次通过 |

## 何时读哪个参考文件

- `references/design-spec.md` — 写任何页面前(主代理与每个子代理都要读);也是复制为 work/SPEC.md 的底稿。
- `references/authoring-prompts.md` — 派子代理前。
- `references/qa.md` — 组装完成后。
- `references/deployment.md` — 内容定稿后。
