#!/usr/bin/env node
'use strict';
/*
 * pdf-to-html-deck — PDF 书籍 → 单文件 HTML 演示站点
 *
 * 子命令:init / extract / build / theme / deploy / install-skill
 * 设计约束:零 npm 依赖;只写目标项目目录,无网络行为,无破坏性操作。
 * 技能资产(SKILL.md + references + scripts + assets + themes)自包含在
 * skills/pdf-to-html-deck/ 下,本 CLI 与 skills.sh CLI(npx skills add)共用同一布局。
 * Python 侧脚本(skills/pdf-to-html-deck/scripts/*.py)由本 CLI 探测解释器后代跑:
 *   - extract 需要 pypdf(探测可用解释器;--setup 可自动 pip 安装)
 *   - build 仅标准库
 */
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const PKG = path.resolve(__dirname, '..');
const SKILL_DIR = path.join(PKG, 'skills', 'pdf-to-html-deck');
const EXTRACT = path.join(SKILL_DIR, 'scripts', 'extract_pdf.py');
const BUILD = path.join(SKILL_DIR, 'scripts', 'build.py');
const SHELL_TPL = path.join(SKILL_DIR, 'assets', 'shell.template.html');
const THEMES_DIR = path.join(SKILL_DIR, 'themes');

const DEPLOY_YML = `name: Deploy deck to Pages
on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: \${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - id: deployment
        uses: actions/deploy-pages@v4
`;

const USAGE = `pdf-to-html-deck — 把 PDF 书做成单文件 HTML 演示站点

用法:
  pdf-to-html-deck init   [--dir .] [--title "书名"]
  pdf-to-html-deck extract <book.pdf> [--dir .] [--setup] [extract_pdf.py 其余参数]
  pdf-to-html-deck build  [--dir .] [--out index.html] [--theme NAME|none]
  pdf-to-html-deck theme  list
  pdf-to-html-deck deploy [--dir .]
  pdf-to-html-deck install-skill [--dest ~/.agents/skills/pdf-to-html-deck]

主题: apple-light | papercut-vox | chalkboard | pixel-blue(缺省=夜航图;--theme none 解除)
环境: Node >=18;extract 需要带 pypdf 的 Python 3(可用 PDF2DECK_PYTHON 指定解释器,--setup 自动安装)
`;

function log(msg) { console.log(msg); }
function die(msg, code = 1) { console.error('✗ ' + msg); process.exit(code); }

/* ---------- 参数解析 ---------- */
function parseArgs(argv) {
  const opt = { _: [] };
  const valued = new Set(['--dir', '--out', '--theme', '--title', '--dest']);
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (valued.has(a)) { opt[a.slice(2)] = argv[++i]; }
    else if (a.startsWith('--')) { opt[a.slice(2)] = true; }
    else opt._.push(a);
  }
  return opt;
}

/* ---------- Python 探测 ----------
 * 顺序:PDF2DECK_PYTHON 环境变量 → ~/.pdf-to-html-deck/venv(--setup 自动创建)→
 * PATH 候选(逐个验证可 import pypdf)→ 任一可用的解释器(供 --setup 建 venv)。
 * HomeBrew 等外部管理(PEP 668)环境不允许全局 pip,故 --setup 走独立 venv。 */
const ENV_DIR = path.join(os.homedir(), '.pdf-to-html-deck');
const VENV_PY = path.join(ENV_DIR, 'venv', 'bin', 'python');

function pythonCandidates() {
  return [
    process.env.PDF2DECK_PYTHON,
    VENV_PY,
    'python3.13', 'python3.12', 'python3.11', 'python3.10', 'python3.9',
    'python3', 'python',
  ].filter(Boolean);
}
function pickPython({ needPypdf = false, setup = false } = {}) {
  let firstExisting = null;
  for (const py of pythonCandidates()) {
    const exists = spawnSync(py, ['--version'], { stdio: 'ignore' });
    if (exists.error) continue;
    if (firstExisting === null) firstExisting = py;
    if (!needPypdf) return py;
    const ok = spawnSync(py, ['-c', 'import pypdf'], { stdio: 'ignore' });
    if (ok.status === 0) return py;
  }
  if (!firstExisting) die('未找到 Python 3,请先安装(https://python.org)。');
  if (setup) {
    log(`· 用 ${firstExisting} 创建独立 venv(${VENV_PY})并安装 pypdf …`);
    const venv = spawnSync(firstExisting, ['-m', 'venv', path.join(ENV_DIR, 'venv')], { stdio: 'inherit' });
    if (venv.status !== 0) die('venv 创建失败,可手动: python3 -m venv ~/.pdf-to-html-deck/venv');
    const pip = spawnSync(VENV_PY, ['-m', 'pip', 'install', '--quiet', 'pypdf'], { stdio: 'inherit' });
    if (pip.status !== 0) die('pip install pypdf 失败(可在 venv 内手动重试)');
    return VENV_PY;
  }
  die(`Python 缺少 pypdf。三种解法任选:① extract 时加 --setup(自动建 venv 并安装,推荐);`
      + `② pip3 install pypdf;③ 设 PDF2DECK_PYTHON 指向已有 pypdf 的解释器`);
}
function run(py, args) {
  const r = spawnSync(py, args, { stdio: 'inherit' });
  if (r.status !== 0) process.exit(r.status || 1);
}

/* ---------- 工具 ---------- */
function mkdirp(p) { fs.mkdirSync(p, { recursive: true }); }
function copyDir(src, dst) {
  mkdirp(dst);
  for (const name of fs.readdirSync(src)) {
    const s = path.join(src, name), d = path.join(dst, name);
    if (fs.statSync(s).isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}
function projectDir(opt) {
  const dir = path.resolve(opt.dir || '.');
  if (!fs.existsSync(dir)) die(`目录不存在: ${dir}`);
  return dir;
}
function listThemes(dir) {
  const out = [];
  const local = path.join(dir, 'work', 'themes');
  for (const base of [THEMES_DIR, local]) {
    if (!fs.existsSync(base)) continue;
    for (const f of fs.readdirSync(base).sort()) {
      if (f.endsWith('.css')) out.push({ name: f.slice(0, -4), from: path.basename(base) === 'themes' && base === THEMES_DIR ? '内置' : '本地' });
    }
  }
  return out;
}

/* ---------- 子命令 ---------- */
function cmdInit(opt) {
  const dir = path.resolve(opt.dir || '.');
  mkdirp(dir);
  const work = path.join(dir, 'work');
  for (const sub of ['fragments', 'text', 'themes']) mkdirp(path.join(work, sub));

  // 外壳:模板 → work/shell.html(可 --title 直接替换标题占位符)
  let shell = fs.readFileSync(SHELL_TPL, 'utf8');
  const placeholders = ['{{DECK_TITLE}}', '{{CORNER_TL_A}}', '{{CORNER_TL_B}}', '{{CORNER_BR_A}}', '{{CORNER_BR_B}}'];
  if (opt.title) shell = shell.replace('{{DECK_TITLE}}', opt.title);
  fs.writeFileSync(path.join(work, 'shell.html'), shell);

  // 片段契约(供人或 AI 按 SPEC 写页面)
  const specSrc = path.join(SKILL_DIR, 'references', 'design-spec.md');
  if (fs.existsSync(specSrc)) fs.copyFileSync(specSrc, path.join(work, 'SPEC.md'));

  const orderStub = `# 顺序表:每行若干片段名(不含 .html);# 开头为注释。\n`
    + `# 第一张通常是 cover,随后 toc / part-N / 章节页 / end,例如:\n`
    + `# cover toc\n# part-1 c01a c01b\n# end\n`;
  const orderPath = path.join(work, 'order.txt');
  if (!fs.existsSync(orderPath)) fs.writeFileSync(orderPath, orderStub);

  log(`✓ 已初始化 ${dir}`);
  if (!opt.title) log(`· 记得编辑 work/shell.html 里的占位符: ${placeholders.join(' ')}`);
  log(`· 下一步: pdf-to-html-deck extract <book.pdf> --dir ${dir}`);
}

function cmdExtract(opt) {
  const pdf = opt._[0];
  if (!pdf || !fs.existsSync(pdf)) die(`请给出存在的 PDF 路径(收到: ${pdf || '无'})`);
  const dir = projectDir(opt);
  const py = pickPython({ needPypdf: true, setup: !!opt.setup });
  const forwarded = opt._.slice(1).concat(
    opt.minPages ? ['--min-pages', String(opt.minPages)] : []);
  run(py, [EXTRACT, pdf, '-o', path.join(dir, 'work', 'text'), ...forwarded]);
  log(`· 下一步: 按 work/SPEC.md 写 work/fragments/*.html 与 work/order.txt,然后 build`);
}

function cmdBuild(opt) {
  const dir = projectDir(opt);
  const py = pickPython();
  const args = [BUILD, '--work', path.join(dir, 'work'),
                '--out', opt.out ? path.resolve(opt.out) : path.join(dir, 'index.html')];
  if (opt.theme !== undefined) args.push('--theme', opt.theme);
  run(py, args);
}

function cmdTheme(opt) {
  const sub = opt._[0] || 'list';
  if (sub !== 'list') die(`未知子命令 theme ${sub}(仅支持 theme list)`);
  const rows = listThemes(process.cwd());
  log('内置主题(缺省=夜航图,无需参数):');
  for (const r of rows.filter(r => r.from === '内置')) log(`  ${r.name}`);
  const local = rows.filter(r => r.from !== '内置');
  if (local.length) { log('work/themes/ 自定义:'); for (const r of local) log(`  ${r.name}`); }
  log('用法: build --theme <名称>;--theme none 解除并恢复默认');
}

function cmdDeploy(opt) {
  const dir = projectDir(opt);
  const wf = path.join(dir, '.github', 'workflows', 'deploy.yml');
  mkdirp(path.dirname(wf));
  fs.writeFileSync(wf, DEPLOY_YML);
  log(`✓ 已写入 ${wf}`);
  log(`上线(gh 一条龙,推荐):\n  gh repo create <repo> --public --source=. --push`
      + `\n  gh api --method POST repos/<user>/<repo>/pages -f build_type=workflow`);
  log(`或手动: git init && git add . && git commit -m "deck" && git branch -M main`
      + `\n        git remote add origin <url> && git push -u origin main`
      + `\n        仓库 Settings → Pages → Source: GitHub Actions`);
  log(`提示: push 报 "without workflow scope" 时,先 gh auth refresh -h github.com -s workflow 再重推`);
}

function cmdInstallSkill(opt) {
  const dest = path.resolve(opt.dest || path.join(os.homedir(), '.agents', 'skills', 'pdf-to-html-deck'));
  if (fs.existsSync(dest)) log(`· 目标已存在,将覆盖更新: ${dest}`);
  copyDir(SKILL_DIR, dest);                       // SKILL.md + references/ + scripts/ + assets/ + themes/ 自包含
  log(`✓ 技能已安装: ${dest}`);
  log(`· 重启会话后对 AI 助手说"把这本 PDF 做成章节演示网页"即可触发`);
}

/* ---------- 入口 ---------- */
function main() {
  const [cmd, ...rest] = process.argv.slice(2);
  const opt = parseArgs(rest);
  switch (cmd) {
    case 'init': return cmdInit(opt);
    case 'extract': return cmdExtract(opt);
    case 'build': return cmdBuild(opt);
    case 'theme': return cmdTheme(opt);
    case 'deploy': return cmdDeploy(opt);
    case 'install-skill': return cmdInstallSkill(opt);
    case undefined:
    case 'help':
    case '--help':
    case '-h': log(USAGE); return;
    case '--version':
    case '-v': log(require(path.join(PKG, 'package.json')).version); return;
    default: die(`未知命令: ${cmd}\n\n${USAGE}`, 2);
  }
}
main();
