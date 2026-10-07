# pdf-to-html-deck

**English** | [简体中文](README.zh-CN.md)

[![npm](https://img.shields.io/npm/v/pdf-to-html-deck?color=cb3837&label=npm%20version)](https://www.npmjs.com/package/pdf-to-html-deck)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Node >=18](https://img.shields.io/badge/node-%3E%3D18-339933)](https://nodejs.org)
[![CI](https://github.com/RCliang/pdf-to-html-deck/actions/workflows/ci.yml/badge.svg)](https://github.com/RCliang/pdf-to-html-deck/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/live%20demo-%E5%A4%9C%E8%88%AA%E5%9B%BE%E6%BC%94%E7%A4%BA-0E1930)](https://rcliang.github.io/agent-book/)

Turn a PDF book, handbook, or long report into a **chapter-by-chapter, diagram-rich, animated, single-file HTML slide deck** — zero-dependency output, deployable to GitHub Pages in one push.

> 🎉 **Live demo**: a [67-page "Night Chart" deck](https://rcliang.github.io/agent-book/) generated from a 599-page technical book — the default theme, including 13 code-walkthrough slides. Navigate with ← →, press `T` for the table of contents.

<!-- TODO(record hero GIF, save as docs/demo.gif, then uncomment):
<p align="center"><img src="docs/demo.gif" width="800" alt="pdf-to-html-deck in action"></p>
-->

## Quick start

```bash
npx pdf-to-html-deck init                      # scaffold the project (work/ + shell + spec)
npx pdf-to-html-deck extract book.pdf          # split the PDF into one text file per chapter
# ...write work/fragments/*.html slide fragments (yourself, or let your AI assistant — see below)
npx pdf-to-html-deck build --theme chalkboard  # assemble into a single index.html (5 themes)
npx pdf-to-html-deck deploy                    # write the GitHub Actions workflow, push to go live
```

> Requires a local Python 3 (extraction uses `pypdf`; the CLI detects it and `--setup` auto-installs into a dedicated venv). The build step is stdlib-only.

## What you get

Each chapter becomes 1–3 slides — cards, hand-drawn SVG diagrams, tables, and the key numbers from the book. Chapters with real code listings become **code-walkthrough slides** (annotated code + numbered explanation cards + a "run it" strip). The output is **one `index.html`**: all CSS/JS/content inlined, opens offline with a double-click, prints to one page per slide.

- 1280×720 slide canvas — ← → / Space navigation, `T` table of contents, `F` fullscreen, deep-linkable URLs, progress rail
- Signature per-page "route line" animation (stroke draw + node light-up), respects `prefers-reduced-motion`
- The assembler validates every fragment (unique ids, required metadata, no external resources)

## Themes — same content, one flag

| Night Chart *(default)* | Apple Light | Chalkboard |
|---|---|---|
| <img src="https://raw.githubusercontent.com/RCliang/pdf-to-html-deck/main/docs/themes/night-chart.png" width="360"> | <img src="https://raw.githubusercontent.com/RCliang/pdf-to-html-deck/main/docs/themes/apple-light.png" width="360"> | <img src="https://raw.githubusercontent.com/RCliang/pdf-to-html-deck/main/docs/themes/chalkboard.png" width="360"> |
| deep-indigo nautical chart, serif display | clean white, SF-style type | green blackboard, chalk white |
| *(no flag)* | `--theme apple-light` | `--theme chalkboard` |

| Papercut Vox | Pixel Blue |
|---|---|
| <img src="https://raw.githubusercontent.com/RCliang/pdf-to-html-deck/main/docs/themes/papercut-vox.png" width="360"> | <img src="https://raw.githubusercontent.com/RCliang/pdf-to-html-deck/main/docs/themes/pixel-blue.png" width="360"> |
| cut-paper collage, hard ink borders | deep-blue neon, monospace, scanlines |
| `--theme papercut-vox` | `--theme pixel-blue` |

Themes are injected as a CSS override layer — content and layout contract stay untouched. Drop a `NAME.css` into `work/themes/` for your own. The chosen theme is remembered (`work/theme.txt`), so rebuilds are idempotent; `--theme none` resets.

## CLI reference

| Command | What it does |
|---|---|
| `init [--dir .] [--title "…"]` | Scaffold `work/` (shell, SPEC, order.txt, fragments/) |
| `extract <pdf> [--dir .] [--setup]` | Split by bookmarks → `work/text/chNN.txt` + `work/manifest.json` |
| `build [--dir .] [--out …] [--theme NAME\|none]` | Assemble the single-file deck |
| `theme list` | List built-in + local themes |
| `deploy [--dir .]` | Write `.github/workflows/deploy.yml` + print the go-live steps |
| `install-skill [--dest …]` | Install the ZCode agent skill (SKILL.md + references + scripts/templates/themes) |

## The 7-stage workflow (full methodology ships in `skill/`)

1. **extract** — bookmark-aware chapter split + manifest for planning
2. **shell** — copy the template, pick a theme
3. **spec + golden sample** — `work/SPEC.md` is the fragment contract; write one high-quality exemplar slide first
4. **author fragments** — one `<section>` per slide: concept pages, code pages, part dividers, cover
5. **build** — assemble in `work/order.txt` order + validate
6. **QA** — DOM overflow audits, per-page screenshots, visual review (`skill/references/qa.md`)
7. **deploy** — GitHub Pages

This is where AI coding assistants shine: after `install-skill`, an assistant (ZCode etc.) follows the full SKILL.md pipeline — including parallel fragment authoring and the QA checklist — and builds the deck for you.

```bash
npx pdf-to-html-deck install-skill
# then tell your assistant: "turn this PDF into a chaptered presentation site"
```

## Development & testing

```bash
git clone https://github.com/RCliang/pdf-to-html-deck && cd pdf-to-html-deck
bash test/smoke.sh     # fixture → init/extract/build/theme-switch end-to-end smoke
npm pack --dry-run     # inspect the published contents
```

CI runs the smoke test on every push; pushing a `v*` tag auto-publishes to npm (requires an `NPM_TOKEN` secret).

## License

MIT
