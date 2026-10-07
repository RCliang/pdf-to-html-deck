# pdf-to-html-deck

把一本 PDF 书籍/手册/长报告,变成**按章节、图文并茂、带动画的单文件 HTML 演示站点**——零依赖输出,可直接部署到 GitHub Pages。

> 🎉 **在线 Demo**:用本工具从一本 599 页的技术书生成的 [67 页「夜航图」演示](https://rcliang.github.io/agent-book/)(五套主题中的默认款,含 13 页代码讲解页;← → 翻页,`T` 看目录)。

```bash
npx pdf-to-html-deck init                     # 在当前目录搭起项目骨架(work/ + 外壳 + 规范)
npx pdf-to-html-deck extract book.pdf         # 按书签把 PDF 拆成「每章一个文本文件」
# ……用你(或你的 AI 助手)按 work/SPEC.md 写 work/fragments/*.html 页面片段
npx pdf-to-html-deck build --theme chalkboard # 组装成单文件 index.html(五套主题可选)
npx pdf-to-html-deck deploy                   # 写入 GitHub Actions workflow,推上去即上线
```

> 需要本机有 Python 3(提取阶段用 `pypdf`;缺了 CLI 会提示,`--setup` 可自动安装)。构建阶段仅标准库。

## 它解决什么问题

把书变成"可放映的讲义":每章提炼成 1-3 页幻灯片(卡片 + 手绘 SVG 图 + 表格 + 关键数字),
书中有真实代码的章节可以做成「代码讲解页」(代码 + ①②③ 逐点讲解)。输出是**一个
index.html**——所有 CSS/JS/内容内联,双击即开,离线可用,打印导出 PDF 每页一纸。

- 1280×720 幻灯片画布,← →/空格翻页、`T` 目录、`F` 全屏、hash 直达、进度轨
- 每页自带"航线"签名动效(描线 + 节点点亮),遵循 `prefers-reduced-motion`
- 组装器校验片段契约(唯一 id、必备元数据、禁外部资源)

## 主题预设(换肤不动内容)

| 主题 | 风格 | `--theme` |
|---|---|---|
| 夜航图(默认) | 深靛蓝 + 航图网格 + 宋体 + 三色信标 | *(不带参数)* |
| 苹果白 | 白底、SF 系字体、克制蓝、深色代码块 | `apple-light` |
| Vox 剪纸 | 米纸底、墨色硬边框、错位实体阴影 | `papercut-vox` |
| 黑板粉笔 | 墨绿板面、粉笔白、虚线手绘框 | `chalkboard` |
| 深蓝像素 | 深夜蓝、霓虹青/街机黄、等宽、扫描线 | `pixel-blue` |

主题以 CSS 覆盖层注入(`build.py --theme NAME`),自定义皮肤只需把 `NAME.css` 放进
`work/themes/`。主题切换有记忆:写入 `work/theme.txt`,重复构建幂等;`--theme none` 解除。

## 命令

| 命令 | 作用 |
|---|---|
| `init [--dir .] [--title "书名"]` | 建骨架:`work/`(shell/SPEC/order.txt/fragments/)` |
| `extract <pdf> [--dir .] [--setup]` | 调 `scripts/extract_pdf.py` 拆章;产物 `work/text/chNN.txt` + `work/manifest.json` |
| `build [--dir .] [--out index.html] [--theme NAME\|none]` | 调 `scripts/build.py` 组装单文件 |
| `theme list` | 列出内置 + `work/themes/` 自定义主题 |
| `deploy [--dir .]` | 写入 `.github/workflows/deploy.yml` 并打印上线三步 |
| `install-skill [--dest ~/.agents/skills/pdf-to-html-deck]` | 把 ZCode 技能(SKILL.md + references + 脚本/模板/主题)装进技能目录 |

## 七阶段工作流(完整方法论文档在 `skill/`)

1. **extract** — 书签拆章 + manifest(规划页数与分工)
2. **init/搭壳** — 复制 shell 模板、替换标题占位符、选主题
3. **规范 + 金标准** — `work/SPEC.md` 是片段契约;先亲手写一张高质量范本页
4. **并行产出片段** — 每页一个 `<section>`,概念页/代码页/扉页/封面
5. **build** — 按 `work/order.txt` 组装 + 校验
6. **QA** — DOM 溢出审计 + 逐页截图 + 视觉验收(详见 skill/references/qa.md)
7. **deploy** — GitHub Pages

配合 AI 编码助手(ZCode 等)效率最高:`install-skill` 后,助手会按 SKILL.md 的完整管线
(含子代理并行撰写片段的调度策略与 QA 清单)替你把书做成站点。

## 作为 ZCode 技能使用

```bash
npx pdf-to-html-deck install-skill
```

之后对助手说"把这本 PDF 做成章节演示网页",技能即被触发。

## 开发与测试

```bash
git clone https://github.com/RCliang/pdf-to-html-deck && cd pdf-to-html-deck
bash test/smoke.sh     # 生成 fixture → init/extract/build/主题切换 全链路冒烟
npm pack --dry-run     # 查看发布包内容
```

CI:push 跑冒烟;打 `v*` 标签自动 `npm publish`(需在仓库 Secrets 配 `NPM_TOKEN`)。

## License

MIT
