# 部署:GitHub Actions → GitHub Pages

产物是**单文件静态 `index.html`**(零依赖、零构建),部署即"把文件放进 Pages"。

## 一、放入 workflow

仓库结构(推荐把 `work/` 一并入库,片段可迭代):

```
<repo>/
├── index.html                  # 成品(根路径,Pages 直接服务)
├── book.pdf                    # 源书(可选;注意版权,公开仓库不要带!)
├── work/                       # 管线中间产物(text/ fragments/ shell.html order.txt build 脚本)
└── .github/workflows/deploy.yml
```

`.github/workflows/deploy.yml`:

```yaml
name: Deploy deck to Pages
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
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .            # index.html 在仓库根;在子目录则改 path
      - id: deployment
        uses: actions/deploy-pages@v4
```

## 二、上线:gh CLI 一条龙(推荐)

```bash
brew install gh && gh auth login          # 首次;浏览器授权一次

cd <项目根>
# 推前把源书挡在公开仓库外(deck 已含全部提炼内容)
echo "book.pdf" >> .gitignore

git init && git add . && git commit -m "deck: <书名> 演示"
git branch -M main
gh repo create <repo> --public --source=. --push

# 打开 Pages 的 Actions 部署源(免浏览器)
gh api --method POST repos/<user>/<repo>/pages -f build_type=workflow
```

推完即触发 Actions;1-2 分钟后站点在 `https://<user>.github.io/<repo>/`。
此后每次改片段 → `python3 work/build.py` 重建 → `git push` 自动重新部署。

## 三、上线:无 gh 的手动路径

1. github.com → New repository(名字如 `agent-book`)→ **不要**勾选任何初始化文件;
2. `git init && git add . && git commit -m "deck" && git branch -M main`;
3. `git remote add origin git@github.com:<user>/<repo>.git && git push -u origin main`
   (或 https 地址,首次推送按提示完成凭据);
4. 仓库 **Settings → Pages → Source 选 "GitHub Actions"**(只需一次)。

## 四、故障排查(实战清单)

| 症状 | 原因与修复 |
|---|---|
| push 被拒:`refusing to allow a Personal Access Token to create or update workflow ... without workflow scope` | 令牌缺 `workflow` 权限(HTTPS 推送含 workflow 文件的提交必须有)。修复:`gh auth refresh -h github.com -s workflow`(浏览器授权一次)后重推 `git push -u origin main`。自建 classic PAT 则到 Settings → Developer settings → Tokens 勾选 workflow;Fine-grained PAT 给 Workflows 读写权限 |
| `gh api ... /pages` 返回 already_exists | Pages 已开过:改 `gh api --method PATCH repos/<user>/<repo>/pages -f build_type=workflow`,或浏览器切 Source |
| Actions 全绿但 404 | Pages 源还没切到 "GitHub Actions"(默认 legacy 分支模式);或 index.html 不在 `upload-pages-artifact` 的 `path` 下 |
| 想私有仓库 | Pages 公开站点需 public 仓;私库仅 GitHub 付费计划支持 Pages,否则改 public 或换 Cloudflare Pages |

## 五、可选:CI 内重建

若希望 push 片段后 CI 自动组装(而不是提交 index.html),在 deploy 前加一步:

```yaml
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python work/build_scripts/build.py   # 把 build.py 复制进仓库并调路径
```

静态单文件已含全部 CSS/JS,无需 npm/构建链。
