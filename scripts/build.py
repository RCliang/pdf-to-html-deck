#!/usr/bin/env python3
"""build.py — 组装:work/shell.html + work/fragments/*.html → 单文件 index.html

用法:
  python3 build.py [--work work] [--out index.html] [--theme NAME|--theme none]

主题:
  --theme NAME   注入 themes/NAME.css(查找顺序:work/themes/ → 脚本所在 ../themes/)
                 并把 NAME 记入 work/theme.txt;此后不带参数的 build 会沿用该主题
  --theme none   解除主题(删除 work/theme.txt)
  不带 --theme   若 work/theme.txt 存在则自动沿用

顺序来源(二选一,优先 order.txt):
  1. work/order.txt —— 每行一个片段名(不含 .html);# 或空行是注释。
     例:
        cover toc
        part-1 c01a c01b
        end
  2. 无 order.txt 时按文件名排序全量组装(仅适合草稿,扉页顺序会错)。

校验(有问题打印并继续,缺文件才退出非零):
  - 片段必须含 <section>;id 全局唯一;必备 data-part/data-crumb/data-title
  - 禁外部 URL、禁片段内 <script>/<style>(一切样式与行为只在 shell 里;
    主题样式由本脚本注入的 <style data-theme> 覆盖层承担,不算片段违规)
"""
import argparse
import os
import re
import sys

REQ_ATTRS = ("data-part", "data-crumb", "data-title")
THEME_MARK = "</head>"


def find_theme(work, name, script_dir):
    """按 work/themes/ → 脚本../themes/ 顺序找主题 css。"""
    cands = [os.path.join(work, "themes", name + ".css"),
             os.path.normpath(os.path.join(script_dir, "..", "themes", name + ".css"))]
    for c in cands:
        if os.path.exists(c):
            return cands, c
    return cands, None


def resolve_theme(args, work, script_dir):
    """返回 (theme_name, theme_css);处理 flag、记忆文件与解除逻辑。"""
    state = os.path.join(work, "theme.txt")
    name = args.theme
    if name is None and os.path.exists(state):
        name = open(state, encoding="utf-8").read().strip() or None
        if name:
            print(f"· 沿用主题 {name}(work/theme.txt;--theme none 可解除)")
    if name == "none":
        if os.path.exists(state):
            os.remove(state)
        print("· 已解除主题(恢复 shell 默认)")
        return None, None
    if not name:
        return None, None
    cands, hit = find_theme(work, name, script_dir)
    if not hit:
        builtin_dir = os.path.normpath(os.path.join(script_dir, "..", "themes"))
        avail = sorted(f[:-4] for f in os.listdir(builtin_dir) if f.endswith(".css")) \
            if os.path.isdir(builtin_dir) else []
        sys.exit(f"未找到主题 {name}。查找过: {cands[0]}, {cands[1]}\n"
                 f"内置主题: {', '.join(avail) or '(无)'};也可把 NAME.css 放进 work/themes/。")
    css = open(hit, encoding="utf-8").read()
    os.makedirs(work, exist_ok=True)
    open(state, "w", encoding="utf-8").write(name)
    print(f"· 应用主题 {name} ← {hit}")
    return name, css


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="work")
    ap.add_argument("--out", default="index.html")
    ap.add_argument("--theme", default=None,
                    help="主题名(见 themes/);none=解除;缺省沿用 work/theme.txt")
    args = ap.parse_args()

    work = args.work
    frag_dir = os.path.join(work, "fragments")
    shell_path = os.path.join(work, "shell.html")
    order_path = os.path.join(work, "order.txt")
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if not os.path.isdir(frag_dir):
        sys.exit(f"缺 {frag_dir};先产出片段。")
    if not os.path.exists(shell_path):
        sys.exit(f"缺 {shell_path};从 skill 的 assets/shell.template.html 复制并改好标题/tokens。")

    theme_name, theme_css = resolve_theme(args, work, script_dir)

    if os.path.exists(order_path):
        order = []
        for line in open(order_path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#"):
                order.extend(line.split())
    else:
        order = sorted(f[:-5] for f in os.listdir(frag_dir) if f.endswith(".html"))
        print("⚠ 无 order.txt,按文件名排序组装(草稿模式)")

    shell = open(shell_path, encoding="utf-8").read()
    frags, ids, missing, problems = [], [], [], []

    for name in order:
        path = os.path.join(frag_dir, name + ".html")
        if not os.path.exists(path):
            missing.append(name)
            continue
        html = open(path, encoding="utf-8").read().strip()
        secs = re.findall(r"<section\b[^>]*>", html)
        if not secs:
            problems.append(f"{name}: 无 <section>")
        for s in secs:
            m = re.search(r'id="([^"]+)"', s)
            sid = m.group(1) if m else "(no-id)"
            if sid in ids:
                problems.append(f"{name}: 重复 id {sid}")
            ids.append(sid)
            for attr in REQ_ATTRS:
                if attr + '="' not in s:
                    problems.append(f"{name}/{sid}: 缺 {attr}")
        if re.search(r"https?://", html):
            problems.append(f"{name}: 含外部 URL")
        if "<script" in html.lower() or "<style" in html.lower():
            problems.append(f"{name}: 含 script/style")
        frags.append(f"<!-- ▸ {name} -->\n{html}")

    out = shell.replace("<!--FRAGMENTS-->", "\n\n".join(frags))

    # 主题注入:</head> 前追加覆盖层;同特异性下后写的规则胜出,故能覆写 shell 默认
    if theme_css:
        if THEME_MARK not in out:
            sys.exit("shell 中找不到 </head>,无法注入主题。")
        block = f'<style data-theme="{theme_name}">\n{theme_css}\n</style>\n'
        out = out.replace(THEME_MARK, block + THEME_MARK, 1)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)

    theme_note = f" · 主题 {theme_name}" if theme_name else ""
    print(f"✓ 写出 {args.out} ({os.path.getsize(args.out) / 1024:.0f} KB){theme_note} · "
          f"片段 {len(frags)}/{len(order)} · 节 {len(ids)} 个")
    if missing:
        print("✗ 缺失:", ", ".join(missing))
    if problems:
        print("⚠ 问题:")
        for p in problems:
            print("  -", p)
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
